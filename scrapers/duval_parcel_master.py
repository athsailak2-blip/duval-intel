#!/usr/bin/env python3
"""
Duval County Property Appraiser Scraper
Source: https://paopropertysearch.coj.net/
Portal Type: Custom Web
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalPropertyAppraiserScraper:
    SOURCE_ID = "duval_parcel_master"
    BASE_URL = "https://paopropertysearch.coj.net"
    
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
        """Get the search page."""
        try:
            response = self.session.get(f"{self.BASE_URL}/Basic/Search.aspx", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting search page: {e}")
            return ""
    
    def search_by_address(self, street_number: str, street_name: str,
                         city: Optional[str] = None) -> List[Dict]:
        """Search parcels by address."""
        parcels = []
        try:
            search_url = f"{self.BASE_URL}/Basic/Search.aspx"
            search_page = self._get_search_page()
            soup = BeautifulSoup(search_page, 'html.parser')
            form = soup.find('form', id='aspnetForm') or soup.find('form')
            
            payload = {
                'StreetNumber': street_number,
                'StreetName': street_name,
                'City': city or '',
                'SearchType': 'MatchAll',
                'ResultsPerPage': 100
            }
            
            if form:
                hidden_fields = form.find_all('input', type='hidden')
                for field in hidden_fields:
                    if field.get('name'):
                        payload[field['name']] = field.get('value', '')
            
            response = self.session.post(search_url, data=payload, timeout=60)
            if response.status_code == 200:
                parcels = self._parse_search_results(response.text)
                print(f"Found {len(parcels)} parcels for address {street_number} {street_name}")
            else:
                print(f"Search returned HTTP {response.status_code}")
        except Exception as e:
            print(f"Error searching by address: {e}")
        return parcels
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse HTML search results into structured parcel records."""
        parcels = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_tables = soup.find_all('table', class_=re.compile(r'result|grid|data|search', re.I))
            if not result_tables:
                result_tables = soup.find_all('table')
            
            for table in result_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        parcel = {
                            'source_id': self.SOURCE_ID,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            if re.match(r'^\d{2}-\d{2}-\d{2}-\d{3}-\d{3}(-\d{3})?$', text):
                                parcel['re_number'] = text
                            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):
                                parcel['date'] = text
                            elif '$' in text and re.search(r'\d+\.\d{2}', text):
                                parcel['value'] = text
                            elif len(text) > 20 and ('st' in text.lower() or 'ave' in text.lower() or 'dr' in text.lower() or 'rd' in text.lower()):
                                parcel['address'] = text
                            elif len(text) > 2 and len(text) < 50 and not any(c in text for c in '0123456789'):
                                if 'owner' not in parcel:
                                    parcel['owner_name'] = text
                                else:
                                    parcel['city'] = text
                        if 're_number' in parcel or 'address' in parcel:
                            parcels.append(parcel)
            
            if not parcels:
                result_divs = soup.find_all('div', class_=re.compile(r'result|parcel|item', re.I))
                for div in result_divs:
                    parcel = {
                        'source_id': self.SOURCE_ID,
                        'scraped_at': datetime.now().isoformat(),
                        'raw_text': div.get_text(strip=True)
                    }
                    parcels.append(parcel)
        except Exception as e:
            print(f"Error parsing search results: {e}")
        return parcels
    
    def bulk_extract_by_zip(self, zip_codes: List[str], max_per_zip: int = 50) -> List[Dict]:
        """Bulk extract parcels by ZIP code batches."""
        all_parcels = []
        for zip_code in zip_codes:
            try:
                print(f"Bulk extracting ZIP {zip_code}...")
                # Search by ZIP prefix - use empty street to get all in area
                parcels = self.search_by_address('', f'ZIP:{zip_code}')
                all_parcels.extend(parcels[:max_per_zip])
                time.sleep(0.5)
            except Exception as e:
                print(f"Error extracting ZIP {zip_code}: {e}")
        return all_parcels
    
    def bulk_extract_by_street_range(self, street_name: str, 
                                    start_number: int, end_number: int,
                                    step: int = 100) -> List[Dict]:
        """Bulk extract parcels by street number ranges."""
        all_parcels = []
        for num in range(start_number, end_number + 1, step):
            try:
                print(f"Bulk extracting {num}-{num+step-1} {street_name}...")
                parcels = self.search_by_address(str(num), street_name)
                all_parcels.extend(parcels)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error extracting {street_name} at {num}: {e}")
        return all_parcels
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for parcel master data."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 7
        
        # Try bulk extraction for key ZIPs in Duval County
        zip_codes = ['32202', '32204', '32205', '32206', '32207', '32208', '32209', '32210', 
                     '32211', '32216', '32217', '32218', '32219', '32220', '32221', '32222',
                     '32223', '32224', '32225', '32226', '32227', '32233', '32244', '32246',
                     '32250', '32254', '32256', '32257', '32258', '32259', '32277']
        
        print(f"Bulk extracting parcels for {len(zip_codes)} ZIP codes (days_back={days_back})")
        parcels = self.bulk_extract_by_zip(zip_codes, max_per_zip=20)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(parcels),
            'new_records': parcels,
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'note': f'Bulk extracted {len(parcels)} parcels across {len(zip_codes)} ZIP codes'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://paopropertysearch.coj.net/'}
    scraper = DuvalPropertyAppraiserScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
