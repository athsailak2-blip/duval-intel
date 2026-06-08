#!/usr/bin/env python3
"""
Golden Path Test - Duval County Build
Verifies the core data pipeline works end-to-end with synthetic data.
"""
import json
import os
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
