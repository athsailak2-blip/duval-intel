#!/usr/bin/env python3
"""Test with Playwright using visible element interaction."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 800}
    )
    page = context.new_page()
    
    try:
        print("1. Navigating to official records...")
        page.goto("https://or.duvalclerk.com/", wait_until="networkidle")
        
        # Accept disclaimer
        print("2. Accepting disclaimer...")
        page.locator('input[type="submit"]').first.click()
        page.wait_for_load_state('networkidle')
        
        # Go to Doc Type search
        print("3. Going to Doc Type search...")
        page.goto("https://or.duvalclerk.com/search/SearchTypeDocType", wait_until="networkidle")
        
        # Take screenshot
        page.screenshot(path='/workspace/search_form2.png')
        print("   Screenshot saved")
        
        # The Kendo ComboBox creates a visible input. Let's look for it.
        print("\n4. Looking for visible inputs...")
        
        # The actual visible input might be different
        # Kendo ComboBox typically creates a wrapper with an input inside
        inputs = page.locator('input[type="text"]').all()
        print(f"   Text inputs found: {len(inputs)}")
        
        for i, inp in enumerate(inputs[:10]):
            name = inp.get_attribute('name') or inp.get_attribute('id') or 'N/A'
            visible = inp.is_visible()
            print(f"     {i}: {name} (visible={visible})")
        
        # Try to find the Kendo ComboBox wrapper
        print("\n5. Looking for Kendo ComboBox wrapper...")
        combo_wrappers = page.locator('.k-combobox, .k-dropdown, [data-role="combobox"]').all()
        print(f"   ComboBox wrappers: {len(combo_wrappers)}")
        
        # Try using the visible input that Kendo creates
        # Kendo ComboBox typically has the original input hidden and creates a new visible one
        print("\n6. Trying to interact with visible form...")
        
        # Look for all visible form elements
        visible_inputs = page.locator('input:visible').all()
        print(f"   Visible inputs: {len(visible_inputs)}")
        
        for i, inp in enumerate(visible_inputs[:10]):
            name = inp.get_attribute('name') or inp.get_attribute('id') or 'N/A'
            placeholder = inp.get_attribute('placeholder') or ''
            print(f"     {i}: {name} placeholder='{placeholder}'")
        
        # Try to find and click the dropdown arrow or button
        print("\n7. Looking for dropdown button...")
        dropdown_btn = page.locator('.k-select, .k-dropdown-wrap .k-icon, [aria-label="select"]').first
        if dropdown_btn.count() > 0:
            print("   Found dropdown button, clicking...")
            dropdown_btn.click()
            page.wait_for_timeout(1000)
            page.screenshot(path='/workspace/dropdown_opened.png')
            print("   Dropdown opened screenshot saved")
        
        # Alternative: Try to directly evaluate JavaScript to set the value
        print("\n8. Trying JavaScript approach...")
        
        # Set the value using JavaScript - Kendo ComboBox stores value in the original input
        page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            if (combo) {
                combo.value("103");  // LIS PENDENS ID
                combo.trigger("change");
                return "Set value to 103";
            }
            return "ComboBox not found";
        }''')
        
        page.wait_for_timeout(500)
        
        # Check what value is now in the field
        val = page.locator('#DocTypesDisplay').first.input_value()
        print(f"   DocTypesDisplay value after JS: '{val}'")
        
        # Also try setting the text
        page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            if (combo) {
                combo.text("LIS PENDENS (LP)");
                combo.trigger("change");
                return "Set text";
            }
            return "ComboBox not found";
        }''')
        
        page.wait_for_timeout(500)
        val = page.locator('#DocTypesDisplay').first.input_value()
        print(f"   DocTypesDisplay value after text set: '{val}'")
        
        # Fill dates
        print("\n9. Filling dates...")
        page.locator('#RecordDateFrom').first.fill("5/1/2026")
        page.locator('#RecordDateTo').first.fill("6/8/2026")
        
        # Submit
        print("\n10. Submitting...")
        page.locator('input[type="submit"]').first.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)
        
        page.screenshot(path='/workspace/results_js.png')
        print("   Results screenshot saved")
        
        # Check content
        content = page.content()
        if 'invalid' in content.lower():
            print("\n   Still getting invalid doctype")
        else:
            print(f"\n   Page content length: {len(content)}")
            print(f"   First 500 chars: {content[:500]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path='/workspace/error.png')
    
    finally:
        browser.close()

print("\nDone!")
