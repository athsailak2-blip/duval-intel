#!/usr/bin/env python3
"""Test with Playwright - properly wait for Kendo Grid to load after search."""
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
        
        # Set Kendo ComboBox value
        print("\n4. Setting Kendo ComboBox value...")
        result = page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            if (combo) {
                combo.value("104");  // LIS PENDENS
                combo.trigger("change");
                return "Set to 104";
            }
            return "ComboBox not found";
        }''')
        print(f"   Result: {result}")
        
        page.wait_for_timeout(500)
        
        # Fill dates
        print("\n5. Filling dates...")
        page.locator('#RecordDateFrom').first.fill("5/1/2026")
        page.locator('#RecordDateTo').first.fill("6/8/2026")
        
        # Submit and wait for results to load
        print("\n6. Submitting and waiting for results...")
        page.locator('input[type="submit"]').first.click()
        
        # Wait for the Kendo Grid to load - look for data rows
        print("   Waiting for grid data to load...")
        try:
            page.wait_for_selector('tr.k-master-row, tr[data-uid]', timeout=15000)
            print("   Grid data loaded!")
        except:
            print("   No grid data found within timeout")
        
        page.wait_for_timeout(3000)
        
        # Save HTML
        content = page.content()
        with open('/workspace/results_with_wait.html', 'w') as f:
            f.write(content)
        
        # Analyze results
        from bs4 import BeautifulSoup
        import re
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for Kendo Grid data rows
        data_rows = soup.find_all('tr', class_='k-master-row')
        alt_rows = soup.find_all('tr', class_='k-alt')
        all_rows = data_rows + alt_rows
        
        print(f"\n7. Results analysis:")
        print(f"   Kendo master rows: {len(data_rows)}")
        print(f"   Kendo alt rows: {len(alt_rows)}")
        print(f"   Total data rows: {len(all_rows)}")
        
        # Extract data from rows
        if all_rows:
            print(f"\n   First few records:")
            for i, row in enumerate(all_rows[:5]):
                cells = row.find_all('td')
                if cells:
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"     Row {i+1}: {cell_texts}")
        
        # Look for the grid's data source in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'dataSource' in script.string and 'data' in script.string:
                # Extract data array
                match = re.search(r'data\s*:\s*(\[[^\]]+\])', script.string, re.DOTALL)
                if match:
                    data_text = match.group(1)
                    print(f"\n   Data source found in script (length: {len(data_text)})")
                    # Try to count records
                    record_count = data_text.count('InstrumentNumber') + data_text.count('DocType')
                    print(f"   Estimated records: {record_count}")
        
        # Check for "No records" message
        no_records = soup.find(text=re.compile(r'no record|empty|0 record', re.I))
        if no_records:
            print(f"\n   No records message found: {no_records.strip()}")
        
        # Check page for result count text
        body_text = soup.get_text()
        count_match = re.search(r'(\d+)\s+item', body_text, re.I)
        if count_match:
            print(f"\n   Items found: {count_match.group(1)}")
        
        page.screenshot(path='/workspace/results_screenshot.png')
        print("\n   Screenshot saved to /workspace/results_screenshot.png")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path='/workspace/error_screenshot.png')
    
    finally:
        browser.close()

print("\nDone!")
