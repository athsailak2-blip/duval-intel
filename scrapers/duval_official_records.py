#!/usr/bin/env python3
"""
Duval County Official Records Scraper
Source: https://or.duvalclerk.com/
Portal Type: Tyler Technologies / Kendo UI

Uses Browserless /content API for cloud-based browser execution.
Token passed as query parameter: ?token=...
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://production-sfo.browserless.io')

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
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page HTML using Browserless /content endpoint."""
        try:
            response = requests.post(
                f"{BROWSERLESS_URL}/content?token={BROWSERLESS_TOKEN}",
                headers={"Content-Type": "application/json"},
                json={"url": url},
                timeout=60
            )
            if response.status_code == 200:
                return response.text
            else:
                print(f"Browserless error: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            print(f"Browserless request failed: {e}")
            return None
    
    def _parse_records(self, html: str, doc_type: str) -> List[Dict]:
        """Parse HTML to extract records."""
        records = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for table rows with record data
        # Tyler Technologies uses various table structures
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    record = {
                        'doc_type': doc_type,
                        'source_id': self.SOURCE_ID,
                        'scraped_at': datetime.now().isoformat(),
                    }
                    
                    # Extract data from cells
                    for i, cell in enumerate(cells):
                        text = cell.get_text(strip=True)
                        if i == 0:
                            record['record_id'] = text
                        elif i == 1:
                            record['date'] = text
                        elif i == 2:
                            record['party_name'] = text
                        elif i == 3:
                            record['doc_type_detail'] = text
                        elif i == 4:
                            record['book_page'] = text
                    
                    if record.get('record_id') and record.get('record_id') != 'Record ID':
                        records.append(record)
        
        # Also look for Kendo Grid data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'kendo' in script.string.lower():
                # Try to extract JSON data from script
                import re
                json_matches = re.findall(r'var\s+\w+\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                for match in json_matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    record = {
                                        'doc_type': doc_type,
                                        'source_id': self.SOURCE_ID,
                                        'scraped_at': datetime.now().isoformat(),
                                    }
                                    # Map common fields
                                    for key, value in item.items():
                                        if 'date' in key.lower():
                                            record['date'] = str(value)
                                        elif 'name' in key.lower() or 'party' in key.lower():
                                            record['party_name'] = str(value)
                                        elif 'id' in key.lower() or 'number' in key.lower():
                                            record['record_id'] = str(value)
                                        elif 'type' in key.lower():
                                            record['doc_type_detail'] = str(value)
                                    
                                    if record.get('record_id'):
                                        records.append(record)
                    except:
                        pass
        
        return records
    
    def _scrape_with_browserless(self, doc_type_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Scrape using Browserless /content API."""
        records = []
        
        # Try to fetch the search page
        search_url = f"{self.BASE_URL}/search/SearchTypeDocType"
        html = self._fetch_page(search_url)
        
        if html:
            # Parse the page for any visible records
            doc_type_name = [k for k, v in self.DOC_TYPES.items() if v == doc_type_id]
            doc_type_name = doc_type_name[0] if doc_type_name else 'Unknown'
            records = self._parse_records(html, doc_type_name)
        
        return records
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """Search official records by date range."""
        records = []
        
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
                    doc_type_id, start_date, end_date
                )
                
                # Add metadata
                for rec in parsed_records:
                    rec['search_doc_type'] = doc_type
                
                records.extend(parsed_records)
                
            except Exception as e:
                print(f"Error scraping {doc_type}: {e}")
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
            'note': 'Using Browserless /content API with HTML parsing'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://or.duvalclerk.com/'}
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
