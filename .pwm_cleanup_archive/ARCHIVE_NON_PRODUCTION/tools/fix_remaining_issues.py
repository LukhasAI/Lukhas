#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Additional Fixes Tool

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This tool fixes remaining issues like duplicate docstrings and character encoding.

For more information, visit: https://lukhas.ai
"""

import re
import sys
from pathlib import Path

# ΛTRACE: Additional fixes tool initialization
# ΛORIGIN_AGENT: Claude
# ΛTASK_ID: LUKHAS-FIX-REMAINING-001


def fix_duplicate_docstrings(content: str) -> str:
    """Fix duplicate docstrings in classes."""
    # Pattern to match duplicate docstrings in classes
    pattern = r'(class\s+\w+.*?:\s*\n\s*"""[^"]*"""\s*\n\s*"""[^"]*""")'

    def replace_duplicates(match):
        class_def = match.group(0)
        # Find all docstrings
        docstrings = re.findall(r'"""[^"]*"""', class_def)
        if len(docstrings) >= 2:
            # Keep only the first docstring
            # Remove the second one
            result = class_def.replace(docstrings[1], "", 1)
            # Clean up extra newlines
            result = re.sub(r"\n\s*\n\s*\n", "\n\n", result)
            return result
        return class_def

    content = re.sub(pattern, replace_duplicates, content, flags=re.DOTALL)
    return content


def fix_footer_issues(content: str) -> str:
    """Fix footer issues and duplicate footers."""
    # Remove duplicate footer comments
    lines = content.split("\n")

    # Find and remove duplicate footer patterns
    footer_patterns = [
        r"# LUKHAS AI System Footer",
        r"# lukhas AI System Footer",
        r"# This file is part of the (Λ|lukhas|LUKHAS) cognitive architecture",
        r"# Integrated with:.*",
        r"# Status:.*Component",
        r"# Last Updated:.*",
    ]

    # Track if we've seen a footer section
    footer_start = -1
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if any(re.match(pattern, line) for pattern in footer_patterns):
            if footer_start == -1:
                footer_start = i
            else:
                # We have duplicate footers, remove earlier ones
                lines[i] = ""

    # Rebuild content
    content = "\n".join(lines)

    # Clean up multiple empty lines at the end
    content = re.sub(r"\n\s*\n\s*$", "\n", content)

    return content


def fix_encoding_issues(content: str) -> str:
    """Fix character encoding issues."""
    replacements = [
        ("LUKHAS", "LUKHAS"),  # Replace Lambda symbol in text
        ("AI", "AI"),  # Replace Lambda-I with AI
        ("LUKHAS ", "LUKHAS "),  # Replace standalone Lambda
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    return content


def fix_python_file(filepath: Path, dry_run: bool = False) -> bool:
    """Fix remaining issues in a Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    original_content = content

    # Apply fixes
    content = fix_duplicate_docstrings(content)
    content = fix_footer_issues(content)
    content = fix_encoding_issues(content)

    # Check if changes were made
    if content != original_content:
        if not dry_run:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Fixed remaining issues in: {filepath}")
                return True
            except Exception as e:
                print(f"❌ Error writing {filepath}: {e}")
                return False
        else:
            print(f"Would fix remaining issues in: {filepath}")
            return True

    return False


def main():
    """Main function to fix remaining issues."""
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        dry_run = True
        print("🔍 DRY RUN MODE - No files will be modified")
    else:
        dry_run = False
        print("🔧 FIXING MODE - Files will be updated")

    lukhas_dir = Path(__file__).parent.parent

    # Target specific files we know have issues
    target_files = [
        lukhas_dir / "consciousness/core_consciousness/consciousness_mapper.py",
        lukhas_dir / "core/identity/identity_engine.py",
        lukhas_dir / "core/identity/identity_mapper.py",
        lukhas_dir / "core/identity/identity_processor.py",
        lukhas_dir / "core/identity/persona_engine.py",
        # Add more files as needed
    ]

    # Also find all Python files with potential issues
    all_python_files = list(lukhas_dir.rglob("*.py"))

    print(f"\n📊 Checking {len(target_files)} known problematic files")

    fixed_count = 0

    # Fix known problematic files first
    for filepath in target_files:
        if filepath.exists() and fix_python_file(filepath, dry_run):
            fixed_count += 1

    # Then check all Python files for remaining issues
    print(
        f"\n📊 Checking all {len(all_python_files)} Python files for remaining issues"
    )

    for filepath in all_python_files:
        if filepath not in target_files and fix_python_file(filepath, dry_run):
            fixed_count += 1

    print("\n📈 Summary:")
    print(f"  - Files checked: {len(all_python_files)}")
    print(f"  - Files fixed: {fixed_count}")

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
