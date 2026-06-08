#!/usr/bin/env python3
"""
Duval County Official Records Scraper
Source: https://or.duvalclerk.com/
Portal Type: Tyler Technologies / Kendo UI (requires JavaScript + Browserless)

Uses Browserless API for cloud-based Playwright execution.
Token passed as query parameter: ?token=...
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://chrome.browserless.io')

class DuvalOfficialRecordsScraper:
    SOURCE_ID = "duval_official_records"
    BASE_URL = "https://or.duvalclerk.com"
    
    # Document type IDs from Kendo ComboBox
    DOC_TYPES = {
        'LIS PENDENS': '104',
        'MORTGAGE': '110',
        'LIEN': '103',
        'JUDGMENT': '97',
        'FORECLOSURE': '104',
        'NOTICE': '120',
        'DEED': '87',
        'QUIT CLAIM': '87',
        'TRUST': '131',
        'PROBATE': '92',
        'ASSIGNMENT': '75',
        'SATISFACTION': '129',
        'RELEASE': '126',
    }
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_browserless(self, doc_type_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Scrape using Browserless API for cloud-based browser automation."""
        records = []
        
        # Browserless script to navigate and extract data
        script = f"""
        async ({{ page }}) => {{
            const records = [];
            try {{
                // Navigate and accept disclaimer
                await page.goto('{self.BASE_URL}/', {{ waitUntil: 'networkidle' }});
                await page.locator('input[type="submit"]').first.click();
                await page.waitForLoadState('networkidle');
                
                // Go to Doc Type search
                await page.goto('{self.BASE_URL}/search/SearchTypeDocType', {{ waitUntil: 'networkidle' }});
                
                // Set Kendo ComboBox value via JavaScript
                await page.evaluate((docTypeId) => {{
                    const combo = $("#DocTypesDisplay").data("kendoComboBox");
                    if (combo) {{
                        combo.value(docTypeId);
                        combo.trigger("change");
                    }}
                }}, '{doc_type_id}');
                await page.waitForTimeout(500);
                
                // Fill dates (MM/DD/YYYY format)
                await page.locator('#RecordDateFrom').first.fill('{start_date}');
                await page.locator('#RecordDateTo').first.fill('{end_date}');
                
                // Submit
                await page.locator('input[type="submit"]').first.click();
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(3000);
                
                // Extract data from Kendo Grid
                const gridData = await page.evaluate(() => {{
                    const grid = $("#RsltsGrid").data("kendoGrid");
                    if (grid) {{
                        const data = grid.dataSource.data();
                        return data.map(item => ({{
                            instrument_number: item.InstrumentNumber || '',
                            record_date: item.RecordDate || '',
                            doc_type: item.DocTypeDescription || '',
                            direct_name: item.DirectName || '',
                            indirect_name: item.IndirectName || '',
                            book_page: item.BookPage || '',
                            book_type: item.BookType || '',
                            consideration: item.Consideration || '',
                            legal_description: item.DocLegalDescription || ''
                        }}));
                    }}
                    return [];
                }});
                
                records.push(...gridData);
            }} catch (e) {{
                console.error('Error:', e.message);
            }}
            return records;
        }}
        """
        
        try:
            response = requests.post(
                f"{BROWSERLESS_URL}/function?token={BROWSERLESS_TOKEN}",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "code": script,
                    "context": {}
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    records = result
                elif isinstance(result, dict) and 'data' in result:
                    records = result['data']
            else:
                print(f"Browserless error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"Browserless request failed: {e}")
        
        return records
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """Search official records by date range."""
        records = []
        
        # Convert dates to MM/DD/YYYY format
        start_parts = start_date.split('-')
        end_parts = end_date.split('-')
        start_formatted = f"{start_parts[1]}/{start_parts[2]}/{start_parts[0]}"
        end_formatted = f"{end_parts[1]}/{end_parts[2]}/{end_parts[0]}"
        
        # Document types that indicate distress
        distress_doc_types = doc_types or [
            'LIS PENDENS', 'MORTGAGE', 'LIEN', 'JUDGMENT',
            'FORECLOSURE', 'NOTICE', 'DEED', 'QUIT CLAIM',
            'TRUST', 'PROBATE', 'ASSIGNMENT', 'SATISFACTION', 'RELEASE'
        ]
        
        for doc_type in distress_doc_types:
            doc_type_id = self.DOC_TYPES.get(doc_type)
            if not doc_type_id:
                continue
            
            try:
                parsed_records = self._scrape_with_browserless(
                    doc_type_id, start_formatted, end_formatted
                )
                
                # Add metadata
                for rec in parsed_records:
                    rec['source_id'] = self.SOURCE_ID
                    rec['search_doc_type'] = doc_type
                    rec['scraped_at'] = datetime.now().isoformat()
                
                records.extend(parsed_records)
                
            except Exception as e:
                continue
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        records = self.search_by_date_range(start_date, end_date)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(records),
            'new_records': records,
            'updated_cursor': end_date,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'note': 'Using Browserless API with token query parameter'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://or.duvalclerk.com/'}
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
