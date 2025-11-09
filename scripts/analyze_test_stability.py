#!/usr/bin/env python3
"""
Analyze smoke test stability across multiple runs.

This script parses pytest JSON reports from multiple test runs,
identifies flaky tests, generates stability metrics, and creates
GitHub issue content if flakiness is detected.

Usage:
    python analyze_test_stability.py report1.json report2.json report3.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def load_test_report(filepath: str) -> Dict:
    """Load and parse a pytest JSON report."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Report file not found: {filepath}", file=sys.stderr)
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in report: {filepath}", file=sys.stderr)
        return {}


def extract_test_results(report: Dict) -> Dict[str, str]:
    """
    Extract test results from a pytest JSON report.

    Returns:
        Dict mapping test nodeid to outcome (passed, failed, skipped, etc.)
    """
    results = {}
    if 'tests' in report:
        for test in report['tests']:
            nodeid = test.get('nodeid', '')
            outcome = test.get('outcome', 'unknown')
            results[nodeid] = outcome
    return results


def analyze_stability(reports: List[Dict]) -> Dict:
    """
    Analyze test stability across multiple runs.

    Args:
        reports: List of pytest JSON report dictionaries

    Returns:
        Dictionary containing stability metrics and flaky test information
    """
    # Track outcomes for each test across all runs
    test_outcomes = defaultdict(list)

    for report in reports:
        results = extract_test_results(report)
        for nodeid, outcome in results.items():
            test_outcomes[nodeid].append(outcome)

    # Identify flaky tests (tests with inconsistent outcomes)
    flaky_tests = []
    stable_tests = []
    total_tests = len(test_outcomes)
    total_runs = len(reports)

    for nodeid, outcomes in test_outcomes.items():
        # Check if all outcomes are the same
        unique_outcomes = set(outcomes)

        if len(unique_outcomes) > 1:
            # Flaky test - different outcomes across runs
            pass_count = outcomes.count('passed')
            fail_count = outcomes.count('failed')
            skip_count = outcomes.count('skipped')
            error_count = outcomes.count('error')

            flaky_tests.append({
                'name': nodeid,
                'outcomes': outcomes,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'skip_count': skip_count,
                'error_count': error_count,
                'total_runs': len(outcomes),
                'stability_score': pass_count / len(outcomes) if outcomes else 0
            })
        else:
            stable_tests.append({
                'name': nodeid,
                'outcome': outcomes[0] if outcomes else 'unknown',
                'runs': len(outcomes)
            })

    # Calculate overall metrics
    flakiness_rate = len(flaky_tests) / total_tests if total_tests > 0 else 0

    return {
        'total_tests': total_tests,
        'total_runs': total_runs,
        'flaky_tests': flaky_tests,
        'stable_tests': stable_tests,
        'flakiness_rate': flakiness_rate,
        'flaky_count': len(flaky_tests),
        'stable_count': len(stable_tests)
    }


def generate_stability_report(metrics: Dict) -> str:
    """Generate a markdown report of stability metrics."""
    report_lines = [
        "# Smoke Test Stability Report",
        "",
        f"**Date:** {metrics.get('timestamp', 'N/A')}",
        f"**Total Tests:** {metrics['total_tests']}",
        f"**Test Runs:** {metrics['total_runs']}",
        f"**Flaky Tests:** {metrics['flaky_count']}",
        f"**Stable Tests:** {metrics['stable_count']}",
        f"**Flakiness Rate:** {metrics['flakiness_rate']:.2%}",
        ""
    ]

    if metrics['flaky_count'] > 0:
        report_lines.extend([
            "## ⚠️ Flaky Tests Detected",
            "",
            "The following tests showed inconsistent behavior across multiple runs:",
            ""
        ])

        for test in sorted(metrics['flaky_tests'], key=lambda x: x['stability_score']):
            stability_pct = test['stability_score'] * 100
            report_lines.extend([
                f"### `{test['name']}`",
                "",
                f"- **Stability:** {stability_pct:.1f}% ({test['pass_count']}/{test['total_runs']} passes)",
                f"- **Passes:** {test['pass_count']}",
                f"- **Failures:** {test['fail_count']}",
                f"- **Skips:** {test['skip_count']}",
                f"- **Errors:** {test['error_count']}",
                f"- **Outcomes:** {', '.join(test['outcomes'])}",
                ""
            ])

        report_lines.extend([
            "## Recommended Actions",
            "",
            "1. **Investigate Root Causes:** Review the flaky tests to identify timing issues, race conditions, or environmental dependencies",
            "2. **Add Retries:** Consider adding retry logic for tests with intermittent failures",
            "3. **Improve Test Isolation:** Ensure tests don't depend on shared state or external resources",
            "4. **Add Debugging:** Add more detailed logging to flaky tests to help diagnose issues",
            "5. **Quarantine if Necessary:** Consider marking extremely flaky tests with `@pytest.mark.flaky` or quarantining them",
            ""
        ])
    else:
        report_lines.extend([
            "## ✅ All Tests Stable",
            "",
            "No flaky tests detected! All tests showed consistent behavior across all runs.",
            ""
        ])

    return '\n'.join(report_lines)


def set_github_output(name: str, value: str):
    """Set a GitHub Actions output variable."""
    github_output = Path(os.environ.get('GITHUB_OUTPUT', '/dev/null'))
    try:
        with open(github_output, 'a') as f:
            f.write(f"{name}={value}\n")
    except Exception as e:
        print(f"Warning: Could not set GitHub output: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    import os
    from datetime import datetime

    if len(sys.argv) < 2:
        print("Usage: analyze_test_stability.py <report1.json> [report2.json] [report3.json] ...", file=sys.stderr)
        sys.exit(1)

    # Load all test reports
    report_files = sys.argv[1:]
    reports = [load_test_report(f) for f in report_files]
    reports = [r for r in reports if r]  # Filter out empty reports

    if not reports:
        print("Error: No valid test reports found", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {len(reports)} test report(s)...")

    # Analyze stability
    metrics = analyze_stability(reports)
    metrics['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    metrics['report_files'] = report_files

    # Generate report
    report = generate_stability_report(metrics)

    # Save report
    report_path = Path('stability_report.md')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Stability report saved to: {report_path}")

    # Save metrics
    metrics_path = Path('stability_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Stability metrics saved to: {metrics_path}")

    # Set GitHub Actions outputs
    flaky_tests_found = 'true' if metrics['flaky_count'] > 0 else 'false'
    set_github_output('flaky_tests_found', flaky_tests_found)
    set_github_output('flaky_count', str(metrics['flaky_count']))
    set_github_output('flakiness_rate', f"{metrics['flakiness_rate']:.2%}")

    # Print summary
    print("\n" + "=" * 60)
    print("STABILITY ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {metrics['total_tests']}")
    print(f"Test Runs: {metrics['total_runs']}")
    print(f"Flaky Tests: {metrics['flaky_count']}")
    print(f"Stable Tests: {metrics['stable_count']}")
    print(f"Flakiness Rate: {metrics['flakiness_rate']:.2%}")

    if metrics['flaky_count'] > 0:
        print("\n⚠️  FLAKY TESTS DETECTED!")
        print("\nMost problematic tests:")
        for test in sorted(metrics['flaky_tests'], key=lambda x: x['stability_score'])[:5]:
            print(f"  - {test['name']} ({test['stability_score']:.0%} stable)")
    else:
        print("\n✅ All tests are stable!")

    print("=" * 60)

    # Exit with error code if flaky tests found
    sys.exit(0)  # Don't fail the workflow, just report


if __name__ == '__main__':
    main()
