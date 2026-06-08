#!/usr/bin/env python3
"""
Duval County Tax Collector Scraper
Source: https://tclieninfo.coj.net
Portal Type: Tax Collector

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

class DuvalTaxCollectorScraper:
    SOURCE_ID = "duval_tax_collector"
    BASE_URL = "https://tclieninfo.coj.net"
    
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
        """Parse HTML to extract tax records."""
        records = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for tax data
        tax_items = soup.find_all(class_=['tax-item', 'property-item'])
        
        for item in tax_items:
            record = {
                'source_id': self.SOURCE_ID,
                'scraped_at': datetime.now().isoformat(),
            }
            
            parcel = item.find(class_=['parcel', 'folio', 're-number'])
            if parcel:
                record['parcel_id'] = parcel.get_text(strip=True)
            
            owner = item.find(class_=['owner', 'taxpayer'])
            if owner:
                record['owner_name'] = owner.get_text(strip=True)
            
            amount = item.find(class_=['amount', 'tax-due'])
            if amount:
                record['tax_due'] = amount.get_text(strip=True)
            
            status = item.find(class_=['status', 'payment-status'])
            if status:
                record['payment_status'] = status.get_text(strip=True)
            
            if record.get('parcel_id'):
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
                                record['parcel_id'] = text
                            elif i == 1:
                                record['owner_name'] = text
                            elif i == 2:
                                record['tax_due'] = text
                        
                        if record.get('parcel_id'):
                            records.append(record)
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch tax search page
        html = self._fetch_page(f"{self.BASE_URL}/Search.aspx")
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
            'note': 'Using Browserless /content API with HTML parsing'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://tclieninfo.coj.net'}
    scraper = DuvalTaxCollectorScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
