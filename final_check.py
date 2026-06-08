import requests
import time

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# The Pages build is complete (built at 05:49:48Z)
# But fetch_url still shows the old version (05:34:28 GMT)
# This is because GitHub Pages has a 10-minute cache by default
# AND the fetch_url tool might be caching

# Let me wait a bit more and check again
print("Waiting 60s for cache to clear...")
time.sleep(60)

# Check with fresh request (no cache)
dash_resp = requests.get(
    f"https://{USERNAME}.github.io/{REPO_NAME}/",
    headers={
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    },
    timeout=30
)
html = dash_resp.text

# Check if new version
if 'XMLHttpRequest' in html:
    print("✅ XHR version confirmed in fresh request")
else:
    print("⚠️ Still old version in fresh request")

# Check if data is showing
if 'Jacksonville' in html:
    print("✅ Data showing in dashboard!")
    # Extract some data
    if '888 Pre foreclosure' in html:
        print("  - Lead 001 showing")
    if '999 Tax Delinquent' in html:
        print("  - Lead 002 showing")
    if '111 Code Violation' in html:
        print("  - Lead 003 showing")
elif 'Error:' in html:
    print("❌ Error showing")
    err_start = html.find('Error:')
    if err_start > 0:
        err_end = html.find('<', err_start)
        print(f"  Error: {html[err_start:err_end]}")
elif 'Initializing...' in html:
    print("⚠️ Still initializing")
else:
    print("ℹ️ Unknown state")

# Check source health
if 'Official Records' in html:
    print("✅ Source health section showing")
    if 'healthy' in html.lower():
        print("  - Sources showing healthy status")
    elif 'online' in html.lower():
        print("  - Sources showing online status")

print(f"\nDashboard: https://{USERNAME}.github.io/{REPO_NAME}/")
