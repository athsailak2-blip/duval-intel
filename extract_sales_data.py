#!/usr/bin/env python3
"""Test foreclosure sales portal with Playwright to extract actual data."""
from playwright.sync_api import sync_playwright
import json

print("=" * 60)
print("Extracting Foreclosure Sales Data")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Navigate to foreclosure sales
        print("\n1. Navigating to foreclosure sales...")
        page.goto("https://www.duval.realforeclose.com/", wait_until="networkidle")
        print(f"   Title: {page.title()}")
        
        # Look for links to sale lists or calendar
        print("\n2. Looking for sale links...")
        links = page.locator('a').all()
        for link in links[:10]:
            href = link.get_attribute('href') or ''
            text = link.inner_text()
            if href and ('sale' in href.lower() or 'auction' in href.lower() or 'calendar' in href.lower() or 'list' in href.lower()):
                print(f"   Link: {text[:50]} -> {href}")
        
        # Try to find and click on a sale date or "View Sales" link
        print("\n3. Looking for sale list or calendar...")
        
        # Common patterns on RealForeclose sites
        sale_link = page.locator('a:has-text("Sales")').first
        if sale_link.count() == 0:
            sale_link = page.locator('a:has-text("Auction")').first
        if sale_link.count() == 0:
            sale_link = page.locator('a:has-text("Calendar")').first
        if sale_link.count() == 0:
            sale_link = page.locator('a:has-text("View")').first
        
        if sale_link.count() > 0:
            print(f"   Clicking: {sale_link.inner_text()[:50]}")
            sale_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            
            print(f"   New URL: {page.url}")
            print(f"   New title: {page.title()}")
            
            page.screenshot(path='/workspace/foreclosure_sales_list.png')
            print("   Screenshot saved")
            
            # Look for property listings
            content = page.content()
            
            # Check for tables with property data
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            tables = soup.find_all('table')
            print(f"\n   Tables found: {len(tables)}")
            
            # Look for property rows
            rows = soup.find_all('tr')
            print(f"   Total rows: {len(rows)}")
            
            # Look for any data
            data_divs = soup.find_all('div', class_=re.compile(r'property|sale|item|result', re.I))
            print(f"   Data divs: {len(data_divs)}")
            
            # Extract any visible data
            body_text = soup.get_text()
            if 'sale' in body_text.lower() or 'property' in body_text.lower() or 'auction' in body_text.lower():
                print(f"\n   Page text preview (first 500 chars):")
                print(f"   {body_text[:500]}")
        else:
            print("   No sale link found")
            
            # Try direct URL patterns
            print("\n4. Trying direct URL patterns...")
            
            urls_to_try = [
                "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=calendar",
                "https://www.duval.realforeclose.com/index.cfm?zaction=auction&zmethod=list",
                "https://www.duval.realforeclose.com/sales",
                "https://www.duval.realforeclose.com/auction",
            ]
            
            for url in urls_to_try:
                try:
                    page.goto(url, wait_until="networkidle", timeout=10000)
                    print(f"   {url}: {page.title()[:50]}")
                    if page.title() and 'sale' in page.title().lower():
                        print(f"   -> Sale page found!")
                        page.screenshot(path='/workspace/foreclosure_direct.png')
                        break
                except Exception as e:
                    print(f"   {url}: Error - {str(e)[:50]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\n" + "=" * 60)
print("Extracting Tax Deed Sales Data")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        print("\n1. Navigating to tax deed sales...")
        page.goto("https://www.duval.realtaxdeed.com/", wait_until="networkidle")
        print(f"   Title: {page.title()}")
        
        # Try direct URL for calendar
        print("\n2. Trying calendar URL...")
        page.goto("https://www.duval.realtaxdeed.com/index.cfm?zaction=auction&zmethod=calendar", 
                 wait_until="networkidle", timeout=15000)
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")
        
        page.screenshot(path='/workspace/taxdeed_calendar.png')
        print("   Screenshot saved")
        
        # Extract any visible sale dates
        content = page.content()
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for date patterns
        dates = re.findall(r'(\d{1,2}/\d{1,2}/\d{4})', soup.get_text())
        if dates:
            print(f"\n   Dates found: {set(dates[:10])}")
        
        # Look for sale counts
        counts = re.findall(r'(\d+)\s+(?:property|properties|sale|sales)', soup.get_text(), re.I)
        if counts:
            print(f"   Sale counts: {counts[:5]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
    
    finally:
        browser.close()

print("\nDone!")
