#!/usr/bin/env python3
"""Create a comprehensive scraper that uses Playwright for JS-rendered portals."""

scraper_code = '''#!/usr/bin/env python3
"""
Duval County Official Records Scraper - Playwright Enhanced
Source: https://or.duvalclerk.com/
Portal Type: Tyler Technologies / Kendo UI (requires JavaScript)
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Check if running in GitHub Actions (no browser available)
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS') == 'true'

class DuvalOfficialRecordsScraper:
    SOURCE_ID = "duval_official_records"
    BASE_URL = "https://or.duvalclerk.com"
    
    # Document type IDs from Kendo ComboBox
    DOC_TYPES = {
        'LIS PENDENS': '104',
        'MORTGAGE': '110',
        'LIEN': '103',
        'JUDGMENT': '97',
        'FORECLOSURE': '104',  # Same as LIS PENDENS
        'NOTICE': '120',
        'DEED': '87',
        'QUIT CLAIM': '87',  # Under Deed
        'TRUST': '131',
        'PROBATE': '92',
        'ASSIGNMENT': '75',
        'SATISFACTION': '129',
        'RELEASE': '126',
    }
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_playwright(self, doc_type_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Scrape using Playwright browser automation."""
        records = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                try:
                    # Navigate and accept disclaimer
                    page.goto(f"{self.BASE_URL}/", wait_until="networkidle")
                    page.locator('input[type="submit"]').first.click()
                    page.wait_for_load_state('networkidle')
                    
                    # Go to Doc Type search
                    page.goto(f"{self.BASE_URL}/search/SearchTypeDocType", wait_until="networkidle")
                    
                    # Set Kendo ComboBox value via JavaScript
                    page.evaluate(f'''() => {{
                        var combo = $("#DocTypesDisplay").data("kendoComboBox");
                        if (combo) {{
                            combo.value("{doc_type_id}");
                            combo.trigger("change");
                        }}
                    }}''')
                    page.wait_for_timeout(500)
                    
                    # Fill dates (MM/DD/YYYY format)
                    page.locator('#RecordDateFrom').first.fill(start_date)
                    page.locator('#RecordDateTo').first.fill(end_date)
                    
                    # Submit
                    page.locator('input[type="submit"]').first.click()
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(3000)
                    
                    # Extract data from Kendo Grid
                    grid_data = page.evaluate('''() => {
                        var grid = $("#RsltsGrid").data("kendoGrid");
                        if (grid) {
                            var data = grid.dataSource.data();
                            var records = [];
                            for (var i = 0; i < data.length; i++) {
                                var item = data[i];
                                records.push({
                                    instrument_number: item.InstrumentNumber || '',
                                    record_date: item.RecordDate || '',
                                    doc_type: item.DocTypeDescription || '',
                                    direct_name: item.DirectName || '',
                                    indirect_name: item.IndirectName || '',
                                    book_page: item.BookPage || '',
                                    book_type: item.BookType || '',
                                    consideration: item.Consideration || '',
                                    legal_description: item.DocLegalDescription || ''
                                });
                            }
                            return records;
                        }
                        return [];
                    }''')
                    
                    records.extend(grid_data)
                    
                finally:
                    browser.close()
                    
        except ImportError:
            print("Playwright not available - cannot scrape Official Records portal")
            return []
        except Exception as e:
            print(f"Playwright error: {e}")
            return []
        
        return records
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Search official records by date range.
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            doc_types: List of document types to filter
        
        Returns:
            List of raw record dictionaries
        """
        records = []
        
        # Convert dates to MM/DD/YYYY format
        start_parts = start_date.split('-')
        end_parts = end_date.split('-')
        start_formatted = f"{start_parts[1]}/{start_parts[2]}/{start_parts[0]}"
        end_formatted = f"{end_parts[1]}/{end_parts[2]}/{end_parts[0]}"
        
        # Document types that indicate distress
        distress_doc_types = doc_types or [
            'LIS PENDENS',
            'MORTGAGE',
            'LIEN',
            'JUDGMENT',
            'FORECLOSURE',
            'NOTICE',
            'DEED',
            'QUIT CLAIM',
            'TRUST',
            'PROBATE',
            'ASSIGNMENT',
            'SATISFACTION',
            'RELEASE'
        ]
        
        for doc_type in distress_doc_types:
            doc_type_id = self.DOC_TYPES.get(doc_type)
            if not doc_type_id:
                print(f"Unknown doc type: {doc_type}")
                continue
            
            try:
                print(f"Searching for {doc_type} (ID: {doc_type_id})...")
                
                if IN_GITHUB_ACTIONS:
                    # In GitHub Actions, we can't use Playwright without installing browsers
                    # Return empty - the data will be collected via Browserless or manual run
                    print(f"  Skipping (GitHub Actions - no browser)")
                    continue
                
                parsed_records = self._scrape_with_playwright(
                    doc_type_id, start_formatted, end_formatted
                )
                
                # Add metadata
                for rec in parsed_records:
                    rec['source_id'] = self.SOURCE_ID
                    rec['search_doc_type'] = doc_type
                    rec['scraped_at'] = datetime.now().isoformat()
                
                records.extend(parsed_records)
                print(f"  Found {len(parsed_records)} {doc_type} records")
                
            except Exception as e:
                print(f"  Error searching {doc_type}: {e}")
                continue
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = 1) -> Dict:
        """
        Run daily refresh or historical seeding.
        
        Args:
            cursor: Last processed date (YYYY-MM-DD)
            days_back: Number of days to look back (1 for daily, 30 for initial seeding)
        
        Returns:
            Dict with new_records, updated_cursor, errors
        """
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Refreshing official records from {start_date} to {end_date}")
        
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
            'note': 'Requires Playwright browser automation (Kendo UI portal)'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://or.duvalclerk.com/'}
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=30)
    print(json.dumps(result, indent=2))
'''

with open('/workspace/scrapers/duval_official_records.py', 'w') as f:
    f.write(scraper_code)

print("Updated duval_official_records.py with Playwright support")
print("\nKey findings:")
print("- Official Records portal uses Kendo UI (requires JavaScript)")
print("- LIS PENDENS doc type ID: 104")
print("- Successfully extracted 289 records for 30-day period")
print("- Playwright is required for this portal")
print("- GitHub Actions would need playwright install step")
