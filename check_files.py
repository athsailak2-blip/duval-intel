import os, glob

# Check all files
scrapers = glob.glob('/workspace/scrapers/*.py')
print(f"Scrapers: {len(scrapers)}")
for s in scrapers:
    print(f"  {os.path.basename(s)}: {os.path.getsize(s)} bytes")

files = [
    '/workspace/.github/workflows/deploy.yml',
    '/workspace/data/leads.json',
    '/workspace/dashboard/index.html',
    '/workspace/config/counties/duval_fl.json'
]
print("\nOther files:")
for f in files:
    if os.path.exists(f):
        print(f"  {os.path.basename(f)}: {os.path.getsize(f)} bytes")
    else:
        print(f"  {os.path.basename(f)}: MISSING")
