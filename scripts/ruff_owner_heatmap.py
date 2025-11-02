#!/usr/bin/env python3
"""
Module: ruff_owner_heatmap.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def nearest_manifest(pyfile: Path) -> dict:
    for parent in [pyfile] + list(pyfile.parents):
        m = parent / "module.manifest.json"
        if m.exists():
            try:
                return load_json(m)
            except Exception:
                return {}
    return {}


def main():
    ap = argparse.ArgumentParser(description="Build Ruff owner heatmap (Star × Owner × Rule).")
    ap.add_argument("--ruff", default="docs/audits/ruff.json")
    ap.add_argument("--csv", default="docs/audits/ruff_heatmap.csv")
    ap.add_argument("--md", default="docs/audits/ruff_heatmap.md")
    args = ap.parse_args()

    ruff = load_json(Path(args.ruff))
    cube = defaultdict(lambda: Counter())  # (star, owner) -> Counter(code)
    totals = Counter()  # overall per code

    for e in ruff:
        code = e.get("code")
        if not code:  # Skip entries without error codes
            continue
        file = Path(e.get("filename"))
        man = nearest_manifest(file)
        star = ((man.get("constellation_alignment") or {}).get("primary_star")) or "Supporting"
        owner = ((man.get("metadata") or {}).get("owner")) or "unknown"
        cube[(star, owner)][code] += 1
        totals[code] += 1

    # Collect all codes present to define header columns
    all_codes = set()
    for _, cnt in cube.items():
        all_codes.update(cnt.keys())
    all_codes = sorted([c for c in all_codes if c is not None])

    # CSV
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.csv).open("w", encoding="utf-8") as f:
        f.write("star,owner," + ",".join(all_codes) + ",total\n")
        for (star, owner), cnt in sorted(cube.items()):
            row = [str(cnt.get(c, 0)) for c in all_codes]
            f.write(f"{star},{owner}," + ",".join(row) + f",{sum(cnt.values())}\n")

    # MD
    with Path(args.md).open("w", encoding="utf-8") as f:
        f.write("# Ruff Heatmap (Star × Owner × Rule)\n\n")
        f.write("| Star | Owner | " + " | ".join(all_codes) + " | Total |\n")
        f.write("|---|---|" + "|".join([":--:" for _ in all_codes]) + "|---:|\n")
        for (star, owner), cnt in sorted(cube.items()):
            row = " | ".join(str(cnt.get(c, 0)) for c in all_codes)
            f.write(f"| {star} | {owner} | {row} | {sum(cnt.values())} |\n")

        f.write("\n**Totals by rule:**\n\n")
        f.write("| Rule | Count |\n|---|---:|\n")
        for c in all_codes:
            f.write(f"| {c} | {totals[c]} |\n")

    print(f"[OK] Wrote {args.csv} and {args.md}")


if __name__ == "__main__":
    sys.exit(main())
