import requests
import time

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# Wait for deployment
print("Waiting 60s for deployment...")
time.sleep(60)

# Check dashboard
dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Check if XHR version deployed
if 'XMLHttpRequest' in html:
    print("✅ XHR dashboard deployed")
else:
    print("⚠️ May still be old version")

# Check if debug info is showing
if 'Debug Info' in html:
    print("✅ Debug section present")

# Check if data loaded
if 'Jacksonville' in html or 'Official Records' in html or 'Court Records' in html:
    print("✅ Dashboard showing data!")
elif 'Error:' in html:
    print("❌ Error loading data")
    # Extract error
    err_start = html.find('Error:')
    if err_start > 0:
        err_end = html.find('<', err_start)
        print(f"  Error: {html[err_start:err_end]}")
elif 'Initializing...' in html:
    print("⚠️ Still initializing (JS may not have run)")
else:
    print("ℹ️ Check manually")

# Check the debug info section
if 'debug-info' in html:
    print("\n✅ Debug info element found")

print(f"\nDashboard: https://{USERNAME}.github.io/{REPO_NAME}/")
print("Open browser console to see debug messages")
