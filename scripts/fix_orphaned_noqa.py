#!/usr/bin/env python3
"""
Fix Orphaned noqa Comments from PR 375
======================================
Removes orphaned # noqa: F821 and # noqa: invalid-syntax comments
that were left behind after TODO removal.

Problem:
    Codex removed TODOs but left noqa markers:
    Before: log = logging.getLogger(__name__)  # noqa: F821  # TODO: logging
    After:  log = logging.getLogger(__name__)  # noqa: F821

    These noqa comments are now orphaned and meaningless.

Solution:
    Remove trailing noqa comments that appear at end of line without context.

Usage:
    python3 scripts/fix_orphaned_noqa.py --dry-run  # Preview changes
    python3 scripts/fix_orphaned_noqa.py --apply    # Apply fixes
"""

import argparse
import re
from pathlib import Path
from typing import List, Tuple

# Patterns for orphaned noqa comments
PATTERNS = [
    (r'  # noqa: F821$', ''),           # Two spaces + noqa F821
    (r' # noqa: F821$', ''),            # One space + noqa F821
    (r'  # noqa: invalid-syntax$', ''), # Two spaces + noqa invalid-syntax
    (r' # noqa: invalid-syntax$', ''),  # One space + noqa invalid-syntax
]


def find_python_files(roots: List[str]) -> List[Path]:
    """Find all Python files in specified roots."""
    files = []
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        files.extend(root_path.rglob("*.py"))
    return sorted(files)


def fix_file(file_path: Path, dry_run: bool = True) -> Tuple[int, List[str]]:
    """
    Fix orphaned noqa comments in a file.

    Returns:
        (changes_made, changed_lines)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return 0, []

    original_lines = content.splitlines(keepends=True)
    modified_lines = original_lines[:]
    changes = 0
    changed_line_numbers = []

    for i, line in enumerate(modified_lines):
        original_line = line

        # Apply all patterns
        for pattern, replacement in PATTERNS:
            if re.search(pattern, line):
                line = re.sub(pattern, replacement, line)

        if line != original_line:
            modified_lines[i] = line
            changes += 1
            changed_line_numbers.append(f"L{i+1}: {original_line.rstrip()} → {line.rstrip()}")

    if changes > 0 and not dry_run:
        try:
            file_path.write_text(''.join(modified_lines), encoding='utf-8')
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return 0, []

    return changes, changed_line_numbers


def main():
    parser = argparse.ArgumentParser(
        description="Fix orphaned noqa comments from PR 375"
    )
    parser.add_argument(
        '--roots',
        nargs='+',
        default=['candidate', 'core'],
        help='Root directories to scan (default: candidate core)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply fixes (default is dry-run)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show all changes line by line'
    )

    args = parser.parse_args()
    dry_run = not args.apply

    print(f"🔍 Scanning for orphaned noqa comments...")
    print(f"📂 Roots: {', '.join(args.roots)}")
    print(f"🎯 Mode: {'DRY RUN' if dry_run else 'APPLY FIXES'}")
    print()

    files = find_python_files(args.roots)
    print(f"📄 Found {len(files)} Python files")
    print()

    total_changes = 0
    files_modified = 0

    for file_path in files:
        changes, changed_lines = fix_file(file_path, dry_run=dry_run)

        if changes > 0:
            files_modified += 1
            total_changes += changes
            try:
                rel_path = file_path.relative_to(Path.cwd())
            except ValueError:
                rel_path = file_path

            if args.verbose:
                print(f"✏️  {rel_path} ({changes} changes)")
                for change in changed_lines:
                    print(f"    {change}")
                print()
            else:
                print(f"✏️  {rel_path}: {changes} changes")

    print()
    print("=" * 70)
    print(f"{'DRY RUN ' if dry_run else ''}SUMMARY:")
    print(f"  Files scanned:   {len(files)}")
    print(f"  Files modified:  {files_modified}")
    print(f"  Total changes:   {total_changes}")
    print("=" * 70)

    if dry_run and total_changes > 0:
        print()
        print("🚀 Run with --apply to make these changes")
        print("💡 Use --verbose to see line-by-line changes")
    elif not dry_run and total_changes > 0:
        print()
        print("✅ Changes applied successfully!")
        print("⚠️  Don't forget to:")
        print("   1. Run tests: make smoke")
        print("   2. Check syntax: ruff check candidate/ core/")
        print("   3. Commit: git add -A && git commit")


if __name__ == "__main__":
    main()
