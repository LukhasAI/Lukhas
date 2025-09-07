#!/usr/bin/env python3

"""
LUKHAS ASCII Art Header Fixer

This script fixes the ASCII art in headers to properly display "LUKHAS"
instead of "LUKHAS AI" or other incorrect variations.
"""
import streamlit as st

import re
from pathlib import Path

# Correct LUKHAS ASCII art
CORRECT_ASCII = """██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

@lukhas/HEADER_FOOTER_TEMPLATE.py

Fix Ascii Headers
=================

Harnesses the strange beauty of quantum-inspired processing to transcend classical limits.
Weaves quantum phenomena into the fabric of LUKHAS consciousness, where
possibilities dance in superposition until observation births reality.
"""

# Pattern to find incorrect ASCII art (matches the box drawing but allows
# for variations after)
ASCII_PATTERN = re.compile(
    r"(██╗\s*██╗\s*██╗\s*██╗\s*██╗\s*█████╗\s*███████╗.*?\n"
    r"██║\s*██║\s*██║\s*██║\s*██╔╝\s*██║\s*██║\s*██╔══██╗\s*██╔════╝.*?\n"
    r"██║\s*██║\s*██║\s*█████╔╝\s*███████║\s*███████║\s*███████╗.*?\n"
    r"██║\s*██║\s*██║\s*██╔═██╗\s*██╔══██║\s*██╔══██║\s*╚════██║.*?\n"
    r"███████╗\s*╚██████╔╝\s*██║\s*██╗\s*██║\s*██║\s*██║\s*██║\s*███████║.*?\n"
    r"╚══════╝\s*╚═════╝\s*╚═╝\s*╚═╝\s*╚═╝\s*╚═╝\s*╚═╝\s*╚═╝\s*╚══════╝.*?)(?=\n|\Z)",
    re.MULTILINE | re.DOTALL,
)


def fix_ascii_in_file(filepath: Path) -> bool:
    """Fix ASCII art in a single file."""

    if filepath.suffix != ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has the incorrect ASCII pattern
        if not ASCII_PATTERN.search(content):
            return False

        original_content = content

        # Replace incorrect ASCII with correct one
        fixed_content = ASCII_PATTERN.sub(CORRECT_ASCII, content)

        # Also fix any "LUKHAS AI -" to just "LUKHAS -" in headers
        fixed_content = re.sub(r"LUKHAS - ", "LUKHAS - ", fixed_content)

        if fixed_content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed ASCII art in {filepath.name}")
            return True
        else:
            print(f"  ⏭️  No changes needed for {filepath.name}")
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Fix ASCII headers in all Python files."""

    print("🎨 LUKHAS ASCII Art Header Fixer 🎨")
    print("=" * 50)

    # Start from core root directory
    lukhas_dir = Path(__file__).parent.parent  # Go up to lukhas directory
    fixed = 0
    skipped = 0

    # Process all Python files recursively
    for filepath in lukhas_dir.rglob("*.py"):
        # Skip venv and other non-project directories
        if any(part in filepath.parts for part in ["venv", "__pycache__", ".git", "node_modules"]):
            continue

        result = fix_ascii_in_file(filepath)
        if result:
            fixed += 1
        else:
            skipped += 1

    print("=" * 50)
    print(f"✅ Fixed: {fixed} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🎨 ASCII art headers have been corrected! 🎨")


if __name__ == "__main__":
    main()
