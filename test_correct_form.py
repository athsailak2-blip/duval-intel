#!/usr/bin/env python3
"""Test the correct form submission for Official Records."""
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
print("Testing Correct Form Submission")
print("=" * 60)

# Step 1: Accept disclaimer
print("\n1. Accepting disclaimer...")
response = session.post(
    BASE_URL + "/search/Disclaimer",
    data={"Disclaimer": "true"},
    timeout=30,
    allow_redirects=True
)
print(f"   Status: {response.status_code}, URL: {response.url}")

# Step 2: Get the search form
print("\n2. Getting search form...")
response = session.get(BASE_URL + "/search/SearchTypeDocType", timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the form
form = soup.find('form')
if form:
    print(f"   Form action: {form.get('action')}")
    
    # Extract ALL inputs
    all_inputs = {}
    for inp in form.find_all('input'):
        name = inp.get('name')
        if name:
            all_inputs[name] = inp.get('value', '')
    
    print(f"\n   All form inputs ({len(all_inputs)}):")
    for k, v in list(all_inputs.items())[:20]:
        print(f"     {k}: {v[:50] if len(str(v)) > 50 else v}")
    
    # Look at ALL checkboxes for doc types
    checkboxes = form.find_all('input', {'name': 'DocTypeInfoCheckBox'})
    print(f"\n   DocType checkboxes: {len(checkboxes)}")
    for cb in checkboxes[:10]:
        print(f"     Value: {cb.get('value')}")
        # Try to find associated label
        parent = cb.find_parent()
        if parent:
            label_text = parent.get_text(strip=True)
            print(f"       Label: {label_text[:80]}")
    
    # Look for the select dropdown
    select = form.find('select', {'name': 'DocTypeGroupDropDown'})
    if select:
        print(f"\n   DocTypeGroupDropDown options:")
        for opt in select.find_all('option'):
            print(f"     {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:80]}")
    
    # Step 3: Try submitting with correct fields
    print("\n3. Submitting search with correct fields...")
    
    # Build the correct payload based on form analysis
    # The form uses checkboxes for individual doc types
    # Let's find the checkbox for LIS PENDENS
    
    # First, let's look at what checkboxes are available
    all_checkboxes = form.find_all('input', type='checkbox')
    print(f"\n   All checkboxes ({len(all_checkboxes)}):")
    for cb in all_checkboxes[:15]:
        name = cb.get('name', 'N/A')
        value = cb.get('value', 'N/A')
        # Find label
        id_ = cb.get('id', '')
        label = soup.find('label', {'for': id_})
        label_text = label.get_text(strip=True) if label else 'N/A'
        print(f"     {name}={value}: {label_text[:60]}")
    
    # Try to submit with the checkbox values we found
    # Based on the output, DocTypeInfoCheckBox values are 67, 69, 68, 70, 71, 72, 75
    # We need to find which one is LIS PENDENS
    
    # Let's try submitting with just the date range and see what happens
    payload = {
        'DocTypesDisplay': '',
        'DateRangeList': ' ',
        'RecordDateFrom': '5/1/2026',
        'RecordDateTo': '6/8/2026',
        'DocTypeInfoCheckBox': '103',  # LIS PENDENS based on the dropdown showing LP=103
    }
    
    # Add all hidden fields
    for inp in form.find_all('input', type='hidden'):
        name = inp.get('name')
        if name and name not in payload:
            payload[name] = inp.get('value', '')
    
    print(f"\n   Payload keys: {list(payload.keys())}")
    
    action = form.get('action', '')
    if action.startswith('/'):
        action = BASE_URL + action
    
    response = session.post(action, data=payload, timeout=60)
    print(f"   Response status: {response.status_code}")
    print(f"   Response URL: {response.url}")
    print(f"   Content length: {len(response.text)}")
    
    # Parse response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for results table
    tables = soup.find_all('table')
    print(f"\n   Tables found: {len(tables)}")
    
    # Look for any result indicators
    body_text = soup.get_text()
    if 'result' in body_text.lower() or 'record' in body_text.lower() or 'found' in body_text.lower():
        print(f"\n   Page text (first 500 chars):")
        print(f"   {body_text[:500]}")
    
    # Check for error messages
    error_divs = soup.find_all(['div', 'span'], class_=re.compile(r'error|alert|validation', re.I))
    if error_divs:
        print(f"\n   Error elements:")
        for div in error_divs[:3]:
            print(f"     {div.get_text(strip=True)[:100]}")
    
    # Look for kendo grid or data
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'data' in script.string.lower():
            text = script.string[:200]
            if 'result' in text.lower() or 'record' in text.lower() or 'grid' in text.lower():
                print(f"\n   Script hint: {text[:150]}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
