import json
import os

# Read the current foreclosure sales scraper
with open('/workspace/scrapers/duval_foreclosure_sales.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Duval County Foreclosure Sales Scraper
Source: https://www.duval.realforeclose.com/
Portal Type: RealAuction
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalForeclosureSalesScraper:
    SOURCE_ID = "duval_foreclosure_sales"
    BASE_URL = "https://www.duval.realforeclose.com"
    
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
    
    def _get_main_page(self) -> str:
        """Get the main auction page."""
        try:
            response = self.session.get(f"{self.BASE_URL}/", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting main page: {e}")
            return ""
    
    def get_sale_calendar(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Dict]:
        """Get upcoming foreclosure sales calendar."""
        sales = []
        
        try:
            # RealAuction portals typically have a calendar view
            calendar_url = f"{self.BASE_URL}/index.cfm"
            
            params = {
                'zaction': 'auction',
                'zmethod': 'calendar'
            }
            
            response = self.session.get(calendar_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for calendar entries or sale dates
                # RealAuction typically shows dates with sale counts
                calendar_items = soup.find_all(['div', 'a', 'td'], class_=re.compile(r'calendar|sale|auction|date', re.I))
                
                for item in calendar_items:
                    text = item.get_text(strip=True)
                    
                    # Look for dates with sale information
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                    count_match = re.search(r'(\d+)\s+(?:sale|property|item)', text, re.I)
                    
                    if date_match:
                        sale = {
                            'source_id': self.SOURCE_ID,
                            'sale_date': date_match.group(1),
                            'scraped_at': datetime.now().isoformat(),
                            'raw_text': text
                        }
                        
                        if count_match:
                            sale['property_count'] = int(count_match.group(1))
                        
                        sales.append(sale)
                
                # If no calendar items found, try looking for any date patterns
                if not sales:
                    date_patterns = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', response.text)
                    
                    for date_str in set(date_patterns):
                        sales.append({
                            'source_id': self.SOURCE_ID,
                            'sale_date': date_str,
                            'scraped_at': datetime.now().isoformat()
                        })
                
                print(f"Found {len(sales)} sale dates in calendar")
            else:
                print(f"Calendar request returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error getting calendar: {e}")
        
        return sales
    
    def get_sale_list(self, sale_date: str) -> List[Dict]:
        """Get list of properties for a specific sale date."""
        properties = []
        
        try:
            # RealAuction typically uses sale date in URL or params
            list_url = f"{self.BASE_URL}/index.cfm"
            
            params = {
                'zaction': 'auction',
                'zmethod': 'list',
                'sale_date': sale_date
            }
            
            response = self.session.get(list_url, params=params, timeout=60)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for property listings
                # RealAuction typically shows properties in tables or cards
                property_rows = soup.find_all('tr', class_=re.compile(r'property|item|sale', re.I))
                
                if not property_rows:
                    property_rows = soup.find_all('tr')
                
                for row in property_rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        prop = {
                            'source_id': self.SOURCE_ID,
                            'sale_date': sale_date,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        
                        # Extract data from cells
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            # Try to identify fields
                            if re.match(r'^\d{4}-\d{2}-[A-Z]{2}-\d{6}$', text):  # Case number
                                prop['case_number'] = text
                            elif '$' in text and re.search(r'\d+\.\d{2}', text):  # Amount
                                prop['opening_bid'] = text
                            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):  # Date
                                prop['sale_date'] = text
                            elif len(text) > 20 and ('st' in text.lower() or 'ave' in text.lower() or 'dr' in text.lower()):
                                # Likely an address
                                prop['property_address'] = text
                            elif 'judgment' in text.lower() or 'plaintiff' in text.lower():
                                prop['legal_info'] = text
                        
                        # Only add if we have some identifying information
                        if 'case_number' in prop or 'property_address' in prop:
                            properties.append(prop)
                
                # If no table rows found, try div-based listings
                if not properties:
                    property_divs = soup.find_all('div', class_=re.compile(r'property|item|listing', re.I))
                    
                    for div in property_divs:
                        prop = {
                            'source_id': self.SOURCE_ID,
                            'sale_date': sale_date,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_text': div.get_text(strip=True)
                        }
                        properties.append(prop)
                
                print(f"Found {len(properties)} properties for sale date {sale_date}")
            else:
                print(f"Sale list request returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error getting sale list: {e}")
        
        return properties
    
    def get_property_details(self, case_number: str) -> Dict:
        """Get details for a specific foreclosure property."""
        details = {}
        
        try:
            detail_url = f"{self.BASE_URL}/index.cfm"
            
            params = {
                'zaction': 'auction',
                'zmethod': 'detail',
                'case_number': case_number
            }
            
            response = self.session.get(detail_url, params=params, timeout=30)
            
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
            print(f"Error getting property details: {e}")
        
        return details
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run daily refresh for foreclosure sales."""
        # Get sales for next 30 days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Refreshing foreclosure sales from {start_date} to {end_date}")
        
        sales = self.get_sale_calendar(start_date, end_date)
        
        # For each sale date, get the property list
        all_properties = []
        for sale in sales:
            sale_date = sale.get('sale_date', '')
            if sale_date:
                properties = self.get_sale_list(sale_date)
                all_properties.extend(properties)
                time.sleep(1)  # Be polite
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(all_properties),
            'new_records': all_properties,
            'updated_cursor': start_date,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'sale_dates_found': len(sales)
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realforeclose.com/'}
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_foreclosure_sales.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced foreclosure sales scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_foreclosure_sales.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")
