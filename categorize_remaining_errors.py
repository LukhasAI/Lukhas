#!/usr/bin/env python3
"""Categorize remaining pytest collection errors."""

import subprocess
import re
from collections import defaultdict

# Run pytest collection
result = subprocess.run(
    ["python3", "-m", "pytest", "tests/unit", "--collect-only",
     "--continue-on-collection-errors", "--maxfail=1000"],
    capture_output=True,
    text=True,
    cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas"
)

output = result.stderr + result.stdout

# Extract error sections
error_pattern = r"ERROR collecting (.+?)\n(.+?)(?=ERROR collecting|short test summary|$)"
errors = re.findall(error_pattern, output, re.DOTALL)

# Categorize by error type
by_error_type = defaultdict(list)
by_module = defaultdict(list)

for file_path, error_text in errors:
    file_path = file_path.strip()

    # Extract error type
    if "ModuleNotFoundError" in error_text and "No module named" in error_text:
        match = re.search(r"No module named '([^']+)'", error_text)
        if match:
            module = match.group(1)
            by_error_type[f"ModuleNotFoundError: {module}"].append(file_path)
            by_module[module].append(file_path)
    elif "ImportError" in error_text:
        if "cannot import name" in error_text:
            match = re.search(r"cannot import name '([^']+)'", error_text)
            if match:
                by_error_type[f"ImportError: cannot import {match.group(1)}"].append(file_path)
        else:
            by_error_type["ImportError: other"].append(file_path)
    elif "SyntaxError" in error_text:
        by_error_type["SyntaxError"].append(file_path)
    elif "IndentationError" in error_text:
        by_error_type["IndentationError"].append(file_path)
    elif "not found in `markers` configuration" in error_text:
        match = re.search(r"'([^']+)' not found in", error_text)
        if match:
            by_error_type[f"pytest marker not configured: {match.group(1)}"].append(file_path)
    else:
        by_error_type["Other"].append(file_path)

print("=" * 80)
print(f"TOTAL ERRORS: {len(errors)}")
print("=" * 80)
print()

print("CATEGORIZATION BY ERROR TYPE:")
print("-" * 80)
for error_type in sorted(by_error_type.keys(), key=lambda x: -len(by_error_type[x])):
    files = by_error_type[error_type]
    print(f"\n{error_type} ({len(files)} files):")
    for f in sorted(files)[:5]:  # Show first 5
        print(f"  - {f}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")

if by_module:
    print("\n" + "=" * 80)
    print("MISSING MODULES (affecting multiple files):")
    print("-" * 80)
    for module in sorted(by_module.keys(), key=lambda x: -len(by_module[x])):
        if len(by_module[module]) > 1:
            print(f"\n'{module}' missing in {len(by_module[module])} files:")
            for f in sorted(by_module[module])[:3]:
                print(f"  - {f}")
            if len(by_module[module]) > 3:
                print(f"  ... and {len(by_module[module]) - 3} more")

print("\n" + "=" * 80)
