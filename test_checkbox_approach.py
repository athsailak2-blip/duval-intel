#!/usr/bin/env python3
"""Test the correct checkbox-based approach for Official Records."""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://or.duvalclerk.com/',
    'Origin': 'https://or.duvalclerk.com'
})

BASE_URL = "https://or.duvalclerk.com"

print("=" * 60)
print("Testing Checkbox-Based Search")
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

# Step 2: Get search form and extract all checkbox values
print("\n2. Getting search form and extracting checkbox values...")
response = session.get(BASE_URL + "/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form')

# Get all checkbox values with their labels
checkboxes = form.find_all('input', {'name': 'DocTypeInfoCheckBox'})
print(f"   Total checkboxes: {len(checkboxes)}")

# Map checkbox values to document types
doc_type_map = {}
for cb in checkboxes:
    value = cb.get('value', '')
    # Find the label - usually in a table cell or adjacent element
    parent = cb.find_parent()
    label_text = ''
    if parent:
        # Try to find text in the same container
        text_nodes = parent.find_all(text=True)
        for text in text_nodes:
            text_str = str(text).strip()
            if text_str and text_str not in ['Date Range', '']:
                label_text = text_str
                break
    
    # Also check for label element
    label = soup.find('label', {'for': cb.get('id', '')})
    if label:
        label_text = label.get_text(strip=True)
    
    doc_type_map[value] = label_text
    
print(f"\n   DocType mapping (first 20):")
for val, label in list(doc_type_map.items())[:20]:
    print(f"     {val}: {label[:60]}")

# Look for LIS PENDENS specifically
print("\n3. Looking for LIS PENDENS checkbox...")
for val, label in doc_type_map.items():
    if 'lis pendens' in label.lower() or 'lp' in label.lower():
        print(f"   Found: {val} = {label}")

# Also look at the dropdown options which showed the mapping
select = form.find('select', {'name': 'DocTypeGroupDropDown'})
if select:
    print("\n   Dropdown option values (showing checkbox IDs):")
    for opt in select.find_all('option'):
        value = opt.get('value', '')
        text = opt.get_text(strip=True)
        if value and value != 'all':
            print(f"     {text}: checkbox IDs = {value}")

# Step 4: Try submitting with multiple checkbox values (as a list)
print("\n4. Testing with multiple checkbox values...")

# From the dropdown, we saw that LIS PENDENS (LP) is in group with IDs 69,75,81,85,86,87,91,92,95,97,103,104,108,110,115,120,122,125,126,128,129,131
# Let's try a few specific ones

# Try submitting with checkbox values as a list (how HTML forms work)
payload = {
    'DocTypesDisplay': '',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
    'DocTypeInfoCheckBox': ['103', '97', '95'],  # Try multiple as list
    'SelectAllDocTypesToggle': ''
}

action = BASE_URL + "/search/SearchTypeDocType"
response = session.post(action, data=payload, timeout=60)
print(f"   Status: {response.status_code}, Length: {len(response.text)}")

# Check response
if 'invalid' in response.text.lower():
    print("   Still getting 'invalid doctype' error")
else:
    print(f"   Response: {response.text[:200]}")

# Step 5: Try with ALL checkbox values from a group
print("\n5. Trying with ALL checkbox values from Financial News group...")
# The dropdown showed: 69,75,81,85,86,87,91,92,95,97,103,104,108,110,115,120,122,125,126,128,129,131
all_values = ['69', '75', '81', '85', '86', '87', '91', '92', '95', '97', '103', '104', '108', '110', '115', '120', '122', '125', '126', '128', '129', '131']

payload_all = {
    'DocTypesDisplay': '',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
}

# Add all checkboxes
for val in all_values:
    payload_all[f'DocTypeInfoCheckBox'] = val

# Actually, let's try a different approach - use the exact format the browser would send
# When multiple checkboxes with same name are checked, they're sent as multiple key-value pairs
print("\n6. Trying with proper multi-value form encoding...")

from urllib.parse import urlencode

# Build query string manually with multiple DocTypeInfoCheckBox values
params = [
    ('DocTypesDisplay', ''),
    ('DateRangeList', ' '),
    ('RecordDateFrom', '5/1/2026'),
    ('RecordDateTo', '6/8/2026'),
    ('DocTypeInfoCheckBox', '103'),
    ('DocTypeInfoCheckBox', '97'),
    ('DocTypeInfoCheckBox', '95'),
    ('SelectAllDocTypesToggle', '')
]

query_string = urlencode(params)
print(f"   Query string: {query_string[:100]}...")

# Try POST with this data
response = session.post(action, data=dict(params), timeout=60)
print(f"   Status: {response.status_code}, Length: {len(response.text)}")

if 'invalid' in response.text.lower():
    print("   ERROR: Still getting invalid doctype")
    print(f"   Response: {response.text[:200]}")
else:
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"   Tables found: {len(tables)}")
    print(f"   First 500 chars: {response.text[:500]}")

# Step 7: Let's look at the actual JavaScript that handles the search
print("\n7. Looking at page scripts for search handling...")
scripts = soup.find_all('script')
for script in scripts:
    if script.string:
        if 'search' in script.string.lower() or 'submit' in script.string.lower() or 'doctype' in script.string.lower():
            text = script.string[:300]
            print(f"   Script: {text[:200]}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
