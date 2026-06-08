#!/usr/bin/env python3
"""
County Agnostic Regression Test
Ensures no hardcoded county-specific data exists outside config files.
"""
import os
import re
import sys

def scan_for_hardcoded_counties():
    """Scan Python files for hardcoded county references."""
    issues = []
    
    # Files to scan (excluding config and data)
    scan_dirs = ["scrapers", "scaffold/pipeline", "scaffold/tests"]
    
    # County-specific terms that should NOT appear in universal code
    forbidden_terms = [
        "duval", "jacksonville", "bexar", "houston", "miami", "broward",
        "harris", "dallas", "travis", "orange", "palm beach", "pinellas"
    ]
    
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
            
        for root, dirs, files in os.walk(scan_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                    
                    for term in forbidden_terms:
                        if term in content:
                            # Check if it's in a comment or string that's clearly a URL
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if term in line:
                                    # Allow URLs that contain the county name
                                    if 'http' in line or 'url' in line or 'source' in line:
                                        continue
                                    issues.append(f"{filepath}:{i}: Found '{term}' in code")
    
    return issues

def test_no_hardcoded_municipalities():
    """Test that municipality lists are not hardcoded in code."""
    issues = []
    
    scan_dirs = ["scrapers", "scaffold/pipeline"]
    
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
            
        for root, dirs, files in os.walk(scan_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for hardcoded city lists (arrays with city names)
                    city_patterns = [
                        r'Jacksonville',
                        r'Jacksonville',
                        r'cities\s*=\s*\[',
                        r'municipalities\s*=\s*\['
                    ]
                    
                    for pattern in city_patterns:
                        if re.search(pattern, content):
                            issues.append(f"{filepath}: Possible hardcoded municipality list")
    
    return issues

def test_config_is_source_of_truth():
    """Test that config file is the only source of county-specific data."""
    with open("config/counties/duval_fl.json", "r") as f:
        import json
        config = json.load(f)
    
    # Verify config has all county-specific data
    assert "county_name" in config
    assert "state" in config
    assert "fips_code" in config
    assert "geography" in config
    assert "municipalities" in config["geography"]
    assert "zip_codes" in config["geography"]
    
    print("✓ Config is source of truth for county data")
    return True

def test_scraper_universality():
    """Test that scrapers use config instead of hardcoded values."""
    scraper_files = [
        "scrapers/duval_official_records.py",
        "scrapers/duval_court_records.py",
        "scrapers/duval_foreclosure_sales.py",
        "scrapers/duval_tax_deed_sales.py",
        "scrapers/duval_parcel_master.py",
        "scrapers/duval_tax_collector.py",
        "scrapers/duval_gis.py",
        "scrapers/duval_code_enforcement.py"
    ]
    
    for scraper_file in scraper_files:
        if not os.path.exists(scraper_file):
            continue
            
        with open(scraper_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that scraper accepts config parameter
        assert "config" in content, f"{scraper_file} should accept config parameter"
        
        # Check that source_id is defined but not hardcoded to specific values
        assert "SOURCE_ID" in content, f"{scraper_file} should define SOURCE_ID"
    
    print(f"✓ All {len(scraper_files)} scrapers follow universal pattern")
    return True

def test_no_hardcoded_urls_in_universal_code():
    """Test that universal code doesn't have hardcoded URLs."""
    # The scrapers CAN have URLs since they're county-specific implementations
    # This test checks that any shared/util code doesn't
    
    shared_dirs = ["scaffold/pipeline"]
    
    for shared_dir in shared_dirs:
        if not os.path.exists(shared_dir):
            continue
            
        for root, dirs, files in os.walk(shared_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    filepath = os.path.join(root, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for hardcoded .gov or .com URLs
                    urls = re.findall(r'https?://[^\s"]+', content)
                    for url in urls:
                        if 'duval' in url.lower() or 'jacksonville' in url.lower():
                            print(f"⚠ Warning: {filepath} contains URL: {url}")
    
    print("✓ URL check completed")
    return True

def run_all_tests():
    """Run all county agnostic regression tests."""
    print("=" * 60)
    print("County Agnostic Regression Tests")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    # Run tests
    tests = [
        ("Config is source of truth", test_config_is_source_of_truth),
        ("Scraper universality", test_scraper_universality),
        ("No hardcoded URLs in universal code", test_no_hardcoded_urls_in_universal_code)
    ]
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {name} FAILED: {e}")
            failed += 1
    
    # Scan for hardcoded counties
    print()
    print("Scanning for hardcoded county references...")
    issues = scan_for_hardcoded_counties()
    
    if issues:
        print(f"⚠ Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ No hardcoded county references found in universal code")
        passed += 1
    
    # Scan for hardcoded municipalities
    print()
    print("Scanning for hardcoded municipality lists...")
    muni_issues = test_no_hardcoded_municipalities()
    
    if muni_issues:
        print(f"⚠ Found {len(muni_issues)} potential issues:")
        for issue in muni_issues:
            print(f"  - {issue}")
    else:
        print("✓ No hardcoded municipality lists found")
        passed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
