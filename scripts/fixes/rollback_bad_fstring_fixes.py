#!/usr/bin/env python3
"""
Module: rollback_bad_fstring_fixes.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Rollback Bad F-string Fixes
Fix the malformed f-strings that were created by the original fixer
"""

import os
import re
from pathlib import Path


def rollback_bad_fstring_patterns(content):
    """Roll back and fix malformed f-strings"""
    fixes = 0

    # Pattern 1: Fix malformed f-strings where complex expressions got mangled
    # Look for patterns like f"...{something} more text" -> should be f"...{something} more text"
    pattern1 = r'(f["\'])([^"\']*)\{([^}]+)\}\}([^"\']*)\1'
    matches = re.findall(pattern1, content)
    if matches:
        content = re.sub(pattern1, r"\1\2{\3}\4\1", content)
        fixes += len(matches)

    # Pattern 2: Fix cases where } got duplicated in variable names
    # f"...{len(something)}..." -> f"...{len(something))}..."
    pattern2 = r'(f["\'])([^"\']*)\{([a-zA-Z_][a-zA-Z0-9_]*\([^}]*)\}\}([^"\']*)\1'
    matches = re.findall(pattern2, content)
    if matches:
        content = re.sub(pattern2, r"\1\2{\3}\4\1", content)
        fixes += len(matches)

    # Pattern 3: Fix specific malformed patterns from original regex
    # Replace specific known bad patterns
    bad_patterns = [
        (r"\{([^}]+)\}\}", r"{\1}"),  # Double closing braces
        (r"\}\}", r"}"),  # Just double braces at end
    ]

    for bad, good in bad_patterns:
        matches = re.findall(bad, content)
        if matches:
            content = re.sub(bad, good, content)
            fixes += len(matches)

    return content, fixes


def process_files_rollback():
    """Process all Python files to rollback bad f-string fixes"""
    total_files_fixed = 0
    total_fixes = 0

    print("🔧 Rolling back bad f-string fixes...")

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = Path(root) / file

            try:
                with open(file_path, encoding="utf-8") as f:
                    original_content = f.read()

                fixed_content, fixes_made = rollback_bad_fstring_patterns(original_content)

                if fixes_made > 0:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)

                    total_files_fixed += 1
                    total_fixes += fixes_made

                    print(f"✅ {file_path}: {fixes_made} rollback fixes")

            except Exception:
                continue

    return total_files_fixed, total_fixes


if __name__ == "__main__":
    print("🔧 ROLLBACK BAD F-STRING FIXES")
    print("=" * 50)

    files_fixed, total_fixes = process_files_rollback()

    print("=" * 50)
    print("📊 ROLLBACK RESULTS:")
    print(f"  📁 Files fixed: {files_fixed}")
    print(f"  🔧 Total fixes: {total_fixes}")
    print("=" * 50)
