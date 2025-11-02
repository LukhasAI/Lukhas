#!/usr/bin/env python3
"""
Check Python files for required license headers.

Verifies that all Python files in production code have proper Apache-2.0 headers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# Required header format (can be customized)
REQUIRED_HEADER = """# Copyright (c) 2025 LUKHAS AI
# SPDX-License-Identifier: Apache-2.0""".strip()

# Alternative acceptable formats
ACCEPTABLE_HEADERS = [
    REQUIRED_HEADER,
    "# SPDX-License-Identifier: Apache-2.0",  # Minimal acceptable
]


def check_file_header(file_path: Path) -> bool:
    """
    Check if a Python file has the required license header.

    Returns:
        bool: True if header present, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        # Check first 10 lines for header
        lines = content.split("\n")[:10]
        first_lines = "\n".join(lines)

        # Check if any acceptable header is present
        return any(header in first_lines for header in ACCEPTABLE_HEADERS)

    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)
        return False


def find_python_files(roots: List[Path], exclude_patterns: List[str]) -> List[Path]:
    """
    Find all Python files in given roots, excluding patterns.

    Args:
        roots: List of root directories to search
        exclude_patterns: List of path patterns to exclude

    Returns:
        List of Path objects for Python files
    """
    python_files = []

    for root in roots:
        if not root.exists():
            print(f"[WARN] Directory not found: {root}")
            continue

        for py_file in root.rglob("*.py"):
            # Check if file should be excluded
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            python_files.append(py_file)

    return sorted(python_files)


def add_header_to_file(file_path: Path, header: str, dry_run: bool = False) -> bool:
    """
    Add license header to a Python file.

    Args:
        file_path: Path to Python file
        header: Header text to add
        dry_run: If True, don't actually modify the file

    Returns:
        bool: True if header was added, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        # Handle shebang
        if content.startswith("#!"):
            lines = content.split("\n")
            shebang = lines[0]
            rest = "\n".join(lines[1:]).lstrip()
            new_content = f"{shebang}\n{header}\n\n{rest}"
        else:
            new_content = f"{header}\n\n{content.lstrip()}"

        if dry_run:
            print(f"[DRY-RUN] Would add header to: {file_path}")
        else:
            file_path.write_text(new_content, encoding="utf-8")
            print(f"[FIXED] Added header to: {file_path}")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to add header to {file_path}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check and add license headers to Python files"
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Specific files to check (if not provided, scans directories)"
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        type=Path,
        default=[Path("lukhas"), Path("matriz"), Path("core")],
        help="Directories to scan (default: lukhas, matriz, core)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Add missing headers to files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            "._cleanup_archive", "archive", "backup", "tests", "test_",
            ".pytest_cache", "build", "dist", ".egg-info"
        ],
        help="Path patterns to exclude"
    )

    args = parser.parse_args()

    # Determine files to check
    if args.files:
        python_files = [f for f in args.files if f.suffix == ".py"]
    else:
        print(f"[INFO] Scanning directories: {', '.join(str(d) for d in args.dirs)}")
        python_files = find_python_files(args.dirs, args.exclude)

    if not python_files:
        print("[ERROR] No Python files found to check")
        return 1

    print(f"[INFO] Checking {len(python_files)} Python files")
    if args.fix or args.dry_run:
        print(f"[INFO] Mode: {'DRY-RUN' if args.dry_run else 'FIX'}")
    print()

    # Check files
    missing_headers = []

    for py_file in python_files:
        if not check_file_header(py_file):
            missing_headers.append(py_file)

    # Report results
    if missing_headers:
        print(f"❌ Found {len(missing_headers)} file(s) without proper license headers:")
        print()

        for file_path in missing_headers:
            print(f"  {file_path}")

        print()

        # Fix if requested
        if args.fix or args.dry_run:
            print(f"{'[DRY-RUN] Would add' if args.dry_run else 'Adding'} headers...")
            print()

            fixed_count = 0
            for file_path in missing_headers:
                if add_header_to_file(file_path, REQUIRED_HEADER, args.dry_run):
                    fixed_count += 1

            print()
            if args.dry_run:
                print(f"[DRY-RUN] Would fix {fixed_count} file(s)")
                print("[INFO] Run without --dry-run to apply changes")
            else:
                print(f"[SUCCESS] Fixed {fixed_count} file(s)")
        else:
            print("[INFO] Run with --fix to add missing headers")

        return 1 if not (args.fix and not args.dry_run) else 0

    else:
        print("✅ All files have proper license headers")
        return 0


if __name__ == "__main__":
    sys.exit(main())
