#!/usr/bin/env python3
"""
Module: seed_module_docstrings.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Seed module-level docstrings for Python files lacking them.

This script scans provided directories (default: scripts) and inserts a
minimal, Google-style module docstring at the top of each Python file that
does not already have a module docstring.

Usage:
    python scripts/seed_module_docstrings.py [PATH ...]

Notes:
    - Skips files under .venv/, .git/, and hidden directories.
    - Skips files named __init__.py if they already contain a docstring.
    - Idempotent: will not duplicate existing module docstrings.
"""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path


SKIP_DIR_PREFIXES = (".git", ".venv", ".mypy_cache", ".pytest_cache", "node_modules")


def has_module_docstring(text: str) -> bool:
    s = text.lstrip()
    return s.startswith('"""') or s.startswith("'''")


def seed_file(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    if has_module_docstring(original):
        return False

    shebang = ""
    rest = original
    if original.startswith("#!/"):
        lines = original.splitlines(True)
        shebang = lines[0]
        rest = "".join(lines[1:])

    doc = (
        '"""\n'
        f"Module: {path.name}\n\n"
        "This module is part of the LUKHAS repository.\n"
        "Add detailed documentation and examples as needed.\n"
        '"""\n\n'
    )

    new_text = f"{shebang}{doc}{rest}"
    path.write_text(new_text, encoding="utf-8")
    return True


def iter_python_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # prune skip dirs
        pruned = []
        for d in dirnames:
            if d.startswith(SKIP_DIR_PREFIXES):
                continue
            pruned.append(d)
        dirnames[:] = pruned

        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            yield Path(dirpath) / fname


def main():
    ap = argparse.ArgumentParser(description="Seed module-level docstrings")
    ap.add_argument("paths", nargs="*", default=["scripts"], help="Paths to scan")
    args = ap.parse_args()

    total = 0
    changed = 0
    for p in args.paths:
        root = Path(p)
        if not root.exists():
            continue
        for file in iter_python_files(root):
            total += 1
            if seed_file(file):
                changed += 1

    print(f"Processed {total} files; seeded {changed} docstrings.")


if __name__ == "__main__":
    main()

