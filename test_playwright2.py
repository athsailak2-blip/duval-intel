#!/usr/bin/env python3
"""Install Playwright browsers and test."""
import subprocess
import sys

# Install browsers
print("Installing Playwright browsers...")
result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                       capture_output=True, text=True, timeout=120)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\nBrowsers installed. Now testing...")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    try:
        print("\n1. Navigating to official records...")
        page.goto("https://or.duvalclerk.com/", wait_until="networkidle")
        print(f"   Page title: {page.title()}")
        
        # Accept disclaimer
        print("\n2. Accepting disclaimer...")
        accept_btn = page.locator('input[type="submit"]').first
        if accept_btn.count() > 0:
            accept_btn.click()
            page.wait_for_load_state('networkidle')
            print(f"   New URL: {page.url}")
        
        # Navigate to Doc Type search
        print("\n3. Going to Doc Type search...")
        page.goto("https://or.duvalclerk.com/search/SearchTypeDocType", wait_until="networkidle")
        print(f"   URL: {page.url}")
        
        # Take screenshot of search form
        page.screenshot(path='/workspace/search_form.png')
        print("   Screenshot saved: /workspace/search_form.png")
        
        # Interact with the Kendo ComboBox
        print("\n4. Interacting with DocTypesDisplay...")
        
        # The combo box might need special handling
        # Try clicking the input field
        combo_input = page.locator('#DocTypesDisplay').first
        if combo_input.count() == 0:
            combo_input = page.locator('input[name="DocTypesDisplay"]').first
        
        if combo_input.count() > 0:
            print("   Found combo box, clicking...")
            combo_input.click()
            page.wait_for_timeout(500)
            
            # Type the value
            combo_input.fill("LIS PENDENS (LP)")
            page.wait_for_timeout(500)
            combo_input.press('Tab')
            page.wait_for_timeout(500)
            
            print("   Filled DocTypesDisplay with 'LIS PENDENS (LP)'")
        
        # Fill dates
        print("\n5. Filling dates...")
        from_date = page.locator('#RecordDateFrom').first
        if from_date.count() > 0:
            from_date.fill("5/1/2026")
            print("   From date: 5/1/2026")
        
        to_date = page.locator('#RecordDateTo').first  
        if to_date.count() > 0:
            to_date.fill("6/8/2026")
            print("   To date: 6/8/2026")
        
        # Submit
        print("\n6. Submitting search...")
        submit = page.locator('input[type="submit"]').first
        if submit.count() > 0:
            submit.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
        
        print(f"   Current URL: {page.url}")
        
        # Check results
        content = page.content()
        if 'invalid' in content.lower():
            print("\n   ERROR: Invalid doctype")
        elif 'result' in content.lower() or 'record' in content.lower():
            print("\n   Results found!")
        
        # Save result page
        page.screenshot(path='/workspace/search_results.png')
        print("   Screenshot saved: /workspace/search_results.png")
        
        with open('/workspace/search_results.html', 'w') as f:
            f.write(content)
        print("   HTML saved: /workspace/search_results.html")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\nDone!")
