#!/usr/bin/env python3
"""T4/0.01% Coverage Trend Analytics

Reads coverage ledger and generates daily delta trends in CSV format.

Usage:
    python scripts/analytics/coverage_trend.py [--output trends/coverage_trend.csv]

Output:
    CSV with columns: date, module, coverage_pct, delta_from_previous
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class CoverageEntry(NamedTuple):
    """Parsed coverage ledger entry."""

    module: str
    timestamp: datetime
    coverage: float


def parse_ledger(ledger_path: Path) -> list[CoverageEntry]:
    """Parse coverage ledger into sorted entries."""
    if not ledger_path.exists():
        return []

    entries = []
    for line in ledger_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            module = data["module"]
            # Support both "timestamp" and "ts" field names
            timestamp_str = data.get("timestamp") or data.get("ts")
            timestamp = datetime.fromisoformat(timestamp_str)
            # Support both "coverage_pct" and "coverage" field names
            coverage = data.get("coverage_pct") or data.get("coverage")
            entries.append(CoverageEntry(module, timestamp, coverage))
        except Exception as e:
            print(f"⚠️  Could not parse entry: {e}", file=sys.stderr)
            continue

    # Sort by timestamp
    return sorted(entries, key=lambda e: e.timestamp)


def calculate_trends(entries: list[CoverageEntry]) -> list[tuple[str, str, float, float]]:
    """Calculate daily trends with deltas.

    Returns:
        List of (date, module, coverage, delta) tuples
    """
    # Group by module
    by_module: dict[str, list[CoverageEntry]] = defaultdict(list)
    for entry in entries:
        by_module[entry.module].append(entry)

    trends = []

    for module, module_entries in by_module.items():
        previous_coverage = None

        for entry in module_entries:
            date = entry.timestamp.date().isoformat()
            coverage = entry.coverage

            if previous_coverage is not None:
                delta = coverage - previous_coverage
            else:
                delta = 0.0

            trends.append((date, module, coverage, delta))
            previous_coverage = coverage

    return sorted(trends, key=lambda t: (t[0], t[1]))


def write_csv(trends: list[tuple[str, str, float, float]], output_path: Path) -> None:
    """Write trends to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        # Write header
        f.write("date,module,coverage_pct,delta_from_previous\n")

        # Write data
        for date, module, coverage, delta in trends:
            f.write(f"{date},{module},{coverage:.2f},{delta:+.2f}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate coverage trend analytics from ledger")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("trends/coverage_trend.csv"),
        help="Output CSV path (default: trends/coverage_trend.csv)",
    )
    args = parser.parse_args()

    ledger_path = Path("manifests/.ledger/coverage.ndjson")

    print(f"📊 Reading coverage ledger: {ledger_path}")
    entries = parse_ledger(ledger_path)

    if not entries:
        print("⚠️  No coverage entries found in ledger")
        return 1

    print(f"   Found {len(entries)} entries")

    print("📈 Calculating trends...")
    trends = calculate_trends(entries)

    print(f"💾 Writing CSV: {args.output}")
    write_csv(trends, args.output)

    print(f"✅ Generated coverage trend CSV with {len(trends)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
