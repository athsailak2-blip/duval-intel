#!/usr/bin/env python3
"""
Duval County Official Records Scraper - Playwright/Browserless Version
Source: https://or.duvalclerk.com/
Portal Type: Tyler Technologies / Kendo UI / ASP.NET MVC

Uses Browserless /function API for cloud-based browser execution with full interaction.
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BROWSERLESS_TOKEN = os.environ.get('BROWSERLESS_TOKEN', '2UfCnQNj9ioAEV89f55a786fd64722a5ae97b27921bf39df1')
BROWSERLESS_URL = os.environ.get('BROWSERLESS_URL', 'https://production-sfo.browserless.io')

class DuvalOfficialRecordsScraper:
    SOURCE_ID = "duval_official_records"
    BASE_URL = "https://or.duvalclerk.com"
    
    # Document type IDs for distress-related documents
    DOC_TYPES = {
        'LIS PENDENS': '104',
        'MORTGAGE': '110',
        'LIEN': '103',
        'JUDGMENT': '97',
        'FORECLOSURE': '104',
        'NOTICE': '120',
        'DEED': '87',
        'QUIT CLAIM': '87',
        'TRUST': '131',
        'PROBATE': '92',
        'ASSIGNMENT': '75',
        'SATISFACTION': '129',
        'RELEASE': '126',
    }
    
    def __init__(self, config: Dict):
        self.config = config
    
    def _run_browserless_function(self, script: str) -> Dict:
        """Execute a Browserless function script."""
        try:
            response = requests.post(
                f"{BROWSERLESS_URL}/function?token={BROWSERLESS_TOKEN}",
                headers={"Content-Type": "application/javascript"},
                data=script,
                timeout=120
            )
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    return {"error": "Invalid JSON response", "raw": response.text[:500]}
            else:
                return {"error": f"HTTP {response.status_code}", "raw": response.text[:500]}
        except Exception as e:
            return {"error": str(e)}
    
    def _search_by_doc_type(self, doc_type_id: str, doc_type_name: str, 
                           start_date: str, end_date: str) -> List[Dict]:
        """Search official records by document type using Browserless."""
        
        # Build the Browserless function script
        script = f'''
export default async ({{ page }}) => {{
  // Navigate to search page
  await page.goto("https://or.duvalclerk.com/search/SearchTypeDocType", {{ 
    waitUntil: "domcontentloaded", 
    timeout: 30000 
  }});
  
  // Wait for page to be ready
  await page.waitForFunction(() => document.readyState === 'complete', {{ timeout: 10000 }});
  
  // Check if disclaimer form exists and accept it
  const hasDisclaimer = await page.evaluate(() => {{
    return document.querySelector("form[action*='Disclaimer']") !== null ||
           document.querySelector("#btnButton") !== null;
  }});
  
  if (hasDisclaimer) {{
    await Promise.all([
      page.waitForNavigation({{ waitUntil: "domcontentloaded", timeout: 15000 }}).catch(() => {{}}),
      page.evaluate(() => {{ document.querySelector("#btnButton").click(); }})
    ]);
    await page.waitForFunction(() => document.readyState === 'complete', {{ timeout: 10000 }});
  }}
  
  // Set the document type in the Kendo ComboBox
  await page.evaluate((docTypeId) => {{
    // Find the combo box and set its value
    const comboBox = document.querySelector('#DocTypesDisplay');
    if (comboBox) {{
      comboBox.value = docTypeId;
      // Trigger change event
      comboBox.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
    
    // Also update the hidden textarea
    const docTypes = document.querySelector('#DocTypes');
    if (docTypes) {{
      docTypes.value = docTypeId;
    }}
  }}, '{doc_type_id}');
  
  // Set date range
  const fromDate = '{start_date}';
  const toDate = '{end_date}';
  
  await page.evaluate((fromDate, toDate) => {{
    // Set from date
    const fromPicker = document.querySelector('#RecordDateFrom');
    if (fromPicker) {{
      fromPicker.value = fromDate;
      fromPicker.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
    
    // Set to date
    const toPicker = document.querySelector('#RecordDateTo');
    if (toPicker) {{
      toPicker.value = toDate;
      toPicker.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
  }}, fromDate, toDate);
  
  // Click search button and wait for results
  await Promise.all([
    page.waitForResponse(response => response.url().includes('/search/SearchTypeDocType'), {{ timeout: 30000 }}).catch(() => {{}}),
    page.evaluate(() => {{ document.querySelector('#btnSearch').click(); }})
  ]);
  
  // Wait for results to load
  await page.waitForFunction(() => document.readyState === 'complete', {{ timeout: 15000 }});
  await page.evaluate(() => new Promise(resolve => setTimeout(resolve, 3000)));
  
  // Extract results from the page
  const records = await page.evaluate(() => {{
    const results = [];
    
    // Look for result rows in various formats
    const rows = document.querySelectorAll('.k-grid-content tr, .results tr, [class*="result"] tr, table tbody tr');
    
    rows.forEach(row => {{
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3) {{
        const record = {{}};
        
        // Try to extract data from cells
        cells.forEach((cell, index) => {{
          const text = cell.textContent.trim();
          if (index === 0) record.record_id = text;
          else if (index === 1) record.date = text;
          else if (index === 2) record.party_name = text;
          else if (index === 3) record.doc_type_detail = text;
          else if (index === 4) record.book_page = text;
        }});
        
        if (record.record_id && record.record_id !== 'Record ID') {{
          results.push(record);
        }}
      }}
    }});
    
    // Also look for any JSON data in scripts
    const scripts = document.querySelectorAll('script');
    scripts.forEach(script => {{
      if (script.textContent && script.textContent.includes('kendo')) {{
        // Try to find data in Kendo grid configuration
        const matches = script.textContent.match(/dataSource:\s*(\[.*?\])/s);
        if (matches) {{
          try {{
            const data = JSON.parse(matches[1]);
            data.forEach(item => {{
              if (typeof item === 'object') {{
                results.push({{
                  record_id: item.DocumentNumber || item.InstrumentNumber || '',
                  date: item.RecordDate || item.Date || '',
                  party_name: item.PartyName || item.Name || '',
                  doc_type_detail: item.DocumentType || item.DocType || '',
                  book_page: item.BookPage || ''
                }});
              }}
            }});
          }} catch (e) {{}}
        }}
      }}
    }});
    
    return results;
  }});
  
  // Get the HTML for debugging
  const html = await page.content();
  
  return {{ 
    records, 
    html: html.substring(0, 10000),
    url: page.url(),
    hasDisclaimer 
  }};
}};
'''
        
        result = self._run_browserless_function(script)
        
        if 'error' in result:
            print(f"Error searching {doc_type_name}: {result['error']}")
            return []
        
        records = result.get('records', [])
        
        # Add metadata to each record
        for record in records:
            record['doc_type'] = doc_type_name
            record['source_id'] = self.SOURCE_ID
            record['scraped_at'] = datetime.now().isoformat()
        
        return records
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                            doc_types: Optional[List[str]] = None) -> List[Dict]:
        """Search official records by date range."""
        records = []
        
        # Document types that indicate distress
        distress_doc_types = doc_types or [
            'LIS PENDENS', 'MORTGAGE', 'LIEN', 'JUDGMENT',
            'FORECLOSURE', 'NOTICE', 'DEED', 'QUIT CLAIM',
            'TRUST', 'PROBATE', 'ASSIGNMENT', 'SATISFACTION', 'RELEASE'
        ]
        
        for doc_type in distress_doc_types:
            doc_type_id = self.DOC_TYPES.get(doc_type)
            if not doc_type_id:
                continue
            
            try:
                parsed_records = self._search_by_doc_type(
                    doc_type_id, doc_type, start_date, end_date
                )
                records.extend(parsed_records)
                
            except Exception as e:
                print(f"Error scraping {doc_type}: {e}")
                continue
        
        return records
    
    def refresh(self, cursor: Optional[str] = None, days_back: int = None) -> Dict:
        """Run daily refresh or historical seeding."""
        # Check for seed mode from environment
        if days_back is None:
            seed_mode = os.environ.get('SEED_MODE', 'false').lower() == 'true'
            days_back = 30 if seed_mode else 1
        
        if cursor:
            start_date = cursor
        else:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')
        
        end_date = datetime.now().strftime('%m/%d/%Y')
        
        records = self.search_by_date_range(start_date, end_date)
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(records),
            'new_records': records,
            'updated_cursor': end_date,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'note': 'Using Browserless /function API with Playwright interaction'
        }

if __name__ == '__main__':
    config = {'source_url': 'https://or.duvalclerk.com/'}
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=1)
    print(json.dumps(result, indent=2))
