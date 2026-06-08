#!/usr/bin/env python3
"""Test foreclosure and tax deed sales with Playwright."""
from playwright.sync_api import sync_playwright

print("=" * 60)
print("Testing Foreclosure Sales Portal")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Test Foreclosure Sales
        print("\n1. Testing duval.realforeclose.com...")
        page.goto("https://www.duval.realforeclose.com/", wait_until="networkidle", timeout=30000)
        print(f"   Page title: {page.title()}")
        print(f"   URL: {page.url}")
        
        # Look for calendar or sale list
        content = page.content()
        if 'sale' in content.lower() or 'auction' in content.lower() or 'property' in content.lower():
            print("   Property/auction content found")
        
        # Look for links to sale lists
        links = page.locator('a').all()
        sale_links = [l for l in links if 'sale' in (l.get_attribute('href') or '').lower() or 'auction' in (l.get_attribute('href') or '').lower()]
        print(f"   Sale-related links: {len(sale_links)}")
        
        page.screenshot(path='/workspace/foreclosure_page.png')
        print("   Screenshot saved")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    browser.close()

print("\n" + "=" * 60)
print("Testing Tax Deed Sales Portal")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Test Tax Deed Sales
        print("\n1. Testing duval.realtaxdeed.com...")
        page.goto("https://www.duval.realtaxdeed.com/", wait_until="networkidle", timeout=30000)
        print(f"   Page title: {page.title()}")
        print(f"   URL: {page.url}")
        
        content = page.content()
        if 'tax' in content.lower() or 'deed' in content.lower() or 'sale' in content.lower():
            print("   Tax deed content found")
        
        page.screenshot(path='/workspace/taxdeed_page.png')
        print("   Screenshot saved")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    browser.close()

print("\n" + "=" * 60)
print("Testing Court Records (CORE)")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        print("\n1. Testing core.duvalclerk.com...")
        page.goto("https://core.duvalclerk.com/", wait_until="networkidle", timeout=30000)
        print(f"   Page title: {page.title()}")
        print(f"   URL: {page.url}")
        
        # Check if login is required
        content = page.content()
        if 'login' in content.lower() or 'password' in content.lower() or 'sign in' in content.lower():
            print("   LOGIN REQUIRED - Court records need authentication")
        elif 'search' in content.lower():
            print("   Search page accessible")
        
        page.screenshot(path='/workspace/court_page.png')
        print("   Screenshot saved")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    browser.close()

print("\n" + "=" * 60)
print("Testing GIS Mapping")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        print("\n1. Testing maps.coj.net/duvalproperty...")
        page.goto("https://maps.coj.net/duvalproperty/", wait_until="networkidle", timeout=30000)
        print(f"   Page title: {page.title()}")
        print(f"   URL: {page.url}")
        
        # Check for ArcGIS/ESRI indicators
        content = page.content()
        if 'arcgis' in content.lower() or 'esri' in content.lower():
            print("   ArcGIS/ESRI detected")
        
        page.screenshot(path='/workspace/gis_page.png')
        print("   Screenshot saved")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    browser.close()

print("\nDone!")
