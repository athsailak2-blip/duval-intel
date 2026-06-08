#!/usr/bin/env python3
"""
Duval County Property Appraiser Scraper
Source: https://paopropertysearch.coj.net/
Portal Type: Custom Web
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://chrome.browserless.io')

class DuvalPropertyAppraiserScraper:
    SOURCE_ID = "duval_parcel_master"
    BASE_URL = "https://paopropertysearch.coj.net"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_browserless(self, zip_codes: List[str], max_per_zip: int = 20) -> List[Dict]:
        """Scrape using Browserless API."""
        all_parcels = []
        
        for zip_code in zip_codes:
            script = f"""
            async ({{ page }}) => {{
                const parcels = [];
                try {{
                    // Navigate to search
                    await page.goto('{self.BASE_URL}/Basic/Search.aspx', {{ waitUntil: 'networkidle' }});
                    await page.waitForTimeout(1000);
                    
                    // Search by ZIP
                    await page.fill('#StreetNumber', '');
                    await page.fill('#StreetName', '');
                    await page.fill('#City', 'Jacksonville');
                    await page.fill('#Zip', '{zip_code}');
                    await page.click('input[type="submit"]');
                    await page.waitForLoadState('networkidle');
                    await page.waitForTimeout(2000);
                    
                    // Extract results
                    const results = await page.evaluate(() => {{
                        const rows = document.querySelectorAll('.result-row, .grid-row, tr');
                        return Array.from(rows).slice(0, {max_per_zip}).map(row => {{
                            const cells = row.querySelectorAll('td');
                            return {{
                                re_number: cells[0]?.textContent?.trim() || '',
                                address: cells[1]?.textContent?.trim() || '',
                                owner_name: cells[2]?.textContent?.trim() || '',
                                city: cells[3]?.textContent?.trim() || 'Jacksonville',
                                zip: cells[4]?.textContent?.trim() || '{zip_code}'
                            }};
                        }});
                    }});
                    
                    parcels.push(...results);
                }} catch (e) {{
                    console.error('Error:', e.message);
                }}
                return parcels;
            }}
            """
            
            try:
                response = requests.post(
                    f"{BROWSERLESS_URL}/function?token={BROWSERLESS_TOKEN}",
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "code": script,
                        "context": {}
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list):
                        all_parcels.extend(result)
                    elif isinstance(result, dict) and 'data' in result:
                        all_parcels.extend(result['data'])
                        
            except Exception as e:
                print(f"Browserless request failed for ZIP {zip_code}: {e}")
                continue
        
        return all_parcels
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for parcel master data."""
        zip_codes = ['32202', '32204', '32205', '32206', '32207', '32208', '32209', '32210', 
                     '32211', '32216', '32217', '32218', '32219', '32220', '32221', '32222',
                     '32223', '32224', '32225', '32226', '32227', '32233', '32244', '32246',
                     '32250', '32254', '32256', '32257', '32258', '32259', '32277']
        
        parcels = self._scrape_with_browserless(zip_codes, max_per_zip=20)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(parcels),
            'new_records': parcels,
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'note': f'Bulk extracted {len(parcels)} parcels across {len(zip_codes)} ZIP codes using Browserless'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://paopropertysearch.coj.net/'}
    scraper = DuvalPropertyAppraiserScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
