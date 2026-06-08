import os

# Read the problematic file and fix it properly
with open("scaffold/tests/test_county_agnostic_regression.py", "r") as f:
    lines = f.readlines()

# Find and fix line 68 (0-indexed: 67)
for i, line in enumerate(lines):
    if "Jacksonville" in line and "r'" in line:
        # Replace the problematic line with a simpler pattern
        lines[i] = "                        r'Jacksonville',\n"
        print(f"Fixed line {i+1}: {lines[i].strip()}")
    elif "Jacksonville Beach" in line and "r'" in line:
        lines[i] = "                        r'Jacksonville Beach',\n"
        print(f"Fixed line {i+1}: {lines[i].strip()}")

with open("scaffold/tests/test_county_agnostic_regression.py", "w") as f:
    f.writelines(lines)

print("\nFixed county agnostic test file")

# Run the tests again
print("\n" + "="*60)
print("Running tests again...")
print("="*60 + "\n")

os.system("python scaffold/tests/run_all.py")
