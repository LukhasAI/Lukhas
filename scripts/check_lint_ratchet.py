#!/usr/bin/env python3
"""
Lint Ratchet: Prevent new E402/F821 violations in PRs.

This script compares lint violations between the current PR branch
and the baseline (main branch) to ensure no new violations are introduced.

Usage:
    python scripts/check_lint_ratchet.py \
        --current /tmp/current_violations.json \
        --baseline /tmp/baseline_violations.json \
        --codes E402 F821

Exit codes:
    0 - No new violations detected (ratchet respected)
    1 - New violations detected (ratchet breached)
    2 - Error (missing files, invalid JSON, etc.)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_violations(path: Path) -> list[dict[str, Any]]:
    """Load violations from a JSON file."""
    try:
        if not path.exists():
            print(f"[WARNING] File not found: {path}, assuming empty violations")
            return []

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
        return []


def count_by_code(violations: list[dict[str, Any]]) -> Counter:
    """Count violations by error code."""
    counter = Counter()
    for violation in violations:
        code = violation.get("code")
        if code:
            counter[code] += 1
    return counter


def get_violation_details(violations: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Get detailed violation information grouped by code."""
    details = {}
    for violation in violations:
        code = violation.get("code")
        if code:
            if code not in details:
                details[code] = []

            filename = violation.get("filename", "unknown")
            location = violation.get("location", {})
            row = location.get("row", "?")
            message = violation.get("message", "")

            details[code].append(f"  {filename}:{row}: {message}")

    return details


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for new lint violations (E402/F821 ratchet)"
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current violations JSON file",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline violations JSON file",
    )
    parser.add_argument(
        "--codes",
        nargs="+",
        default=["E402", "F821"],
        help="Error codes to track (default: E402 F821)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed violation information",
    )

    args = parser.parse_args()

    # Load violations
    current_violations = load_violations(args.current)
    baseline_violations = load_violations(args.baseline)

    # Count by code
    current_counts = count_by_code(current_violations)
    baseline_counts = count_by_code(baseline_violations)

    # Check for ratchet violations
    new_violations = []
    print("\n" + "=" * 70)
    print("LINT RATCHET REPORT (E402/F821)")
    print("=" * 70)
    print(f"\n{'Code':<8} {'Baseline':<12} {'Current':<12} {'Delta':<12} {'Status'}")
    print("-" * 70)

    for code in args.codes:
        baseline_count = baseline_counts.get(code, 0)
        current_count = current_counts.get(code, 0)
        delta = current_count - baseline_count

        status = "✓ OK" if delta <= 0 else "✗ FAIL"
        delta_str = f"{delta:+d}" if delta != 0 else "0"

        print(f"{code:<8} {baseline_count:<12} {current_count:<12} {delta_str:<12} {status}")

        if delta > 0:
            new_violations.append((code, delta))

    print("-" * 70)

    # Show detailed information if verbose or if there are new violations
    if args.verbose or new_violations:
        current_details = get_violation_details(current_violations)

        for code, delta in new_violations:
            if code in current_details:
                print(f"\n[{code}] New violations detected (+{delta}):")
                for detail in current_details[code][:10]:  # Show first 10
                    print(detail)
                if len(current_details[code]) > 10:
                    print(f"  ... and {len(current_details[code]) - 10} more")

    # Summary
    print("\n" + "=" * 70)
    if new_violations:
        print("❌ RATCHET BREACHED")
        print("\nNew violations introduced:")
        for code, delta in new_violations:
            print(f"  - {code}: +{delta} violation(s)")
        print("\nAction required:")
        print("  1. Fix the new violations in your PR")
        print("  2. Or add # noqa: <code> comments with justification")
        print("=" * 70 + "\n")
        return 1
    else:
        print("✅ RATCHET RESPECTED")
        print("\nNo new E402/F821 violations introduced.")
        print("=" * 70 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
