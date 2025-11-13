#!/usr/bin/env python3
"""T4/0.01% Benchmark Trend Analytics

Reads benchmark ledger and generates daily performance delta trends in CSV format.

Usage:
    python scripts/analytics/bench_trend.py [--output trends/bench_trend.csv]

Output:
    CSV with columns: date, module, p50_ms, p95_ms, p99_ms, delta_p95, env_fingerprint
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class BenchEntry(NamedTuple):
    """Parsed benchmark ledger entry."""
    module: str
    timestamp: datetime
    p50: float
    p95: float
    p99: float
    env_fingerprint: str


def parse_ledger(ledger_path: Path) -> list[BenchEntry]:
    """Parse benchmark ledger into sorted entries."""
    if not ledger_path.exists():
        return []

    entries = []
    for line in ledger_path.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            data = json.loads(line)
            module = data["module"]
            timestamp = datetime.fromisoformat(data["timestamp"])
            p50 = data["p50_ms"]
            p95 = data["p95_ms"]
            p99 = data["p99_ms"]
            env = data.get("env_fingerprint", "unknown")
            entries.append(BenchEntry(module, timestamp, p50, p95, p99, env))
        except Exception as e:
            print(f"⚠️  Could not parse entry: {e}", file=sys.stderr)
            continue

    # Sort by timestamp
    return sorted(entries, key=lambda e: e.timestamp)


def calculate_trends(entries: list[BenchEntry]) -> list[tuple[str, str, float, float, float, float, str]]:
    """Calculate daily trends with p95 deltas.

    Returns:
        List of (date, module, p50, p95, p99, delta_p95, env) tuples
    """
    # Group by module
    by_module: dict[str, list[BenchEntry]] = defaultdict(list)
    for entry in entries:
        by_module[entry.module].append(entry)

    trends = []

    for module, module_entries in by_module.items():
        previous_p95 = None

        for entry in module_entries:
            date = entry.timestamp.date().isoformat()
            p50 = entry.p50
            p95 = entry.p95
            p99 = entry.p99
            env = entry.env_fingerprint

            delta_p95 = p95 - previous_p95 if previous_p95 is not None else 0.0

            trends.append((date, module, p50, p95, p99, delta_p95, env))
            previous_p95 = p95

    return sorted(trends, key=lambda t: (t[0], t[1]))


def write_csv(trends: list[tuple[str, str, float, float, float, float, str]], output_path: Path) -> None:
    """Write trends to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        # Write header
        f.write("date,module,p50_ms,p95_ms,p99_ms,delta_p95,env_fingerprint\n")

        # Write data
        for date, module, p50, p95, p99, delta_p95, env in trends:
            f.write(f"{date},{module},{p50:.2f},{p95:.2f},{p99:.2f},{delta_p95:+.2f},{env}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate benchmark trend analytics from ledger"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("trends/bench_trend.csv"),
        help="Output CSV path (default: trends/bench_trend.csv)"
    )
    args = parser.parse_args()

    ledger_path = Path("manifests/.ledger/bench.ndjson")

    print(f"📊 Reading benchmark ledger: {ledger_path}")
    entries = parse_ledger(ledger_path)

    if not entries:
        print("⚠️  No benchmark entries found in ledger")
        return 1

    print(f"   Found {len(entries)} entries")

    print("📈 Calculating trends...")
    trends = calculate_trends(entries)

    print(f"💾 Writing CSV: {args.output}")
    write_csv(trends, args.output)

    print(f"✅ Generated benchmark trend CSV with {len(trends)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
