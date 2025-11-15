#!/usr/bin/env python3
"""
Track error reduction progress over time.

Usage:
    python3 tools/track_error_progress.py                    # Run check and save snapshot
    python3 tools/track_error_progress.py --compare          # Compare with baseline
    python3 tools/track_error_progress.py --report           # Generate detailed report
    python3 tools/track_error_progress.py --baseline         # Set new baseline
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[1]
PROGRESS_DIR = REPO_ROOT / "reports" / "error_tracking"
BASELINE_FILE = PROGRESS_DIR / "baseline.json"


def run_pytest_collection() -> tuple[str, str]:
    """Run pytest collection and return stdout, stderr."""
    result = subprocess.run(
        [
            "python3",
            "-m",
            "pytest",
            "tests/unit",
            "--collect-only",
            "--continue-on-collection-errors",
            "--maxfail=1000",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.stdout, result.stderr


def parse_collection_output(stdout: str, stderr: str) -> Dict[str, Any]:
    """Parse pytest collection output."""
    output = stdout + stderr

    # Extract summary line
    summary_match = re.search(
        r"(\d+) tests collected(?:, (\d+) errors?)?", output
    )
    if not summary_match:
        return {"tests": 0, "errors": 0, "error_details": []}

    tests = int(summary_match.group(1))
    errors = int(summary_match.group(2)) if summary_match.group(2) else 0

    # Extract error details
    error_pattern = r"ERROR collecting (.+?)\n(.+?)(?=ERROR collecting|short test summary|$)"
    error_matches = re.findall(error_pattern, output, re.DOTALL)

    error_details = []
    for file_path, error_text in error_matches:
        file_path = file_path.strip()

        # Categorize error
        category = "unknown"
        error_type = "unknown"
        missing_item = None

        if "ModuleNotFoundError" in error_text:
            category = "module_not_found"
            match = re.search(r"No module named '([^']+)'", error_text)
            if match:
                missing_item = match.group(1)
                error_type = f"ModuleNotFoundError: {missing_item}"

        elif "ImportError" in error_text:
            category = "import_error"
            if "cannot import name" in error_text:
                match = re.search(r"cannot import name '([^']+)'", error_text)
                if match:
                    missing_item = match.group(1)
                    error_type = f"cannot import {missing_item}"
            else:
                error_type = "ImportError: other"

        elif "SyntaxError" in error_text:
            category = "syntax_error"
            error_type = "SyntaxError"

        elif "IndentationError" in error_text:
            category = "indentation_error"
            error_type = "IndentationError"

        elif "not found in `markers` configuration" in error_text:
            category = "pytest_marker"
            match = re.search(r"'([^']+)' not found in", error_text)
            if match:
                missing_item = match.group(1)
                error_type = f"missing marker: {missing_item}"

        error_details.append(
            {
                "file": file_path,
                "category": category,
                "type": error_type,
                "missing_item": missing_item,
            }
        )

    return {
        "tests": tests,
        "errors": errors,
        "error_details": error_details,
    }


def categorize_errors(error_details: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Categorize errors by type."""
    by_type = defaultdict(list)

    for error in error_details:
        by_type[error["type"]].append(error["file"])

    return dict(by_type)


def save_snapshot(
    tests: int, errors: int, error_details: List[Dict[str, Any]]
) -> Path:
    """Save current state snapshot."""
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    snapshot = {
        "timestamp": timestamp,
        "tests": tests,
        "errors": errors,
        "error_details": error_details,
        "categorized": categorize_errors(error_details),
    }

    # Save timestamped snapshot
    snapshot_file = PROGRESS_DIR / f"snapshot_{datetime.now():%Y%m%d_%H%M%S}.json"
    snapshot_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    # Update latest
    latest_file = PROGRESS_DIR / "latest.json"
    latest_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    return snapshot_file


def load_baseline() -> Optional[Dict[str, Any]]:
    """Load baseline snapshot."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def set_baseline() -> None:
    """Set current state as baseline."""
    latest_file = PROGRESS_DIR / "latest.json"
    if not latest_file.exists():
        print("Error: No latest snapshot. Run without --baseline first.")
        return

    import shutil

    shutil.copy(latest_file, BASELINE_FILE)
    print(f"✅ Baseline set from {latest_file}")


def compare_with_baseline(
    current: Dict[str, Any], baseline: Dict[str, Any]
) -> None:
    """Compare current state with baseline."""
    print("\n" + "=" * 80)
    print("PROGRESS COMPARISON")
    print("=" * 80)

    # Tests
    test_delta = current["tests"] - baseline["tests"]
    test_symbol = "📈" if test_delta > 0 else "📉" if test_delta < 0 else "➡️"
    print(
        f"\nTests: {baseline['tests']} → {current['tests']} "
        f"({test_delta:+d}) {test_symbol}"
    )

    # Errors
    error_delta = current["errors"] - baseline["errors"]
    error_symbol = "✅" if error_delta < 0 else "⚠️" if error_delta > 0 else "➡️"
    print(
        f"Errors: {baseline['errors']} → {current['errors']} "
        f"({error_delta:+d}) {error_symbol}"
    )

    # Error rate
    baseline_rate = (
        baseline["errors"] / baseline["tests"] * 100
        if baseline["tests"] > 0
        else 0
    )
    current_rate = (
        current["errors"] / current["tests"] * 100
        if current["tests"] > 0
        else 0
    )
    print(f"Error Rate: {baseline_rate:.2f}% → {current_rate:.2f}%")

    # Category changes
    baseline_cats = baseline.get("categorized", {})
    current_cats = current.get("categorized", {})

    all_cats = set(baseline_cats.keys()) | set(current_cats.keys())

    print("\n" + "-" * 80)
    print("ERROR CATEGORY CHANGES")
    print("-" * 80)

    for cat in sorted(all_cats):
        baseline_count = len(baseline_cats.get(cat, []))
        current_count = len(current_cats.get(cat, []))
        delta = current_count - baseline_count

        if delta != 0:
            symbol = "✅" if delta < 0 else "⚠️"
            print(
                f"{symbol} {cat:40s} {baseline_count:3d} → {current_count:3d} ({delta:+d})"
            )

    # Resolved errors
    baseline_files = {e["file"] for e in baseline.get("error_details", [])}
    current_files = {e["file"] for e in current.get("error_details", [])}

    resolved = baseline_files - current_files
    new_errors = current_files - baseline_files

    if resolved:
        print("\n" + "-" * 80)
        print(f"RESOLVED ERRORS ({len(resolved)})")
        print("-" * 80)
        for file in sorted(resolved)[:10]:
            print(f"  ✅ {file}")
        if len(resolved) > 10:
            print(f"  ... and {len(resolved) - 10} more")

    if new_errors:
        print("\n" + "-" * 80)
        print(f"NEW ERRORS ({len(new_errors)})")
        print("-" * 80)
        for file in sorted(new_errors)[:10]:
            print(f"  ⚠️  {file}")
        if len(new_errors) > 10:
            print(f"  ... and {len(new_errors) - 10} more")

    print("\n" + "=" * 80)


def generate_detailed_report(snapshot: Dict[str, Any]) -> None:
    """Generate detailed error report."""
    print("\n" + "=" * 80)
    print("DETAILED ERROR REPORT")
    print("=" * 80)
    print(f"\nTimestamp: {snapshot['timestamp']}")
    print(f"Tests Collected: {snapshot['tests']}")
    print(f"Total Errors: {snapshot['errors']}")

    categorized = snapshot.get("categorized", {})

    print("\n" + "-" * 80)
    print("ERRORS BY TYPE")
    print("-" * 80)

    for error_type in sorted(categorized.keys(), key=lambda x: -len(categorized[x])):
        files = categorized[error_type]
        print(f"\n{error_type} ({len(files)} files):")
        for file in sorted(files)[:5]:
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")

    # Priority breakdown
    error_details = snapshot.get("error_details", [])

    by_category = defaultdict(int)
    for error in error_details:
        by_category[error["category"]] += 1

    print("\n" + "-" * 80)
    print("ERRORS BY CATEGORY")
    print("-" * 80)
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat:30s} {count:3d}")

    print("\n" + "=" * 80)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Track error reduction progress"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Compare with baseline"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )
    parser.add_argument(
        "--baseline", action="store_true", help="Set new baseline"
    )
    parser.add_argument(
        "--no-save", action="store_true", help="Don't save snapshot"
    )

    args = parser.parse_args()

    if args.baseline:
        set_baseline()
        return

    # Run collection
    print("Running pytest collection...")
    stdout, stderr = run_pytest_collection()

    # Parse results
    result = parse_collection_output(stdout, stderr)

    print(f"✅ Tests collected: {result['tests']}")
    print(f"{'✅' if result['errors'] == 0 else '⚠️'}  Errors: {result['errors']}")

    # Save snapshot
    if not args.no_save:
        snapshot_file = save_snapshot(
            result["tests"], result["errors"], result["error_details"]
        )
        print(f"📸 Snapshot saved: {snapshot_file}")

    # Load current snapshot
    latest_file = PROGRESS_DIR / "latest.json"
    if latest_file.exists():
        current = json.loads(latest_file.read_text(encoding="utf-8"))
    else:
        current = result

    # Compare with baseline
    if args.compare:
        baseline = load_baseline()
        if baseline is None:
            print("\n⚠️  No baseline set. Run with --baseline to set one.")
        else:
            compare_with_baseline(current, baseline)

    # Detailed report
    if args.report:
        generate_detailed_report(current)


if __name__ == "__main__":
    main()
