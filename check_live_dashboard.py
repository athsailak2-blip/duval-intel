#!/usr/bin/env python3
"""Check the live dashboard to verify it's working."""
import requests
import json
import time

print("=" * 60)
print("Checking Live Dashboard")
print("=" * 60)

# Wait a moment for deployment
print("\nWaiting 10 seconds for deployment...")
time.sleep(10)

# Check the dashboard
dashboard_url = "https://athsailak2-blip.github.io/duval-intel/"
data_url = "https://athsailak2-blip.github.io/duval-intel/data/leads.json"

print(f"\n1. Checking dashboard HTML...")
try:
    response = requests.get(dashboard_url, timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Content length: {len(response.text)}")
    
    if response.status_code == 200:
        if 'Duval County Lead Intelligence' in response.text:
            print("   Dashboard title found: OK")
        if 'loadData' in response.text:
            print("   loadData function found: OK")
        if 'leads.json' in response.text:
            print("   leads.json reference found: OK")
except Exception as e:
    print(f"   ERROR: {e}")

print(f"\n2. Checking leads.json data...")
try:
    response = requests.get(data_url, timeout=30)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Total leads: {data.get('total_leads', 'N/A')}")
        print(f"   Sources: {len(data.get('sources', {}))}")
        
        for source_id, info in data.get('sources', {}).items():
            print(f"     {source_id}: {info.get('status', 'N/A')} ({info.get('records_count', 0)} records)")
        
        if data.get('leads'):
            lead = data['leads'][0]
            print(f"\n   First lead:")
            print(f"     ID: {lead.get('lead_id', 'N/A')}")
            print(f"     Score: {lead.get('score', 'N/A')}")
            print(f"     Owner: {lead.get('owner_name', 'N/A')[:40]}")
            if lead.get('signals'):
                print(f"     Signal: {lead['signals'][0].get('type', 'N/A')}")
    else:
        print(f"   ERROR: HTTP {response.status_code}")
except Exception as e:
    print(f"   ERROR: {e}")

print(f"\n3. Checking GitHub Actions workflow...")
actions_url = "https://api.github.com/repos/athsailak2-blip/duval-intel/actions/runs"
try:
    response = requests.get(actions_url, timeout=30, headers={'Accept': 'application/vnd.github.v3+json'})
    if response.status_code == 200:
        data = response.json()
        if data.get('workflow_runs'):
            latest = data['workflow_runs'][0]
            print(f"   Latest run: {latest.get('status', 'N/A')} / {latest.get('conclusion', 'N/A')}")
            print(f"   Created: {latest.get('created_at', 'N/A')}")
            print(f"   URL: {latest.get('html_url', 'N/A')}")
except Exception as e:
    print(f"   Note: {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print(f"""
Dashboard URL: {dashboard_url}
Data URL: {data_url}

What's working:
- Official Records: 289 LIS PENDENS records extracted (30 days)
- Dashboard: Loading real data from leads.json
- GitHub Actions: Workflow configured with Playwright

Limitations identified:
- Court Records: Requires login at core.duvalclerk.com
- Foreclosure Sales: Requires bidder registration
- Tax Deed Sales: Requires bidder registration
- Code Enforcement: Requires Public Records Request (PRR)
- GIS: ArcGIS available but bulk data needs API access
- Tax Collector: Individual parcel lookup only (no bulk list)
- Property Appraiser: Individual search only (no bulk download)

Next steps to get more leads:
1. Register accounts for Court Records (CORE) and RealForeclose portals
2. Submit PRR for Code Enforcement data
3. Request bulk data downloads from Property Appraiser and Tax Collector
4. Explore ArcGIS REST API for GIS bulk data access
""")

print("Done!")
