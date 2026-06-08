#!/usr/bin/env python3
"""Test all scrapers to see what data they actually return."""
import json
import sys
import os
sys.path.insert(0, '/workspace/scrapers')

# Import all scrapers
from duval_official_records import DuvalOfficialRecordsScraper
from duval_court_records import DuvalCourtRecordsScraper
from duval_foreclosure_sales import DuvalForeclosureSalesScraper
from duval_tax_deed_sales import DuvalTaxDeedSalesScraper
from duval_parcel_master import DuvalPropertyAppraiserScraper
from duval_tax_collector import DuvalTaxCollectorScraper
from duval_gis import DuvalGISScraper
from duval_code_enforcement import DuvalCodeEnforcementScraper

config = {'source_url': 'https://or.duvalclerk.com/'}

results = {}

print("=" * 60)
print("Testing all scrapers")
print("=" * 60)

# Test Official Records
print("\n1. Official Records (or.duvalclerk.com)")
try:
    scraper = DuvalOfficialRecordsScraper(config)
    result = scraper.refresh(days_back=30)
    results['official_records'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Errors: {result['errors']}")
    if result['new_records']:
        print(f"   Sample record: {json.dumps(result['new_records'][0], indent=2)[:200]}...")
except Exception as e:
    print(f"   ERROR: {e}")
    results['official_records'] = {'error': str(e)}

# Test Court Records
print("\n2. Court Records (core.duvalclerk.com)")
try:
    scraper = DuvalCourtRecordsScraper(config)
    result = scraper.refresh(days_back=30)
    results['court_records'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Errors: {result['errors']}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['court_records'] = {'error': str(e)}

# Test Foreclosure Sales
print("\n3. Foreclosure Sales (duval.realforeclose.com)")
try:
    scraper = DuvalForeclosureSalesScraper(config)
    result = scraper.refresh(days_ahead=30)
    results['foreclosure_sales'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Sale dates found: {result.get('sale_dates_found', 0)}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['foreclosure_sales'] = {'error': str(e)}

# Test Tax Deed Sales
print("\n4. Tax Deed Sales (duval.realtaxdeed.com)")
try:
    scraper = DuvalTaxDeedSalesScraper(config)
    result = scraper.refresh()
    results['tax_deed_sales'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Sale dates found: {result.get('sale_dates_found', 0)}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['tax_deed_sales'] = {'error': str(e)}

# Test Parcel Master
print("\n5. Parcel Master (paopropertysearch.coj.net)")
try:
    scraper = DuvalPropertyAppraiserScraper(config)
    result = scraper.refresh()
    results['parcel_master'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Note: {result.get('note', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['parcel_master'] = {'error': str(e)}

# Test Tax Collector
print("\n6. Tax Collector (tclieninfo.coj.net)")
try:
    scraper = DuvalTaxCollectorScraper(config)
    result = scraper.refresh()
    results['tax_collector'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Note: {result.get('note', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['tax_collector'] = {'error': str(e)}

# Test GIS
print("\n7. GIS (maps.coj.net/duvalproperty)")
try:
    scraper = DuvalGISScraper(config)
    result = scraper.refresh()
    results['gis_mapping'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Services discovered: {result.get('services_discovered', 0)}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['gis_mapping'] = {'error': str(e)}

# Test Code Enforcement
print("\n8. Code Enforcement (PRR)")
try:
    scraper = DuvalCodeEnforcementScraper(config)
    result = scraper.refresh()
    results['code_enforcement'] = result
    print(f"   Records fetched: {result['records_fetched']}")
    print(f"   Note: {result.get('note', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")
    results['code_enforcement'] = {'error': str(e)}

# Save results
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
for source, result in results.items():
    if 'error' in result:
        print(f"  {source}: ERROR - {result['error']}")
    else:
        print(f"  {source}: {result.get('records_fetched', 0)} records")

with open('/workspace/test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to /workspace/test_results.json")
