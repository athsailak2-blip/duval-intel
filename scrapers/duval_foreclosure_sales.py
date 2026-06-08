#!/usr/bin/env python3
"""
Duval County Foreclosure Sales Scraper
Source: https://www.duval.realforeclose.com/
Portal Type: RealAuction
Credentials: ath.sailak2@gmail.com / Heyheyhey@1
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://chrome.browserless.io')

FORECLOSURE_USERNAME = os.environ.get('FORECLOSURE_USERNAME', 'sailak1')
FORECLOSURE_PASSWORD = os.environ.get('FORECLOSURE_PASSWORD', 'Heyheyhey@1')

class DuvalForeclosureSalesScraper:
    SOURCE_ID = "duval_foreclosure_sales"
    BASE_URL = "https://www.duval.realforeclose.com"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_browserless(self, days_ahead: int = 30) -> List[Dict]:
        """Scrape using Browserless API with login credentials."""
        records = []
        
        script = f"""
        async ({{ page }}) => {{
            const records = [];
            try {{
                // Navigate to RealForeclose
                await page.goto('{self.BASE_URL}/', {{ waitUntil: 'networkidle' }});
                
                // Login
                await page.fill('#Username', '{FORECLOSURE_USERNAME}');
                await page.fill('#Password', '{FORECLOSURE_PASSWORD}');
                await page.click('input[type="submit"]');
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(2000);
                
                // Navigate to sales calendar
                await page.goto('{self.BASE_URL}/SalesCalendar', {{ waitUntil: 'networkidle' }});
                await page.waitForTimeout(2000);
                
                // Extract sales data
                const results = await page.evaluate(() => {{
                    const rows = document.querySelectorAll('.sale-item, .auction-item, tr[data-sale-id]');
                    return Array.from(rows).map(row => {{
                        const cells = row.querySelectorAll('td');
                        return {{
                            sale_id: row.getAttribute('data-sale-id') || '',
                            case_number: cells[0]?.textContent?.trim() || '',
                            property_address: cells[1]?.textContent?.trim() || '',
                            sale_date: cells[2]?.textContent?.trim() || '',
                            opening_bid: cells[3]?.textContent?.trim() || '',
                            sale_status: cells[4]?.textContent?.trim() || 'Scheduled'
                        }};
                    }});
                }});
                
                records.push(...results);
            }} catch (e) {{
                console.error('Error:', e.message);
            }}
            return records;
        }}
        """
        
        try:
            response = requests.post(
                f"{BROWSERLESS_URL}/function",
                headers={
                    "Authorization": f"Bearer {BROWSERLESS_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "code": script,
                    "context": {}
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    records = result
                elif isinstance(result, dict) and 'data' in result:
                    records = result['data']
            else:
                print(f"Browserless error: {response.status_code}")
                
        except Exception as e:
            print(f"Browserless request failed: {e}")
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
        """Run daily refresh for upcoming sales."""
        if days_ahead is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_ahead = 90 if seed_mode else 30
        
        end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        records = self._scrape_with_browserless(days_ahead)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(records),
            'new_records': records,
            'updated_cursor': end_date,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': datetime.now().strftime('%Y-%m-%d'),
                'end': end_date
            },
            'note': 'Using Browserless API with login credentials'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realforeclose.com/'}
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh(days_ahead=30)
    print(json.dumps(result, indent=2))
