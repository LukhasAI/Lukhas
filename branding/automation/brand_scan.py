#!/usr/bin/env python3
"""
Brand terminology scanner

Policy:
- Disallow any usage of 'quantum' unless immediately qualified as
  'quantum-inspired' or 'quantum metaphors' (case-insensitive).

Scan scope:
- Textual docs by default: .md, .txt, .rst, .html
- Skips heavy/archival dirs by default.

Exit codes:
- 0: no violations
- 1: violations found

Usage:
  python tools/ci/brand_scan.py [root_dir]
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()

INCLUDE_EXT = {".md", ".txt", ".rst", ".html"}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "._cleanup_archive",
    "archive",
    "recovery",
    "dist",
    "build",
}

# Flag any 'quantum' token not followed by 'inspired' or 'metaphor(s)'
RE_BARE_QUANTUM = re.compile(
    r"\bquantum\b(?![\s-]?(?:inspired|metaphor|metaphors))", re.IGNORECASE
)
RE_ALLOWED_LINE = re.compile(
    r"(quantum-inspired|quantum\s+metaphors|post[- ]?quantum|quantum[- ]?(secure|safe|resistant))",
    re.IGNORECASE,
)


def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in INCLUDE_EXT:
            continue
        # Skip excluded dirs
        parts = set(p.parts)
        if parts & EXCLUDE_DIRS:
            continue
        yield p


def scan_file(path: Path) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return out
    in_codeblock = False
    fence = None
    for i, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
        # Basic markdown fence tracking (```) and (~~~)
        if path.suffix.lower() in {".md", ".rst"}:
            if not in_codeblock and (
                line.strip().startswith("```") or line.strip().startswith("~~~")
            ):
                in_codeblock = True
                fence = line.strip()[:3]
                continue
            if in_codeblock and line.strip().startswith(fence or "```"):
                in_codeblock = False
                fence = None
                continue
        if in_codeblock:
            continue
        # Skip lines that already contain acceptable qualifiers or cryptographic terms
        if RE_ALLOWED_LINE.search(line):
            continue
        if RE_BARE_QUANTUM.search(line):
            out.append((i, line.strip()))
    return out


def main() -> int:
    violations: list[tuple[Path, int, str]] = []
    for f in iter_files(ROOT):
        hits = scan_file(f)
        for ln, snippet in hits:
            violations.append((f, ln, snippet))

    if violations:
        print("Brand Guard: Found unqualified 'quantum' usage.")
        for f, ln, snip in violations:
            print(f" - {f}:{ln}: {snip}")
        print(
            "\nPolicy: Use 'quantum-inspired' or 'quantum metaphors' instead of bare 'quantum'."
        )
        return 1

    print("Brand Guard: no violations found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
