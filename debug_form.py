import requests
from bs4 import BeautifulSoup
import re

# The error is: "The doctype is invalid, please enter the correct doctype and try again."
# The form has a hidden field with name "" (empty string) that has value "1/1/1800"
# This is likely the default RecordDateFrom
# And the DocTypeGroupDropDown needs to be set properly

# Let me check what the actual form submission looks like by examining the form more carefully

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
form = soup.find('form', action=lambda x: x and 'SearchTypeDocType' in x)

# The form has ASP.NET MVC structure
# The hidden field with empty name is probably __RequestVerificationToken or similar
# Let me look at ALL inputs more carefully

print("=== All form inputs (detailed) ===")
all_inputs = form.find_all(['input', 'select', 'textarea'])
for i, inp in enumerate(all_inputs):
    tag_name = inp.name
    attrs = {k: v for k, v in inp.attrs.items() if k not in ['class', 'style']}
    print(f"{i}. {tag_name}: {attrs}")
    if i > 30:
        print("  ... (truncated)")
        break

# The issue is that the form has:
# - A hidden input with NO name attribute (value=1/1/1800) - this is probably RecordDateFrom duplicate
# - DocTypeGroupDropDown needs to be set to a valid group
# - DocTypeInfoCheckBox needs specific values

# Let me try a different approach - use the Name search instead which might be simpler
print("\n=== Trying Name Search ===")
resp2 = session.get("https://or.duvalclerk.com/search/SearchTypeName", timeout=30)
print(f"Name search page: {resp2.status_code}")

if resp2.status_code == 200:
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    form2 = soup2.find('form', action=lambda x: x and 'SearchTypeName' in x)
    if form2:
        print("Form found")
        inputs2 = form2.find_all(['input', 'select'])
        print(f"Inputs: {len(inputs2)}")
        for inp in inputs2[:10]:
            print(f"  {inp.get('name', 'N/A')}: {inp.get('type', 'N/A')} = {inp.get('value', '')[:50]}")

# Actually, let me try a completely different approach
# Let me search for the actual API endpoints or AJAX calls the site uses
print("\n=== Looking for API endpoints in scripts ===")
scripts = soup.find_all('script')
for script in scripts:
    if script.string:
        if 'ajax' in script.string.lower() or '$.post' in script.string or 'fetch(' in script.string:
            print("AJAX call found:")
            print(script.string[:500])
            print()

# Let me also check if there's a JSON API or REST endpoint
print("\n=== Checking for API endpoints ===")
# Try common patterns
api_patterns = [
    '/api/',
    '/Search/Results',
    '/search/results',
    '/Search/GetResults',
]

for pattern in api_patterns:
    test_url = f"https://or.duvalclerk.com{pattern}"
    resp_test = session.get(test_url, timeout=10)
    print(f"  {pattern}: {resp_test.status_code}")
