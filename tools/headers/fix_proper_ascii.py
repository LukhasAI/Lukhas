#!/usr/bin/env python3
from __future__ import annotations

"""
LUKHAS Proper ASCII Art Fixer

This script fixes the ASCII art to properly display "LUKHAS"
with correct alignment and characters.
"""

import re
from pathlib import Path

# Correct LUKHAS ASCII art
CORRECT_LUKHAS_ASCII = """██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"""

# Pattern to find any corrupted ASCII art that starts with box drawing characters
ASCII_PATTERN = re.compile(
    r"(██╗.*?███████╗\s*\n"
    r"██║.*?██╔════╝\s*\n"
    r"██║.*?███████╗\s*\n"
    r"██║.*?╚════██║\s*\n"
    r"███████╗.*?███████║\s*\n"
    r"╚══════╝.*?╚══════╝)",
    re.MULTILINE | re.DOTALL,
)


def fix_ascii_in_file(filepath: Path) -> bool:
    """Fix ASCII art in a single file."""

    if filepath.suffix != ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has any ASCII pattern
        if not ASCII_PATTERN.search(content):
            return False

        original_content = content

        # Replace any found ASCII with correct LUKHAS ASCII
        fixed_content = ASCII_PATTERN.sub(CORRECT_LUKHAS_ASCII, content)

        if fixed_content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"  ✅ Fixed LUKHAS ASCII art in {filepath.name}")
            return True
        else:
            return False

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Fix LUKHAS ASCII art in all Python files."""

    print("🎨 LUKHAS Proper ASCII Art Fixer 🎨")
    print("=" * 50)
    print("Correct LUKHAS ASCII art:")
    print(CORRECT_LUKHAS_ASCII)
    print("=" * 50)

    # Start from current quantum directory
    qi_dir = Path(__file__).parent
    fixed = 0
    skipped = 0

    # Process all Python files in quantum directory
    for filepath in qi_dir.glob("*.py"):
        if filepath.name == "fix_proper_lukhas_ascii.py":
            continue

        result = fix_ascii_in_file(filepath)
        if result:
            fixed += 1
        else:
            skipped += 1

    # Process subdirectories
    for subdir in ["systems", "qi_meta", "bio", "src"]:
        subdir_path = qi_dir / subdir
        if subdir_path.exists():
            for filepath in subdir_path.glob("**/*.py"):
                result = fix_ascii_in_file(filepath)
                if result:
                    fixed += 1
                else:
                    skipped += 1

    print("=" * 50)
    print(f"✅ Fixed: {fixed} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n🎨 LUKHAS ASCII art has been properly fixed! 🎨")


if __name__ == "__main__":
    main()
