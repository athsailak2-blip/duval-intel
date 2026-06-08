import json
import os

# Read the current code enforcement scraper
with open('/workspace/scrapers/duval_code_enforcement.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Jacksonville Municipal Code Compliance Scraper
Source: https://www.jacksonville.gov/departments/neighborhoods/municipal-code-compliance
Portal Type: Public Records Request (PRR)
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalCodeEnforcementScraper:
    SOURCE_ID = "duval_code_enforcement"
    BASE_URL = "https://jacksonvillefl.govqa.us"
    PRR_BASE_URL = "https://records.coj.net"
    
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
    
    def _check_prr_portal(self) -> Dict:
        """Check if the PRR portal is accessible."""
        status = {}
        
        try:
            response = self.session.get(f"{self.PRR_BASE_URL}/", timeout=30)
            
            status['accessible'] = response.status_code == 200
            status['status_code'] = response.status_code
            status['url'] = self.PRR_BASE_URL
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for common PRR portal elements
                status['has_search'] = bool(soup.find('input', type='search') or soup.find('input', {'name': re.compile(r'search', re.I)}))
                status['has_submit'] = bool(soup.find('button', type='submit') or soup.find('input', type='submit'))
                status['has_form'] = bool(soup.find('form'))
        
        except Exception as e:
            status['accessible'] = False
            status['error'] = str(e)
        
        return status
    
    def submit_records_request(self, request_details: Dict) -> str:
        """Submit a public records request for code enforcement data."""
        request_id = ""
        
        try:
            # Check PRR portal first
            portal_status = self._check_prr_portal()
            
            if not portal_status.get('accessible', False):
                print(f"PRR portal not accessible: {portal_status.get('error', 'Unknown error')}")
                return ""
            
            prr_url = f"{self.PRR_BASE_URL}/WEBAPP/_rs/supporthome.aspx"
            
            # Get the PRR form page
            response = self.session.get(prr_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                form = soup.find('form', id='aspnetForm') or soup.find('form')
                
                # Build the PRR payload
                payload = {
                    'RequestType': 'Public Records Request',
                    'RequestDescription': request_details.get('description', 'Code enforcement case data for properties in Duval County'),
                    'RequestCategory': 'Code Enforcement',
                    'ContactName': request_details.get('contact_name', ''),
                    'ContactEmail': request_details.get('contact_email', ''),
                    'ContactPhone': request_details.get('contact_phone', ''),
                    'DateRangeStart': request_details.get('start_date', ''),
                    'DateRangeEnd': request_details.get('end_date', '')
                }
                
                # Add any hidden form fields
                if form:
                    hidden_fields = form.find_all('input', type='hidden')
                    for field in hidden_fields:
                        if field.get('name'):
                            payload[field['name']] = field.get('value', '')
                
                # Submit the PRR
                submit_response = self.session.post(prr_url, data=payload, timeout=60)
                
                if submit_response.status_code == 200:
                    # Try to extract request ID from response
                    submit_soup = BeautifulSoup(submit_response.text, 'html.parser')
                    
                    # Look for confirmation message with request ID
                    confirmation = submit_soup.find(text=re.compile(r'request\s*(?:id|number|#)', re.I))
                    
                    if confirmation:
                        id_match = re.search(r'(\d{4,})', confirmation)
                        if id_match:
                            request_id = id_match.group(1)
                    
                    if not request_id:
                        # Try to find any numeric ID in the page
                        id_elements = submit_soup.find_all(text=re.compile(r'^\d{6,}$'))
                        if id_elements:
                            request_id = id_elements[0].strip()
                    
                    print(f"PRR submitted successfully. Request ID: {request_id or 'Unknown'}")
                else:
                    print(f"PRR submission returned HTTP {submit_response.status_code}")
            else:
                print(f"PRR form page returned HTTP {response.status_code}")
        
        except Exception as e:
            print(f"Error submitting PRR: {e}")
        
        return request_id
    
    def check_request_status(self, request_id: str) -> Dict:
        """Check status of a public records request."""
        status = {}
        
        try:
            status_url = f"{self.PRR_BASE_URL}/WEBAPP/_rs/RequestStatus.aspx"
            
            payload = {
                'RequestId': request_id
            }
            
            response = self.session.post(status_url, data=payload, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                status['request_id'] = request_id
                status['raw_html'] = response.text[:3000]
                
                # Try to extract status information
                status_elements = soup.find_all(text=re.compile(r'status|pending|complete|closed', re.I))
                
                if status_elements:
                    status['status_text'] = status_elements[0].strip()
                
                # Look for any date information
                date_elements = soup.find_all(text=re.compile(r'\d{1,2}/\d{1,2}/\d{4}'))
                
                if date_elements:
                    status['dates_found'] = [d.strip() for d in date_elements[:5]]
        
        except Exception as e:
            print(f"Error checking status: {e}")
        
        return status
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run weekly refresh for code enforcement data."""
        print("Code enforcement refresh requires PRR submission")
        
        # Check PRR portal status
        portal_status = self._check_prr_portal()
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': ["PRR required - manual process"],
            'timestamp': datetime.now().isoformat(),
            'prr_portal_status': portal_status,
            'note': 'Code enforcement data requires Public Records Request (PRR) submission'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.jacksonville.gov/departments/neighborhoods/municipal-code-compliance'}
    scraper = DuvalCodeEnforcementScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_code_enforcement.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced code enforcement scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_code_enforcement.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")

# Now let's create a summary of all enhanced scrapers
print("\n" + "="*60)
print("SCRAPER ENHANCEMENT SUMMARY")
print("="*60)

scrapers = [
    'duval_official_records.py',
    'duval_court_records.py',
    'duval_foreclosure_sales.py',
    'duval_tax_deed_sales.py',
    'duval_parcel_master.py',
    'duval_tax_collector.py',
    'duval_gis.py',
    'duval_code_enforcement.py'
]

for scraper_name in scrapers:
    scraper_path = f'/workspace/scrapers/{scraper_name}'
    if os.path.exists(scraper_path):
        with open(scraper_path, 'r') as f:
            content = f.read()
        
        # Check for key indicators of enhancement
        has_requests = 'requests.' in content
        has_parsing = 'BeautifulSoup' in content
        has_actual_post = 'session.post' in content
        has_actual_get = 'session.get' in content
        
        print(f"\n{scraper_name}:")
        print(f"  Size: {len(content)} chars")
        print(f"  HTTP requests: {'YES' if has_requests else 'NO'}")
        print(f"  HTML parsing: {'YES' if has_parsing else 'NO'}")
        print(f"  POST requests: {'YES' if has_actual_post else 'NO'}")
        print(f"  GET requests: {'YES' if has_actual_get else 'NO'}")
    else:
        print(f"\n{scraper_name}: NOT FOUND")

print("\n" + "="*60)
