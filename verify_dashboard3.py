import requests
import time

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# Wait for deployment
print("Waiting 30s for deployment...")
time.sleep(30)

# Check dashboard
dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Check if data loaded
if 'Loading leads data' in html and 'Error loading data' not in html:
    print("⚠️ Still showing loading state (JS may still be running)")
elif 'Error loading data' in html:
    print("❌ Error loading data")
else:
    # Check if actual lead data is rendered
    if 'Jacksonville' in html and ('Lis Pendens' in html or 'Foreclosure' in html or 'Tax Delinquent' in html):
        print("✅ Dashboard showing real lead data!")
    else:
        print("ℹ️ Dashboard loaded but may not show leads yet")

# Check the fetch path in deployed HTML
fetch_idx = html.find("fetch('")
if fetch_idx > 0:
    end_quote = html.find("'", fetch_idx + 7)
    fetch_path = html[fetch_idx+7:end_quote]
    print(f"\nFetch path in deployed HTML: {fetch_path}")
    
    # Test the path
    test_url = f"https://{USERNAME}.github.io/{REPO_NAME}/{fetch_path.split('?')[0]}"
    data_resp = requests.get(test_url, timeout=30)
    print(f"Data URL: {test_url}")
    print(f"Data response: {data_resp.status_code}")
    if data_resp.status_code == 200:
        try:
            data = data_resp.json()
            print(f"✅ Data accessible: {len(data.get('leads', []))} leads")
        except:
            print("❌ Not valid JSON")

print(f"\nDashboard: https://{USERNAME}.github.io/{REPO_NAME}/")
