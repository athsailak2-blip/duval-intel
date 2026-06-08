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

# Check if simplified dashboard deployed
if 'function loadData()' in html and 'console.log' in html:
    print("✅ Simplified dashboard deployed")
else:
    print("⚠️ May still be old version")

# Check if data loaded
if 'Loading leads data' in html:
    print("⚠️ Still showing loading (JS may still be running)")
elif 'Error:' in html:
    print("❌ Error loading data")
elif 'Jacksonville' in html or 'Official Records' in html:
    print("✅ Dashboard showing data!")
else:
    print("ℹ️ Check manually - may need more time")

# Check data file directly
print("\n--- Data file check ---")
data_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/data/leads.json", timeout=30)
print(f"Status: {data_resp.status_code}")
if data_resp.status_code == 200:
    try:
        data = data_resp.json()
        print(f"Leads: {len(data.get('leads', []))}")
        print(f"Sources: {len(data.get('sources', {}))}")
    except:
        print("Invalid JSON")

print(f"\nDashboard: https://{USERNAME}.github.io/{REPO_NAME}/")
