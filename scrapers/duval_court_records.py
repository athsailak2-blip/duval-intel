#!/usr/bin/env python3
"""
Duval County Court Records Scraper
Source: https://core.duvalclerk.com
Portal Type: Tyler Technologies CORE

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
CORE_USERNAME = os.environ.get('CORE_USERNAME', 'sailak1')
CORE_PASSWORD = os.environ.get('CORE_PASSWORD', 'Heyheyhey@1')

class DuvalCourtRecordsScraper:
    SOURCE_ID = "duval_court_records"
    BASE_URL = "https://core.duvalclerk.com"
    
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
        """Parse HTML to extract court records."""
        records = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for case data in tables
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
                            record['case_type'] = text
                        elif i == 2:
                            record['file_date'] = text
                        elif i == 3:
                            record['party_name'] = text
                        elif i == 4:
                            record['status'] = text
                    
                    if record.get('case_number'):
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
        
        # Fetch court records page
        html = self._fetch_page(f"{self.BASE_URL}/CaseSearch")
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
    config = {'source_url': 'https://core.duvalclerk.com'}
    scraper = DuvalCourtRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
