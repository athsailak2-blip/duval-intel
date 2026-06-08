import json
import os

# Read the current tax deed sales scraper
with open('/workspace/scrapers/duval_tax_deed_sales.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Duval County Tax Deed Sales Scraper
Source: https://www.duval.realtaxdeed.com/
Portal Type: RealAuction
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalTaxDeedSalesScraper:
    SOURCE_ID = "duval_tax_deed_sales"
    BASE_URL = "https://www.duval.realtaxdeed.com"
    
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
    
    def get_sale_calendar(self) -> List[Dict]:
        """Get upcoming tax deed sales calendar."""
        sales = []
        
        try:
            calendar_url = f"{self.BASE_URL}/index.cfm"
            
            params = {
                'zaction': 'auction',
                'zmethod': 'calendar'
            }
            
            response = self.session.get(calendar_url, params=params, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for calendar entries
                calendar_items = soup.find_all(['div', 'a', 'td'], class_=re.compile(r'calendar|sale|auction|date', re.I))
                
                for item in calendar_items:
                    text = item.get_text(strip=True)
                    
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
                
                print(f"Found {len(sales)} tax deed sale dates in calendar")
            else:
                print(f"Calendar request returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error getting calendar: {e}")
        
        return sales
    
    def get_sale_list(self, sale_date: str) -> List[Dict]:
        """Get list of properties for a specific tax deed sale."""
        properties = []
        
        try:
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
                            if re.match(r'^\d{2}-\d{2}-\d{2}-\d{3}-\d{3}(-\d{3})?$', text):  # Parcel ID
                                prop['parcel_id'] = text
                            elif '$' in text and re.search(r'\d+\.\d{2}', text):  # Amount
                                prop['opening_bid'] = text
                            elif re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', text):  # Date
                                prop['sale_date'] = text
                            elif len(text) > 20 and ('st' in text.lower() or 'ave' in text.lower() or 'dr' in text.lower()):
                                prop['property_address'] = text
                            elif 'tax deed' in text.lower() or 'certificate' in text.lower():
                                prop['legal_info'] = text
                        
                        # Only add if we have some identifying information
                        if 'parcel_id' in prop or 'property_address' in prop:
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
                
                print(f"Found {len(properties)} tax deed properties for sale date {sale_date}")
            else:
                print(f"Sale list request returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error getting sale list: {e}")
        
        return properties
    
    def get_lands_available(self) -> List[Dict]:
        """Get List of Lands Available (unsold properties)."""
        properties = []
        
        try:
            lands_url = f"{self.BASE_URL}/index.cfm"
            
            params = {
                'zaction': 'auction',
                'zmethod': 'lands_available'
            }
            
            response = self.session.get(lands_url, params=params, timeout=60)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for property listings in lands available
                property_rows = soup.find_all('tr', class_=re.compile(r'property|item|land', re.I))
                
                if not property_rows:
                    property_rows = soup.find_all('tr')
                
                for row in property_rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        prop = {
                            'source_id': self.SOURCE_ID,
                            'list_type': 'lands_available',
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        
                        # Extract data from cells
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            
                            if re.match(r'^\d{2}-\d{2}-\d{2}-\d{3}-\d{3}(-\d{3})?$', text):
                                prop['parcel_id'] = text
                            elif '$' in text and re.search(r'\d+\.\d{2}', text):
                                prop['minimum_bid'] = text
                            elif len(text) > 20 and ('st' in text.lower() or 'ave' in text.lower() or 'dr' in text.lower()):
                                prop['property_address'] = text
                        
                        if 'parcel_id' in prop or 'property_address' in prop:
                            properties.append(prop)
                
                print(f"Found {len(properties)} lands available properties")
            else:
                print(f"Lands available request returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error getting lands available: {e}")
        
        return properties
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run weekly refresh for tax deed sales."""
        print("Refreshing tax deed sales...")
        
        sales = self.get_sale_calendar()
        
        # For each sale date, get the property list
        all_properties = []
        for sale in sales:
            sale_date = sale.get('sale_date', '')
            if sale_date:
                properties = self.get_sale_list(sale_date)
                all_properties.extend(properties)
                time.sleep(1)  # Be polite
        
        # Also get lands available
        lands = self.get_lands_available()
        all_properties.extend(lands)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(all_properties),
            'new_records': all_properties,
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'sale_dates_found': len(sales),
            'lands_available': len(lands)
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realtaxdeed.com/'}
    scraper = DuvalTaxDeedSalesScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_tax_deed_sales.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced tax deed sales scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_tax_deed_sales.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")
