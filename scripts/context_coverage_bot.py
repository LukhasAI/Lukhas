#!/usr/bin/env python3
"""
Module: context_coverage_bot.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Context Coverage Bot

Computes coverage for manifests having a lukhas_context.md with valid-looking
front-matter. Writes a small report and exits non-zero if coverage is below
the specified threshold.

Usage:
  python scripts/context_coverage_bot.py --manifests manifests --min 0.95
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

FM_START = re.compile(r"^\s*---\s*$")
FM_END = re.compile(r"^\s*---\s*$")


def has_front_matter(p: pathlib.Path) -> bool:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    lines = text.splitlines()
    if not lines or not FM_START.match(lines[0]):
        return False
    for i in range(1, min(len(lines), 200)):
        if FM_END.match(lines[i]):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--min", type=float, default=0.95)
    ap.add_argument("--report", default="docs/audits/context_coverage.txt")
    args = ap.parse_args()

    root = pathlib.Path(args.manifests)
    all_files = list(root.rglob("module.manifest.json"))
    def is_archived(path: pathlib.Path) -> bool:
        return any(part == ".archive" for part in path.parts)
    manifest_files = [p for p in all_files if not is_archived(p)]
    ctx_files = [mf.parent / "lukhas_context.md" for mf in manifest_files]

    present = [p for p in ctx_files if p.exists()]
    with_fm = [p for p in present if has_front_matter(p)]

    total = len(manifest_files)
    present_pct = (len(present) / total) if total else 1.0
    fm_pct = (len(with_fm) / total) if total else 1.0

    out = pathlib.Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        (
            f"Context coverage report\n"
            f"Manifests: {total}\n"
            f"Context files present: {len(present)} ({present_pct:.1%})\n"
            f"With front-matter: {len(with_fm)} ({fm_pct:.1%})\n"
            f"Threshold (front-matter): {args.min:.0%}\n"
        ),
        encoding="utf-8",
    )

    skipped = len(all_files) - total
    print(f"Front-matter coverage: {fm_pct:.1%} (threshold {args.min:.0%})")
    print(f"Debug: all={len(all_files)} filtered={total} skipped={skipped}")
    if fm_pct + 1e-9 < args.min:
        sys.exit(1)


if __name__ == "__main__":
    main()
