"""Dry-run codemod: constellation -> constellation

This script searches the repository for likely places to update the "constellation"
terminology and prints suggested replacements without modifying files. It's
conservative: it only reports matches and shows a suggested replacement.

Usage (dry-run):
    python scripts/codemods/trinity_to_constellation_dryrun.py --dry-run

Options:
    --apply    # Not implemented for safety; this script currently only reports

Notes:
- Skips common virtualenv/build directories and binary files.
- Reports surrounding context for reviewer convenience.
"""

from __future__ import annotations

import argparse
import os
import re
from collections.abc import Iterable
from re import Pattern

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Exclude heavy or generated dirs
EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    ".venv3.11",
    ".venv_ruff",
    ".venv_metrics",
    ".venv_count",
    "dist",
    "build",
    "__pycache__",
    "env",
    "venv",
    "site-packages",
    "docs/_build",
}

# File patterns to scan
SCAN_EXTS = {".py", ".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".ini", ".cfg", ".html", ".js", ".ts", ".css"}

# Replacement rules: pattern -> suggested replacement template
# We include identifier-aware patterns and phrase replacements.
REPLACEMENTS: list[tuple[Pattern, str]] = [
    (re.compile(r"\bTRINITY\b"), "CONSTELLATION"),
    (re.compile(r"\bTrinity\b"), "Constellation"),
    (re.compile(r"\btrinity\b"), "constellation"),
    # identifiers
    (re.compile(r"\bget_trinity_context\b"), "get_constellation_context"),
    (re.compile(r"\bTRINITY_FRAMEWORK\b"), "CONSTELLATION_FRAMEWORK"),
    (re.compile(r"\btrinity_framework\b"), "constellation_framework"),
    (re.compile(r"\btrinity_descriptions\b"), "constellation_descriptions"),
    (re.compile(r"\bTrinity Framework\b"), "Constellation Framework"),
]

CONTEXT_LINES = 1


def should_skip_dir(path: str) -> bool:
    parts = set(p for p in path.split(os.sep) if p)
    return bool(parts & EXCLUDE_DIRS)


def iter_files(root: str) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        # mutate dirnames in-place to skip excluded dirs
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if should_skip_dir(dirpath):
            continue
        for fn in filenames:
            _, ext = os.path.splitext(fn)
            if ext.lower() in SCAN_EXTS:
                yield os.path.join(dirpath, fn)


def scan_file(path: str) -> list[tuple[int, int, str, str]]:
    """Return list of (lineno, col, original, suggestion) matches."""
    results = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception:
        return results

    for i, line in enumerate(lines, start=1):
        for pattern, repl in REPLACEMENTS:
            for m in pattern.finditer(line):
                col = m.start() + 1
                orig = m.group(0)
                suggestion = pattern.sub(repl, orig)
                # For identifier patterns, suggestion is fine; for plain words ensure case mapping
                results.append((i, col, orig, suggestion))
    return results


def print_match(path: str, lineno: int, col: int, orig: str, suggestion: str, context: list[str]) -> None:
    print(f"{path}:{lineno}:{col}: {orig} -> {suggestion}")
    for ctx_lineno, ctx_line in context:
        prefix = "-->" if ctx_lineno == lineno else "   "
        print(f"{prefix} {ctx_lineno:4d}: {ctx_line.rstrip()}")
    print()


def get_context(lines: list[str], lineno: int, ctx: int = CONTEXT_LINES) -> list[tuple[int, str]]:
    start = max(1, lineno - ctx)
    end = min(len(lines), lineno + ctx)
    return [(i, lines[i - 1]) for i in range(start, end + 1)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True, help="Only report, do not modify files")
    args = parser.parse_args(argv or [])

    repo = ROOT
    print(f"Scanning {repo} (dry-run={args.dry_run})")

    total_matches = 0
    matches_by_file = {}
    for path in iter_files(repo):
        matches = scan_file(path)
        if not matches:
            continue
        # read file lines once for context printing
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for lineno, col, orig, suggestion in matches:
            total_matches += 1
            matches_by_file.setdefault(path, []).append((lineno, col, orig, suggestion))

    if not matches_by_file:
        print("No candidate occurrences found.")
        return 0

    print(f"Found {total_matches} candidate occurrences in {len(matches_by_file)} file(s).\n")

    # Print top-level summary and a per-file snippet list
    for path, items in sorted(matches_by_file.items()):
        print(f"== {path} ==")
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
        for lineno, col, orig, suggestion in items:
            ctx = get_context(lines, lineno)
            print_match(path, lineno, col, orig, suggestion, ctx)

    print("Dry-run complete. Review the suggestions above and run a codemod/patch in a feature branch when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
