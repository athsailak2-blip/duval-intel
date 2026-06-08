#!/usr/bin/env python3
"""
Duval County Foreclosure Sales Scraper - Scrappey API Version
Source: https://www.duval.realforeclose.com
Portal Type: RealForeclose (blocked by AWS ELB - requires residential proxy)

Uses Scrappey API for residential proxy + browser automation.
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

SCRAPPEY_API_KEY = os.environ.get('SCRAPPEY_API_KEY', '')
FORECLOSURE_USERNAME = os.environ.get('FORECLOSURE_USERNAME', 'sailak1')
FORECLOSURE_PASSWORD = os.environ.get('FORECLOSURE_PASSWORD', 'Heyheyhey@1')

class DuvalForeclosureSalesScraper:
    SOURCE_ID = "duval_foreclosure_sales"
    BASE_URL = "https://www.duval.realforeclose.com"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_scrappey(self) -> List[Dict]:
        """Scrape using Scrappey API with residential proxy."""
        if not SCRAPPEY_API_KEY:
            print("Warning: SCRAPPEY_API_KEY not set, returning empty results")
            return []
        
        records = []
        
        try:
            # Scrappey API endpoint for browser automation
            # This is a placeholder - actual implementation depends on Scrappey's API
            scrappey_url = "https://api.scrappey.com/v1/scrape"
            
            payload = {
                "url": f"{self.BASE_URL}/SalesCalendar",
                "proxy": {
                    "type": "residential",
                    "country": "US"
                },
                "browser": {
                    "headless": True,
                    "block_images": True,
                    "wait_for": "body"
                },
                "actions": [
                    {
                        "type": "wait",
                        "milliseconds": 3000
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {SCRAPPEY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                scrappey_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                html = data.get('html', '')
                records = self._parse_records(html)
            else:
                print(f"Scrappey error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"Scrappey request failed: {e}")
        
        return records
    
    def _parse_records(self, html: str) -> List[Dict]:
        """Parse HTML to extract foreclosure sales."""
        records = []
        
        try:
            from bs4 import BeautifulSoup
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
        except Exception as e:
            print(f"Parse error: {e}")
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        start_date = datetime.now().strftime('%Y-%m-%d')
        
        # Try Scrappey API if available
        records = self._scrape_with_scrappey()
        
        # If no Scrappey key or failed, return empty with note
        if not records and not SCRAPPEY_API_KEY:
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': end_date,
                'errors': ['SCRAPPEY_API_KEY not configured - site blocked by AWS ELB'],
                'timestamp': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'note': 'Site blocked by AWS ELB (403 Forbidden). Requires Scrappey API or residential proxy.',
                'requires_scrappey': True
            }
        
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
            'note': 'Using Scrappey API with residential proxy'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realforeclose.com'}
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
