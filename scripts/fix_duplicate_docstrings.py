#!/usr/bin/env python3
"""
Fix duplicate module docstrings caused by the seeder script.

This script removes the generic "Module: filename.py" docstring
and keeps only the more descriptive second docstring.

Usage:
    python scripts/fix_duplicate_docstrings.py [--dry-run]
"""

import argparse
from pathlib import Path


def has_duplicate_docstring(content: str) -> bool:
    """Check if file has duplicate docstrings."""
    # Count triple-quote pairs in first 50 lines
    lines = content.splitlines()[:50]
    first_50 = "\n".join(lines)
    quote_count = first_50.count('"""')
    return quote_count >= 4


def fix_file(path: Path, dry_run: bool = False) -> bool:
    content = path.read_text()
    lines = content.splitlines()
    
    # Try to remove it
    fixed_lines = []
    i = 0
    removed = False

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a generic docstring
        if line.strip().startswith('"""') and not removed:
            # Collect the full docstring
            docstring_lines = [line]
            i += 1
            while i < len(lines):
                docstring_lines.append(lines[i])
                if '"""' in lines[i] and i > len(fixed_lines):
                    i += 1
                    break
                i += 1

            docstring = "".join(docstring_lines)

            # Check if it's the generic one
            if "Module:" in docstring and "This module is part of the LUKHAS repository" in docstring:
                # Skip it (remove it)
                removed = True
                # Skip blank line after if present
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
                continue
            else:
                # Keep it
                fixed_lines.extend(docstring_lines)
        else:
            fixed_lines.append(line)
            i += 1

    if not removed:
        return False

    if dry_run:
        print(f"  [DRY RUN] Would fix: {path}")
        return True

    # Write the fixed content
    path.write_text("".join(fixed_lines))
    print(f"  ✅ Fixed: {path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Fix duplicate module docstrings")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without changing files")
    parser.add_argument("paths", nargs="*", default=["scripts"], help="Paths to scan")
    args = parser.parse_args()

    total = 0
    fixed = 0

    for root_path in args.paths:
        root = Path(root_path)
        if not root.exists():
            continue

        for py_file in root.rglob("*.py"):
            # Skip directories
            if any(skip in str(py_file) for skip in [".venv", ".git", "__pycache__", "node_modules"]):
                continue

            total += 1
            if fix_file(py_file, dry_run=args.dry_run):
                fixed += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Processed {total} files; fixed {fixed} files")

    if args.dry_run:
        print("\nRun without --dry-run to apply fixes")


if __name__ == "__main__":
    main()
