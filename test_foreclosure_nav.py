#!/usr/bin/env python3
"""Test foreclosure sales with proper navigation."""
from playwright.sync_api import sync_playwright
import re
from bs4 import BeautifulSoup

print("=" * 60)
print("Testing Foreclosure Sales - Proper Navigation")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = context.new_page()
    
    try:
        # Navigate to foreclosure sales
        print("\n1. Navigating to foreclosure sales...")
        page.goto("https://www.duval.realforeclose.com/", wait_until="networkidle")
        
        # Look for all links on the page
        print("\n2. All links on splash page:")
        links = page.locator('a').all()
        for link in links:
            href = link.get_attribute('href') or ''
            text = link.inner_text().strip()
            if text and href:
                print(f"   '{text[:60]}' -> {href[:80]}")
        
        # Look for buttons
        print("\n3. All buttons:")
        buttons = page.locator('button, input[type="submit"]').all()
        for btn in buttons:
            text = btn.inner_text().strip() or btn.get_attribute('value') or ''
            print(f"   '{text[:60]}'")
        
        # Look for forms
        print("\n4. All forms:")
        forms = page.locator('form').all()
        for form in forms:
            action = form.get_attribute('action') or ''
            print(f"   Action: {action[:80]}")
        
        # Check the page content for clues
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for any JavaScript that redirects
        scripts = soup.find_all('script')
        print(f"\n5. Scripts found: {len(scripts)}")
        for script in scripts:
            if script.string:
                text = script.string[:200]
                if 'redirect' in text.lower() or 'location' in text.lower() or 'href' in text.lower():
                    print(f"   Redirect script: {text[:150]}")
        
        # Look for meta refresh
        meta_refresh = soup.find('meta', {'http-equiv': 'refresh'})
        if meta_refresh:
            print(f"\n   Meta refresh found: {meta_refresh}")
        
        # Check if there's a "Continue" or "Enter" button
        enter_btn = page.locator('text=/Enter|Continue|Start|Go|Proceed/i').first
        if enter_btn.count() > 0:
            print(f"\n6. Found enter/continue button: {enter_btn.inner_text()[:50]}")
            enter_btn.click()
            page.wait_for_load_state('networkidle')
            print(f"   New URL: {page.url}")
            print(f"   New title: {page.title()}")
        
        # Try looking for county selection
        print("\n7. Looking for county/jurisdiction selection...")
        selects = page.locator('select').all()
        for select in selects:
            name = select.get_attribute('name') or select.get_attribute('id') or 'N/A'
            print(f"   Select: {name}")
            options = select.locator('option').all()
            for opt in options[:5]:
                print(f"     {opt.get_attribute('value')}: {opt.inner_text()[:50]}")
        
        page.screenshot(path='/workspace/foreclosure_splash.png')
        print("\n   Screenshot saved")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\nDone!")
