#!/usr/bin/env python3
"""
Test runner for LUKHAS Unified Grammar test suite.

Run all Unified Grammar tests and generate a report.
"""

import sys
from pathlib import Path

import pytest


def run_unified_grammar_tests():
    """Run all Unified Grammar tests."""
    print("🧪 LUKHAS Unified Grammar Test Suite")
    print("=" * 70)
    print()

    # Test categories
    test_categories = [
        ("Base Module Tests", "test_base_module.py"),
        ("Symbolic Vocabulary Tests", "test_symbolic_vocabulary.py"),
        ("Module Integration Tests", "test_module_integration.py"),
        ("Grammar Compliance Tests", "test_grammar_compliance.py"),
    ]

    # Get test directory
    test_dir = Path(__file__).parent

    # Run each test category
    all_passed = True
    results = []

    for category_name, test_file in test_categories:
        print(f"\n📋 Running {category_name}...")
        print("-" * 50)

        test_path = test_dir / test_file

        # Run tests
        result = pytest.main([str(test_path), "-v", "--tb=short", "--no-header", "-q"])

        passed = result == 0
        all_passed = all_passed and passed

        status = "✅ PASSED" if passed else "❌ FAILED"
        results.append((category_name, status))
        print(f"\n{status} - {category_name}")

    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    for category, status in results:
        print(f"{status} {category}")

    print("\n" + "=" * 70)

    if all_passed:
        print("✨ All Unified Grammar tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1


def run_specific_test(test_name):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 70)

    test_dir = Path(__file__).parent
    test_path = test_dir / test_name

    if not test_path.exists():
        print(f"❌ Test file not found: {test_name}")
        return 1

    result = pytest.main([str(test_path), "-v", "--tb=short"])

    return result


def generate_coverage_report():
    """Generate test coverage report."""
    print("📊 Generating coverage report...")

    test_dir = Path(__file__).parent

    result = pytest.main(
        [
            str(test_dir),
            "--cov=lukhas_unified_grammar",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html",
            "-q",
        ]
    )

    if result == 0:
        print("✅ Coverage report generated in coverage_html/")
    else:
        print("❌ Failed to generate coverage report")

    return result


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Unified Grammar Test Runner")
    parser.add_argument("--test", help="Run specific test file", type=str)
    parser.add_argument(
        "--coverage", help="Generate coverage report", action="store_true"
    )
    parser.add_argument(
        "--quick", help="Run quick smoke tests only", action="store_true"
    )

    args = parser.parse_args()

    if args.coverage:
        return generate_coverage_report()
    elif args.test:
        return run_specific_test(args.test)
    elif args.quick:
        # Run just compliance tests as smoke test
        return run_specific_test("test_grammar_compliance.py")
    else:
        return run_unified_grammar_tests()


if __name__ == "__main__":
    sys.exit(main())
