#!/usr/bin/env python3
"""
Quick f-string fixer for single brace errors
Fixes patterns like f"text{variable}" where } is missing
"""

import os
import re
from pathlib import Path


def fix_f_string_single_brace(content: str) -> str:
    """Fix f-string single '}' errors by adding missing closing brace"""

    # Pattern to match f-strings with single } (missing closing brace)
    # This looks for f"...{something" followed by more content
    patterns_to_fix = [
        # Basic pattern: f"text{var" -> f"text{var}"
        (r'f"([^"]*)\{([^}]+)\"(?=[^}])', r'f"\1{\2}"'),
        # With additional text: f"text{var" more -> f"text{var}" more
        (r'f"([^"]*)\{([^}]+)"(\s*[,\)\]\s])', r'f"\1{\2}"\3'),
    ]

    original_content = content
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)

    # Also fix obvious single } cases in f-strings
    # Look for f-strings that have { but end without }
    content = re.sub(r'f"([^"]*\{[^}]*)"(?=[\s,\)\]])', r'f"\1}"', content)

    if content != original_content:
        print("  Fixed f-string single brace error")

    return content


def process_file(file_path: Path) -> bool:
    """Process a single file and fix f-string errors"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        fixed_content = fix_f_string_single_brace(content)

        if fixed_content != content:
            print(f"Fixing: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix f-string errors in key directories"""
    base_dir = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    # Focus on the most critical directories
    directories = ["candidate/bio", "candidate/audit", "candidate/bridge/adapters", "tools/scripts"]

    total_fixes = 0

    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            continue

        print(f"\nProcessing {directory}...")

        # Find all Python files
        for py_file in dir_path.rglob("*.py"):
            if process_file(py_file):
                total_fixes += 1

    print(f"\n🎯 Fixed f-string errors in {total_fixes} files")


if __name__ == "__main__":
    main()
