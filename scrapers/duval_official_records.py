#!/usr/bin/env python3
"""
Duval County Official Records Scraper - Direct API Version
Source: https://or.duvalclerk.com/

Simple approach: accept disclaimer to get session cookies, then call the
GridResults JSON API directly. No browser automation needed.
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://production-sfo.browserless.io')

class DuvalOfficialRecordsScraper:
    SOURCE_ID = "duval_official_records"
    BASE_URL = "https://or.duvalclerk.com"
    
    # Document type IDs for distress-related documents
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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _accept_disclaimer(self) -> bool:
        """Accept disclaimer to get session cookies."""
        try:
            # POST to disclaimer endpoint
            response = self.session.post(
                f"{self.BASE_URL}/Search/Disclaimer?st=/search/SearchTypeDocType",
                data={'disclaimer': 'true'},
                timeout=30,
                allow_redirects=True
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Disclaimer error: {e}")
            return False
    
    def _get_grid_results(self, doc_type_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Get results from the GridResults JSON API."""
        try:
            # First submit the search form to set up the session state
            form_data = {
                'DocTypes': doc_type_id,
                'DocTypesDisplay': doc_type_id,
                'DateRangeList': ' ',
                'RecordDateFrom': start_date,
                'RecordDateTo': end_date,
                'DefaultFromDate': start_date,
            }
            
            # Submit search form
            search_response = self.session.post(
                f"{self.BASE_URL}/search/SearchTypeDocType?Length=6",
                data=form_data,
                timeout=30
            )
            
            # Now get the grid results JSON
            grid_response = self.session.post(
                f"{self.BASE_URL}/Search/GridResults",
                headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                timeout=60
            )
            
            if grid_response.status_code == 200:
                data = grid_response.json()
                return data.get('Data', [])
            else:
                print(f"GridResults error: {grid_response.status_code}")
                return []
                
        except Exception as e:
            print(f"Grid results error: {e}")
            return []
    
    def _parse_record(self, raw_record: Dict, doc_type_name: str) -> Dict:
        """Parse a raw record from the API into our standard format."""
        return {
            'record_id': raw_record.get('InstrumentNumber', ''),
            'date': raw_record.get('RecordDate', '').replace('/', '-'),
            'party_name': raw_record.get('DirectName', ''),
            'counter_party': raw_record.get('IndirectName', ''),
            'doc_type': doc_type_name,
            'doc_type_detail': raw_record.get('DocTypeDescription', ''),
            'book_page': raw_record.get('BookPage', ''),
            'legal_description': raw_record.get('DocLegalDescription', ''),
            'consideration': raw_record.get('Consideration', 0),
            'transaction_id': raw_record.get('TransactionId', ''),
            'source_id': self.SOURCE_ID,
            'scraped_at': datetime.now().isoformat(),
        }
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """Search official records by date range."""
        records = []
        
        # Accept disclaimer first
        if not self._accept_disclaimer():
            print("Failed to accept disclaimer")
            return []
        
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
                raw_records = self._get_grid_results(doc_type_id, start_date, end_date)
                
                for raw in raw_records:
                    record = self._parse_record(raw, doc_type)
                    records.append(record)
                
                print(f"Found {len(raw_records)} {doc_type} records")
                
            except Exception as e:
                print(f"Error scraping {doc_type}: {e}")
                continue
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')
        
        end_date = datetime.now().strftime('%m/%d/%Y')
        
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
            'note': 'Using direct GridResults JSON API'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://or.duvalclerk.com/'}
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
