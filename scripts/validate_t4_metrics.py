#!/usr/bin/env python3
"""
T4 Stability Sentinel: Validates core metrics remain stable across test runs
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_metric_from_logs(log_content: str, metric_pattern: str) -> float:
    """Extract a numeric metric from test logs using regex pattern"""
    match = re.search(metric_pattern, log_content)
    if match:
        return float(match.group(1))
    return 0.0


def validate_t4_metrics():
    """Validate that T4 metrics meet stability thresholds"""

    # Check if t4_logs.txt exists (created during workflow runs)
    log_file = Path("/tmp/t4_logs.txt")
    if not log_file.exists():
        print("⚠️  T4 logs not found - running in local mode")
        return True

    log_content = log_file.read_text()

    # Extract key metrics from logs
    metrics = {
        "unit_duration": extract_metric_from_logs(log_content, r"Unit contracts: elapsed (\d+)s"),
        "capability_duration": extract_metric_from_logs(log_content, r"Capability suite: elapsed (\d+)s"),
        "e2e_duration": extract_metric_from_logs(log_content, r"E2E smoke: elapsed (\d+)s"),
        "total_tests": len(re.findall(r"PASSED|FAILED|SKIPPED", log_content)),
        "failed_tests": len(re.findall(r"FAILED", log_content))
    }

    # Stability thresholds
    thresholds = {
        "unit_duration": 60,      # Unit tests should complete within 60s
        "capability_duration": 120, # Capability tests within 120s
        "e2e_duration": 60,       # E2E smoke within 60s
        "min_total_tests": 5,     # At least 5 tests should run
        "max_failed_tests": 0     # Zero failures allowed
    }

    violations = []

    # Check duration thresholds
    if metrics["unit_duration"] > thresholds["unit_duration"]:
        violations.append(f"Unit duration {metrics['unit_duration']}s > {thresholds['unit_duration']}s threshold")

    if metrics["capability_duration"] > thresholds["capability_duration"]:
        violations.append(f"Capability duration {metrics['capability_duration']}s > {thresholds['capability_duration']}s threshold")

    if metrics["e2e_duration"] > thresholds["e2e_duration"]:
        violations.append(f"E2E duration {metrics['e2e_duration']}s > {thresholds['e2e_duration']}s threshold")

    # Check test coverage
    if metrics["total_tests"] < thresholds["min_total_tests"]:
        violations.append(f"Only {metrics['total_tests']} tests ran, expected at least {thresholds['min_total_tests']}")

    # Check failure rate
    if metrics["failed_tests"] > thresholds["max_failed_tests"]:
        violations.append(f"{metrics['failed_tests']} tests failed, expected {thresholds['max_failed_tests']}")

    # Report results
    print("=== T4 Stability Sentinel ===")
    print(f"Unit duration: {metrics['unit_duration']}s")
    print(f"Capability duration: {metrics['capability_duration']}s")
    print(f"E2E duration: {metrics['e2e_duration']}s")
    print(f"Total tests: {metrics['total_tests']}")
    print(f"Failed tests: {metrics['failed_tests']}")

    if violations:
        print("\n❌ Stability violations detected:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("\n✅ All T4 metrics within stability thresholds")
        return True


if __name__ == "__main__":
    success = validate_t4_metrics()
    sys.exit(0 if success else 1)