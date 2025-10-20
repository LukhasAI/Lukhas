#!/usr/bin/env python3
"""
Check compat layer alias hits and enforce optional thresholds.

Usage:
  python3 scripts/check_alias_hits.py                    # Report only
  python3 scripts/check_alias_hits.py --max-hits 100     # Enforce threshold
  python3 scripts/check_alias_hits.py --trend            # Show trend over time

Reads: docs/audits/compat_alias_hits.json
Reports: Alias usage statistics and optionally enforces caps

Exit codes:
  0: Success (below threshold or no threshold)
  1: Above threshold (CI should fail)
  2: Error reading file
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


def load_alias_hits(path: Path):
    """Load alias hits from JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except FileNotFoundError:
        print(f"⚠️  File not found: {path}", file=sys.stderr)
        print("💡 Run: python3 scripts/report_compat_hits.py", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}", file=sys.stderr)
        return None


def count_hits(data):
    """Count total alias hits from data structure."""
    if not data:
        return 0

    # Handle different data structures
    if isinstance(data, dict):
        if "total_hits" in data:
            return data["total_hits"]
        if "aliases" in data:
            return sum(
                alias.get("hit_count", 0)
                for alias in data["aliases"]
            )
        # Fallback: count all numeric values
        return sum(
            v for v in data.values()
            if isinstance(v, (int, float))
        )

    return 0


def format_summary(data):
    """Format alias hits summary."""
    total = count_hits(data)

    lines = []
    lines.append("=" * 70)
    lines.append("COMPAT LAYER ALIAS HITS REPORT")
    lines.append("=" * 70)
    lines.append(f"Total Hits: {total}")

    if isinstance(data, dict) and "aliases" in data:
        lines.append(f"Unique Aliases: {len(data['aliases'])}")
        lines.append("")
        lines.append("Top 10 Most Used Aliases:")

        sorted_aliases = sorted(
            data["aliases"],
            key=lambda x: x.get("hit_count", 0),
            reverse=True
        )[:10]

        for i, alias in enumerate(sorted_aliases, 1):
            name = alias.get("name", "unknown")
            hits = alias.get("hit_count", 0)
            lines.append(f"  {i:2d}. {name:40s} {hits:>6d} hits")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Check compat layer alias hits"
    )
    ap.add_argument(
        "--file",
        default="docs/audits/compat_alias_hits.json",
        help="Path to alias hits JSON (default: docs/audits/compat_alias_hits.json)"
    )
    ap.add_argument(
        "--max-hits",
        type=int,
        help="Maximum allowed hits (exit 1 if exceeded)"
    )
    ap.add_argument(
        "--trend",
        action="store_true",
        help="Show trend over time (requires historical data)"
    )
    args = ap.parse_args()

    file_path = Path(args.file)
    data = load_alias_hits(file_path)

    if data is None:
        return 2

    total = count_hits(data)

    # Print summary
    print(format_summary(data))

    # Check threshold
    if args.max_hits is not None:
        print()
        if total > args.max_hits:
            print(f"❌ THRESHOLD EXCEEDED: {total} > {args.max_hits}")
            print(f"💡 Reduce compat layer usage before merging")
            return 1
        else:
            print(f"✅ Below threshold: {total} ≤ {args.max_hits}")

    # Trend analysis (future enhancement)
    if args.trend:
        print()
        print("📊 Trend Analysis:")
        print("💡 Historical tracking not yet implemented")
        print("   Consider adding timestamp + hits to track over time")

    return 0


if __name__ == "__main__":
    sys.exit(main())
