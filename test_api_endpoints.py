import requests
from bs4 import BeautifulSoup
import re

# I found API endpoints! Let me check /Search/Results and /Search/GetResults
# These might be the actual data endpoints

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Accept disclaimer
resp = session.get("https://or.duvalclerk.com/search/Disclaimer", timeout=30)
if resp.status_code == 200:
    session.post("https://or.duvalclerk.com/search/Disclaimer", 
                data={'disclaimer': 'true'}, timeout=30)

# Try /Search/Results
print("=== Testing /Search/Results ===")
resp = session.get("https://or.duvalclerk.com/Search/Results", timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"Content length: {len(resp.text)}")
    print(f"First 500 chars: {resp.text[:500]}")

# Try /Search/GetResults
print("\n=== Testing /Search/GetResults ===")
resp = session.get("https://or.duvalclerk.com/Search/GetResults", timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"Content length: {len(resp.text)}")
    print(f"First 500 chars: {resp.text[:500]}")

# Try /api/
print("\n=== Testing /api/ ===")
resp = session.get("https://or.duvalclerk.com/api/", timeout=30)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"Content length: {len(resp.text)}")
    print(f"First 500 chars: {resp.text[:500]}")

# The form structure is clear now:
# - DocTypes (textarea, hidden): stores selected doc types
# - DocTypesDisplay (text): display field
# - DateRangeList (text): date range 
# - RecordDateFrom (text): start date
# - RecordDateTo (text): end date
# - DocTypeGroupDropDown (select): group selection
# - DocTypeInfoCheckBox (checkboxes): individual doc types with values
# - btnSearch (submit): search button

# The key insight: the checkboxes have values like 67, 69, 68, 70, etc.
# And the titles show the doc type names
# I need to find which checkbox values correspond to distress signals

# Let me find the specific checkbox values for distress doc types
print("\n=== Finding Distress Doc Type Checkboxes ===")
resp = session.get("https://or.duvalclerk.com/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')
form = soup.find('form', action=lambda x: x and 'SearchTypeDocType' in x)

checkboxes = form.find_all('input', {'name': 'DocTypeInfoCheckBox'})
distress_types = {
    'LIS PENDENS': None,
    'LIEN': None,
    'JUDGMENT': None,
    'FORECLOSURE': None,
    'MORTGAGE': None,
    'NOTICE': None,
    'DEED': None,
    'SATISFACTION': None,
    'RELEASE': None,
    'ASSIGNMENT': None,
}

for cb in checkboxes:
    title = cb.get('title', '')
    value = cb.get('value', '')
    for distress in distress_types:
        if distress.lower() in title.lower():
            distress_types[distress] = value
            print(f"  {distress}: checkbox value = {value} (title: {title})")

print(f"\nDistress types found: {sum(1 for v in distress_types.values() if v is not None)}/{len(distress_types)}")
for k, v in distress_types.items():
    if v is None:
        print(f"  ❌ {k}: NOT FOUND")

# Now try a proper search with the correct form data
print("\n=== Trying Proper Search ===")

# Get all form data first
form_data = {}
for inp in form.find_all(['input', 'select', 'textarea']):
    name = inp.get('name')
    if name:
        if inp.name == 'select':
            selected = inp.find('option', selected=True)
            form_data[name] = selected.get('value', '') if selected else ''
        elif inp.get('type') == 'checkbox':
            # Don't include unchecked checkboxes
            pass
        elif inp.get('type') not in ['button', 'submit', 'reset']:
            form_data[name] = inp.get('value', '')

# Set search parameters
form_data['RecordDateFrom'] = '6/1/2026'
form_data['RecordDateTo'] = '6/8/2026'

# Add distress checkbox values
# We need to send DocTypeInfoCheckBox as a list for multiple values
# But requests handles this automatically if we use a list

# Actually, let me try a simpler approach - just search for ALL records in date range
# without any doc type filter
search_data = {
    'DocTypes': '',
    'DocTypesDisplay': '',
    'DateRangeList': '',
    'RecordDateFrom': '6/1/2026',
    'RecordDateTo': '6/8/2026',
    'DocTypeGroupDropDown': 'all',
    'DocTypeInfoCheckBox': [],  # Empty = all types
    'btnSearch': 'Search'
}

# Add hidden fields
for inp in form.find_all('input', type='hidden'):
    name = inp.get('name')
    if name and name not in search_data:
        search_data[name] = inp.get('value', '')

print(f"Search data: {search_data}")

resp = session.post("https://or.duvalclerk.com/search/SearchTypeDocType", 
                   data=search_data, timeout=60)
print(f"\nSearch response: {resp.status_code}")
print(f"URL: {resp.url}")

if resp.status_code == 200:
    if 'ShowError' in resp.text:
        # Extract error
        error_match = re.search(r"ShowError\(\s*'([^']+)", resp.text)
        if error_match:
            print(f"Error: {error_match.group(1)}")
        else:
            print("Error in response (ShowError called)")
    else:
        soup_result = BeautifulSoup(resp.text, 'html.parser')
        tables = soup_result.find_all('table')
        print(f"Tables: {len(tables)}")
        
        # Look for result count
        result_text = soup_result.find(string=re.compile(r'\d+\s+record', re.I))
        if result_text:
            print(f"Results: {result_text.strip()}")
        
        # Check for any data
        rows = soup_result.find_all('tr')
        print(f"Rows: {len(rows)}")
        
        if len(rows) > 1:
            print("\n✅ Results found!")
            # Show first few rows
            for row in rows[:5]:
                cells = row.find_all(['td', 'th'])
                if cells:
                    print(f"  Row: {[c.get_text(strip=True)[:30] for c in cells]}")
