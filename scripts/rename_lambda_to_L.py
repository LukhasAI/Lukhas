#!/usr/bin/env python3
"""Safe, opt-in script to replace 'Lambda'/'lambda' tokens with 'L'/'l'.

Usage:
  python scripts/rename_lambda_to_L.py --dry-run
  python scripts/rename_lambda_to_L.py --apply

The script performs a prioritized list of replacements and prints a
summary. It excludes .git, .venv, node_modules, dist, build, and binary files.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

# use PEP 585 built-in generics (list, dict, tuple) for annotations

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}

# Ordered replacements (longer tokens first to avoid double-replacement)
REPLACEMENTS: list[tuple[str, str]] = [
    ("LambdaID", "LID"),
    ("lambda_id", "l_id"),
    ("lambdaId", "lId"),
    ("Lambda", "L"),
    ("lambda", "l"),
    ("LAMBDAID", "LID"),
    ("Λambda", "Λ"),
]


def is_text_file(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(4096)
            if b"\0" in chunk:
                return False
    except Exception:
        return False
    return True


def find_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        # skip excluded directories
        parts = set(Path(dirpath).parts)
        if parts & EXCLUDE_DIRS:
            continue
        for name in filenames:
            path = Path(dirpath) / name
            if not is_text_file(path):
                continue
            files.append(path)
    return files


def apply_replacements_to_text(text: str, replacements: list[tuple[str, str]]) -> tuple[str, int]:
    count = 0
    for old, new in replacements:
        # use plain replace to preserve case mapping defined above
        occurrences = text.count(old)
        if occurrences:
            text = text.replace(old, new)
            count += occurrences
    return text, count


def dry_run(root: Path) -> dict[Path, int]:
    files = find_files(root)
    changes: dict[Path, int] = {}
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        _, c = apply_replacements_to_text(text, REPLACEMENTS)
        if c:
            changes[p] = c
    return changes


def apply_changes(root: Path) -> dict[Path, int]:
    files = find_files(root)
    applied: dict[Path, int] = {}
    for p in files:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text, c = apply_replacements_to_text(text, REPLACEMENTS)
        if c:
            # write backup
            backup = p.with_suffix(p.suffix + ".bak")
            p.rename(backup)
            p.write_text(new_text, encoding="utf-8")
            applied[p] = c
    return applied


def print_summary(changes: dict[Path, int]) -> None:
    total = sum(changes.values())
    print(f"Found {len(changes)} files with {total} total replacements")
    for p, c in sorted(changes.items(), key=lambda x: -x[1])[:50]:
        print(f"{p.relative_to(ROOT)}: {c}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")

    print(f"Scanning {ROOT} (excludes: {', '.join(sorted(EXCLUDE_DIRS))})")
    changes = dry_run(ROOT)
    print_summary(changes)

    if args.apply:
        if not changes:
            print("No changes to apply")
            return
        confirm = input("Proceed to apply replacements and create .bak backups? [y/N]: ")
        if confirm.lower() != "y":
            print("Aborting")
            return
        applied = apply_changes(ROOT)
        print_summary(applied)


if __name__ == "__main__":
    main()
