#!/usr/bin/env python3
"""Rewrite PEP 604 unions (`X | None`) to `Optional[X]` for Python 3.9."""

from __future__ import annotations

import io
import os
import re
import sys
from typing import Tuple
from collections.abc import Iterable

OPT_PATTERN = re.compile(r"(\b[A-Za-z_][A-Za-z0-9_.]*\b)\s*\|\s*None\b")


def fix_text(source: str) -> Tuple[str, bool]:
    """Return rewritten source and whether a change was made."""

    changed = False

    def _replace(match: re.Match[str]) -> str:
        nonlocal changed
        changed = True
        return f"Optional[{match.group(1)}]"

    rewritten = OPT_PATTERN.sub(_replace, source)

    if changed and "Optional[" in rewritten and "Optional" not in source:
        rewritten = _ensure_optional_import(rewritten)

    return rewritten, changed


def _ensure_optional_import(source: str) -> str:
    """Insert `from typing import Optional` if missing."""

    lines = source.splitlines()
    insert_at = 0

    # Skip shebang
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    # Skip module docstring and future imports
    while insert_at < len(lines):
        line = lines[insert_at]
        stripped = line.strip()
        if stripped.startswith("from __future__"):
            insert_at += 1
            continue
        if (stripped.startswith('"""') and stripped.count('"""') == 1) or (
            stripped.startswith("'''") and stripped.count("'''") == 1
        ):
            # Skip docstring block
            quote = stripped[:3]
            insert_at += 1
            while insert_at < len(lines) and quote not in lines[insert_at]:
                insert_at += 1
            if insert_at < len(lines):
                insert_at += 1
            continue
        break

    lines.insert(insert_at, "from typing import Optional")
    return "\n".join(lines)


def iter_targets(paths: Iterable[str]) -> Iterable[str]:
    """Yield python file paths under provided targets."""

    for path in paths:
        if os.path.isfile(path) and path.endswith(".py"):
            yield path
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for filename in files:
                    if filename.endswith(".py"):
                        yield os.path.join(root, filename)


def main(argv: Iterable[str]) -> int:
    paths = list(argv)
    if not paths:
        print("Usage: fix_pep604_typing.py <path...>")
        return 1

    for file_path in iter_targets(paths):
        with io.open(file_path, "r", encoding="utf-8") as handle:
            original = handle.read()
        rewritten, changed = fix_text(original)
        if changed:
            with io.open(file_path, "w", encoding="utf-8") as handle:
                handle.write(rewritten)
            print(f"rewrote: {file_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
