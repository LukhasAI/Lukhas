#!/usr/bin/env python3
"""
Import Health Checker

Validates that all imports work correctly after directory consolidation.
Tests both old (deprecated) and new import paths.

Usage:
    python3 scripts/consolidation/check_import_health.py
    python3 scripts/consolidation/check_import_health.py --verbose
"""

import argparse
import importlib
import sys
import warnings
from typing import Tuple

# Import paths to test
IMPORT_TESTS = [
    # MATRIZ (uppercase - canonical)
    ("MATRIZ", "MATRIZ core module"),
    ("MATRIZ.consciousness", "MATRIZ consciousness module"),
    ("MATRIZ.adapters", "MATRIZ adapters"),
    ("MATRIZ.runtime", "MATRIZ runtime"),
    ("MATRIZ.nodes", "MATRIZ nodes"),

    # matriz (lowercase - compatibility shim, should show deprecation)
    ("matriz", "matriz compatibility shim"),

    # Core modules
    ("core", "Core module"),
    ("lukhas", "LUKHAS production module"),

    # Labs
    ("labs.consciousness.dream", "Dream synthesis (new location)"),

    # Bio
    ("bio", "Bio-inspired systems"),

    # Governance
    ("governance", "Governance module"),
]


def test_import(module_name: str, description: str, verbose: bool = False) -> Tuple[bool, str]:
    """
    Test if a module can be imported.

    Returns:
        (success, message)
    """
    try:
        # Capture warnings for deprecated imports
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            module = importlib.import_module(module_name)

            # Check for deprecation warnings
            if w:
                deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
                if deprecation_warnings:
                    msg = f"DeprecationWarning: {deprecation_warnings[0].message}"
                    return True, msg

            # Success with no warnings
            if verbose:
                return True, f"Module found at: {module.__file__ if hasattr(module, '__file__') else 'built-in'}"
            return True, "OK"

    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"Unexpected error: {type(e).__name__}: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Check import health after directory consolidation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with module locations')
    parser.add_argument('--fail-on-deprecation', action='store_true', help='Fail if deprecation warnings found')

    args = parser.parse_args()

    print("=" * 70)
    print("Import Health Check")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    deprecated = 0

    for module_name, description in IMPORT_TESTS:
        success, message = test_import(module_name, description, args.verbose)

        if success:
            if "DeprecationWarning" in message:
                status = "⚠️  DEPRECATED"
                deprecated += 1
                color_start = "\033[1;33m"  # Yellow
            else:
                status = "✅ PASS"
                passed += 1
                color_start = "\033[0;32m"  # Green
        else:
            status = "❌ FAIL"
            failed += 1
            color_start = "\033[0;31m"  # Red

        color_end = "\033[0m"

        print(f"{color_start}{status}{color_end} {module_name:<30} {description}")

        if args.verbose or not success or "DeprecationWarning" in message:
            print(f"     {message}")
            print()

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Passed:     {passed}")
    print(f"Failed:     {failed}")
    print(f"Deprecated: {deprecated}")
    print()

    if failed > 0:
        print("❌ Import health check FAILED")
        print("   Some modules could not be imported")
        print("   Review errors above and fix import paths")
        print()
        print("Tip: Run isolated validation in a worktree (recommended):")
        print("  bash scripts/run_lane_guard_worktree.sh")
        print("This creates a venv, installs minimal deps, and runs import-health.")
        print("If running locally, ensure PYTHONPATH includes repo root and install import-linter:")
        print("  python3 -m pip install import-linter")
        return 1

    if deprecated > 0 and args.fail_on_deprecation:
        print("⚠️  Import health check FAILED (deprecation warnings)")
        print("   Deprecated imports found")
        print("   Update code to use new import paths")
        return 1

    if deprecated > 0:
        print("✅ Import health check PASSED (with deprecation warnings)")
        print("   All imports work, but some use deprecated paths")
        print("   Consider updating deprecated imports:")
        print("   - matriz → MATRIZ")
        print("   - dream → labs.consciousness.dream.synthesis")
        return 0

    print("✅ Import health check PASSED")
    print("   All imports working correctly")
    return 0


if __name__ == '__main__':
    sys.exit(main())
