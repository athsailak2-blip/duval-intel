import requests
from bs4 import BeautifulSoup
import re

# The search returned an error. Let me check what the error is and fix the search parameters

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Accept disclaimer
resp = session.get("https://or.duvalclerk.com/search/Disclaimer", timeout=30)
if resp.status_code == 200:
    session.post("https://or.duvalclerk.com/search/Disclaimer", 
                data={'disclaimer': 'true'}, timeout=30)

# Get the search form
resp = session.get("https://or.duvalclerk.com/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

# Find the actual form
form = soup.find('form', action=lambda x: x and 'SearchTypeDocType' in x)

# Get all form data including hidden fields
form_data = {}
for inp in form.find_all(['input', 'select', 'textarea']):
    name = inp.get('name')
    if name:
        if inp.name == 'select':
            selected = inp.find('option', selected=True)
            form_data[name] = selected.get('value', '') if selected else ''
        elif inp.get('type') == 'checkbox':
            # Only include checked checkboxes
            if inp.get('checked') or name not in form_data:
                form_data[name] = inp.get('value', 'on')
        elif inp.get('type') == 'radio':
            if inp.get('checked'):
                form_data[name] = inp.get('value', '')
        elif inp.get('type') not in ['button', 'submit', 'reset']:
            form_data[name] = inp.get('value', '')

print("All form fields:")
for k, v in list(form_data.items())[:20]:
    print(f"  {k}: {v[:50] if isinstance(v, str) else v}")

# The issue is that we need to properly submit the form with all required fields
# Let me look at the actual form structure more carefully

# Check for hidden fields
hidden_fields = form.find_all('input', type='hidden')
print(f"\nHidden fields: {len(hidden_fields)}")
for hf in hidden_fields:
    print(f"  {hf.get('name', 'N/A')}: {hf.get('value', '')[:50]}")

# Check for __RequestVerificationToken
rvt = form.find('input', {'name': '__RequestVerificationToken'})
if rvt:
    print(f"\nRequestVerificationToken: {rvt.get('value', 'N/A')[:50]}")

# The form might need specific ASP.NET fields
# Let me check the form action URL
print(f"\nForm action: {form.get('action', 'N/A')}")

# Try a simpler search - just date range, no doc type filter
print("\n=== Trying simple date search ===")
search_data = {
    'RecordDateFrom': '6/1/2026',
    'RecordDateTo': '6/8/2026',
}

# Add all hidden fields
for hf in hidden_fields:
    name = hf.get('name')
    if name and name not in search_data:
        search_data[name] = hf.get('value', '')

# Add the submit button
submit_btn = form.find('input', type='submit')
if submit_btn:
    search_data[submit_btn.get('name', 'N/A')] = submit_btn.get('value', 'Search')

print(f"Search data keys: {list(search_data.keys())}")

resp2 = session.post("https://or.duvalclerk.com/search/SearchTypeDocType", 
                    data=search_data, timeout=60)
print(f"\nSearch response: {resp2.status_code}")
print(f"URL: {resp2.url}")

if resp2.status_code == 200:
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    
    # Check for error
    error_div = soup2.find('div', class_=re.compile(r'error|validation', re.I))
    if error_div:
        print(f"Error: {error_div.get_text(strip=True)[:200]}")
    
    # Check for results
    result_count = soup2.find(text=re.compile(r'\d+\s+record', re.I))
    if result_count:
        print(f"Results: {result_count.strip()}")
    
    # Look for table with results
    tables = soup2.find_all('table')
    print(f"Tables: {len(tables)}")
    
    # Check for any content that indicates results
    if 'No results' in resp2.text or 'no records' in resp2.text.lower():
        print("No results found")
    elif 'result' in resp2.text.lower():
        print("Results page loaded")
        
    # Save response for analysis
    print(f"\nResponse snippet (first 1500 chars):")
    print(resp2.text[:1500])
