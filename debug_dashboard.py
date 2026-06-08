import requests

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# The dashboard shows "Error loading data" but data/leads.json is accessible
# This means the fetch in the browser is failing - likely a CORS issue
# OR the JavaScript has an error
# Let's check the actual HTML being served

dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Find the loadData function
start = html.find('function loadData()')
end = html.find('// Initialize', start)
if start > 0 and end > 0:
    js = html[start:end]
    print("loadData function found:")
    print(js[:500])
    print("...")
    
# Check if there's a CORS issue or path issue
# The fetch is for 'data/leads.json' which should be relative to root
# On GitHub Pages, the root is /duval-intel/
# So data/leads.json should resolve to /duval-intel/data/leads.json
# This should work...

# Let's check if the error is in the catch block
if "Error loading data" in html:
    print("\nDashboard shows error - checking if it's the catch block")
    
# The issue might be that the leads.json structure doesn't match what the JS expects
# Let's check the JS expectations vs actual data structure
print("\n--- Checking data structure mismatch ---")

# The JS expects: data.leads, data.sources
# The actual data has: data.leads (array), data.sources (object)
# That should match...

# Let's check if the issue is that data.leads is empty or undefined
# Looking at the JS: sampleLeads = data.leads || []
# If data.leads is undefined, it becomes []
# Then renderLeads([]) would show nothing

# But the error message says "Error loading data" which means the catch block fired
# So the fetch failed or the JSON parsing failed

# Let's verify the JSON is valid
import json
data_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/data/leads.json", timeout=30)
try:
    data = data_resp.json()
    print("✅ JSON is valid")
    print(f"Keys: {list(data.keys())}")
    print(f"leads type: {type(data.get('leads'))}")
    print(f"sources type: {type(data.get('sources'))}")
except Exception as e:
    print(f"❌ JSON parse error: {e}")

# The issue might be CORS on GitHub Pages
# Or the fetch might be blocked by CSP
print("\n--- Checking response headers ---")
print(f"Content-Type: {data_resp.headers.get('Content-Type', 'N/A')}")
print(f"Access-Control-Allow-Origin: {data_resp.headers.get('Access-Control-Allow-Origin', 'N/A')}")
