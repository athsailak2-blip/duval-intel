#!/usr/bin/env python3
"""Analyze the results page to see if we got actual data."""
from bs4 import BeautifulSoup

with open('/workspace/results_js.html', 'w') as f:
    # We need to get the content from the Playwright test
    pass

# Let's re-run and save the HTML properly
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
        
        # Use JavaScript to set Kendo ComboBox value properly
        print("\n4. Setting Kendo ComboBox value...")
        
        # Try multiple approaches
        result = page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            if (combo) {
                // Try to find LIS PENDENS in the data source
                var ds = combo.dataSource;
                var items = ds.data();
                var lpItem = null;
                for (var i = 0; i < items.length; i++) {
                    if (items[i].Text && items[i].Text.indexOf("LIS PENDENS") >= 0) {
                        lpItem = items[i];
                        break;
                    }
                }
                
                if (lpItem) {
                    combo.value(lpItem.Value);
                    combo.trigger("change");
                    return "Found LIS PENDENS: " + JSON.stringify(lpItem);
                }
                
                // Fallback: try value 103
                combo.value("103");
                combo.trigger("change");
                return "Set to 103";
            }
            return "ComboBox not found";
        }''')
        print(f"   Result: {result}")
        
        page.wait_for_timeout(500)
        
        # Check the value
        val = page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            return combo ? {value: combo.value(), text: combo.text()} : "not found";
        }''')
        print(f"   ComboBox state: {val}")
        
        # Fill dates
        print("\n5. Filling dates...")
        page.locator('#RecordDateFrom').first.fill("5/1/2026")
        page.locator('#RecordDateTo').first.fill("6/8/2026")
        
        # Submit
        print("\n6. Submitting...")
        page.locator('input[type="submit"]').first.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)
        
        # Save HTML
        content = page.content()
        with open('/workspace/results_final.html', 'w') as f:
            f.write(content)
        print(f"   HTML saved, length: {len(content)}")
        
        # Analyze results
        print("\n7. Analyzing results...")
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for result tables
        tables = soup.find_all('table')
        print(f"   Tables found: {len(tables)}")
        
        # Look for result count
        body_text = soup.get_text()
        
        # Check for error
        if 'invalid' in body_text.lower():
            print("   ERROR: Invalid doctype still occurring")
            # Try to find what value is expected
            error_script = soup.find('script', text=lambda t: t and 'ShowError' in t)
            if error_script:
                print(f"   Error script: {error_script.string[:200]}")
        
        # Look for any result indicators
        import re
        result_patterns = [
            r'(\d+)\s+result',
            r'(\d+)\s+record',
            r'found\s+(\d+)',
            r'showing\s+(\d+)',
        ]
        
        for pattern in result_patterns:
            matches = re.findall(pattern, body_text, re.I)
            if matches:
                print(f"   Found result count: {matches}")
        
        # Look for Kendo Grid
        kendo_grid = soup.find('div', {'data-role': 'grid'})
        if kendo_grid:
            print("   Kendo Grid found!")
        
        # Check for any data rows
        data_rows = soup.find_all('tr', class_=re.compile(r'data|k-master|k-alt', re.I))
        print(f"   Data rows: {len(data_rows)}")
        
        # Print first 1000 chars of body text for debugging
        print(f"\n   Body text (first 1000 chars):")
        print(f"   {body_text[:1000]}")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\nDone!")
