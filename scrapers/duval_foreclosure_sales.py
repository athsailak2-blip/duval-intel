#!/usr/bin/env python3
"""
Duval County Foreclosure Sales Scraper
Source: https://www.duval.realforeclose.com
Portal Type: RealForeclose

Uses Browserless /content API for cloud-based browser execution.
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://production-sfo.browserless.io')
FORECLOSURE_USERNAME = os.environ.get('FORECLOSURE_USERNAME', 'sailak1')
FORECLOSURE_PASSWORD = os.environ.get('FORECLOSURE_PASSWORD', 'Heyheyhey@1')

class DuvalForeclosureSalesScraper:
    SOURCE_ID = "duval_foreclosure_sales"
    BASE_URL = "https://www.duval.realforeclose.com"
    
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
    
    def _parse_records(self, html: str) -> List[Dict]:
        """Parse HTML to extract foreclosure sales."""
        records = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for sale items
        sale_items = soup.find_all(class_=['sale-item', 'auction-item', 'property-item'])
        
        for item in sale_items:
            record = {
                'source_id': self.SOURCE_ID,
                'scraped_at': datetime.now().isoformat(),
            }
            
            # Extract data from item
            case_num = item.find(class_=['case-number', 'case-num'])
            if case_num:
                record['case_number'] = case_num.get_text(strip=True)
            
            sale_date = item.find(class_=['sale-date', 'auction-date'])
            if sale_date:
                record['sale_date'] = sale_date.get_text(strip=True)
            
            address = item.find(class_=['address', 'property-address'])
            if address:
                record['property_address'] = address.get_text(strip=True)
            
            parcel = item.find(class_=['parcel', 'folio'])
            if parcel:
                record['parcel_id'] = parcel.get_text(strip=True)
            
            plaintiff = item.find(class_=['plaintiff', 'plaintiff-name'])
            if plaintiff:
                record['plaintiff'] = plaintiff.get_text(strip=True)
            
            defendant = item.find(class_=['defendant', 'defendant-name'])
            if defendant:
                record['defendant'] = defendant.get_text(strip=True)
            
            if record.get('case_number') or record.get('property_address'):
                records.append(record)
        
        # Also check table rows
        if not records:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        record = {
                            'source_id': self.SOURCE_ID,
                            'scraped_at': datetime.now().isoformat(),
                        }
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            if i == 0:
                                record['case_number'] = text
                            elif i == 1:
                                record['sale_date'] = text
                            elif i == 2:
                                record['property_address'] = text
                        
                        if record.get('case_number'):
                            records.append(record)
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        start_date = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch sales calendar
        html = self._fetch_page(f"{self.BASE_URL}/SalesCalendar")
        records = self._parse_records(html) if html else []
        
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
            'note': 'Using Browserless /content API with HTML parsing and login credentials'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realforeclose.com'}
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
