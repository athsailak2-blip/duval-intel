#!/usr/bin/env python3
"""Test accepting disclaimer and then accessing search."""
import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://or.duvalclerk.com/'
})

BASE_URL = "https://or.duvalclerk.com"

print("=" * 60)
print("Testing Disclaimer Acceptance Flow")
print("=" * 60)

# Step 1: Accept disclaimer
print("\n1. Accepting disclaimer...")
try:
    response = session.post(
        BASE_URL + "/search/Disclaimer",
        data={"Disclaimer": "true"},
        timeout=30,
        allow_redirects=True
    )
    print(f"   Status: {response.status_code}")
    print(f"   URL after post: {response.url}")
    if response.history:
        print(f"   Redirect chain: {[r.url for r in response.history]}")
    
    # Check cookies
    print(f"\n   Cookies after disclaimer:")
    for cookie in session.cookies:
        print(f"     {cookie.name}: {cookie.value[:50] if len(cookie.value) > 50 else cookie.value}")
    
except Exception as e:
    print(f"   ERROR: {e}")

# Step 2: Try to access search page
print("\n2. Accessing Doc Type search page...")
try:
    response = session.get(BASE_URL + "/search/SearchTypeDocType", timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    print(f"   Content length: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for search form
    forms = soup.find_all('form')
    print(f"\n   Forms found: {len(forms)}")
    
    for i, form in enumerate(forms):
        print(f"\n   Form {i+1}:")
        print(f"     Action: {form.get('action', 'N/A')}")
        print(f"     Method: {form.get('method', 'N/A')}")
        
        inputs = form.find_all('input')
        print(f"     Inputs: {len(inputs)}")
        for inp in inputs[:15]:
            name = inp.get('name', 'N/A')
            type_ = inp.get('type', 'N/A')
            value = inp.get('value', '')
            print(f"       - {name} (type={type_}, value={value[:50]})")
        
        selects = form.find_all('select')
        print(f"     Selects: {len(selects)}")
        for sel in selects:
            name = sel.get('name', 'N/A')
            print(f"       - {name}")
            options = sel.find_all('option')
            for opt in options[:10]:
                print(f"         {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:50]}")
    
    # Check if we're back at disclaimer
    if 'disclaimer' in response.text.lower():
        print("\n   WARNING: Still seeing disclaimer page!")
    
    # Look for any error messages
    error_elements = soup.find_all(text=re.compile(r'error|invalid|unauthorized|login', re.I))
    if error_elements:
        print(f"\n   Potential issues found:")
        for el in error_elements[:5]:
            print(f"     {el.strip()[:100]}")
    
except Exception as e:
    print(f"   ERROR: {e}")

# Step 3: Try to submit a search
print("\n3. Submitting a test search...")
try:
    # First, get the search form to extract any tokens
    response = session.get(BASE_URL + "/search/SearchTypeDocType", timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the search form
    search_form = None
    for form in soup.find_all('form'):
        if 'search' in form.get('action', '').lower() or 'doc' in form.get('action', '').lower():
            search_form = form
            break
    
    if search_form:
        action = search_form.get('action', '')
        if action.startswith('/'):
            action = BASE_URL + action
        elif not action.startswith('http'):
            action = BASE_URL + '/search/' + action
        
        print(f"   Form action: {action}")
        
        # Build payload from form inputs
        payload = {}
        for inp in search_form.find_all('input'):
            name = inp.get('name')
            if name:
                payload[name] = inp.get('value', '')
        
        # Add search parameters
        # Look for doc type field
        doc_type_select = search_form.find('select', {'name': re.compile(r'doc|type', re.I)})
        if doc_type_select:
            print(f"   Doc type field: {doc_type_select.get('name')}")
            options = doc_type_select.find_all('option')
            for opt in options[:5]:
                print(f"     {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:50]}")
        
        # Look for date fields
        date_inputs = search_form.find_all('input', {'name': re.compile(r'date|start|end|from|to', re.I)})
        print(f"   Date fields: {len(date_inputs)}")
        for inp in date_inputs:
            print(f"     {inp.get('name')}: {inp.get('value', 'N/A')}")
        
        print(f"\n   Form payload keys: {list(payload.keys())}")
        
        # Try submitting with minimal data
        test_payload = {
            'DocType': 'LIS PENDENS',
            'StartDate': '05/01/2026',
            'EndDate': '06/08/2026'
        }
        
        # Merge with form defaults
        for key in payload:
            if key not in test_payload:
                test_payload[key] = payload[key]
        
        print(f"   Submitting with: {test_payload}")
        
        response = session.post(action, data=test_payload, timeout=60)
        print(f"   Response status: {response.status_code}")
        print(f"   Response URL: {response.url}")
        print(f"   Content length: {len(response.text)}")
        
        # Check for results
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        print(f"\n   Tables in response: {len(tables)}")
        
        # Look for result count
        result_text = soup.find_all(text=re.compile(r'\d+\s+result|found|record', re.I))
        if result_text:
            print(f"   Result indicators:")
            for text in result_text[:5]:
                print(f"     {text.strip()[:100]}")
        
        # Check for error
        error_divs = soup.find_all('div', class_=re.compile(r'error|alert|message', re.I))
        if error_divs:
            print(f"\n   Error/alert elements:")
            for div in error_divs[:3]:
                print(f"     {div.get_text(strip=True)[:100]}")
    else:
        print("   No search form found!")
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
