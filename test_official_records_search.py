import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta

# Now I understand the actual portal structure:
# 1. Official Records: Has disclaimer, then DocType search with checkbox IDs
# 2. Court Records: Requires login (not publicly accessible)
# 3. Foreclosure Sales: RealAuction - needs JS/browser

# Let me test the Official Records search with the actual form structure

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Step 1: Accept disclaimer
print("=== Step 1: Accept Disclaimer ===")
resp = session.get("https://or.duvalclerk.com/search/Disclaimer", timeout=30)
print(f"Disclaimer page: {resp.status_code}")

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    form = soup.find('form', action='/search/Disclaimer')
    if form:
        disclaimer_data = {'disclaimer': 'true'}
        resp2 = session.post("https://or.duvalclerk.com/search/Disclaimer", 
                            data=disclaimer_data, timeout=30)
        print(f"Disclaimer accepted: {resp2.status_code}")

# Step 2: Get Doc Type search page and find the actual form
print("\n=== Step 2: Get Doc Type Search Form ===")
resp3 = session.get("https://or.duvalclerk.com/search/SearchTypeDocType", timeout=30)
print(f"Doc Type page: {resp3.status_code}")

if resp3.status_code == 200:
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    form3 = soup3.find('form', action=lambda x: x and 'SearchTypeDocType' in x)
    
    if form3:
        # Get all form inputs
        all_inputs = {}
        for inp in form3.find_all(['input', 'select', 'textarea']):
            name = inp.get('name')
            if name:
                if inp.name == 'select':
                    # Get selected option
                    selected = inp.find('option', selected=True)
                    all_inputs[name] = selected.get('value', '') if selected else ''
                elif inp.get('type') == 'checkbox':
                    all_inputs[name] = inp.get('value', 'on')
                elif inp.get('type') == 'radio':
                    if inp.get('checked'):
                        all_inputs[name] = inp.get('value', '')
                else:
                    all_inputs[name] = inp.get('value', '')
        
        print(f"Form inputs found: {len(all_inputs)}")
        
        # Key fields for search
        # RecordDateFrom: default is 1/1/1800
        # RecordDateTo: default is today
        # DocTypeInfoCheckBox: multiple checkboxes with IDs
        # We need to find which checkbox IDs correspond to distress doc types
        
        # Look at the select dropdown for doc type groups
        doc_type_select = soup3.find('select', {'name': 'DocTypeGroupDropDown'})
        if doc_type_select:
            print("\nDoc Type Groups:")
            for opt in doc_type_select.find_all('option'):
                print(f"  {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:80]}")
        
        # Find the checkbox values that correspond to distress types
        # From the options, we can see:
        # LIEN/JUDGMENT group: 94,97,98,99,103 (LIS PENDENS, JUDGMENT, LIEN)
        # Mortgage group: 75,110,129,155 (ASSIGNMENT, MORTGAGE, SATISFACTION, MTGND)
        # NOTICE group: 115,120,149 (N/C, NOTICE, NTD)
        
        # Let's search for LIS PENDENS (LP) - checkbox value 97
        # And LIEN (LN) - checkbox value 103
        # And JUDGMENT (JDG) - checkbox value 98
        # And FORECLOSURE - need to find the right checkbox
        
        # First, let's look at all checkboxes and their labels
        checkboxes = soup3.find_all('input', {'name': 'DocTypeInfoCheckBox'})
        print(f"\nTotal checkboxes: {len(checkboxes)}")
        
        # Find labels for checkboxes
        for cb in checkboxes[:10]:
            cb_id = cb.get('id', '')
            cb_val = cb.get('value', '')
            # Find associated label
            label = soup3.find('label', {'for': cb_id})
            if label:
                print(f"  Checkbox {cb_val}: {label.get_text(strip=True)[:50]}")
            else:
                # Try finding nearby text
                parent = cb.find_parent()
                if parent:
                    text = parent.get_text(strip=True)
                    print(f"  Checkbox {cb_val}: {text[:50]}")

# Step 3: Try a search with specific doc types
print("\n=== Step 3: Search for LIS PENDENS ===")

# Build search data
# We need to include the checkbox values for the doc types we want
search_data = {
    'DocTypesDisplay': '',
    'DateRangeList': '',
    'RecordDateFrom': '6/1/2026',  # Last 7 days
    'RecordDateTo': '6/8/2026',
    'DocTypeInfoCheckBox': ['97', '103', '98'],  # LIS PENDENS, LIEN, JUDGMENT
    'DocTypeGroupDropDown': 'all',
}

# Try the search
resp4 = session.post("https://or.duvalclerk.com/search/SearchTypeDocType", 
                    data=search_data, timeout=60)
print(f"Search response: {resp4.status_code}")
print(f"URL: {resp4.url}")

if resp4.status_code == 200:
    # Check if we got results or an error
    if 'No results found' in resp4.text or 'no records' in resp4.text.lower():
        print("No results found")
    elif 'error' in resp4.text.lower():
        print("Error in response")
        # Find error message
        soup4 = BeautifulSoup(resp4.text, 'html.parser')
        error_div = soup4.find('div', class_=re.compile(r'error|alert', re.I))
        if error_div:
            print(f"Error: {error_div.get_text(strip=True)[:200]}")
    else:
        # Look for result table
        soup4 = BeautifulSoup(resp4.text, 'html.parser')
        tables = soup4.find_all('table')
        print(f"Tables found: {len(tables)}")
        
        # Look for result count
        result_text = soup4.find(text=re.compile(r'\d+\s+result', re.I))
        if result_text:
            print(f"Results: {result_text.strip()}")
        
        # Check for any data rows
        rows = soup4.find_all('tr')
        print(f"Total rows: {len(rows)}")
        
        # Look for pagination
        pagination = soup4.find(text=re.compile(r'page|Page \d+', re.I))
        if pagination:
            print(f"Pagination: {pagination.strip()[:100]}")
            
        # Save a sample of the HTML for analysis
        print(f"\nResponse preview (first 1000 chars):")
        print(resp4.text[:1000])
