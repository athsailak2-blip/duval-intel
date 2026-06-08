import json

# The issue: dashboard/index.html is served from /dashboard/index.html
# But the fetch is for 'data/leads.json' which resolves relative to /dashboard/
# So it tries to fetch /dashboard/data/leads.json which doesn't exist
# The actual leads.json is at /data/leads.json

# Fix: change the fetch path from 'data/leads.json' to '../data/leads.json'
# OR better: move index.html to root so it's at /index.html

with open('/workspace/dashboard/index.html', 'r') as f:
    html = f.read()

# Fix the fetch path - when served from /dashboard/index.html, 
# data/leads.json is at ../data/leads.json
html = html.replace("fetch('data/leads.json", "fetch('../data/leads.json")
html = html.replace("fetch('data/leads.json", "fetch('../data/leads.json")

# Also need to update any other relative paths
# The CSS/JS is inline so no other paths to fix

with open('/workspace/dashboard/index.html', 'w') as f:
    f.write(html)

print("Fixed fetch path from 'data/leads.json' to '../data/leads.json'")
print("This is correct when dashboard/index.html is served from /dashboard/ path")

# Also update the workflow to copy index.html to root
with open('/workspace/.github/workflows/deploy.yml', 'r') as f:
    workflow = f.read()

# The workflow copies dashboard/* to _site/ but index.html should be at root
# Let's check current workflow copy logic
if 'cp -r dashboard/* _site/' in workflow:
    print("\nWorkflow copies dashboard/* to _site/")
    print("This means index.html ends up at _site/index.html (root)")
    print("But the fetch path 'data/leads.json' would be relative to root - CORRECT")
    print("Wait - the fetch_url showed the page at /dashboard/index.html")
    print("This means the workflow might be copying differently")
    
# Actually, looking at the workflow:
# cp -r dashboard/* _site/  -> puts index.html at _site/index.html
# cp -r data _site/        -> puts data at _site/data/
# So the root index.html should fetch from data/leads.json correctly
# But the fetch_url showed the page at /dashboard/index.html
# This suggests there's also a copy at /dashboard/index.html

# Let me check if there's an index.html at root too
print("\nLet me check if root index.html exists...")
