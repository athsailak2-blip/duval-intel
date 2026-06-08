#!/usr/bin/env python3
"""Navigate foreclosure sales properly - find the sales list."""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

print("=" * 60)
print("Finding Foreclosure Sales List")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Navigate to home page
        print("\n1. Navigating to home...")
        page.goto("https://www.duval.realforeclose.com/index.cfm?zaction=home", wait_until="networkidle")
        print(f"   Title: {page.title()}")
        
        # Look for links to auction/sales
        print("\n2. Looking for auction links...")
        links = page.locator('a').all()
        for link in links:
            href = link.get_attribute('href') or ''
            text = link.inner_text().strip()
            if 'auction' in text.lower() or 'sale' in text.lower() or 'bid' in text.lower() or 'calendar' in text.lower():
                print(f"   '{text[:60]}' -> {href[:80]}")
        
        # Try direct navigation to auction
        print("\n3. Trying auction URLs...")
        
        auction_urls = [
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction",
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=calendar",
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=list",
            "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=nextauction",
        ]
        
        for url in auction_urls:
            try:
                page.goto(url, wait_until="networkidle", timeout=10000)
                print(f"   {url.split('/')[-1]}: {page.title()[:60]}")
                
                # Check if we got actual content
                content = page.content()
                if 'sale' in content.lower() or 'property' in content.lower() or 'auction' in content.lower():
                    print(f"      -> Has auction content!")
                    
                    # Look for property data
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for tables
                    tables = soup.find_all('table')
                    print(f"      Tables: {len(tables)}")
                    
                    # Look for any data rows
                    rows = soup.find_all('tr')
                    print(f"      Rows: {len(rows)}")
                    
                    # Look for property addresses
                    addresses = re.findall(r'\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Dr|Rd|Blvd|Ln|Ct|Way)', content)
                    if addresses:
                        print(f"      Addresses found: {len(addresses)}")
                        print(f"      Sample: {addresses[:3]}")
                    
                    page.screenshot(path=f'/workspace/auction_{url.split("=")[-1]}.png')
                    break
                    
            except Exception as e:
                print(f"   {url.split('/')[-1]}: Error - {str(e)[:50]}")
        
        # Try to find login/register requirement
        print("\n4. Checking if login is required...")
        content = page.content()
        if 'login' in content.lower() or 'register' in content.lower() or 'password' in content.lower() or 'username' in content.lower():
            print("   Login/registration may be required for full access")
        
        # Look for any sale date information
        print("\n5. Looking for sale dates...")
        dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', content)
        if dates:
            print(f"   Dates found: {set(dates[:10])}")
        
        # Look for sale counts
        counts = re.findall(r'(\d+)\s+(?:property|properties|sale|sales|item|items)', content, re.I)
        if counts:
            print(f"   Counts found: {counts[:5]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\n" + "=" * 60)
print("Finding Tax Deed Sales List")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        print("\n1. Navigating to tax deed...")
        page.goto("https://www.duval.realtaxdeed.com/index.cfm?zaction=auction", wait_until="networkidle")
        print(f"   Title: {page.title()}")
        
        # Try calendar
        print("\n2. Trying calendar...")
        page.goto("https://www.duval.realtaxdeed.com/index.cfm?zaction=auction&zmethod=calendar", wait_until="networkidle")
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for calendar entries
        dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', soup.get_text())
        if dates:
            print(f"   Dates: {set(dates[:10])}")
        
        # Look for sale counts
        counts = re.findall(r'(\d+)\s+(?:property|properties|sale|sales)', soup.get_text(), re.I)
        if counts:
            print(f"   Counts: {counts[:5]}")
        
        page.screenshot(path='/workspace/taxdeed_auction.png')
        print("   Screenshot saved")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
    
    finally:
        browser.close()

print("\nDone!")
