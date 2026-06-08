import requests
from bs4 import BeautifulSoup
import re

# Official Records portal has a disclaimer page first, then search options
# The search links are: /search/SearchTypeName, /search/SearchTypeDocType, etc.
# Need to accept disclaimer first, then use the search forms

print("=== Testing Official Records Search ===")

# Step 1: Accept disclaimer
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Get the disclaimer page
resp = session.get("https://or.duvalclerk.com/search/Disclaimer", timeout=30)
print(f"Disclaimer page: {resp.status_code}")

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    form = soup.find('form', action='/search/Disclaimer')
    if form:
        # Submit disclaimer acceptance
        disclaimer_data = {}
        for inp in form.find_all('input'):
            name = inp.get('name')
            if name:
                disclaimer_data[name] = inp.get('value', '')
        
        print(f"Disclaimer form data: {disclaimer_data}")
        
        # Post to accept disclaimer
        resp2 = session.post("https://or.duvalclerk.com/search/Disclaimer", 
                            data=disclaimer_data, timeout=30)
        print(f"Disclaimer acceptance: {resp2.status_code}")
        
        # Now try the Doc Type search
        print("\n--- Trying Doc Type Search ---")
        resp3 = session.get("https://or.duvalclerk.com/search/SearchTypeDocType", timeout=30)
        print(f"Doc Type search page: {resp3.status_code}")
        
        if resp3.status_code == 200:
            soup3 = BeautifulSoup(resp3.text, 'html.parser')
            form3 = soup3.find('form')
            if form3:
                print(f"Form action: {form3.get('action', 'N/A')}")
                inputs = form3.find_all('input')
                print(f"Inputs: {len(inputs)}")
                for inp in inputs:
                    print(f"  - {inp.get('name', 'N/A')} ({inp.get('type', 'text')}) = {inp.get('value', '')[:50]}")
                
                # Also check selects
                selects = form3.find_all('select')
                print(f"\nSelects: {len(selects)}")
                for sel in selects:
                    print(f"  - {sel.get('name', 'N/A')}")
                    options = sel.find_all('option')
                    print(f"    Options: {len(options)}")
                    for opt in options[:10]:
                        print(f"      {opt.get('value', 'N/A')}: {opt.get_text(strip=True)[:50]}")

print("\n=== Testing Court Records (CORE) ===")
resp = requests.get("https://core.duvalclerk.com/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    # Look for case search links
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Check for any links
    all_links = soup.find_all('a', href=True)
    print(f"Total links: {len(all_links)}")
    
    # Look for specific patterns
    for link in all_links[:20]:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if any(k in href.lower() for k in ['search', 'case', 'docket', 'public']):
            print(f"  - {href}: {text[:50]}")
    
    # Check if it's a redirect or login page
    if 'login' in resp.text.lower() or 'sign in' in resp.text.lower():
        print("\n⚠️ Portal requires login")
    
    # Check for public access
    if 'public' in resp.text.lower():
        print("\n✅ Public access mentioned")

print("\n=== Testing Foreclosure Sales (RealAuction) ===")
resp = requests.get("https://www.duval.realforeclose.com/", timeout=30, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    # RealAuction typically uses JavaScript to load auction data
    # The page might be a shell that loads data via JS
    
    # Check for script tags that might load data
    soup = BeautifulSoup(resp.text, 'html.parser')
    scripts = soup.find_all('script')
    print(f"Scripts: {len(scripts)}")
    
    # Look for any data URLs or API endpoints in scripts
    for script in scripts:
        if script.string:
            if 'auction' in script.string.lower() or 'calendar' in script.string.lower():
                print(f"\nScript with auction/calendar reference found:")
                print(script.string[:500])
                
    # Look for iframe or embedded content
    iframes = soup.find_all('iframe')
    print(f"\nIframes: {len(iframes)}")
    for iframe in iframes:
        print(f"  - src: {iframe.get('src', 'N/A')}")
        
    # Check for meta refresh or redirects
    meta_refresh = soup.find('meta', http_equiv='refresh')
    if meta_refresh:
        print(f"\nMeta refresh: {meta_refresh.get('content', 'N/A')}")
