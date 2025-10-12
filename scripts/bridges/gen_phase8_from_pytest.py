#!/usr/bin/env python3
"""
Parse `pytest --collect-only` stderr, rank missing modules/symbols,
and print the top offenders + ready-to-use bridge paths.
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter, defaultdict


def run_collect() -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
    )
    return proc.stderr + proc.stdout


def main():
    raw = run_collect()
    mod_missing = re.findall(r"No module named '([^']+)'", raw)
    sym_missing = re.findall(r"ImportError: .* cannot import name '([^']+)'", raw)
    pkg_attr = re.findall(r"__path__ attribute not found on '([^']+)'", raw)

    print("\n== Top missing modules ==")
    for m, c in Counter(mod_missing).most_common(12):
        print(f"{c:3d}  {m}")

    print("\n== Top missing symbols ==")
    for s, c in Counter(sym_missing).most_common(12):
        print(f"{c:3d}  {s}")

    if pkg_attr:
        print("\n== Module–package collisions (prefer package/) ==")
        for m, c in Counter(pkg_attr).most_common():
            print(f"{c:3d}  {m}  (has .py shadowing a package?)")

    # naïve mapping hints → bridge paths
    hints = defaultdict(list)
    for m in set(mod_missing):
        parts = m.split(".")
        if len(parts) >= 2:
            pkg = "/".join(parts) + "/__init__.py"
            hints[m].append(pkg)
    print("\n== Suggested bridge files ==")
    for k, v in hints.items():
        print(f"- {k}  →  {v[0]}")


if __name__ == "__main__":
    main()
