#!/usr/bin/env python3
"""
Fail-fast check for fragile import patterns in stable lanes.

Blocks:
- sys.path modification (insert/append/extend)
- star imports (from x import *) in stable code

Usage:
  python tools/ci/no_syspath_hacks.py [paths...]

Exit codes:
  0 = no violations
  1 = violations found
  2 = invalid invocation
"""
from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

SYSPATH_PATTERNS = (re.compile(r"\bsys\.path\.(insert|append|extend)\s*\(\s*"),)
STAR_IMPORT_PATTERN = re.compile(r"^\s*from\s+\S+\s+import\s+\*\s*(#.*)?$")


def iter_py_files(paths: Iterable[str]) -> Iterable[Path]:
    for raw in paths:
        root = Path(raw)
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix == ".py":
                yield root
            continue
        for p in root.rglob("*.py"):
            # Skip caches and virtualenvs
            sp = str(p)
            if any(x in sp for x in (".venv", "venv", "__pycache__")):
                continue
            yield p


def check_file(path: Path) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations

    # Line-level checks
    for lineno, line in enumerate(text.splitlines(), start=1):
        if STAR_IMPORT_PATTERN.search(line):
            violations.append(
                (
                    lineno,
                    "star import detected; replace with explicit imports",
                )
            )

    # File-level sys.path mutations
    for pat in SYSPATH_PATTERNS:
        m = pat.search(text)
        if m:
            # Find approximate line
            idx = text[: m.start()].count("\n") + 1
            violations.append(
                (
                    idx,
                    "sys.path mutation detected; use package-relative or absolute imports",
                )
            )

    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: no_syspath_hacks.py <path> [<path> ...]", file=sys.stderr)
        return 2

    roots = argv[1:]
    total = 0
    for path in roots:
        for f in iter_py_files([path]):
            viols = check_file(f)
            if not viols:
                continue
            total += len(viols)
            for lineno, msg in viols:
                print(f"{f}:{lineno}: {msg}")

    if total:
        print()
        print("❌ Fragile import patterns detected.")
        print("   - Replace sys.path hacks with proper package imports (run as module).")
        print("   - Replace 'from X import *' with explicit imports.")
        return 1

    print("✅ No fragile import patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))