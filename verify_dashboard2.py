import requests

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

# Check the dashboard
dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
if dash_resp.status_code == 200:
    html = dash_resp.text
    if 'loadData()' in html:
        print("✅ Root index.html has loadData() - new version deployed")
    else:
        print("⚠ Root index.html still old version (no loadData)")
    if "Error loading data" in html:
        print("⚠ Dashboard shows error loading data")
    elif "Loading leads" in html:
        print("⚠ Dashboard still shows loading state")
    else:
        print("✅ Dashboard appears to have loaded data")
else:
    print(f"⚠ Dashboard returned {dash_resp.status_code}")

# Check data file
print("\n--- Checking data/leads.json ---")
data_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/data/leads.json", timeout=30)
if data_resp.status_code == 200:
    print("✅ data/leads.json is accessible")
    try:
        data = data_resp.json()
        print(f"Total leads: {data.get('total_leads', 'N/A')}")
        print(f"Sources: {len(data.get('sources', {}))}")
        for src, info in data.get('sources', {}).items():
            print(f"  {src}: {info.get('status', 'N/A')} ({info.get('records_count', 0)} records)")
    except:
        print("Could not parse JSON")
else:
    print(f"⚠ data/leads.json returned {data_resp.status_code}")

print(f"\nDashboard: https://{USERNAME}.github.io/{REPO_NAME}/")
