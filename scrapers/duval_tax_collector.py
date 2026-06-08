#!/usr/bin/env python3
"""
Duval County Tax Collector Lien Info Scraper
Source: https://tclieninfo.coj.net/
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

class DuvalTaxCollectorScraper:
    SOURCE_ID = "duval_tax_collector"
    BASE_URL = "https://tclieninfo.coj.net"
    
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
            response = self.session.get(f"{self.BASE_URL}/Search.aspx", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting search page: {e}")
            return ""
    
    def search_by_parcel(self, re_number: str) -> Dict:
        """Search tax lien info by parcel ID (RE Number)."""
        lien_info = {}
        try:
            search_url = f"{self.BASE_URL}/Search.aspx"
            search_page = self._get_search_page()
            soup = BeautifulSoup(search_page, 'html.parser')
            form = soup.find('form', id='aspnetForm') or soup.find('form')
            
            payload = {'RENumber': re_number}
            
            if form:
                hidden_fields = form.find_all('input', type='hidden')
                for field in hidden_fields:
                    if field.get('name'):
                        payload[field['name']] = field.get('value', '')
            
            response = self.session.post(search_url, data=payload, timeout=60)
            if response.status_code == 200:
                lien_info = self._parse_tax_results(response.text, re_number)
                print(f"Found tax lien info for RE# {re_number}")
            else:
                print(f"Search returned HTTP {response.status_code}")
        except Exception as e:
            print(f"Error searching tax liens: {e}")
        return lien_info
    
    def _parse_tax_results(self, html_content: str, re_number: str) -> Dict:
        """Parse HTML tax results into structured lien info."""
        lien_info = {
            're_number': re_number,
            'source_id': self.SOURCE_ID,
            'scraped_at': datetime.now().isoformat()
        }
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tax_tables = soup.find_all('table', class_=re.compile(r'tax|lien|amount|due', re.I))
            if not tax_tables:
                tax_tables = soup.find_all('table')
            
            for table in tax_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        if 'amount' in label or 'due' in label or 'balance' in label:
                            lien_info['amount_due'] = value
                        elif 'year' in label or 'tax year' in label:
                            lien_info['tax_year'] = value
                        elif 'status' in label or 'delinquent' in label:
                            lien_info['status'] = value
                        elif 'owner' in label:
                            lien_info['owner_name'] = value
                        elif 'address' in label or 'situs' in label:
                            lien_info['property_address'] = value
            
            if not lien_info.get('amount_due'):
                info_divs = soup.find_all('div', class_=re.compile(r'info|detail|field', re.I))
                for div in info_divs:
                    text = div.get_text(strip=True)
                    if ':' in text:
                        key, value = text.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if 'amount' in key or 'due' in key or 'balance' in key:
                            lien_info['amount_due'] = value
                        elif 'year' in key:
                            lien_info['tax_year'] = value
                        elif 'status' in key:
                            lien_info['status'] = value
            
            lien_info['raw_html'] = html_content[:3000]
        except Exception as e:
            print(f"Error parsing tax results: {e}")
        return lien_info
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for tax collector data."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 7
        
        print(f"Tax collector refresh would iterate all tracked parcels (days_back={days_back})")
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Tax collector requires a list of tracked parcels to check individually'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://tclieninfo.coj.net/'}
    scraper = DuvalTaxCollectorScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
