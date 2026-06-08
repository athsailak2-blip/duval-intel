import json
import os

# Read the current court records scraper
with open('/workspace/scrapers/duval_court_records.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Duval County Court Records Scraper (CORE)
Source: https://core.duvalclerk.com/
Portal Type: Tyler Technologies / CORE
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalCourtRecordsScraper:
    SOURCE_ID = "duval_court_records"
    BASE_URL = "https://core.duvalclerk.com"
    
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
    
    def search_cases(self, case_type: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict]:
        """
        Search court cases.
        
        Case types of interest:
        - FORECLOSURE (Circuit Civil)
        - LIS PENDENS
        - PROBATE
        - COUNTY CIVIL (evictions, small claims)
        - FAMILY LAW
        """
        cases = []
        
        case_types = case_type or [
            'FORECLOSURE',
            'LIS PENDENS',
            'PROBATE',
            'COUNTY CIVIL',
            'FAMILY LAW'
        ]
        
        # Convert dates to MM/DD/YYYY format
        start_formatted = None
        end_formatted = None
        
        if start_date:
            start_parts = start_date.split('-')
            start_formatted = f"{start_parts[1]}/{start_parts[2]}/{start_parts[0]}"
        
        if end_date:
            end_parts = end_date.split('-')
            end_formatted = f"{end_parts[1]}/{end_parts[2]}/{end_parts[0]}"
        
        for ct in case_types:
            try:
                # Get the search page first
                search_page = self._get_search_page()
                
                # Search by case type and date range
                # CORE portal typically has a case search at /CaseSearch
                search_url = f"{self.BASE_URL}/CaseSearch"
                
                payload = {
                    'CaseType': ct,
                    'FiledStartDate': start_formatted or '',
                    'FiledEndDate': end_formatted or '',
                    'MaxResults': 500,
                    'SearchType': 'Case'
                }
                
                response = self.session.post(search_url, data=payload, timeout=60)
                
                if response.status_code == 200:
                    parsed_cases = self._parse_case_results(response.text, ct)
                    cases.extend(parsed_cases)
                    print(f"Found {len(parsed_cases)} {ct} cases")
                else:
                    print(f"Search returned HTTP {response.status_code} for {ct}")
                
                # Be polite - add delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching {ct}: {e}")
                continue
        
        return cases
    
    def _parse_case_results(self, html_content: str, case_type: str) -> List[Dict]:
        """Parse HTML case search results into structured records."""
        cases = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for result tables
            result_tables = soup.find_all('table', class_=re.compile(r'result|grid|data|case', re.I))
            
            if not result_tables:
                result_tables = soup.find_all('table')
            
            for table in result_tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        case_record = {
                            'source_id': self.SOURCE_ID,
                            'case_type': case_type,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        
                        # Extract data from cells
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            # Try to identify fields by content patterns
                            if re.match(r'^\d{4}-\d{2}-[A-Z]{2}-\d{6}$', text):  # Case number format
                                case_record['case_number'] = text
                            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):  # Date
                                case_record['file_date'] = text
                            elif 'v.' in text.lower() or 'vs.' in text.lower():  # Party names
                                case_record['parties'] = text
                            elif 'judge' in text.lower() or 'division' in text.lower():
                                case_record['court_info'] = text
                            elif len(text) > 10 and 'status' not in text.lower():
                                case_record['case_title'] = text
                        
                        # Only add if we have at least a case number or title
                        if 'case_number' in case_record or 'case_title' in case_record:
                            cases.append(case_record)
            
            # If no tables found, try div-based results
            if not cases:
                result_divs = soup.find_all('div', class_=re.compile(r'result|case|record', re.I))
                
                for div in result_divs:
                    case_record = {
                        'source_id': self.SOURCE_ID,
                        'case_type': case_type,
                        'scraped_at': datetime.now().isoformat(),
                        'raw_text': div.get_text(strip=True)
                    }
                    cases.append(case_record)
            
        except Exception as e:
            print(f"Error parsing case results: {e}")
        
        return cases
    
    def get_case_details(self, case_number: str) -> Dict:
        """Get detailed case information."""
        details = {}
        
        try:
            detail_url = f"{self.BASE_URL}/CaseDetail"
            
            payload = {
                'CaseNumber': case_number
            }
            
            response = self.session.post(detail_url, data=payload, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                details['case_number'] = case_number
                details['raw_html'] = response.text[:5000]
                
                # Extract detail fields
                detail_divs = soup.find_all('div', class_=re.compile(r'detail|field|label', re.I))
                
                for div in detail_divs:
                    text = div.get_text(strip=True)
                    
                    if ':' in text:
                        key, value = text.split(':', 1)
                        details[key.strip().lower().replace(' ', '_')] = value.strip()
        
        except Exception as e:
            print(f"Error getting case details: {e}")
        
        return details
    
    def get_docket_entries(self, case_number: str) -> List[Dict]:
        """Get docket entries for a case."""
        entries = []
        
        try:
            docket_url = f"{self.BASE_URL}/DocketEntries"
            
            payload = {
                'CaseNumber': case_number
            }
            
            response = self.session.post(docket_url, data=payload, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse docket entries
                docket_rows = soup.find_all('tr', class_=re.compile(r'docket|entry', re.I))
                
                for row in docket_rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 2:
                        entry = {
                            'case_number': case_number,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
                                entry['entry_date'] = text
                            elif len(text) > 5:
                                entry['description'] = text
                        
                        entries.append(entry)
        
        except Exception as e:
            print(f"Error getting docket: {e}")
        
        return entries
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run daily refresh for court records."""
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Refreshing court records from {start_date} to {end_date}")
        
        cases = self.search_cases(start_date=start_date, end_date=end_date)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(cases),
            'new_records': cases,
            'updated_cursor': end_date,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }

if __name__ == '__main__':
    config = {'source_url': 'https://core.duvalclerk.com/'}
    scraper = DuvalCourtRecordsScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_court_records.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced court records scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_court_records.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")
