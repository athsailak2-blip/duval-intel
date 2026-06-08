import requests

# The dashboard still shows "Loading leads data..." which means the JavaScript
# is not executing or the fetch is failing silently
# Let me check the actual HTML source to see what's happening

USERNAME = "athsailak2-blip"
REPO_NAME = "duval-intel"

dash_resp = requests.get(f"https://{USERNAME}.github.io/{REPO_NAME}/", timeout=30)
html = dash_resp.text

# Check if the loadData function exists
if 'function loadData()' in html:
    print("✅ loadData function exists in HTML")
else:
    print("❌ loadData function NOT found - old version still deployed")

# Check if there's a script error or syntax issue
# Look for the script tag
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)
if script_start > 0 and script_end > 0:
    script = html[script_start:script_end+9]
    print(f"\nScript tag found: {len(script)} characters")
    
    # Check for common JS issues
    if '=&gt;' in script or '&gt;' in script or '&lt;' in script:
        print("⚠️ HTML entities found in JS - may cause syntax errors")
    
    if 'sampleLeads' in script:
        print("✅ sampleLeads variable referenced")
    
    if 'fetch(' in script:
        print("✅ fetch() call found")
    else:
        print("❌ No fetch() call found")

# Check if the page has the old hardcoded data
if 'LEAD-001' in html:
    print("\n⚠️ Old hardcoded LEAD-001 found in HTML - may be cached/old version")
else:
    print("\n✅ No hardcoded LEAD-001 - new version")

# Check the very end of the HTML for the script
last_script = html.rfind('<script>')
if last_script > 0:
    end_script = html.find('</script>', last_script)
    if end_script > 0:
        last_js = html[last_script:end_script+9]
        print(f"\nLast script tag: {len(last_js)} chars")
        if 'loadData()' in last_js:
            print("✅ loadData() in last script")
        elif 'loadData' in last_js:
            print("⚠️ loadData referenced but not called")
        else:
            print("❌ No loadData in last script")

# Check if there's a closing body/html tag after the script
if html.rfind('</html>') > html.rfind('</script>'):
    print("✅ HTML structure is valid (</html> after </script>)")
else:
    print("⚠️ HTML structure may be broken")
