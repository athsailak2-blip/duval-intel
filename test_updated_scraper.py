#!/usr/bin/env python3
"""Test the updated scraper."""
import sys
sys.path.insert(0, '/workspace/scrapers')

from duval_official_records import DuvalOfficialRecordsScraper

config = {'source_url': 'https://or.duvalclerk.com/'}
scraper = DuvalOfficialRecordsScraper(config)

print("Testing updated Official Records scraper...")
print("=" * 60)

# Test with just LIS PENDENS for speed
result = scraper.search_by_date_range('2026-05-01', '2026-06-08', ['LIS PENDENS'])

print(f"\nFound {len(result)} records")
if result:
    print("\nFirst record:")
    import json
    print(json.dumps(result[0], indent=2))
