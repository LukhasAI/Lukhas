"""Apply-mode codemod: constellation -> constellation (code-only)

This script applies a conservative set of identifier and constant
replacements to Python source files only. It was designed to be
safe-for-review:

- Operates only on .py files within specified directories (default set)
- Creates a .bak file for each file it edits
- Makes minimal identifier-aware replacements (not free-text docs)
- Prints a summary of changed files

Usage (recommended):
    python scripts/codemods/trinity_to_constellation_apply.py --paths lukhas core candidate trace tools scripts

Run this on a feature branch and review changes before pushing.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Conservative replacements (identifier-aware)
REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bTRINITY_FRAMEWORK\b"), "CONSTELLATION_FRAMEWORK"),
    (re.compile(r"\bget_trinity_context\b"), "get_constellation_context"),
    (re.compile(r"\btrinity_framework\b"), "constellation_framework"),
    (re.compile(r"\btrinity_descriptions\b"), "constellation_descriptions"),
    # case variations for identifiers
    (re.compile(r"\bTrinityFramework\b"), "ConstellationFramework"),
    (re.compile(r"\btrinity\b"), "constellation"),
]

# Default code dirs to operate on
DEFAULT_PATHS = ["lukhas", "core", "candidate", "trace", "tools", "scripts"]


def iter_py_files(paths: Iterable[str]) -> Iterable[Path]:
    for p in paths:
        root = (ROOT / p).resolve()
        if not root.exists():
            continue
        for fp in root.rglob("*.py"):
            # skip virtual envs and common build dirs
            if any(part.startswith(".") for part in fp.parts):
                # allow files like .something only if explicit; conservative skip
                if ".venv" in fp.parts or "venv" in fp.parts:
                    continue
            yield fp


def apply_replacements_to_text(text: str) -> tuple[str, int]:
    changed = 0
    new_text = text
    for pattern, repl in REPLACEMENTS:
        new_text, n = pattern.subn(repl, new_text)
        changed += n
    return new_text, changed


def backup_and_write(path: Path, new_text: str) -> None:
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        path.replace(path)  # no-op to ensure permission errors surface early
    # create backup copy
    with open(path, encoding="utf-8") as fh:
        orig = fh.read()
    with open(str(bak), "w", encoding="utf-8") as fh:
        fh.write(orig)
    # write new content
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(new_text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="*", default=DEFAULT_PATHS, help="Directories to scan (relative to repo root)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Only print would-change files")
    args = parser.parse_args(argv or [])

    changed_files = []
    total_replacements = 0

    for fp in iter_py_files(args.paths):
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text, count = apply_replacements_to_text(text)
        if count > 0:
            total_replacements += count
            changed_files.append((fp, count))
            if args.dry_run:
                print(f"DRY: {fp} ({count} replacements)")
            else:
                print(f"Patching {fp} ({count} replacements)")
                backup_and_write(fp, new_text)

    if not changed_files:
        print("No code-level replacements needed.")
        return 0

    print("\nSummary:")
    for fp, count in changed_files:
        print(f" - {fp}: {count} replacements")
    print(f"Total replacements: {total_replacements}")

    if args.dry_run:
        print("Dry-run complete. Re-run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())