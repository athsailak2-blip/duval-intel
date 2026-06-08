import requests
from bs4 import BeautifulSoup
import re

# The scrapers are returning 0 or empty records because:
# 1. Official Records: portal structure doesn't match the assumed form submission
# 2. Court Records: 404 on the assumed API endpoints
# 3. Foreclosure/Tax Deed: finding dates but no actual property data (raw_text is empty)

# Let me check the actual portal structures by fetching the pages

print("=== Checking Official Records Portal ===")
resp = requests.get("https://or.duvalclerk.com/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Look for forms
    forms = soup.find_all('form')
    print(f"Forms found: {len(forms)}")
    for i, form in enumerate(forms[:3]):
        action = form.get('action', 'N/A')
        method = form.get('method', 'GET')
        print(f"  Form {i}: action={action}, method={method}")
        inputs = form.find_all('input')
        print(f"    Inputs: {len(inputs)}")
        for inp in inputs[:5]:
            print(f"      - {inp.get('name', 'N/A')} ({inp.get('type', 'text')})")
    
    # Look for links to search pages
    links = soup.find_all('a', href=re.compile(r'search|Search', re.I))
    print(f"\nSearch links: {len(links)}")
    for link in links[:10]:
        print(f"  - {link.get('href', 'N/A')}: {link.get_text(strip=True)[:50]}")
    
    # Look for any navigation/menu
    nav = soup.find_all(['nav', 'ul', 'div'], class_=re.compile(r'nav|menu|sidebar', re.I))
    print(f"\nNav elements: {len(nav)}")

print("\n=== Checking Court Records Portal ===")
resp = requests.get("https://core.duvalclerk.com/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    forms = soup.find_all('form')
    print(f"Forms found: {len(forms)}")
    for i, form in enumerate(forms[:3]):
        action = form.get('action', 'N/A')
        print(f"  Form {i}: action={action}")
    
    links = soup.find_all('a', href=re.compile(r'search|Search|case|Case', re.I))
    print(f"\nSearch/case links: {len(links)}")
    for link in links[:10]:
        print(f"  - {link.get('href', 'N/A')}: {link.get_text(strip=True)[:50]}")

print("\n=== Checking Foreclosure Sales Portal ===")
resp = requests.get("https://www.duval.realforeclose.com/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Look for calendar or auction links
    links = soup.find_all('a', href=re.compile(r'auction|calendar|sale', re.I))
    print(f"Auction/calendar links: {len(links)}")
    for link in links[:10]:
        print(f"  - {link.get('href', 'N/A')}: {link.get_text(strip=True)[:50]}")
    
    # Look for date patterns
    dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', resp.text)
    print(f"\nDates found in page: {len(dates)}")
    if dates:
        print(f"  Sample: {dates[:5]}")
    
    # Look for property/case numbers
    cases = re.findall(r'\d{4}-\d{2}-[A-Z]{2}-\d+', resp.text)
    print(f"Case numbers found: {len(cases)}")
    if cases:
        print(f"  Sample: {cases[:5]}")
