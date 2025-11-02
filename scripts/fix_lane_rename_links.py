#!/usr/bin/env python3
"""
Fix lane rename links: candidate/ → labs/

Updates markdown links in docs/** and *.md files from old lane paths to new ones.
Run after lane directory is renamed but before deployment.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple, Optional


def fix_markdown_links(text: str, old_lane: str, new_lane: str) -> Tuple[str, int]:
    """
    Replace old lane path with new in markdown links.
    
    Handles both regular links [text](path) and image links ![alt](path).
    
    Returns:
        tuple: (updated_text, count_of_changes)
    """
    # Pattern matches: [text](candidate/...) or ![alt](candidate/...)
    pattern = rf'(\[!?\[[^\]]*\]\()({old_lane}/[^\)]*)\)'

    changes = 0
    def replacer(match):
        nonlocal changes
        prefix = match.group(1)  # [text]( or ![alt](
        path = match.group(2)     # candidate/path/to/file
        new_path = path.replace(f"{old_lane}/", f"{new_lane}/", 1)
        changes += 1
        return f"{prefix}{new_path})"

    new_text = re.sub(pattern, replacer, text)
    return new_text, changes


def fix_file(file_path: Path, old_lane: str, new_lane: str, dry_run: bool = False) -> int:
    """
    Fix links in a single file.
    
    Returns:
        int: Number of changes made
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}")
        return 0

    new_text, changes = fix_markdown_links(text, old_lane, new_lane)

    if changes > 0:
        if dry_run:
            print(f"[DRY-RUN] Would fix {changes} link(s) in: {file_path}")
        else:
            file_path.write_text(new_text, encoding="utf-8")
            print(f"[FIXED] {changes} link(s) in: {file_path}")

    return changes


def find_markdown_files(root: Path, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
    """
    Find all markdown files in the repository.
    
    Args:
        root: Root directory to search
        exclude_patterns: List of path patterns to exclude
    
    Returns:
        List of Path objects for markdown files
    """
    exclude_patterns = exclude_patterns or [
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "._cleanup_archive", "archive", "backup"
    ]

    markdown_files = []
    for md_file in root.rglob("*.md"):
        # Check if file should be excluded
        if any(pattern in str(md_file) for pattern in exclude_patterns):
            continue
        markdown_files.append(md_file)

    return sorted(markdown_files)


def main():
    parser = argparse.ArgumentParser(
        description="Fix lane rename links in markdown files"
    )
    parser.add_argument(
        "--old-lane",
        default="candidate",
        help="Old lane name (default: candidate)"
    )
    parser.add_argument(
        "--new-lane",
        default="labs",
        help="New lane name (default: labs)"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Root directory to search (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Additional path patterns to exclude"
    )

    args = parser.parse_args()

    # Resolve root path
    root = args.root.resolve()
    if not root.exists():
        print(f"[ERROR] Root directory not found: {root}")
        return 1

    print(f"[INFO] Searching for markdown files in: {root}")
    print(f"[INFO] Renaming links: {args.old_lane}/ → {args.new_lane}/")
    if args.dry_run:
        print("[INFO] DRY-RUN MODE: No files will be modified")
    print()

    # Build exclude list
    exclude_patterns = [
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "._cleanup_archive", "archive", "backup"
    ]
    if args.exclude:
        exclude_patterns.extend(args.exclude)

    # Find all markdown files
    markdown_files = find_markdown_files(root, exclude_patterns)
    print(f"[INFO] Found {len(markdown_files)} markdown files to check")
    print()

    # Fix links in each file
    total_changes = 0
    files_changed = 0

    for md_file in markdown_files:
        changes = fix_file(md_file, args.old_lane, args.new_lane, args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    print()
    print(f"[SUMMARY] Total changes: {total_changes} in {files_changed} file(s)")

    if args.dry_run:
        print("[INFO] Run without --dry-run to apply changes")
        return 0

    if total_changes > 0:
        print("[SUCCESS] Link fixes applied")
        print("[NEXT] Run scripts/check_links.py to verify links")
        return 0
    else:
        print("[INFO] No changes needed")
        return 0


if __name__ == "__main__":
    exit(main())
