#!/usr/bin/env python3
"""
Module: check_perf_budgets.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Performance budget checker for T4 hardening
Validates test durations against historical p95 baselines
"""
import json
import sys
from pathlib import Path


def load_budgets():
    """Load performance budgets from tests/perf_budgets.json"""
    budget_file = Path("tests/perf_budgets.json")
    if not budget_file.exists():
        print("⚠️  No performance budgets file found")
        return None

    with open(budget_file) as f:
        return json.load(f)


def check_suite_budget(suite_name, duration, budgets):
    """Check if suite duration exceeds budget"""
    suite_key = suite_name.lower().replace(" ", "_")
    if suite_key not in budgets["test_budgets"]:
        print(f"⚠️  No budget found for suite: {suite_name}")
        return True

    budget_info = budgets["test_budgets"][suite_key]
    p95_baseline = budget_info["p95_baseline"]
    max_allowed = p95_baseline * 3.0  # 3x p95 threshold

    if duration > max_allowed:
        print(f"❌ {suite_name}: {duration:.2f}s > {max_allowed:.2f}s (3x p95)")
        return False
    elif duration > p95_baseline:
        print(f"⚠️  {suite_name}: {duration:.2f}s > p95 baseline {p95_baseline:.2f}s")
    else:
        print(f"✅ {suite_name}: {duration:.2f}s within p95 baseline {p95_baseline:.2f}s")

    return True


def check_individual_test_budget(test_name, duration, budgets):
    """Check if individual test exceeds its budget"""
    if test_name not in budgets["individual_test_budgets"]:
        return True  # No budget defined, pass

    budget_info = budgets["individual_test_budgets"][test_name]
    p95_baseline = budget_info["p95_baseline"]
    max_allowed = p95_baseline * 3.0  # 3x p95 threshold

    if duration > max_allowed:
        print(f"❌ {test_name}: {duration:.2f}s > {max_allowed:.2f}s (3x p95)")
        return False
    elif duration > p95_baseline:
        print(f"⚠️  {test_name}: {duration:.2f}s > p95 baseline {p95_baseline:.2f}s")

    return True


def extract_durations_from_json(json_file):
    """Extract test durations from pytest JSON report"""
    if not Path(json_file).exists():
        return []

    with open(json_file) as f:
        data = json.load(f)

    durations = []
    suite_duration = data.get("report", {}).get("duration", 0)

    # Extract individual test durations
    for test in data.get("tests", []):
        test_name = test.get("nodeid", "").split("::")[-1]
        duration = test.get("call", {}).get("duration", 0)
        if duration > 0:
            durations.append((test_name, duration))

    return suite_duration, durations


def main():
    """Main budget checking logic"""
    budgets = load_budgets()
    if not budgets:
        sys.exit(0)  # Skip if no budgets defined

    violations = []

    # Check suite budgets from JSON reports
    reports = [
        ("Unit contracts", "reports/unit.json"),
        ("Capabilities", "reports/capabilities.json"),
        ("E2E smoke", "reports/e2e.json")
    ]

    print("=== Performance Budget Check ===")

    for suite_name, json_file in reports:
        if Path(json_file).exists():
            suite_duration, test_durations = extract_durations_from_json(json_file)

            # Check suite budget
            if not check_suite_budget(suite_name, suite_duration, budgets):
                violations.append(f"Suite {suite_name} exceeded budget")

            # Check individual test budgets
            for test_name, duration in test_durations:
                if not check_individual_test_budget(test_name, duration, budgets):
                    violations.append(f"Test {test_name} exceeded budget")

    if violations:
        print(f"\n❌ {len(violations)} performance budget violations:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    else:
        print("\n✅ All performance budgets within limits")


if __name__ == "__main__":
    main()
