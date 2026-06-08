#!/usr/bin/env python3
"""Debug the Official Records portal to understand its actual structure."""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
})

BASE_URL = "https://or.duvalclerk.com"

print("=" * 60)
print("Debugging Official Records Portal")
print("=" * 60)

# Step 1: Get the main page
print("\n1. Getting main page...")
try:
    response = session.get(BASE_URL + "/", timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    print(f"   Content length: {len(response.text)}")
    
    # Check for redirects
    if response.history:
        print(f"   Redirects: {[r.url for r in response.history]}")
    
    # Look for forms
    soup = BeautifulSoup(response.text, 'html.parser')
    forms = soup.find_all('form')
    print(f"\n   Forms found: {len(forms)}")
    
    for i, form in enumerate(forms[:3]):
        print(f"\n   Form {i+1}:")
        print(f"     Action: {form.get('action', 'N/A')}")
        print(f"     Method: {form.get('method', 'N/A')}")
        print(f"     ID: {form.get('id', 'N/A')}")
        
        # List all inputs
        inputs = form.find_all('input')
        print(f"     Inputs: {len(inputs)}")
        for inp in inputs[:10]:
            print(f"       - {inp.get('name', 'N/A')} (type={inp.get('type', 'N/A')}, value={inp.get('value', 'N/A')[:50]})")
        
        # List all selects
        selects = form.find_all('select')
        print(f"     Selects: {len(selects)}")
        for sel in selects:
            print(f"       - {sel.get('name', 'N/A')}")
            options = sel.find_all('option')
            for opt in options[:5]:
                print(f"         {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:50]}")
    
    # Look for links to search pages
    print("\n   Links to search functionality:")
    links = soup.find_all('a', href=re.compile(r'search|Search|doc|Doc', re.I))
    for link in links[:10]:
        print(f"     {link.get('href', 'N/A')}: {link.get_text(strip=True)[:50]}")
    
    # Look for any script that might indicate the portal type
    scripts = soup.find_all('script')
    print(f"\n   Scripts found: {len(scripts)}")
    for script in scripts[:5]:
        if script.string:
            text = script.string[:200]
            if 'tyler' in text.lower() or 'search' in text.lower() or 'angular' in text.lower() or 'react' in text.lower():
                print(f"     Script hint: {text[:100]}")
    
except Exception as e:
    print(f"   ERROR: {e}")

# Step 2: Try common search endpoints
print("\n2. Testing common search endpoints...")
endpoints_to_test = [
    "/search/SearchTypeDocType",
    "/Search/SearchTypeDocType",
    "/search/SearchTypeName",
    "/Search/SearchTypeName",
    "/Search.aspx",
    "/search.aspx",
    "/search",
    "/Search",
]

for endpoint in endpoints_to_test:
    try:
        url = BASE_URL + endpoint
        response = session.get(url, timeout=10, allow_redirects=False)
        print(f"   {endpoint}: HTTP {response.status_code} (redirects: {len(response.history)})")
    except Exception as e:
        print(f"   {endpoint}: ERROR - {str(e)[:50]}")

# Step 3: Check if there's a disclaimer/acceptance page
print("\n3. Checking for disclaimer or acceptance requirements...")
try:
    response = session.get(BASE_URL + "/", timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for disclaimer text
    disclaimer_keywords = ['disclaimer', 'accept', 'agree', 'terms', 'conditions', 'i understand', 'acknowledge']
    for keyword in disclaimer_keywords:
        elements = soup.find_all(text=re.compile(keyword, re.I))
        if elements:
            print(f"   Found '{keyword}' in page: {len(elements)} occurrences")
            for el in elements[:2]:
                print(f"     Context: {el.strip()[:100]}")
    
    # Look for checkbox inputs
    checkboxes = soup.find_all('input', type='checkbox')
    print(f"\n   Checkboxes found: {len(checkboxes)}")
    for cb in checkboxes:
        print(f"     Name: {cb.get('name', 'N/A')}, Value: {cb.get('value', 'N/A')}")
    
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Debug complete")
print("=" * 60)
