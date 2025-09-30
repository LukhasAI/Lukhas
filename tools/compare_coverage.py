#!/usr/bin/env python3
"""
Coverage Comparison Tool - Compare baseline vs current coverage
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any

def load_coverage(path: str) -> Dict[str, Any]:
    """Load coverage data from JSON file"""
    if not Path(path).exists():
        print(f"❌ Coverage file not found: {path}")
        sys.exit(1)

    with open(path, 'r') as f:
        return json.load(f)

def extract_metrics(coverage_data: Dict[str, Any]) -> Dict[str, float]:
    """Extract key coverage metrics"""
    # Support different coverage report formats
    if 'totals' in coverage_data:
        # coverage.py format
        totals = coverage_data['totals']
        return {
            'line_coverage': totals.get('percent_covered', 0.0),
            'lines_covered': totals.get('covered_lines', 0),
            'lines_missing': totals.get('missing_lines', 0),
            'total_lines': totals.get('num_statements', 0)
        }
    elif 'summary' in coverage_data:
        # Custom format
        summary = coverage_data['summary']
        return {
            'line_coverage': summary.get('line_coverage', 0.0),
            'branch_coverage': summary.get('branch_coverage', 0.0),
            'total_files': summary.get('total_files', 0)
        }
    else:
        # Try to extract basic metrics
        return {
            'coverage': coverage_data.get('coverage', 0.0),
            'files': coverage_data.get('files', 0)
        }

def compare_coverage(baseline: Dict[str, float], current: Dict[str, float]) -> bool:
    """Compare coverage metrics and return True if current >= baseline"""

    print("📊 Coverage Comparison")
    print("=" * 50)

    all_good = True

    for metric in baseline.keys():
        if metric in current:
            baseline_val = baseline[metric]
            current_val = current[metric]
            change = current_val - baseline_val

            if change >= 0:
                status = "✅"
            else:
                status = "❌"
                all_good = False

            print(f"{status} {metric}: {baseline_val:.2f} → {current_val:.2f} ({change:+.2f})")
        else:
            print(f"⚠️  {metric}: baseline {baseline[metric]:.2f} → current: N/A")

    # Check for new metrics in current
    for metric in current.keys():
        if metric not in baseline:
            print(f"🆕 {metric}: new metric → {current[metric]:.2f}")

    print("=" * 50)

    if all_good:
        print("✅ Coverage check PASSED")
        return True
    else:
        print("❌ Coverage check FAILED")
        print("💡 Add 'allow:coverage-drop' label with justification to bypass")
        return False

def main():
    parser = argparse.ArgumentParser(description="Compare coverage reports")
    parser.add_argument("--baseline", required=True,
                       help="Path to baseline coverage JSON")
    parser.add_argument("--current", required=True,
                       help="Path to current coverage JSON")
    parser.add_argument("--allow-drop", action="store_true",
                       help="Allow coverage decrease")
    args = parser.parse_args()

    # Load coverage data
    baseline_data = load_coverage(args.baseline)
    current_data = load_coverage(args.current)

    # Extract metrics
    baseline_metrics = extract_metrics(baseline_data)
    current_metrics = extract_metrics(current_data)

    # Compare
    success = compare_coverage(baseline_metrics, current_metrics)

    if not success and not args.allow_drop:
        sys.exit(1)

    if not success and args.allow_drop:
        print("⚠️  Coverage decreased but --allow-drop specified")

    sys.exit(0)

if __name__ == "__main__":
    main()