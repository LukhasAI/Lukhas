#!/usr/bin/env python3
"""
LUKHAS TODO Pattern Verification Script
Test removal patterns before execution to ensure safety.
"""

import re
import subprocess


def test_patterns_against_samples():
    """Test our removal patterns against known samples"""

    # Test samples with expected behavior
    test_cases = [
        # Completion references (SHOULD be removed)
        ("    # Addresses TODO 123: Memory management issue", "completion_references", True),
        ("// Implements TODO 456 for authentication", "completion_references", True),
        ("# TODO 789: this is still needed", "completion_references", False),  # Should NOT be removed
        # Symbol resolver duplicates (SHOULD be removed)
        ("# TODO(symbol-resolver): implement missing functionality", "symbol_resolver_duplicates", True),
        ("    # TODO(symbol-resolver): implement missing functionality", "symbol_resolver_duplicates", True),
        (
            "# TODO(symbol-resolver): implement advanced functionality",
            "symbol_resolver_duplicates",
            False,
        ),  # Different text
        # Streamlit stubs (SHOULD be removed)
        ("# TODO: Install or implement streamlit", "streamlit_stubs", True),
        ("    # TODO: Install or implement streamlit", "streamlit_stubs", True),
        ("# TODO: Configure streamlit dashboard", "streamlit_stubs", False),  # Different text
        # Consolidation stubs (SHOULD be removed)
        ("# TODO: Implement actual consolidation logic", "consolidation_stubs", True),
        ("    # TODO: Implement actual consolidation logic", "consolidation_stubs", True),
        ("# TODO: Implement better consolidation logic", "consolidation_stubs", False),  # Different text
        # Placeholder stubs (SHOULD be removed)
        ("    pass  # TODO: implement this", "placeholder_stubs", True),
        ("pass # TODO", "placeholder_stubs", True),
        ("pass  # NOTE: temporary", "placeholder_stubs", False),  # Not a TODO
        # Dependency stubs (SHOULD be removed)
        ("# TODO: Install numpy", "dependency_stubs", True),
        ("# TODO: Install or implement pandas", "dependency_stubs", True),
        ("# TODO: Optimize numpy usage", "dependency_stubs", False),  # Not installation
    ]

    # Define patterns (copied from main script)
    removal_patterns = {
        "completion_references": {
            "patterns": [
                r".*[Aa]ddresses TODO \d+.*\n",
                r".*[Ii]mplements TODO \d+.*\n",
                r".*[Cc]ompletes TODO \d+.*\n",
                r".*[Ff]ixes TODO \d+.*\n",
                r".*[Rr]esolves TODO \d+.*\n",
                r".*TODO \d+:.*implemented.*\n",
                r".*TODO \d+:.*completed.*\n",
                r".*TODO \d+ is now.*\n",
            ],
            "safety_check": lambda line: "address" in line.lower()
            or "implement" in line.lower()
            or "complete" in line.lower(),
        },
        "symbol_resolver_duplicates": {
            "patterns": [
                r"^[\s]*#?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
                r"^[\s]*\/\/?\s*TODO\(symbol-resolver\):\s*implement missing functionality\s*\n",
            ],
            "safety_check": lambda line: "symbol-resolver" in line and "implement missing functionality" in line,
        },
        "streamlit_stubs": {
            "patterns": [
                r"^[\s]*#\s*TODO:\s*Install or implement streamlit\s*\n",
                r"^[\s]*\/\/?\s*TODO:\s*Install or implement streamlit\s*\n",
            ],
            "safety_check": lambda line: "install or implement streamlit" in line.lower(),
        },
        "consolidation_stubs": {
            "patterns": [
                r"^[\s]*#?\s*TODO:\s*Implement actual consolidation logic\s*\n",
                r"^[\s]*\/\/?\s*TODO:\s*Implement actual consolidation logic\s*\n",
            ],
            "safety_check": lambda line: "implement actual consolidation logic" in line.lower(),
        },
        "placeholder_stubs": {
            "patterns": [r"^[\s]*pass\s*#\s*TODO.*\n", r"^[\s]*pass\s*#.*TODO.*\n"],
            "safety_check": lambda line: "pass" in line and "TODO" in line,
        },
        "dependency_stubs": {
            "patterns": [r"^[\s]*#\s*TODO:\s*Install or implement \w+\s*\n", r"^[\s]*#\s*TODO:\s*Install \w+\s*\n"],
            "safety_check": lambda line: "TODO:" in line and ("install" in line.lower() or "implement" in line.lower()),
        },
    }

    print("🧪 Testing TODO removal patterns...")
    print("=" * 50)

    total_tests = len(test_cases)
    passed_tests = 0

    for test_line, expected_category, should_match in test_cases:
        test_line_with_newline = test_line + "\n"

        # Test against the specific category
        if expected_category in removal_patterns:
            config = removal_patterns[expected_category]
            matched = False

            for pattern in config["patterns"]:
                if re.search(pattern, test_line_with_newline, re.MULTILINE):
                    if config["safety_check"](test_line):
                        matched = True
                        break

            # Check if result matches expectation
            if matched == should_match:
                status = "✅ PASS"
                passed_tests += 1
            else:
                status = "❌ FAIL"

            print(f"{status} | {expected_category:25} | {should_match:5} | {test_line[:50]}")
        else:
            print(f"❌ FAIL | Unknown category: {expected_category}")

    print("=" * 50)
    print(f"Tests passed: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("🎉 All pattern tests passed!")
        return True
    else:
        print("⚠️  Some pattern tests failed - review before proceeding")
        return False


def scan_real_samples():
    """Scan actual codebase for samples of each pattern type"""
    print("\n🔍 Scanning codebase for real samples...")

    patterns_to_test = {
        "Symbol resolver duplicates": r"TODO\(symbol-resolver\): implement missing functionality",
        "Streamlit stubs": r"TODO: Install or implement streamlit",
        "Consolidation stubs": r"TODO: Implement actual consolidation logic",
        "Completion references": r"[Aa]ddresses TODO \d+",
        "Pass stubs": r"pass.*#.*TODO",
    }

    for pattern_name, pattern in patterns_to_test.items():
        print(f"\n📋 {pattern_name}:")
        try:
            result = subprocess.run(["git", "grep", "-n", pattern], capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[:5]  # Show first 5 matches
                for line in lines:
                    print(f"  {line}")
                total_matches = len(result.stdout.strip().split("\n"))
                if total_matches > 5:
                    remaining = total_matches - 5
                    print(f"  ... and {remaining} more")
            else:
                print("  No matches found")

        except Exception as e:
            print(f"  Error: {e}")


def count_current_todos():
    """Count current TODOs by type for comparison"""
    print("\n📊 Current TODO distribution:")

    try:
        result = subprocess.run(["git", "grep", "-i", "TODO"], capture_output=True, text=True)

        if result.returncode == 0:
            total_lines = len(result.stdout.strip().split("\n"))
            print(f"  Total TODO lines: {total_lines}")

            # Count specific patterns
            patterns = {
                "symbol-resolver": r"TODO\(symbol-resolver\)",
                "streamlit install": r"TODO:.*[Ii]nstall.*streamlit",
                "consolidation": r"TODO:.*consolidation logic",
                "completion refs": r"[Aa]ddresses TODO \d+",
                "pass stubs": r"pass.*TODO",
            }

            for name, pattern in patterns.items():
                count_result = subprocess.run(["git", "grep", "-c", pattern], capture_output=True, text=True)
                if count_result.returncode == 0:
                    total_count = sum(
                        int(line.split(":")[1]) for line in count_result.stdout.strip().split("\n") if ":" in line
                    )
                    print(f"  {name}: {total_count}")

    except Exception as e:
        print(f"  Error counting TODOs: {e}")


def main():
    """Main verification function"""
    print("🔬 LUKHAS TODO Pattern Verification")
    print("=" * 60)

    # Test patterns against known cases
    patterns_valid = test_patterns_against_samples()

    # Scan for real samples
    scan_real_samples()

    # Count current state
    count_current_todos()

    print("\n" + "=" * 60)
    if patterns_valid:
        print("✅ Pattern verification completed - patterns are working correctly")
        print("🟢 Safe to proceed with TODO removal")
    else:
        print("⚠️  Pattern verification found issues")
        print("🔴 Review patterns before proceeding")

    return patterns_valid


if __name__ == "__main__":
    main()
