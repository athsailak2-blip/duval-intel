#!/usr/bin/env python3
"""Test the correct approach - using DocTypesDisplay (Kendo ComboBox) field."""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://or.duvalclerk.com/search/SearchTypeDocType',
    'Origin': 'https://or.duvalclerk.com'
})

BASE_URL = "https://or.duvalclerk.com"

print("=" * 60)
print("Testing DocTypesDisplay Field Approach")
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

# Look at the Kendo ComboBox data source
print("\n3. Extracting Kendo ComboBox data source...")
scripts = soup.find_all('script')
for script in scripts:
    if script.string and 'DocTypesDisplay' in script.string and 'dataSource' in script.string:
        # Extract the data source values
        match = re.search(r'dataSource\s*:\s*(\[[^\]]+\])', script.string, re.DOTALL)
        if match:
            print(f"   DataSource found!")
            # Try to parse the data source
            ds_text = match.group(1)
            # Extract Text/Value pairs
            pairs = re.findall(r'"Text"\s*:\s*"([^"]+)"\s*,\s*"Value"\s*:\s*"([^"]*)"', ds_text)
            print(f"   Found {len(pairs)} document types:")
            for text, value in pairs[:20]:
                print(f"     {value}: {text}")

# Step 4: Try submitting with DocTypesDisplay value
print("\n4. Testing with DocTypesDisplay value...")

# The Kendo ComboBox likely sends the text value
# Let's try different formats

test_values = [
    'LIS PENDENS (LP)',
    'LP',
    'LIS PENDENS',
    '103',
]

for test_val in test_values:
    print(f"\n   Trying DocTypesDisplay='{test_val}'...")
    
    payload = {
        'DocTypesDisplay': test_val,
        'DateRangeList': ' ',
        'RecordDateFrom': '5/1/2026',
        'RecordDateTo': '6/8/2026',
    }
    
    action = BASE_URL + "/search/SearchTypeDocType"
    response = session.post(action, data=payload, timeout=60)
    
    print(f"   Status: {response.status_code}, Length: {len(response.text)}")
    
    if 'invalid' not in response.text.lower() and len(response.text) > 200:
        print(f"   SUCCESS! Response preview:")
        print(f"   {response.text[:300]}")
        break
    elif 'invalid' in response.text.lower():
        print(f"   Invalid doctype error")
    else:
        print(f"   Response: {response.text[:100]}")

# Step 5: Try with ALL as DocTypesDisplay
print("\n5. Testing with DocTypesDisplay='All'...")
payload = {
    'DocTypesDisplay': 'All',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
}

response = session.post(action, data=payload, timeout=60)
print(f"   Status: {response.status_code}, Length: {len(response.text)}")

if 'invalid' not in response.text.lower():
    print(f"   Response preview: {response.text[:300]}")
else:
    print(f"   Error: {response.text[:100]}")

# Step 6: Try with empty DocTypesDisplay but with ALL selected via checkboxes
print("\n6. Testing with SelectAllDocTypesToggle...")
payload = {
    'DocTypesDisplay': '',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
    'SelectAllDocTypesToggle': 'on',
}

response = session.post(action, data=payload, timeout=60)
print(f"   Status: {response.status_code}, Length: {len(response.text)}")

if 'invalid' not in response.text.lower():
    print(f"   Response preview: {response.text[:300]}")
else:
    print(f"   Error: {response.text[:100]}")

# Step 7: Try with the actual value from the dropdown
print("\n7. Testing with actual dropdown value format...")
# From the dropdown we saw: All|all
# The format seems to be DisplayText|Value
payload = {
    'DocTypesDisplay': 'all',
    'DateRangeList': ' ',
    'RecordDateFrom': '5/1/2026',
    'RecordDateTo': '6/8/2026',
}

response = session.post(action, data=payload, timeout=60)
print(f"   Status: {response.status_code}, Length: {len(response.text)}")

if 'invalid' not in response.text.lower():
    print(f"   Response preview: {response.text[:300]}")
else:
    print(f"   Error: {response.text[:100]}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
