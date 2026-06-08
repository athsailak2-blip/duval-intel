import json

# The leads.json only has 3 leads - these are SAMPLE/DEMO data, not real scraped data
# The sources show record counts (156, 42, 18, 12, etc.) but these are also fabricated
# The scrapers are stubs that don't actually extract data from the portals

# Let me run the scrapers to see what they actually return
# and then build a proper data aggregation pipeline

# First, let's run the official records scraper with 30-day lookback
import subprocess
import sys

# Run official records scraper
print("=== Running Official Records Scraper ===")
result = subprocess.run([sys.executable, '/workspace/scrapers/duval_official_records.py'], 
                       capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])

print("\n=== Running Court Records Scraper ===")
result = subprocess.run([sys.executable, '/workspace/scrapers/duval_court_records.py'], 
                       capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])

print("\n=== Running Foreclosure Sales Scraper ===")
result = subprocess.run([sys.executable, '/workspace/scrapers/duval_foreclosure_sales.py'], 
                       capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])

print("\n=== Running Tax Deed Sales Scraper ===")
result = subprocess.run([sys.executable, '/workspace/scrapers/duval_tax_deed_sales.py'], 
                       capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
