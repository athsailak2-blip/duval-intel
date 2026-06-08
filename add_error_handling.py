#!/usr/bin/env python3
"""Add robust error handling to all scrapers that need it."""
import os

SCRAPERS_DIR = "/workspace/scrapers"

# duval_court_records.py - add try/except wrapper
with open(f"{SCRAPERS_DIR}/duval_court_records.py", 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        """Court records require login - cannot scrape without credentials."""
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': 0,
            'new_records': [],
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': ["Login required - CORE portal requires authentication"],
            'timestamp': datetime.now().isoformat(),
            'status': 'login_required',
            'note': 'Court records require registered account at core.duvalclerk.com'
        }'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        try:
            if days_back is None:
                seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
                days_back = 30 if seed_mode else 1
            """Court records require login - cannot scrape without credentials."""
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
                'errors': ["Login required - CORE portal requires authentication"],
                'timestamp': datetime.now().isoformat(),
                'status': 'login_required',
                'note': 'Court records require registered account at core.duvalclerk.com'
            }
        except Exception as e:
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
                'errors': [f"Unexpected error: {str(e)}"],
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'note': 'Court records require registered account at core.duvalclerk.com'
            }'''

content = content.replace(old_refresh, new_refresh)
with open(f"{SCRAPERS_DIR}/duval_court_records.py", 'w') as f:
    f.write(content)
print("Updated duval_court_records.py")

# duval_foreclosure_sales.py - add try/except wrapper
with open(f"{SCRAPERS_DIR}/duval_foreclosure_sales.py", 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
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
        }'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
        """Foreclosure sales require login - cannot scrape without bidder account."""
        try:
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
        except Exception as e:
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
                'errors': [f"Unexpected error: {str(e)}"],
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'note': 'Foreclosure sales require registered bidder account at duval.realforeclose.com'
            }'''

content = content.replace(old_refresh, new_refresh)
with open(f"{SCRAPERS_DIR}/duval_foreclosure_sales.py", 'w') as f:
    f.write(content)
print("Updated duval_foreclosure_sales.py")

# duval_tax_deed_sales.py - add try/except wrapper
with open(f"{SCRAPERS_DIR}/duval_tax_deed_sales.py", 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
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
        }'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = None) -> Dict:
        """Tax deed sales require login - cannot scrape without bidder account."""
        try:
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
        except Exception as e:
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
                'errors': [f"Unexpected error: {str(e)}"],
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'note': 'Tax deed sales require registered bidder account at duval.realtaxdeed.com'
            }'''

content = content.replace(old_refresh, new_refresh)
with open(f"{SCRAPERS_DIR}/duval_tax_deed_sales.py", 'w') as f:
    f.write(content)
print("Updated duval_tax_deed_sales.py")

# duval_gis.py - add try/except wrapper
with open(f"{SCRAPERS_DIR}/duval_gis.py", 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
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
        }'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """GIS data available via ArcGIS - may require authentication for bulk queries."""
        try:
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
        except Exception as e:
            return {
                'source_id': self.SOURCE_ID,
                'records_fetched': 0,
                'new_records': [],
                'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
                'errors': [f"Unexpected error: {str(e)}"],
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'note': 'GIS ArcGIS portal available at maps.coj.net/duvalproperty - bulk data requires API access'
            }'''

content = content.replace(old_refresh, new_refresh)
with open(f"{SCRAPERS_DIR}/duval_gis.py", 'w') as f:
    f.write(content)
print("Updated duval_gis.py")

print("\nAll scrapers now have robust error handling!")
