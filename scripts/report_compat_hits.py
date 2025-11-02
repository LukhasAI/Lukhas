#!/usr/bin/env python3
"""
Track compat layer usage via runtime telemetry.

Reads docs/audits/compat_alias_hits.json and reports total hits.
Phase 3 gate: LUKHAS_COMPAT_MAX_HITS=0 enforces zero usage in CI.

Usage:
  python3 scripts/report_compat_hits.py --out docs/audits/compat_alias_hits.json
"""
import argparse
import json
import os
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Report compat alias hits")
    ap.add_argument("--out", default="docs/audits/compat_alias_hits.json", help="Path to compat hits JSON file")
    args = ap.parse_args()

    p = Path(args.out)
    if not p.exists():
        print(f"[report_compat_hits] No file at {p}, assuming 0 hits")
        data = {}
    else:
        with open(p) as f:
            data = json.load(f)

    # Count total hits across all keys
    total_hits = 0
    if isinstance(data, dict):
        for key, count in data.items():
            if isinstance(count, int):
                total_hits += count
            elif isinstance(count, dict) and "count" in count:
                total_hits += count["count"]

    print(f"[report_compat_hits] Total compat alias hits: {total_hits}")

    # Check against env limit
    max_hits = int(os.environ.get("LUKHAS_COMPAT_MAX_HITS", "999999"))
    if total_hits > max_hits:
        print(f"[report_compat_hits] ❌ FAIL: {total_hits} hits exceeds limit {max_hits}")
        sys.exit(2)
    else:
        print(f"[report_compat_hits] ✅ PASS: {total_hits} hits within limit {max_hits}")
        sys.exit(0)


if __name__ == "__main__":
    main()
