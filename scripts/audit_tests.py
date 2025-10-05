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

    # Use pytest directly (CI environments don't have .venv)
    import os
    if os.path.exists(".venv/bin/pytest"):
        pytest_cmd = ".venv/bin/pytest"
    else:
        pytest_cmd = "pytest"

    # Run pytest collection check for T4 hardening test directories only
    test_dirs = [
        "tests/unit/metrics/",
        "tests/capabilities/",
        "tests/e2e/consciousness/test_consciousness_emergence.py"
    ]

    # Check each directory individually for focused audit
    all_results = []
    for test_dir in test_dirs:
        result = subprocess.run(
            [pytest_cmd, "--collect-only", "-q", test_dir],
            capture_output=True,
            text=True
        )
        all_results.append((test_dir, result))

    # Check if any individual result failed
    failed_dirs = []
    for test_dir, result in all_results:
        if result.returncode != 0:
            failed_dirs.append((test_dir, result))

    if failed_dirs:
        print("❌ Test collection errors found in T4 directories")
        for test_dir, result in failed_dirs:
            print(f"\n--- {test_dir} ---")
            print(result.stdout)
            print(result.stderr)
        sys.exit(1)

    # Use the last result for the main check (this is mostly for compatibility)
    result = all_results[-1][1] if all_results else result

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
