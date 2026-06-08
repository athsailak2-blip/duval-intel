import os

# Read the file and find the exact problematic line
with open("scaffold/tests/test_county_agnostic_regression.py", "r") as f:
    lines = f.readlines()

# Find line 146 (0-indexed: 145)
for i in range(140, min(150, len(lines))):
    print(f"Line {i+1}: {repr(lines[i])}")

# Fix the specific problematic line
if len(lines) > 145:
    # Line 146 has the issue - replace with a simpler pattern
    lines[145] = "                    urls = re.findall(r'https?://[^\\s\"]+', content)\n"
    print(f"\nFixed line 146: {lines[145].strip()}")

with open("scaffold/tests/test_county_agnostic_regression.py", "w") as f:
    f.writelines(lines)

print("\nFixed line 146")

# Run the tests again
print("\n" + "="*60)
print("Running tests again...")
print("="*60 + "\n")

os.system("python scaffold/tests/run_all.py")
