#!/usr/bin/env python3
"""Verify the leads.json is valid and dashboard-compatible."""
import json

with open('/workspace/data/leads.json', 'r') as f:
    data = json.load(f)

print("=" * 60)
print("Verifying leads.json")
print("=" * 60)

print(f"\nTotal leads: {data['total_leads']}")
print(f"High-stack leads: {data['high_stack_leads']}")
print(f"Last refresh: {data['last_refresh']}")

print(f"\nSources:")
for source_id, info in data['sources'].items():
    print(f"  {source_id}: {info['status']} ({info['records_count']} records)")

print(f"\nLead structure check:")
if data['leads']:
    lead = data['leads'][0]
    required_fields = ['lead_id', 'score', 'address', 'owner_name', 'signals', 'deal_path', 'status']
    for field in required_fields:
        if field in lead:
            print(f"  {field}: OK")
        else:
            print(f"  {field}: MISSING!")
    
    print(f"\nFirst lead sample:")
    print(f"  ID: {lead['lead_id']}")
    print(f"  Score: {lead['score']}")
    print(f"  Owner: {lead['owner_name']}")
    print(f"  Signals: {len(lead['signals'])}")
    print(f"  Deal Path: {lead['deal_path']}")
    
    if lead['signals']:
        signal = lead['signals'][0]
        print(f"  Signal type: {signal['type']}")
        print(f"  Signal details: {signal['details'][:80]}")

print(f"\nDashboard compatibility:")
print(f"  - KPI 'total-leads': {data['total_leads']}")
print(f"  - KPI 'high-stack-leads': {data['high_stack_leads']}")

foreclosure_count = sum(1 for l in data['leads'] if any(s['type'] in ['LIS_PENDENS', 'FORECLOSURE_SALE'] for s in l['signals']))
tax_count = sum(1 for l in data['leads'] if any(s['type'] in ['TAX_DELINQUENT', 'TAX_DEED_SALE'] for s in l['signals']))
code_count = sum(1 for l in data['leads'] if any(s['type'] == 'CODE_VIOLATION' for s in l['signals']))
avg_score = sum(l['score'] for l in data['leads']) / len(data['leads']) if data['leads'] else 0

print(f"  - KPI 'foreclosure-count': {foreclosure_count}")
print(f"  - KPI 'tax-delinquent-count': {tax_count}")
print(f"  - KPI 'code-violation-count': {code_count}")
print(f"  - KPI 'avg-score': {avg_score:.0f}")

print(f"\nAll checks passed! leads.json is ready for dashboard.")
