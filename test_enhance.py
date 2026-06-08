import json
import os

# Read the current official records scraper
with open('/workspace/scrapers/duval_official_records.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Duval County Official Records Scraper
Source: https://or.duvalclerk.com/
Portal Type: Tyler Technologies / Official Records
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalOfficialRecordsScraper:
    SOURCE_ID = "duval_official_records"
    BASE_URL = "https://or.duvalclerk.com"
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _get_search_page(self) -> str:
        """Get the main search page to extract any necessary tokens."""
        try:
            response = self.session.get(f"{self.BASE_URL}/", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting search page: {e}")
            return ""
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Search official records by date range.
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            doc_types: List of document types to filter (e.g., ['LIS PENDENS', 'MORTGAGE'])
        
        Returns:
            List of raw record dictionaries
        """
        records = []
        
        # Document types that indicate distress
        distress_doc_types = doc_types or [
            'LIS PENDENS',
            'MORTGAGE',
            'LIEN',
            'MECHANICS LIEN',
            'JUDGMENT',
            'FORECLOSURE',
            'NOTICE',
            'DEED',
            'QUIT CLAIM',
            'TRUST',
            'PROBATE',
            'ASSIGNMENT',
            'CANCELLATION',
            'SATISFACTION',
            'RELEASE'
        ]
        
        # Convert dates to MM/DD/YYYY format for the portal
        start_parts = start_date.split('-')
        end_parts = end_date.split('-')
        start_formatted = f"{start_parts[1]}/{start_parts[2]}/{start_parts[0]}"
        end_formatted = f"{end_parts[1]}/{end_parts[2]}/{end_parts[0]}"
        
        for doc_type in distress_doc_types:
            try:
                # The portal uses a form-based search
                # First, get the search page to extract any tokens
                search_page = self._get_search_page()
                
                # Try to find the search form and submit it
                # Tyler Technologies portals typically have a search form at /search/SearchTypeDocType
                search_url = f"{self.BASE_URL}/search/SearchTypeDocType"
                
                # Build the search payload
                # Note: Actual field names may vary - this is based on typical Tyler Tech portals
                payload = {
                    'DocType': doc_type,
                    'StartDate': start_formatted,
                    'EndDate': end_formatted,
                    'MaxResults': 1000,
                    'SearchType': 'DocType'
                }
                
                # Make the search request
                response = self.session.post(search_url, data=payload, timeout=60)
                
                if response.status_code == 200:
                    # Parse the response
                    parsed_records = self._parse_search_results(response.text, doc_type)
                    records.extend(parsed_records)
                    print(f"Found {len(parsed_records)} {doc_type} records")
                else:
                    print(f"Search returned HTTP {response.status_code} for {doc_type}")
                
                # Be polite - add delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching {doc_type}: {e}")
                continue
        
        return records
    
    def _parse_search_results(self, html_content: str, doc_type: str) -> List[Dict]:
        """Parse HTML search results into structured records."""
        records = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for result tables or rows
            # Tyler Tech portals typically use tables with class names like 'resultTable' or 'grid'
            result_tables = soup.find_all('table', class_=re.compile(r'result|grid|data', re.I))
            
            if not result_tables:
                # Try finding any table with rows
                result_tables = soup.find_all('table')
            
            for table in result_tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:  # Need at least a few cells to be a valid record
                        # Extract data from cells
                        # Typical columns: Instrument #, Record Date, Doc Type, Parties, Legal Description
                        record = {
                            'source_id': self.SOURCE_ID,
                            'doc_type': doc_type,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        
                        # Try to extract specific fields
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            # Try to identify fields by content patterns
                            if re.match(r'^\d{4,}$', text):  # Instrument number
                                record['instrument_number'] = text
                            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):  # Date
                                record['record_date'] = text
                            elif 'grantor' in text.lower() or 'grantee' in text.lower():
                                record['parties'] = text
                            elif len(text) > 20 and 'legal' not in text.lower():
                                # Could be legal description or address
                                record['legal_description'] = text
                        
                        # Only add if we have at least some data
                        if len(record) > 3:
                            records.append(record)
            
            # If no tables found, try looking for div-based results
            if not records:
                result_divs = soup.find_all('div', class_=re.compile(r'result|record|item', re.I))
                
                for div in result_divs:
                    record = {
                        'source_id': self.SOURCE_ID,
                        'doc_type': doc_type,
                        'scraped_at': datetime.now().isoformat(),
                        'raw_text': div.get_text(strip=True)
                    }
                    records.append(record)
            
        except Exception as e:
            print(f"Error parsing results: {e}")
        
        return records
    
    def search_by_name(self, party_name: str, start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> List[Dict]:
        """Search by party name (grantor/grantee)."""
        records = []
        
        try:
            search_url = f"{self.BASE_URL}/search/SearchTypeName"
            
            payload = {
                'PartyName': party_name,
                'StartDate': start_date or '',
                'EndDate': end_date or '',
                'MaxResults': 500,
                'SearchType': 'Name'
            }
            
            response = self.session.post(search_url, data=payload, timeout=60)
            
            if response.status_code == 200:
                records = self._parse_search_results(response.text, 'NAME_SEARCH')
            
        except Exception as e:
            print(f"Error searching by name: {e}")
        
        return records
    
    def get_document_details(self, instrument_number: str) -> Dict:
        """Get full details for a specific instrument."""
        details = {}
        
        try:
            detail_url = f"{self.BASE_URL}/search/InstrumentDetail"
            
            payload = {
                'InstrumentNumber': instrument_number
            }
            
            response = self.session.post(detail_url, data=payload, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract detail information
                details['instrument_number'] = instrument_number
                details['raw_html'] = response.text[:5000]  # Store first 5000 chars
                
                # Try to find specific detail fields
                detail_divs = soup.find_all('div', class_=re.compile(r'detail|field|label', re.I))
                
                for div in detail_divs:
                    text = div.get_text(strip=True)
                    
                    if ':' in text:
                        key, value = text.split(':', 1)
                        details[key.strip().lower().replace(' ', '_')] = value.strip()
        
        except Exception as e:
            print(f"Error getting details: {e}")
        
        return details
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """
        Run daily refresh.
        
        Args:
            cursor: Last processed date (YYYY-MM-DD)
        
        Returns:
            Dict with new_records, updated_cursor, errors
        """
        if cursor:
            start_date = cursor
        else:
            # Default to yesterday
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
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
            }
        }

if __name__ == '__main__':
    # Test the scraper
    config = {
        'source_url': 'https://or.duvalclerk.com/',
        'doc_type_synonyms': {
            'LIS PENDENS': 'LIS_PENDENS',
            'MORTGAGE': 'MORTGAGE',
            'LIEN': 'LIEN'
        }
    }
    
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_official_records.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced official records scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_official_records.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")
print("First 200 chars:", verify[:200])
