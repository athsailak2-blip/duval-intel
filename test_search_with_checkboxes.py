import requests
from bs4 import BeautifulSoup
import re

# The error is "The doctype is invalid" - I need to include the actual doc type checkboxes
# The form requires DocTypeInfoCheckBox to be populated with valid values

# Key checkbox values for distress signals:
# - LIS PENDENS (LP): 104
# - LIEN (LN): 103
# - JUDGMENT (JDG): 97
# - MORTGAGE (MTG): 110
# - NOTICE (NOTICE): 120
# - DEED (DEED): 87
# - ASSIGNMENT (ASSIGN): 75
# - SATISFACTION (SAT): 129
# - RELEASE (RELEASE): 126

# Let me try with specific checkbox values

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Accept disclaimer
resp = session.get("https://or.duvalclerk.com/search/Disclaimer", timeout=30)
if resp.status_code == 200:
    session.post("https://or.duvalclerk.com/search/Disclaimer", 
                data={'disclaimer': 'true'}, timeout=30)

# Get the search form to extract all hidden fields
resp = session.get("https://or.duvalclerk.com/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')
form = soup.find('form', action=lambda x: x and 'SearchTypeDocType' in x)

# Build complete form data with all hidden fields and proper checkbox values
search_data = {}

# Add all hidden fields
for inp in form.find_all('input', type='hidden'):
    name = inp.get('name')
    if name:
        search_data[name] = inp.get('value', '')

# Add text inputs (except buttons)
for inp in form.find_all('input'):
    name = inp.get('name')
    input_type = inp.get('type', 'text')
    if name and input_type not in ['button', 'submit', 'reset', 'checkbox', 'radio']:
        search_data[name] = inp.get('value', '')

# Set search parameters
search_data['RecordDateFrom'] = '6/1/2026'
search_data['RecordDateTo'] = '6/8/2026'
search_data['DocTypeGroupDropDown'] = 'all'

# Add specific doc type checkboxes for distress signals
# The checkbox name is 'DocTypeInfoCheckBox' and values are the IDs
# For multiple checkboxes, we need to send multiple values with the same name
# requests handles this if we use a list

# Let's try with just a few key distress types
distress_checkbox_values = ['104', '103', '97', '110', '120', '87', '75', '129', '126']

# Build the data properly for requests
# When sending multiple values with same key, requests will encode them correctly
final_data = {}
for k, v in search_data.items():
    final_data[k] = v

# Add checkbox values as a list - this creates DocTypeInfoCheckBox=104&DocTypeInfoCheckBox=103 etc.
final_data['DocTypeInfoCheckBox'] = distress_checkbox_values

# Add the submit button
final_data['btnSearch'] = 'Search'

print("Search data keys:", list(final_data.keys()))
print(f"DocTypeInfoCheckBox values: {final_data['DocTypeInfoCheckBox']}")

resp = session.post("https://or.duvalclerk.com/search/SearchTypeDocType", 
                   data=final_data, timeout=60)
print(f"\nSearch response: {resp.status_code}")
print(f"URL: {resp.url}")

if resp.status_code == 200:
    if 'ShowError' in resp.text:
        error_match = re.search(r"ShowError\(\s*'([^']+)", resp.text)
        if error_match:
            print(f"❌ Error: {error_match.group(1)}")
        else:
            print("❌ Error in response (ShowError called)")
    else:
        soup_result = BeautifulSoup(resp.text, 'html.parser')
        tables = soup_result.find_all('table')
        print(f"✅ Tables found: {len(tables)}")
        
        # Look for result count
        result_text = soup_result.find(string=re.compile(r'\d+\s+record', re.I))
        if result_text:
            print(f"✅ Results: {result_text.strip()}")
        
        # Check for any data rows
        rows = soup_result.find_all('tr')
        print(f"Rows: {len(rows)}")
        
        if len(rows) > 1:
            print("\n✅ Results found!")
            # Show first few rows
            for row in rows[:3]:
                cells = row.find_all(['td', 'th'])
                if cells:
                    texts = [c.get_text(strip=True)[:40] for c in cells]
                    print(f"  {texts}")
        else:
            print("\n⚠️ No results or empty table")
            
        # Check for pagination or result info
        page_info = soup_result.find(text=re.compile(r'page|Page \d+', re.I))
        if page_info:
            print(f"Pagination: {page_info.strip()[:100]}")
            
        # Save response for analysis
        if len(tables) == 0:
            print(f"\nResponse (first 2000 chars):")
            print(resp.text[:2000])
