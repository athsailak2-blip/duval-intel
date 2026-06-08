#!/usr/bin/env python3
"""Test if the RealForeclose portals require login for data access."""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

print("=" * 60)
print("Checking Login Requirements for RealForeclose")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Check foreclosure sales
        print("\n1. Foreclosure Sales (duval.realforeclose.com)...")
        page.goto("https://www.duval.realforeclose.com/", wait_until="networkidle")
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for login form
        login_form = soup.find('form', action=re.compile(r'login|auth', re.I))
        if login_form:
            print("   Login form found!")
        
        # Look for register link
        register_links = soup.find_all('a', href=re.compile(r'register|signup|create', re.I))
        if register_links:
            print(f"   Register links: {len(register_links)}")
            for link in register_links[:3]:
                print(f"     {link.get_text(strip=True)[:50]}: {link.get('href', 'N/A')}")
        
        # Look for guest/public access
        guest_links = soup.find_all('a', text=re.compile(r'guest|public|view|search', re.I))
        if guest_links:
            print(f"   Guest/public links: {len(guest_links)}")
        
        # Check page text for access info
        body_text = soup.get_text()
        if 'login' in body_text.lower() or 'register' in body_text.lower() or 'account' in body_text.lower():
            print("   Page mentions login/register/account")
        
        if 'guest' in body_text.lower() or 'public' in body_text.lower() or 'free' in body_text.lower():
            print("   Page mentions guest/public/free access")
        
        page.screenshot(path='/workspace/foreclosure_login_check.png')
        
        # Check tax deed
        print("\n2. Tax Deed Sales (duval.realtaxdeed.com)...")
        page.goto("https://www.duval.realtaxdeed.com/", wait_until="networkidle")
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        login_form = soup.find('form', action=re.compile(r'login|auth', re.I))
        if login_form:
            print("   Login form found!")
        
        register_links = soup.find_all('a', href=re.compile(r'register|signup|create', re.I))
        if register_links:
            print(f"   Register links: {len(register_links)}")
        
        body_text = soup.get_text()
        if 'login' in body_text.lower() or 'register' in body_text.lower():
            print("   Page mentions login/register")
        
        page.screenshot(path='/workspace/taxdeed_login_check.png')
        
        # Try to find any public sale list without logging in
        print("\n3. Looking for public sale list URLs...")
        
        # Common patterns for public access
        public_urls = [
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=nextauction",
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=calendar",
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=list",
            "https://www.duval.realtaxdeed.com/index.cfm?zaction=auction&zmethod=nextauction",
            "https://www.duval.realtaxdeed.com/index.cfm?zaction=auction&zmethod=calendar",
        ]
        
        for url in public_urls:
            try:
                page.goto(url, wait_until="networkidle", timeout=10000)
                title = page.title()
                print(f"   {url.split('/')[-1]}: {title[:60]}")
                
                # Check if we got actual data or a login page
                content = page.content()
                if 'login' in content.lower() and 'password' in content.lower():
                    print(f"      -> LOGIN REQUIRED")
                elif 'sale' in content.lower() or 'property' in content.lower() or 'auction' in content.lower():
                    print(f"      -> Has content")
                    
                    # Look for actual data
                    soup = BeautifulSoup(content, 'html.parser')
                    tables = soup.find_all('table')
                    if len(tables) > 1:
                        print(f"      -> Multiple tables found ({len(tables)})")
                    
                    # Check for data rows
                    rows = soup.find_all('tr')
                    data_rows = [r for r in rows if len(r.find_all('td')) > 2]
                    if data_rows:
                        print(f"      -> Data rows found: {len(data_rows)}")
                        
            except Exception as e:
                print(f"   {url.split('/')[-1]}: Error - {str(e)[:50]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
    
    finally:
        browser.close()

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("""
Key Findings:
1. Official Records (or.duvalclerk.com): 
   - Requires Playwright (Kendo UI JavaScript)
   - Successfully extracted 289 LIS PENDENS records for 30 days
   - DocType ID for LIS PENDENS: 104

2. Court Records (core.duvalclerk.com):
   - LOGIN REQUIRED - requires authentication
   - Cannot scrape without credentials

3. Foreclosure Sales (duval.realforeclose.com):
   - May require login/registration for full access
   - Public calendar may be available

4. Tax Deed Sales (duval.realtaxdeed.com):
   - Similar to foreclosure - may require login
   - Public calendar may be available

5. Property Appraiser (paopropertysearch.coj.net):
   - Requires individual parcel searches
   - No bulk data available via web scraping

6. Tax Collector (tclieninfo.coj.net):
   - Requires individual parcel searches
   - No bulk delinquent list available

7. GIS (maps.coj.net/duvalproperty):
   - ArcGIS/ESRI detected
   - REST API may require authentication

8. Code Enforcement:
   - Requires Public Records Request (PRR)
   - Manual process
""")

print("\nDone!")
