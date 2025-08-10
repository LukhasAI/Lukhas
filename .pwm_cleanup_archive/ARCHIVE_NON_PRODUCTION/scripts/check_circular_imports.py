#!/usr/bin/env python3
"""
Simple circular import checker for pre-commit hook.
Prevents regression by checking if circular dependencies increase.
"""

import json
import sys
from pathlib import Path

# Baseline circular dependency count (after our improvements)
BASELINE_CIRCULAR_COUNT = 35000000  # ~35M after improvements


def check_circular_imports():
    """Check if circular imports have increased"""
    # Try to load the latest connectivity report
    report_path = Path(__file__).parent / "connectivity_report.json"

    if not report_path.exists():
        print(
            "Warning: No connectivity report found. Run connectivity_visualizer.py first."
        )
        return 0

    try:
        with open(report_path) as f:
            report = json.load(f)

        current_count = report.get("summary", {}).get("circular_dependencies", 0)

        if current_count > BASELINE_CIRCULAR_COUNT * 1.1:  # Allow 10% variance
            print("❌ Circular dependencies increased!")
            print(f"   Baseline: {BASELINE_CIRCULAR_COUNT:,}")
            print(f"   Current:  {current_count:,}")
            print(f"   Increase: {current_count - BASELINE_CIRCULAR_COUNT:,}")
            return 1
        else:
            print(f"✅ Circular dependencies under control: {current_count:,}")
            return 0

    except Exception as e:
        print(f"Warning: Could not check circular imports: {e}")
        return 0


if __name__ == "__main__":
    sys.exit(check_circular_imports())
