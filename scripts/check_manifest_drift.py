#!/usr/bin/env python3
"""
Module: check_manifest_drift.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def pct_drop(old: int, new: int) -> float:
    if old == 0: return 0.0
    return max(0.0, (old - new) / old * 100.0)

def main():
    ap = argparse.ArgumentParser(description="Fail if manifest count drops beyond threshold.")
    ap.add_argument("--baseline", required=True, help="Path to baseline manifest_stats.json")
    ap.add_argument("--current", required=True, help="Path to current manifest_stats.json")
    ap.add_argument("--max-drop", type=float, default=1.0, help="Max allowed % drop (default: 1.0)")
    args = ap.parse_args()

    base = load(Path(args.baseline))
    curr = load(Path(args.current))
    old = int(base.get("total_manifests", 0))
    new = int(curr.get("total_manifests", 0))

    drop = pct_drop(old, new)
    print(f"[DRIFT] baseline={old} current={new} drop={drop:.2f}% (limit={args.max_drop:.2f}%)")
    if drop > args.max_drop:
        print("[FAIL] Manifest count drop exceeds threshold.")
        sys.exit(1)
    print("[OK] No unacceptable drift detected.")

if __name__ == "__main__":
    main()
