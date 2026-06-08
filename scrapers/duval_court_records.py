#!/usr/bin/env python3
"""
Duval County Court Records Scraper (CORE)
Source: https://core.duvalclerk.com/
Portal Type: Tyler Technologies / CORE
Credentials: ath.sailak2@gmail.com / Heyheyhey@1
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://chrome.browserless.io')

CORE_USERNAME = os.environ.get('CORE_USERNAME', 'sailak1')
CORE_PASSWORD = os.environ.get('CORE_PASSWORD', 'Heyheyhey@1')

class DuvalCourtRecordsScraper:
    SOURCE_ID = "duval_court_records"
    BASE_URL = "https://core.duvalclerk.com"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _scrape_with_browserless(self, start_date: str, end_date: str) -> List[Dict]:
        """Scrape using Browserless API with login credentials."""
        records = []
        
        script = f"""
        async ({{ page }}) => {{
            const records = [];
            try {{
                // Navigate to CORE
                await page.goto('{self.BASE_URL}/', {{ waitUntil: 'networkidle' }});
                
                // Login
                await page.fill('#UserName', '{CORE_USERNAME}');
                await page.fill('#Password', '{CORE_PASSWORD}');
                await page.click('input[type="submit"]');
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(2000);
                
                // Navigate to case search
                await page.goto('{self.BASE_URL}/CaseSearch', {{ waitUntil: 'networkidle' }});
                await page.waitForTimeout(1000);
                
                // Search for foreclosure cases
                await page.selectOption('#CaseType', 'FORECLOSURE');
                await page.fill('#FileDateFrom', '{start_date}');
                await page.fill('#FileDateTo', '{end_date}');
                await page.click('input[type="submit"]');
                await page.waitForLoadState('networkidle');
                await page.waitForTimeout(3000);
                
                // Extract results
                const results = await page.evaluate(() => {{
                    const rows = document.querySelectorAll('.k-grid-content tr');
                    return Array.from(rows).map(row => {{
                        const cells = row.querySelectorAll('td');
                        return {{
                            case_number: cells[0]?.textContent?.trim() || '',
                            case_type: cells[1]?.textContent?.trim() || '',
                            party_name: cells[2]?.textContent?.trim() || '',
                            file_date: cells[3]?.textContent?.trim() || '',
                            status: cells[4]?.textContent?.trim() || ''
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
                f"{BROWSERLESS_URL}/function?token={BROWSERLESS_TOKEN}",
                headers={
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
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert to MM/DD/YYYY format
        start_parts = start_date.split('-')
        end_parts = end_date.split('-')
        start_formatted = f"{start_parts[1]}/{start_parts[2]}/{start_parts[0]}"
        end_formatted = f"{end_parts[1]}/{end_parts[2]}/{end_parts[0]}"
        
        records = self._scrape_with_browserless(start_formatted, end_formatted)
        
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
            'note': 'Using Browserless API with token query parameter and login credentials'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://core.duvalclerk.com/'}
    scraper = DuvalCourtRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
