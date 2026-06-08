#!/usr/bin/env python3
"""
Test Runner - Duval County Build
Runs all gate tests and reports results.
"""
import sys
import os

def run_test_file(test_file):
    """Run a single test file and return success/failure."""
    print(f"\nRunning: {test_file}")
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
            print(f"\n⚠ Test file not found: {test_file}")
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
