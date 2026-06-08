import requests

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# The dashboard shows "Error loading data: Failed to load leads.json"
# But the data file is accessible at /data/leads.json
# The issue is that the browser fetch is failing while curl/requests works

# This is a classic CORS or CSP issue
# Let me check the actual response headers more carefully

# Check dashboard page headers
dash_url = f"https://{USERNAME}.github.io/{REPO_NAME}/"
dash_resp = requests.get(dash_url, timeout=30)
print("Dashboard page headers:")
for k, v in dash_resp.headers.items():
    if k.lower() in ['content-security-policy', 'access-control-allow-origin', 'x-frame-options', 'cache-control']:
        print(f"  {k}: {v}")

# Check data file headers
data_url = f"https://{USERNAME}.github.io/{REPO_NAME}/data/leads.json"
data_resp = requests.get(data_url, timeout=30)
print("\nData file headers:")
for k, v in data_resp.headers.items():
    if k.lower() in ['content-security-policy', 'access-control-allow-origin', 'x-frame-options', 'cache-control', 'content-type']:
        print(f"  {k}: {v}")

# The issue might be that GitHub Pages serves the page with a CSP that blocks fetch
# OR the browser is using a cached version

# Let me check if there's a cache-busting issue
print(f"\nCache-Control: {dash_resp.headers.get('Cache-Control', 'N/A')}")
print(f"ETag: {dash_resp.headers.get('ETag', 'N/A')}")

# The real solution: add a simple inline script that loads the data
# without using fetch, or use a different approach

# Actually, the issue might be that the browser console shows a more specific error
# Let me create a version that shows the actual error in the UI

# Or better yet - let me check if the issue is that the page is being served
# from a different origin or path than expected

print(f"\n--- Checking path resolution ---")
print(f"Page URL: {dash_url}")
print(f"Data URL: {data_url}")
print(f"Data status: {data_resp.status_code}")

# The fetch path is 'data/leads.json'
# When page is at /duval-intel/, this resolves to /duval-intel/data/leads.json
# That should be correct

# But maybe the browser is interpreting the path differently
# Let me try with an absolute path

# Actually, I think the issue might be that GitHub Pages has a service worker
# or the browser is caching aggressively
# Let me add cache-busting headers and a no-cache meta tag

print("\n--- Checking for service worker ---")
if 'serviceWorker' in dash_resp.text.lower():
    print("⚠️ Service worker found in page")
else:
    print("✅ No service worker")

# Check if the error is from a previous version being cached
# The Published Time shows 05:34:28 GMT which is the OLD version
# The new version should have been deployed by now

# Let me force a fresh request with no-cache
fresh_resp = requests.get(dash_url, headers={'Cache-Control': 'no-cache'}, timeout=30)
print(f"\nFresh request status: {fresh_resp.status_code}")
if 'Error loading data' in fresh_resp.text:
    print("❌ Still shows error even with no-cache")
else:
    print("✅ No error with fresh request")

# The issue is definitely that the browser fetch fails
# Let me check if there's a CORS preflight issue
print("\n--- Testing CORS preflight ---")
preflight = requests.options(data_url, headers={
    'Origin': dash_url,
    'Access-Control-Request-Method': 'GET'
}, timeout=30)
print(f"Preflight status: {preflight.status_code}")
print(f"Preflight ACAO: {preflight.headers.get('Access-Control-Allow-Origin', 'N/A')}")
print(f"Preflight ACAM: {preflight.headers.get('Access-Control-Allow-Methods', 'N/A')}")
