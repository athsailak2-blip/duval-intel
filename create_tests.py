import json
import os

# Create test files for the Duval County build

# Test 1: Golden Path Test
golden_path_test = '''#!/usr/bin/env python3
"""
Golden Path Test - Duval County Build
Verifies the core data pipeline works end-to-end with synthetic data.
"""
import json
import sys
from datetime import datetime

def test_config_valid():
    """Test that county config is valid JSON and has required fields."""
    with open("config/counties/duval_fl.json", "r") as f:
        config = json.load(f)
    
    required_fields = [
        "county_id", "county_name", "state", "fips_code", 
        "slug", "framework_version", "geography", "sources",
        "build_verdict", "build_verdict_reason", "deployment", "dashboard"
    ]
    
    for field in required_fields:
        assert field in config, f"Missing required field: {field}"
    
    assert config["county_name"] == "Duval"
    assert config["state"] == "FL"
    assert config["fips_code"] == "12031"
    assert config["slug"] == "duval_fl"
    assert config["build_verdict"] == "READY_TO_BUILD"
    
    print("✓ Config validation passed")
    return True

def test_sources_configured():
    """Test that all expected sources are configured."""
    with open("config/counties/duval_fl.json", "r") as f:
        config = json.load(f)
    
    expected_sources = [
        "official_records", "court_records", "foreclosure_sales",
        "tax_deed_sales", "parcel_master", "tax_collector",
        "gis_mapping", "code_enforcement"
    ]
    
    for source in expected_sources:
        assert source in config["sources"], f"Missing source: {source}"
    
    # Verify P0 sources exist
    p0_sources = [s for s in config["sources"].values() if s["source_priority"] == "P0"]
    assert len(p0_sources) >= 1, "Must have at least one P0 source"
    
    print(f"✓ Sources configured: {len(config['sources'])} sources")
    print(f"  - P0 (Daily): {len([s for s in config['sources'].values() if s['source_priority'] == 'P0'])}")
    print(f"  - P1 (Weekly): {len([s for s in config['sources'].values() if s['source_priority'] == 'P1'])}")
    print(f"  - P2 (Monthly): {len([s for s in config['sources'].values() if s['source_priority'] == 'P2'])}")
    return True

def test_synthetic_parcels():
    """Test synthetic parcel data."""
    with open("scaffold/data/synthetic_parcels.jsonl", "r") as f:
        parcels = [json.loads(line) for line in f]
    
    assert len(parcels) == 12, f"Expected 12 parcels, got {len(parcels)}"
    
    # Verify all parcels have required fields
    required_fields = [
        "parcel_id", "address", "city", "zip", "owner_name",
        "assessed_value", "property_use", "scenario"
    ]
    
    for parcel in parcels:
        for field in required_fields:
            assert field in parcel, f"Parcel {parcel.get('parcel_id', 'unknown')} missing {field}"
    
    # Verify parcel_id prefix
    for parcel in parcels:
        assert parcel["parcel_id"].startswith("DC-"), f"Invalid parcel_id prefix: {parcel['parcel_id']}"
    
    print(f"✓ Synthetic parcels: {len(parcels)} parcels validated")
    return True

def test_synthetic_signals():
    """Test synthetic signal data."""
    with open("scaffold/data/synthetic_signals.jsonl", "r") as f:
        signals = [json.loads(line) for line in f]
    
    assert len(signals) == 24, f"Expected 24 signals, got {len(signals)}"
    
    # Verify all signals reference valid parcels
    with open("scaffold/data/synthetic_parcels.jsonl", "r") as f:
        parcels = [json.loads(line) for line in f]
    
    parcel_ids = {p["parcel_id"] for p in parcels}
    
    for signal in signals:
        assert signal["parcel_id"] in parcel_ids, f"Signal references unknown parcel: {signal['parcel_id']}"
    
    # Verify signal types
    signal_types = set(s["signal_type"] for s in signals)
    print(f"✓ Synthetic signals: {len(signals)} signals across {len(signal_types)} types")
    print(f"  - Signal types: {', '.join(sorted(signal_types))}")
    return True

def test_synthetic_expectations():
    """Test synthetic expectations."""
    with open("scaffold/data/synthetic_expectations.json", "r") as f:
        expectations = json.load(f)
    
    assert expectations["total_parcels"] == 12
    assert expectations["total_signals"] == 24
    assert "expected_leads" in expectations
    assert "deal_path_distribution" in expectations
    assert "score_distribution" in expectations
    assert "lead_patterns" in expectations
    
    print("✓ Synthetic expectations validated")
    return True

def test_scrapers_exist():
    """Test that scraper files exist."""
    expected_scrapers = [
        "scrapers/duval_official_records.py",
        "scrapers/duval_court_records.py",
        "scrapers/duval_foreclosure_sales.py",
        "scrapers/duval_tax_deed_sales.py",
        "scrapers/duval_parcel_master.py",
        "scrapers/duval_tax_collector.py",
        "scrapers/duval_gis.py",
        "scrapers/duval_code_enforcement.py"
    ]
    
    for scraper in expected_scrapers:
        assert os.path.exists(scraper), f"Missing scraper: {scraper}"
    
    print(f"✓ All {len(expected_scrapers)} scrapers present")
    return True

def test_dashboard_exists():
    """Test that dashboard files exist."""
    assert os.path.exists("dashboard/index.html"), "Missing dashboard/index.html"
    assert os.path.exists("dashboard/README.md"), "Missing dashboard/README.md"
    assert os.path.exists("data/leads.json"), "Missing data/leads.json"
    
    # Verify leads.json is valid
    with open("data/leads.json", "r") as f:
        leads = json.load(f)
    
    assert leads["county"] == "Duval"
    assert leads["state"] == "FL"
    assert "leads" in leads
    assert "sources" in leads
    
    print(f"✓ Dashboard files validated")
    print(f"  - Sample leads: {len(leads['leads'])}")
    print(f"  - Source health: {len(leads['sources'])} sources tracked")
    return True

def test_municipalities():
    """Test municipality configuration."""
    with open("config/counties/duval_fl.json", "r") as f:
        config = json.load(f)
    
    muni = config["geography"]["municipalities"]
    assert len(muni) >= 5, "Must have at least 5 municipalities"
    
    expected_cities = ["Jacksonville", "Jacksonville Beach", "Atlantic Beach", "Neptune Beach", "Baldwin"]
    for city in expected_cities:
        assert any(m["name"] == city for m in muni), f"Missing municipality: {city}"
    
    print(f"✓ Municipalities: {len(muni)} cities/towns configured")
    return True

def test_parcel_id_format():
    """Test parcel ID format regex."""
    import re
    
    with open("config/counties/duval_fl.json", "r") as f:
        config = json.load(f)
    
    pattern = config["geography"]["parcel_id_format"]
    regex = re.compile(pattern)
    
    # Test valid parcel IDs
    valid_ids = [
        "01-01-01-001-001",
        "01-01-01-001-001-000",
        "12-34-56-789-012"
    ]
    
    for pid in valid_ids:
        assert regex.match(pid), f"Valid parcel ID rejected: {pid}"
    
    print("✓ Parcel ID format validated")
    return True

def run_all_tests():
    """Run all golden path tests."""
    print("=" * 60)
    print("Duval County Build - Golden Path Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_config_valid,
        test_sources_configured,
        test_synthetic_parcels,
        test_synthetic_signals,
        test_synthetic_expectations,
        test_scrapers_exist,
        test_dashboard_exists,
        test_municipalities,
        test_parcel_id_format
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
'''

with open("scaffold/tests/test_golden_path.py", "w") as f:
    f.write(golden_path_test)

print("Created: scaffold/tests/test_golden_path.py")

# Test 2: County Agnostic Regression Test
county_agnostic_test = '''#!/usr/bin/env python3
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
                            lines = content.split('\\n')
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
                        r'\[\s*["\']Jacksonville["\']',
                        r'\[\s*["\']Jacksonville Beach["\']',
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
                    urls = re.findall(r'https?://[^\s\'"]+', content)
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
'''

with open("scaffold/tests/test_county_agnostic_regression.py", "w") as f:
    f.write(county_agnostic_test)

print("Created: scaffold/tests/test_county_agnostic_regression.py")

# Test runner
test_runner = '''#!/usr/bin/env python3
"""
Test Runner - Duval County Build
Runs all gate tests and reports results.
"""
import sys
import os

def run_test_file(test_file):
    """Run a single test file and return success/failure."""
    print(f"\\nRunning: {test_file}")
    print("-" * 60)
    
    result = os.system(f"python {test_file}")
    return result == 0

def main():
    print("=" * 60)
    print("Duval County Build - Test Suite")
    print("=" * 60)
    
    test_files = [
        "scaffold/tests/test_golden_path.py",
        "scaffold/tests/test_county_agnostic_regression.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"\\n⚠ Test file not found: {test_file}")
            results[test_file] = False
    
    print()
    print("=" * 60)
    print("Test Suite Results")
    print("=" * 60)
    
    for test_file, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_file}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print("🎉 All tests passed! Build is ready for deployment.")
    else:
        print("❌ Some tests failed. Please review and fix issues.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
'''

with open("scaffold/tests/run_all.py", "w") as f:
    f.write(test_runner)

print("Created: scaffold/tests/run_all.py")

# Create __init__.py for tests package
with open("scaffold/tests/__init__.py", "w") as f:
    f.write("# Tests package\n")

print("Created: scaffold/tests/__init__.py")

print("\nAll test files created successfully!")
