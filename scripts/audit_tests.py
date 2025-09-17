#!/usr/bin/env python3
"""
Test Collection Audit Script
T4-Approved: Simple exit code validation only, no auto-fix

Usage:
    python scripts/audit_tests.py

Returns:
    0: No collection errors
    Non-zero: Collection errors found
"""
import subprocess
import sys

def main():
    """Audit test collection - exit code based validation only"""
    print("🔍 Auditing test collection...")

    # Try .venv/bin/pytest first, fallback to pytest
    pytest_cmd = ".venv/bin/pytest"
    try:
        # Check if .venv/bin/pytest exists
        result = subprocess.run([pytest_cmd, "--version"], capture_output=True)
        if result.returncode != 0:
            pytest_cmd = "pytest"
    except FileNotFoundError:
        pytest_cmd = "pytest"

    # Run pytest collection check
    result = subprocess.run(
        [pytest_cmd, "--collect-only", "-q"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Test collection errors found")
        print("Fix manually by analyzing root causes:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

    print("✅ No collection errors")
    return 0

if __name__ == "__main__":
    main()