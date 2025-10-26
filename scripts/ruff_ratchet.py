#!/usr/bin/env python3
"""
Module: ruff_ratchet.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))

def counts_by_code(events: list[dict]) -> Counter:
    c = Counter()
    for e in events:
        code = e.get("code")
        if code:
            c[code] += 1
    return c

def main():
    ap = argparse.ArgumentParser(description="Ruff ratchet: fail if tracked codes increase vs baseline.")
    ap.add_argument("--baseline", default="docs/audits/ruff_baseline.json")
    ap.add_argument("--current",  default="docs/audits/ruff.json")
    ap.add_argument("--track", action="append", default=["F821"], help="Ruff code(s) to ratchet (repeatable).")
    ap.add_argument("--init", action="store_true", help="Create baseline from current and exit 0.")
    ap.add_argument("--write-baseline", action="store_true", help="Overwrite baseline with current counts.")
    args = ap.parse_args()

    cur_path = Path(args.current)
    base_path = Path(args.baseline)

    if args.init:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(cur_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[INIT] Baseline created at {base_path}")
        return 0

    if not base_path.exists():
        print(f"[ERROR] Baseline missing: {base_path}. Run with --init on main to establish.")
        return 2

    cur_counts = counts_by_code(load(cur_path))
    base_counts = counts_by_code(load(base_path))

    bad = []
    rows = []
    for code in args.track:
        cur = cur_counts.get(code, 0)
        base = base_counts.get(code, 0)
        delta = cur - base
        rows.append((code, base, cur, delta))
        if delta > 0:
            bad.append((code, delta))

    print("| Code | Baseline | Current | Δ |")
    print("|---|---:|---:|---:|")
    for code, base, cur, delta in rows:
        print(f"| {code} | {base} | {cur} | {delta:+d} |")

    if args.write_baseline:
        base_path.write_text(cur_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[OK] Baseline updated: {base_path}")

    if bad:
        print("[FAIL] Ratchet breached: " + ", ".join([f"{c} +{d}" for c,d in bad]))
        return 1

    print("[OK] Ratchet respected.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
