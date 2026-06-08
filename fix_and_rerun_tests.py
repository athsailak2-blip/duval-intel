import os

# Fix the golden path test - add missing import
with open("scaffold/tests/test_golden_path.py", "r") as f:
    content = f.read()

# Add os import at the top if missing
if "import os" not in content:
    content = content.replace("import sys", "import os\nimport sys")

with open("scaffold/tests/test_golden_path.py", "w") as f:
    f.write(content)

print("Fixed: Added os import to test_golden_path.py")

# Fix the county agnostic test - fix the regex syntax error
with open("scaffold/tests/test_county_agnostic_regression.py", "r") as f:
    content = f.read()

# Fix the broken regex pattern - use raw string properly
content = content.replace(
    r"r'\[\s*['\"]Jacksonville['\"]'",
    r"r'\[\s*\"Jacksonville\"'"
)

# Also fix the other similar patterns
content = content.replace(
    r"r'\[\s*['\"]Jacksonville Beach['\"]'",
    r"r'\[\s*\"Jacksonville Beach\"'"
)

with open("scaffold/tests/test_county_agnostic_regression.py", "w") as f:
    f.write(content)

print("Fixed: Regex syntax in test_county_agnostic_regression.py")

# Now run the tests again
print("\n" + "="*60)
print("Re-running tests...")
print("="*60 + "\n")

os.system("python scaffold/tests/run_all.py")
