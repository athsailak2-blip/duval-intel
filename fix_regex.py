import os

# Read the problematic file and fix all regex issues
with open("scaffold/tests/test_county_agnostic_regression.py", "r") as f:
    content = f.read()

# Fix all regex patterns with quote issues
# The issue is with r'https?://[^\s'"]+' - the single quote inside the regex breaks the string
content = content.replace(
    r"r'https?://[^\s'\"]+', content)",
    r"r'https?://[^\s\"]+', content)"
)

# Also fix any other problematic patterns
content = content.replace(
    r"r'https?://[^\s'\"]+'",
    r"r'https?://[^\s\"]+'"
)

with open("scaffold/tests/test_county_agnostic_regression.py", "w") as f:
    f.write(content)

print("Fixed all regex patterns in test file")

# Run the tests again
print("\n" + "="*60)
print("Running tests again...")
print("="*60 + "\n")

os.system("python scaffold/tests/run_all.py")
