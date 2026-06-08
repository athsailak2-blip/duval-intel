import requests

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# The data is accessible (200 OK, 3 leads) but dashboard shows "Error loading data"
# This means the JavaScript fetch is failing in the browser but works via curl/requests
# This is likely a CORS issue or the JavaScript has a syntax error

# Let me check the actual JavaScript for syntax errors by examining the script
dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Extract the script
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)
script = html[script_start+8:script_end]

# Check for JS syntax issues that would prevent execution
# Common issues: HTML entities, unclosed braces, template literal issues

issues = []

# Check for HTML entities in JS
entities = ['&gt;', '&lt;', '&amp;', '&quot;', '&#39;']
for ent in entities:
    if ent in script:
        issues.append(f"HTML entity {ent} found in JS - breaks syntax")

# Check for unclosed braces (basic check)
open_braces = script.count('{')
close_braces = script.count('}')
if open_braces != close_braces:
    issues.append(f"Unclosed braces: {open_braces} open, {close_braces} close")

open_parens = script.count('(')
close_parens = script.count(')')
if open_parens != close_parens:
    issues.append(f"Unclosed parens: {open_parens} open, {close_parens} close")

# Check for template literal issues (backticks with ${})
if '`' in script:
    backticks = script.count('`')
    if backticks % 2 != 0:
        issues.append(f"Unclosed template literals: {backticks} backticks (should be even)")

if issues:
    print("❌ JavaScript issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ No obvious JS syntax issues")

# Check the specific error handling in the JS
if 'catch(err' in script or '.catch(err' in script:
    print("\n✅ Error handling exists in JS")
    
    # Find the catch block
    catch_idx = script.find('.catch(err')
    if catch_idx > 0:
        # Show context around catch
        context = script[catch_idx:catch_idx+200]
        print(f"\nCatch block context:")
        print(context[:300])

# The issue might be that the leads.json structure doesn't match what the JS expects
# Let me check the data structure vs JS expectations
data_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/data/leads.json", timeout=30)
data = data_resp.json()

print(f"\n--- Data Structure Check ---")
print(f"Keys: {list(data.keys())}")
if 'leads' in data:
    print(f"leads is array: {isinstance(data['leads'], list)}")
    if data['leads']:
        print(f"First lead keys: {list(data['leads'][0].keys())}")
        if 'signals' in data['leads'][0]:
            print(f"signals is array: {isinstance(data['leads'][0]['signals'], list)}")
            if data['leads'][0]['signals']:
                print(f"First signal keys: {list(data['leads'][0]['signals'][0].keys())}")

# The JS expects: lead.signals with .type and .label
# But the data has: lead.signals with .type (LIS_PENDENS) and NO .label
# This would cause 'undefined' for s.label but not a crash

# Check if the issue is that data.sources uses different keys than JS expects
if 'sources' in data:
    print(f"\nSources keys: {list(data['sources'].keys())}")
    # JS expects: duval_official_records, duval_court_records, etc.
    # Data has: official_records, court_records, etc. (without duval_ prefix)
    
    source_map = {
        'official_records': 'duval_official_records',
        'court_records': 'duval_court_records',
        'foreclosure_sales': 'duval_foreclosure_sales',
        'tax_deed_sales': 'duval_tax_deed_sales',
        'parcel_master': 'duval_parcel_master',
        'tax_collector': 'duval_tax_collector',
        'gis_mapping': 'duval_gis',
        'code_enforcement': 'duval_code_enforcement'
    }
    
    for data_key, js_key in source_map.items():
        if data_key in data['sources']:
            print(f"  ✅ Data has '{data_key}' - JS expects '{js_key}'")
        else:
            print(f"  ❌ Data missing '{data_key}'")
