#!/usr/bin/env python3
"""Test using a browser automation approach with Playwright."""
import subprocess
import sys

# Check if playwright is installed
try:
    from playwright.sync_api import sync_playwright
    print("Playwright is available")
    has_playwright = True
except ImportError:
    print("Playwright not installed, trying to install...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], capture_output=True)
    try:
        from playwright.sync_api import sync_playwright
        print("Playwright installed successfully")
        has_playwright = True
    except:
        print("Could not install Playwright")
        has_playwright = False

if not has_playwright:
    print("\nPlaywright not available. Using requests with enhanced headers.")
    print("The Official Records portal requires JavaScript interaction (Kendo UI).")
    print("This is a known limitation - the portal uses client-side validation.")
    sys.exit(0)

print("\n" + "=" * 60)
print("Testing with Playwright Browser Automation")
print("=" * 60)

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()
    
    try:
        # Step 1: Navigate to main page and accept disclaimer
        print("\n1. Navigating to official records...")
        page.goto("https://or.duvalclerk.com/", wait_until="networkidle")
        print(f"   Page title: {page.title()}")
        
        # Check if we're on disclaimer page
        if 'disclaimer' in page.content().lower() or 'accept' in page.content().lower():
            print("   Disclaimer page detected")
            
            # Find and click accept button
            accept_button = page.locator('input[type="submit"], button:has-text("Accept"), button:has-text("I accept")').first
            if accept_button.count() > 0:
                print("   Clicking accept button...")
                accept_button.click()
                page.wait_for_load_state('networkidle')
                print(f"   New URL: {page.url}")
        
        # Step 2: Navigate to Doc Type search
        print("\n2. Navigating to Doc Type search...")
        
        # Look for Doc Type search link
        doc_type_link = page.locator('a:has-text("Doc Type")').first
        if doc_type_link.count() > 0:
            doc_type_link.click()
            page.wait_for_load_state('networkidle')
        else:
            # Direct navigation
            page.goto("https://or.duvalclerk.com/search/SearchTypeDocType", wait_until="networkidle")
        
        print(f"   Current URL: {page.url}")
        print(f"   Page title: {page.title()}")
        
        # Step 3: Interact with the Kendo ComboBox
        print("\n3. Interacting with document type selector...")
        
        # The DocTypesDisplay is a Kendo ComboBox
        # We need to interact with it properly
        
        # First, let's see what fields are available
        form_fields = page.locator('form input, form select').all()
        print(f"   Form fields found: {len(form_fields)}")
        
        for field in form_fields[:10]:
            tag = field.evaluate('el => el.tagName')
            name = field.get_attribute('name') or field.get_attribute('id') or 'N/A'
            type_attr = field.get_attribute('type') or 'N/A'
            print(f"     {tag} {type_attr}: {name}")
        
        # Try to fill the DocTypesDisplay field
        print("\n4. Filling search form...")
        
        # Try clicking on the combo box and selecting an option
        combo = page.locator('#DocTypesDisplay').first
        if combo.count() > 0:
            print("   Found DocTypesDisplay combo box")
            combo.click()
            page.wait_for_timeout(500)
            
            # Try to find and click on LIS PENDENS option
            option = page.locator('.k-list-item:has-text("LIS PENDENS")').first
            if option.count() > 0:
                option.click()
                print("   Selected LIS PENDENS")
            else:
                # Try typing
                combo.fill("LIS PENDENS (LP)")
                page.wait_for_timeout(500)
                combo.press('Enter')
                print("   Typed LIS PENDENS (LP)")
        
        # Fill date range
        from_date = page.locator('#RecordDateFrom').first
        if from_date.count() > 0:
            from_date.fill("5/1/2026")
            print("   Filled from date: 5/1/2026")
        
        to_date = page.locator('#RecordDateTo').first
        if to_date.count() > 0:
            to_date.fill("6/8/2026")
            print("   Filled to date: 6/8/2026")
        
        # Submit the form
        print("\n5. Submitting search...")
        submit_button = page.locator('input[type="submit"], button[type="submit"]').first
        if submit_button.count() > 0:
            submit_button.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
        else:
            # Try pressing Enter on the form
            page.locator('form').first.press('Enter')
            page.wait_for_timeout(2000)
        
        print(f"   Current URL: {page.url}")
        print(f"   Page title: {page.title()}")
        
        # Check for results
        content = page.content()
        if 'result' in content.lower() or 'record' in content.lower():
            print("\n   Results page detected!")
            # Try to count result rows
            rows = page.locator('table tr').count()
            print(f"   Table rows found: {rows}")
        
        if 'invalid' in content.lower():
            print("\n   ERROR: Invalid doctype error still occurring")
            # Take screenshot for debugging
            page.screenshot(path='/workspace/playwright_error.png')
            print("   Screenshot saved to /workspace/playwright_error.png")
        
        # Save page content for analysis
        with open('/workspace/playwright_page.html', 'w') as f:
            f.write(content)
        print("\n   Page content saved to /workspace/playwright_page.html")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\n" + "=" * 60)
print("Browser automation test complete")
print("=" * 60)
