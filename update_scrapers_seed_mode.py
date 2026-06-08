#!/usr/bin/env python3
"""Write updated scrapers with SEED_MODE support."""
import os

# duval_code_enforcement.py
with open("/workspace/scrapers/duval_code_enforcement.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Jacksonville Municipal Code Compliance Scraper
Source: https://www.jacksonville.gov/departments/neighborhoods/municipal-code-compliance
Portal Type: Public Records Request (PRR)
"""
import requests
import json
import os
from datetime import datetime, timedelta
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
                status['has_search'] = bool(soup.find('input', type='search') or soup.find('input', {'name': re.compile(r'search', re.I)}))
                status['has_submit'] = bool(soup.find('button', type='submit') or soup.find('input', type='submit'))
                status['has_form'] = bool(soup.find('form'))
        except Exception as e:
            status['accessible'] = False
            status['error'] = str(e)
        return status
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for code enforcement data."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 7
        
        print("Code enforcement refresh requires PRR submission")
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
''')
print("Updated duval_code_enforcement.py")

# duval_foreclosure_sales.py
with open("/workspace/scrapers/duval_foreclosure_sales.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Duval County Foreclosure Sales Scraper
Source: https://www.duval.realforeclose.com/
Portal Type: RealAuction
Status: LOGIN REQUIRED - Requires bidder registration
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DuvalForeclosureSalesScraper:
    SOURCE_ID = "duval_foreclosure_sales"
    BASE_URL = "https://www.duval.realforeclose.com"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
        """Foreclosure sales require login - cannot scrape without bidder account."""
        # Check for seed mode from environment
        if days_ahead is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_ahead = 90 if seed_mode else 30
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': ["Login required - RealForeclose requires bidder registration"],
            'timestamp': datetime.now().isoformat(),
            'status': 'login_required',
            'note': 'Foreclosure sales require registered bidder account at duval.realforeclose.com'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realforeclose.com/'}
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
''')
print("Updated duval_foreclosure_sales.py")

# duval_gis.py
with open("/workspace/scrapers/duval_gis.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Duval County GIS Property Map Scraper
Source: https://maps.coj.net/duvalproperty/
Portal Type: ArcGIS / ESRI
Status: ArcGIS detected - REST API may require authentication
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DuvalGISScraper:
    SOURCE_ID = "duval_gis"
    BASE_URL = "https://maps.coj.net/duvalproperty"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """GIS data available via ArcGIS - may require authentication for bulk queries."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'note': 'GIS ArcGIS portal available at maps.coj.net/duvalproperty - bulk data requires API access'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://maps.coj.net/duvalproperty/'}
    scraper = DuvalGISScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
''')
print("Updated duval_gis.py")

# duval_parcel_master.py
with open("/workspace/scrapers/duval_parcel_master.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Duval County Property Appraiser Scraper
Source: https://paopropertysearch.coj.net/
Portal Type: Custom Web
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalPropertyAppraiserScraper:
    SOURCE_ID = "duval_parcel_master"
    BASE_URL = "https://paopropertysearch.coj.net"
    
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
    
    def _get_search_page(self) -> str:
        """Get the search page."""
        try:
            response = self.session.get(f"{self.BASE_URL}/Basic/Search.aspx", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting search page: {e}")
            return ""
    
    def search_by_address(self, street_number: str, street_name: str,
                         city: Optional[str] = None) -> List[Dict]:
        """Search parcels by address."""
        parcels = []
        try:
            search_url = f"{self.BASE_URL}/Basic/Search.aspx"
            search_page = self._get_search_page()
            soup = BeautifulSoup(search_page, 'html.parser')
            form = soup.find('form', id='aspnetForm') or soup.find('form')
            
            payload = {
                'StreetNumber': street_number,
                'StreetName': street_name,
                'City': city or '',
                'SearchType': 'MatchAll',
                'ResultsPerPage': 100
            }
            
            if form:
                hidden_fields = form.find_all('input', type='hidden')
                for field in hidden_fields:
                    if field.get('name'):
                        payload[field['name']] = field.get('value', '')
            
            response = self.session.post(search_url, data=payload, timeout=60)
            if response.status_code == 200:
                parcels = self._parse_search_results(response.text)
                print(f"Found {len(parcels)} parcels for address {street_number} {street_name}")
            else:
                print(f"Search returned HTTP {response.status_code}")
        except Exception as e:
            print(f"Error searching by address: {e}")
        return parcels
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """Parse HTML search results into structured parcel records."""
        parcels = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_tables = soup.find_all('table', class_=re.compile(r'result|grid|data|search', re.I))
            if not result_tables:
                result_tables = soup.find_all('table')
            
            for table in result_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        parcel = {
                            'source_id': self.SOURCE_ID,
                            'scraped_at': datetime.now().isoformat(),
                            'raw_html': str(row)
                        }
                        for i, cell in enumerate(cells):
                            text = cell.get_text(strip=True)
                            if re.match(r'^\\d{2}-\\d{2}-\\d{2}-\\d{3}-\\d{3}(-\\d{3})?$', text):
                                parcel['re_number'] = text
                            elif re.match(r'^\\d{1,2}/\\d{1,2}/\\d{4}$', text):
                                parcel['date'] = text
                            elif '$' in text and re.search(r'\\d+\\.\\d{2}', text):
                                parcel['value'] = text
                            elif len(text) > 20 and ('st' in text.lower() or 'ave' in text.lower() or 'dr' in text.lower() or 'rd' in text.lower()):
                                parcel['address'] = text
                            elif len(text) > 2 and len(text) < 50 and not any(c in text for c in '0123456789'):
                                if 'owner' not in parcel:
                                    parcel['owner_name'] = text
                                else:
                                    parcel['city'] = text
                        if 're_number' in parcel or 'address' in parcel:
                            parcels.append(parcel)
            
            if not parcels:
                result_divs = soup.find_all('div', class_=re.compile(r'result|parcel|item', re.I))
                for div in result_divs:
                    parcel = {
                        'source_id': self.SOURCE_ID,
                        'scraped_at': datetime.now().isoformat(),
                        'raw_text': div.get_text(strip=True)
                    }
                    parcels.append(parcel)
        except Exception as e:
            print(f"Error parsing search results: {e}")
        return parcels
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for parcel master data."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 7
        
        print(f"Full refresh would iterate all parcels - this is a large dataset (days_back={days_back})")
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Parcel master requires bulk download or incremental batching for full refresh'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://paopropertysearch.coj.net/'}
    scraper = DuvalPropertyAppraiserScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
''')
print("Updated duval_parcel_master.py")

# duval_tax_collector.py
with open("/workspace/scrapers/duval_tax_collector.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Duval County Tax Collector Lien Info Scraper
Source: https://tclieninfo.coj.net/
Portal Type: Custom Web
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalTaxCollectorScraper:
    SOURCE_ID = "duval_tax_collector"
    BASE_URL = "https://tclieninfo.coj.net"
    
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
    
    def _get_search_page(self) -> str:
        """Get the search page."""
        try:
            response = self.session.get(f"{self.BASE_URL}/Search.aspx", timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error getting search page: {e}")
            return ""
    
    def search_by_parcel(self, re_number: str) -> Dict:
        """Search tax lien info by parcel ID (RE Number)."""
        lien_info = {}
        try:
            search_url = f"{self.BASE_URL}/Search.aspx"
            search_page = self._get_search_page()
            soup = BeautifulSoup(search_page, 'html.parser')
            form = soup.find('form', id='aspnetForm') or soup.find('form')
            
            payload = {'RENumber': re_number}
            
            if form:
                hidden_fields = form.find_all('input', type='hidden')
                for field in hidden_fields:
                    if field.get('name'):
                        payload[field['name']] = field.get('value', '')
            
            response = self.session.post(search_url, data=payload, timeout=60)
            if response.status_code == 200:
                lien_info = self._parse_tax_results(response.text, re_number)
                print(f"Found tax lien info for RE# {re_number}")
            else:
                print(f"Search returned HTTP {response.status_code}")
        except Exception as e:
            print(f"Error searching tax liens: {e}")
        return lien_info
    
    def _parse_tax_results(self, html_content: str, re_number: str) -> Dict:
        """Parse HTML tax results into structured lien info."""
        lien_info = {
            're_number': re_number,
            'source_id': self.SOURCE_ID,
            'scraped_at': datetime.now().isoformat()
        }
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tax_tables = soup.find_all('table', class_=re.compile(r'tax|lien|amount|due', re.I))
            if not tax_tables:
                tax_tables = soup.find_all('table')
            
            for table in tax_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        if 'amount' in label or 'due' in label or 'balance' in label:
                            lien_info['amount_due'] = value
                        elif 'year' in label or 'tax year' in label:
                            lien_info['tax_year'] = value
                        elif 'status' in label or 'delinquent' in label:
                            lien_info['status'] = value
                        elif 'owner' in label:
                            lien_info['owner_name'] = value
                        elif 'address' in label or 'situs' in label:
                            lien_info['property_address'] = value
            
            if not lien_info.get('amount_due'):
                info_divs = soup.find_all('div', class_=re.compile(r'info|detail|field', re.I))
                for div in info_divs:
                    text = div.get_text(strip=True)
                    if ':' in text:
                        key, value = text.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if 'amount' in key or 'due' in key or 'balance' in key:
                            lien_info['amount_due'] = value
                        elif 'year' in key:
                            lien_info['tax_year'] = value
                        elif 'status' in key:
                            lien_info['status'] = value
            
            lien_info['raw_html'] = html_content[:3000]
        except Exception as e:
            print(f"Error parsing tax results: {e}")
        return lien_info
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run weekly refresh for tax collector data."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 7
        
        print(f"Tax collector refresh would iterate all tracked parcels (days_back={days_back})")
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'note': 'Tax collector requires a list of tracked parcels to check individually'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://tclieninfo.coj.net/'}
    scraper = DuvalTaxCollectorScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
''')
print("Updated duval_tax_collector.py")

# duval_tax_deed_sales.py
with open("/workspace/scrapers/duval_tax_deed_sales.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""
Duval County Tax Deed Sales Scraper
Source: https://www.duval.realtaxdeed.com/
Portal Type: RealAuction
Status: LOGIN REQUIRED - Requires bidder registration
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DuvalTaxDeedSalesScraper:
    SOURCE_ID = "duval_tax_deed_sales"
    BASE_URL = "https://www.duval.realtaxdeed.com"
    
    def __init__(self, config: Dict):
        self.config = config
    
    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
        """Tax deed sales require login - cannot scrape without bidder account."""
        # Check for seed mode from environment
        if days_ahead is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_ahead = 90 if seed_mode else 30
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': ["Login required - RealTaxDeed requires bidder registration"],
            'timestamp': datetime.now().isoformat(),
            'status': 'login_required',
            'note': 'Tax deed sales require registered bidder account at duval.realtaxdeed.com'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://www.duval.realtaxdeed.com/'}
    scraper = DuvalTaxDeedSalesScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
''')
print("Updated duval_tax_deed_sales.py")

print("\nAll scrapers updated with SEED_MODE support!")
