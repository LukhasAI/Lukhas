#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Fix Corrupted Text

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This tool fixes all corrupted LUKHAS text variations in the codebase.

For more information, visit: https://lukhas.ai
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ΛTRACE: Corrupted text fix tool initialization
# ΛORIGIN_AGENT: Claude
# ΛTASK_ID: LUKHAS-CORRUPTED-FIX-001

# All known corrupted patterns and their corrections
CORRUPTED_PATTERNS = [
    # Main corrupted variations
    (r"LUKHlukhasS", "LUKHAS"),
    (r"LUKHlukhas", "LUKHAS"),
    (r"lukhasI", "AI"),
    (r"ΛI", "AI"),
    (r"LUKHΛS", "LUKHAS"),
    (r"Lukhʌs", "LUKHAS"),  # New pattern found
    # Full phrase corruptions
    (r"LUKHlukhasS lukhasI", "LUKHAS AI"),
    (r"LUKHlukhas AI", "LUKHAS AI"),
    (r"LUKHlukhasS Core", "LUKHAS Core"),
    (r"LUKHlukhasS Multi-Brain", "LUKHAS Multi-Brain"),
    (r"LUKHlukhasS Tutorial", "LUKHAS Tutorial"),
    (r"LUKHlukhasS Philosophy", "LUKHAS Philosophy"),
    (r"LUKHlukhasS Ecosystem", "LUKHAS Ecosystem"),
    # Specific system references
    (r"LUKHlukhas AI SYSTEMS", "LUKHAS AI SYSTEMS"),
    (r"Λ AI System", "LUKHAS AI System"),
    (r"Λ core consciousness system", "LUKHAS core consciousness system"),
    (r"Λ cognitive architecture", "LUKHAS cognitive architecture"),
    (r"Lukhʌs Brain", "LUKHAS Brain"),  # New pattern
    (r"Lukhʌs Radar", "LUKHAS Radar"),  # New pattern
    # Standalone Lambda that should be LUKHAS
    (r"(?<!\w)Λ(?!\w)", "LUKHAS"),  # Lambda not part of another word
]


def fix_corrupted_text(content: str) -> Tuple[str, Dict[str, int]]:
    """Fix corrupted LUKHAS text and return fixed content with change counts."""
    change_counts = {}

    for pattern, replacement in CORRUPTED_PATTERNS:
        # Count occurrences before replacement
        matches = re.findall(pattern, content)
        if matches:
            change_counts[pattern] = len(matches)
            content = re.sub(pattern, replacement, content)

    return content, change_counts


def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped."""
    skip_patterns = [
        "fix_corrupted_lukhas.py",  # Skip this script
        "fix_lukhas_headers.py",  # Skip other fix scripts
        "fix_remaining_issues.py",
        ".git/",
        "__pycache__/",
        ".pyc",
        "LUKHAS_DEFINITION_AUDIT_REPORT.md",  # Skip reports that document the issues
    ]

    filepath_str = str(filepath)
    return any(pattern in filepath_str for pattern in skip_patterns)


def fix_file(filepath: Path, dry_run: bool = False) -> Tuple[bool, Dict[str, int]]:
    """Fix corrupted text in a single file."""
    if should_skip_file(filepath):
        return False, {}

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, {}

    original_content = content
    fixed_content, change_counts = fix_corrupted_text(content)

    if fixed_content != original_content:
        if not dry_run:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"✅ Fixed: {filepath}")
                for pattern, count in change_counts.items():
                    print(f"   - Fixed '{pattern}' {count} time(s)")
                return True, change_counts
            except Exception as e:
                print(f"❌ Error writing {filepath}: {e}")
                return False, {}
        else:
            print(f"Would fix: {filepath}")
            for pattern, count in change_counts.items():
                print(f"   - Would fix '{pattern}' {count} time(s)")
            return True, change_counts

    return False, {}


def find_all_text_files(directory: Path) -> List[Path]:
    """Find all text files that might contain LUKHAS references."""
    text_extensions = [
        ".py",
        ".md",
        ".txt",
        ".yml",
        ".yaml",
        ".json",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
    ]
    files = []

    for ext in text_extensions:
        files.extend(directory.rglob(f"*{ext}"))

    return files


def main():
    """Main function to fix all corrupted LUKHAS text."""
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run = True
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        dry_run = False
        print("🔧 FIXING MODE - Files will be updated")

    lukhas_dir = Path(__file__).parent.parent  # Go up from tools to lukhas
    text_files = find_all_text_files(lukhas_dir)

    print(f"\n📊 Found {len(text_files)} text files to check")

    fixed_count = 0
    total_changes = {}

    for filepath in text_files:
        fixed, changes = fix_file(filepath, dry_run)
        if fixed:
            fixed_count += 1
            for pattern, count in changes.items():
                total_changes[pattern] = total_changes.get(pattern, 0) + count

    print("\n📈 Summary:")
    print(f"  - Files checked: {len(text_files)}")
    print(f"  - Files fixed: {fixed_count}")

    if total_changes:
        print("\n📊 Total changes by pattern:")
        for pattern, count in sorted(
            total_changes.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - '{pattern}': {count} occurrences")

    if dry_run and fixed_count > 0:
        print("\n💡 Run without --dry-run to apply changes")


if __name__ == "__main__":
    main()

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
