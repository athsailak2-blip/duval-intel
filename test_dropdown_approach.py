#!/usr/bin/env python3
"""Test using the dropdown group selection approach."""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://or.duvalclerk.com/',
    'Origin': 'https://or.duvalclerk.com',
    'X-Requested-With': 'XMLHttpRequest'
})

BASE_URL = "https://or.duvalclerk.com"

print("=" * 60)
print("Testing Dropdown Group Selection")
print("=" * 60)

# Step 1: Accept disclaimer
print("\n1. Accepting disclaimer...")
response = session.post(
    BASE_URL + "/search/Disclaimer",
    data={"Disclaimer": "true"},
    timeout=30,
    allow_redirects=True
)
print(f"   Status: {response.status_code}")

# Step 2: Get search form
print("\n2. Getting search form...")
response = session.get(BASE_URL + "/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form')

# Step 3: Try different submission approaches
print("\n3. Testing different submission approaches...")

# Approach A: Use DocTypeGroupDropDown with the LIEN/JUDGMENT group
print("\n   Approach A: Using DocTypeGroupDropDown with LIEN/JUDGMENT group...")
payload_a = {
    'DocTypeGroupDropDown': '94,97,98,99,103',  # LIEN/JUDGMENT group
    'DocTypesDisplay': '',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
}

action = BASE_URL + "/search/SearchTypeDocType"
response_a = session.post(action, data=payload_a, timeout=60)
print(f"   Status: {response_a.status_code}, Length: {len(response_a.text)}")

# Check if we got results
soup_a = BeautifulSoup(response_a.text, 'html.parser')
tables_a = soup_a.find_all('table')
print(f"   Tables: {len(tables_a)}")

# Look for the results grid (Kendo UI)
scripts = soup_a.find_all('script')
for script in scripts:
    if script.string and 'kendo' in script.string.lower():
        print(f"   Kendo script found (length: {len(script.string)})")
        # Look for dataSource
        if 'datasource' in script.string.lower() or 'dataSource' in script.string:
            print(f"   DataSource found in script!")
            # Extract the data
            match = re.search(r'dataSource:\s*\{[^}]*data:\s*(\[[^\]]*\])', script.string, re.DOTALL)
            if match:
                print(f"   Data array found!")

# Approach B: Try with ALL doc types selected
print("\n   Approach B: Using 'All' in DocTypeGroupDropDown...")
payload_b = {
    'DocTypeGroupDropDown': 'all',
    'DocTypesDisplay': '',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
}

response_b = session.post(action, data=payload_b, timeout=60)
print(f"   Status: {response_b.status_code}, Length: {len(response_b.text)}")

# Approach C: Check if there's an AJAX endpoint
print("\n   Approach C: Looking for AJAX/API endpoints...")
# Check the page for any API URLs
api_patterns = re.findall(r'https?://[^\s"\']+api[^\s"\']*', response.text, re.I)
if api_patterns:
    print(f"   API URLs found: {api_patterns[:5]}")

# Look for any data URLs in scripts
for script in soup.find_all('script'):
    if script.string:
        urls = re.findall(r'url:\s*["\']([^"\']+)["\']', script.string)
        if urls:
            print(f"   URLs in scripts: {urls[:5]}")

# Approach D: Try the search with __RequestVerificationToken if present
print("\n   Approach D: Checking for anti-forgery tokens...")
# The form might need a request verification token
token_input = soup.find('input', {'name': '__RequestVerificationToken'})
if token_input:
    print(f"   Token found: {token_input.get('value', 'N/A')[:30]}...")
else:
    print("   No anti-forgery token found")

# Check all hidden inputs again
print("\n   All hidden inputs in form:")
for inp in form.find_all('input', type='hidden'):
    print(f"     {inp.get('name', 'N/A')}: {inp.get('value', 'N/A')[:50]}")

# Approach E: Try submitting to the results endpoint directly
print("\n   Approach E: Checking if there's a results endpoint...")
# Look for any iframe or redirect that might show results
iframes = soup.find_all('iframe')
print(f"   Iframes in form page: {len(iframes)}")
for iframe in iframes:
    print(f"     Src: {iframe.get('src', 'N/A')}")

# Look at the actual response content more carefully
print("\n   Response content analysis (first 1000 chars):")
print(f"   {response_a.text[:1000]}")

print("\n" + "=" * 60)
print("Analysis complete")
print("=" * 60)
