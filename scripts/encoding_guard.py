#!/usr/bin/env python3
"""
Module: encoding_guard.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
LUKHAS Documentation Encoding Guard (T4/0.01%)

Scans all .md files for non-UTF-8 encoding and provides --apply mode to rewrite.
Integrates with docs_lint.py for CI enforcement.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

# Excluded directories
EXCLUDED_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', '.venv',
    '_generated', '_inventory', 'archive'
}


def check_encoding(file_path: Path) -> Tuple[bool, str]:
    """
    Check if file is valid UTF-8.
    Returns (is_valid, encoding_detected).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True, 'utf-8'
    except UnicodeDecodeError:
        # Try common encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return False, encoding
            except (UnicodeDecodeError, LookupError):
                continue
        return False, 'unknown'


def rewrite_to_utf8(file_path: Path, source_encoding: str) -> bool:
    """
    Rewrite file from source_encoding to UTF-8.
    Returns True if successful.
    """
    try:
        # Read with source encoding
        with open(file_path, 'r', encoding=source_encoding, errors='replace') as f:
            content = f.read()

        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.rename(backup_path)

        # Write as UTF-8
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

        print(f"   ✅ Rewritten: {file_path} ({source_encoding} → UTF-8)")

        # Remove backup on success
        backup_path.unlink()
        return True

    except Exception as e:
        print(f"   ❌ Failed to rewrite {file_path}: {e}")
        # Restore from backup if it exists
        if backup_path.exists():
            backup_path.rename(file_path)
        return False


def scan_docs(apply: bool = False) -> Tuple[List[Path], List[Path]]:
    """
    Scan all .md files for encoding issues.
    Returns (non_utf8_files, failed_rewrites).
    """
    non_utf8_files = []
    failed_rewrites = []

    for md_file in DOCS_ROOT.rglob("*.md"):
        # Skip excluded directories
        if any(excluded in md_file.parts for excluded in EXCLUDED_DIRS):
            continue

        is_valid, detected_encoding = check_encoding(md_file)

        if not is_valid:
            non_utf8_files.append((md_file, detected_encoding))

            if apply:
                success = rewrite_to_utf8(md_file, detected_encoding)
                if not success:
                    failed_rewrites.append(md_file)

    return non_utf8_files, failed_rewrites


def main():
    """Main workflow."""
    print("=" * 80)
    print("LUKHAS Documentation Encoding Guard (T4/0.01%)")
    print("=" * 80)
    print()

    # Parse flags
    apply = '--apply' in sys.argv
    dry_run = not apply

    if dry_run:
        print("🔍 DRY-RUN MODE (use --apply to rewrite files)")
    else:
        print("⚠️  APPLY MODE - Will rewrite non-UTF-8 files to UTF-8")

    print()

    # Scan
    print(f"📂 Scanning {DOCS_ROOT} for non-UTF-8 files...")
    non_utf8_files, failed_rewrites = scan_docs(apply=apply)

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()

    if not non_utf8_files:
        print("✅ All markdown files are UTF-8 encoded!")
        return 0

    if dry_run:
        print(f"❌ Found {len(non_utf8_files)} file(s) with non-UTF-8 encoding:")
        print()
        for file_path, encoding in non_utf8_files:
            rel_path = file_path.relative_to(REPO_ROOT)
            print(f"  - {rel_path} (detected: {encoding})")
        print()
        print("To fix these files, run:")
        print("  python3 scripts/encoding_guard.py --apply")
        print()
        return 1

    else:  # apply mode
        success_count = len(non_utf8_files) - len(failed_rewrites)
        print(f"✅ Successfully rewritten: {success_count}/{len(non_utf8_files)} files")

        if failed_rewrites:
            print()
            print(f"❌ Failed to rewrite {len(failed_rewrites)} file(s):")
            for file_path in failed_rewrites:
                rel_path = file_path.relative_to(REPO_ROOT)
                print(f"  - {rel_path}")
            print()
            return 1

        print()
        print("🎯 All files now UTF-8 encoded!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
