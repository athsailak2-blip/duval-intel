import json
import os

# Update official records scraper to use 30-day lookback for initial seeding
with open('/workspace/scrapers/duval_official_records.py', 'r') as f:
    content = f.read()

# Replace the refresh method to support 30-day seeding
old_refresh = '''    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """
        Run daily refresh.
        
        Args:
            cursor: Last processed date (YYYY-MM-DD)
        
        Returns:
            Dict with new_records, updated_cursor, errors
        """
        if cursor:
            start_date = cursor
        else:
            # Default to yesterday
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = 1) -> Dict:
        """
        Run daily refresh or historical seeding.
        
        Args:
            cursor: Last processed date (YYYY-MM-DD)
            days_back: Number of days to look back (1 for daily, 30 for initial seeding)
        
        Returns:
            Dict with new_records, updated_cursor, errors
        """
        if cursor:
            start_date = cursor
        else:
            # Default: 1 day for daily refresh, 30 days for initial seeding
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')'''

content = content.replace(old_refresh, new_refresh)

with open('/workspace/scrapers/duval_official_records.py', 'w') as f:
    f.write(content)

print("Updated official_records scraper with days_back parameter")

# Update court records scraper
with open('/workspace/scrapers/duval_court_records.py', 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run daily refresh for court records."""
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_back: int = 1) -> Dict:
        """Run daily refresh or historical seeding for court records."""
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        end_date = datetime.now().strftime('%Y-%m-%d')'''

content = content.replace(old_refresh, new_refresh)

with open('/workspace/scrapers/duval_court_records.py', 'w') as f:
    f.write(content)

print("Updated court_records scraper with days_back parameter")

# Update foreclosure sales scraper
with open('/workspace/scrapers/duval_foreclosure_sales.py', 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run daily refresh for foreclosure sales."""
        # Get sales for next 30 days
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = 30) -> Dict:
        """Run daily refresh for foreclosure sales."""
        # Get sales for next N days (30 for daily, 90 for initial seeding)
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')'''

content = content.replace(old_refresh, new_refresh)

with open('/workspace/scrapers/duval_foreclosure_sales.py', 'w') as f:
    f.write(content)

print("Updated foreclosure_sales scraper with days_ahead parameter")

# Update tax deed sales scraper
with open('/workspace/scrapers/duval_tax_deed_sales.py', 'r') as f:
    content = f.read()

old_refresh = '''    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run weekly refresh for tax deed sales."""
        sales = self.get_sale_calendar()'''

new_refresh = '''    def refresh(self, cursor: Optional[str] = None, days_ahead: int = 30) -> Dict:
        """Run weekly refresh for tax deed sales."""
        sales = self.get_sale_calendar()'''

content = content.replace(old_refresh, new_refresh)

with open('/workspace/scrapers/duval_tax_deed_sales.py', 'w') as f:
    f.write(content)

print("Updated tax_deed_sales scraper")

print("\nAll scrapers updated with configurable lookback/lookahead periods")
print("Default: 1 day for daily refresh")
print("Seeding: 30 days for initial historical data collection")
