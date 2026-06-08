import json

# The leads.json has 'healthy' status but the dashboard fetch might be failing
# Let's check the dashboard's fetch logic - it looks for 'scraped' or 'healthy'
# The issue might be that the fetch is failing and showing the loading state

# Let's verify the dashboard HTML has the right fetch path
with open('/workspace/dashboard/index.html', 'r') as f:
    html = f.read()

# Check if fetch path is correct - on GitHub Pages, data/leads.json should be at root
if "fetch('data/leads.json" in html:
    print("Dashboard fetches from: data/leads.json (relative path)")
    print("This is correct for GitHub Pages deployment")
else:
    print("Fetch path not found as expected")

# The dashboard loads from leads.json which has 'healthy' status
# But the fetch might fail because the file isn't at the right path
# On GitHub Pages, the deploy.yml copies data/ to _site/data/
# So the path should be correct

# Let's check the workflow to see if data is copied correctly
with open('/workspace/.github/workflows/deploy.yml', 'r') as f:
    workflow = f.read()

if 'cp -r data _site/' in workflow or 'cp -r data' in workflow:
    print("\nWorkflow copies data/ to _site/ - correct")
else:
    print("\nWorkflow may not copy data/ correctly")

# The real issue: the dashboard shows "Pending" because the fetch might be 
# failing with 404, and the old cached HTML is showing
# OR the leads.json has 'healthy' but the dashboard JS maps it to 'online'
# Let's verify the mapping logic

if "isHealthy = info.status === 'healthy' || info.status === 'scraped'" in html:
    print("\nDashboard correctly maps 'healthy' to 'online' status")
else:
    print("\nDashboard mapping logic may be different")

# The issue is likely that GitHub Pages hasn't deployed the latest version yet
# OR the data/leads.json file isn't being served correctly
print("\n--- Analysis ---")
print("leads.json has status: 'healthy' for most sources")
print("Dashboard JS maps 'healthy' -> 'online' (green)")
print("Dashboard JS maps 'prr_required' -> 'warning' (yellow)")
print("The fetch should work if data/ is copied to _site/")
print("If you still see 'Pending', the page is cached or the fetch failed")
