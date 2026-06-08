import requests

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# The dashboard has the right JS but shows loading state
# This means the JS is executing but the fetch might be failing
# Let me check the actual fetch path and the data file

# Check the fetch path in the HTML
dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Find the fetch call
fetch_idx = html.find("fetch('")
if fetch_idx > 0:
    end_quote = html.find("'", fetch_idx + 7)
    fetch_path = html[fetch_idx+7:end_quote]
    print(f"Fetch path: {fetch_path}")
    
    # Test if this path resolves correctly
    # The page is at /duval-intel/
    # fetch('data/leads.json') should resolve to /duval-intel/data/leads.json
    test_url = f"https://{USERNAME}.github.io/{REPO_NAME}/{fetch_path}"
    print(f"Full URL: {test_url}")
    
    data_resp = requests.get(test_url, timeout=30)
    print(f"Data response: {data_resp.status_code}")
    if data_resp.status_code == 200:
        try:
            data = data_resp.json()
            print(f"✅ JSON valid, leads: {len(data.get('leads', []))}")
            print(f"Sources: {list(data.get('sources', {}).keys())}")
        except:
            print("❌ Not valid JSON")
    else:
        print(f"❌ Failed to fetch data")

# Check if there's a CORS issue by checking headers
print(f"\n--- Response Headers ---")
print(f"Content-Type: {data_resp.headers.get('Content-Type', 'N/A')}")
print(f"Access-Control-Allow-Origin: {data_resp.headers.get('Access-Control-Allow-Origin', 'N/A')}")

# The issue might be that the fetch is blocked by CSP or CORS
# OR the JavaScript has a syntax error that prevents execution
# Let me check for any JS syntax issues

# Check for HTML entities in the script that might break JS
if '&gt;' in html or '&lt;' in html or '&amp;' in html:
    print("\n⚠️ HTML entities found in HTML - checking if in script...")
    script_start = html.find('<script>')
    script_end = html.find('</script>', script_start)
    script_content = html[script_start+8:script_end]
    
    entities = ['&gt;', '&lt;', '&amp;']
    for ent in entities:
        if ent in script_content:
            print(f"  ❌ {ent} found in script content - WILL BREAK JS")
        else:
            print(f"  ✅ No {ent} in script content")
