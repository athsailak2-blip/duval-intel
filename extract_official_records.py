#!/usr/bin/env python3
"""Extract actual data from the Kendo Grid using JavaScript evaluation."""
from playwright.sync_api import sync_playwright
import json

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
        page.evaluate('''() => {
            var combo = $("#DocTypesDisplay").data("kendoComboBox");
            if (combo) {
                combo.value("104");  // LIS PENDENS
                combo.trigger("change");
            }
        }''')
        page.wait_for_timeout(500)
        
        # Fill dates
        print("5. Filling dates...")
        page.locator('#RecordDateFrom').first.fill("5/1/2026")
        page.locator('#RecordDateTo').first.fill("6/8/2026")
        
        # Submit
        print("6. Submitting...")
        page.locator('input[type="submit"]').first.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)
        
        # Extract data from the Kendo Grid using JavaScript
        print("\n7. Extracting data from Kendo Grid...")
        
        grid_data = page.evaluate('''() => {
            var grid = $("#RsltsGrid").data("kendoGrid");
            if (grid) {
                var data = grid.dataSource.data();
                var records = [];
                for (var i = 0; i < data.length; i++) {
                    var item = data[i];
                    records.push({
                        instrument_number: item.InstrumentNumber || '',
                        record_date: item.RecordDate || '',
                        doc_type: item.DocTypeDescription || '',
                        direct_name: item.DirectName || '',
                        indirect_name: item.IndirectName || '',
                        book_page: item.BookPage || '',
                        book_type: item.BookType || '',
                        consideration: item.Consideration || '',
                        legal_description: item.DocLegalDescription || ''
                    });
                }
                return {
                    total: records.length,
                    records: records
                };
            }
            return {total: 0, records: [], error: "Grid not found"};
        }''')
        
        print(f"\n   Total records extracted: {grid_data['total']}")
        
        if grid_data['records']:
            print(f"\n   First 5 records:")
            for i, rec in enumerate(grid_data['records'][:5]):
                print(f"\n   Record {i+1}:")
                print(f"     Instrument: {rec['instrument_number']}")
                print(f"     Date: {rec['record_date']}")
                print(f"     Type: {rec['doc_type']}")
                print(f"     Direct: {rec['direct_name']}")
                print(f"     Indirect: {rec['indirect_name']}")
                print(f"     Book/Page: {rec['book_page']}")
                print(f"     Legal: {rec['legal_description'][:80] if rec['legal_description'] else 'N/A'}")
        
        # Save to JSON
        with open('/workspace/official_records_data.json', 'w') as f:
            json.dump(grid_data, f, indent=2)
        print(f"\n   Data saved to /workspace/official_records_data.json")
        
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        browser.close()

print("\nDone!")
