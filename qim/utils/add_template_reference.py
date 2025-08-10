#!/usr/bin/env python3

"""
LUKHAS Template Reference Adder

This script adds the @lukhas/HEADER_FOOTER_TEMPLATE.py reference
right after the ASCII art in all Python files.
"""

import re
from pathlib import Path

# Pattern to find the ASCII art ending
ASCII_END_PATTERN = re.compile(
    r"(╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝)\n", re.MULTILINE
)

# Template reference to add
TEMPLATE_REFERENCE = """
@lukhas/HEADER_FOOTER_TEMPLATE.py
"""


def add_template_reference(filepath: Path) -> bool:
    """Add template reference after ASCII art in a single file."""

    if not filepath.suffix == ".py":
        return False

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Check if file has ASCII art
        match = ASCII_END_PATTERN.search(content)
        if not match:
            return False

        # Check if template reference already exists
        if "@lukhas/HEADER_FOOTER_TEMPLATE.py" in content:
            print(f"  ⏭️  Template reference already exists in {filepath.name}")
            return False

        # Add template reference after ASCII art
        position = match.end()
        new_content = content[:position] + TEMPLATE_REFERENCE + content[position:]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"  ✅ Added template reference to {filepath.name}")
        return True

    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    """Add template reference to all Python files."""

    print("📚 LUKHAS Template Reference Adder 📚")
    print("=" * 50)
    print("Adding: @lukhas/HEADER_FOOTER_TEMPLATE.py")
    print("=" * 50)

    # Start from current quantum directory
    quantum_dir = Path(__file__).parent
    added = 0
    skipped = 0

    # Process all Python files in quantum directory
    for filepath in quantum_dir.glob("*.py"):
        if filepath.name == "add_template_reference.py":
            continue

        result = add_template_reference(filepath)
        if result:
            added += 1
        else:
            skipped += 1

    # Process subdirectories
    for subdir in ["systems", "quantum_meta", "bio", "src"]:
        subdir_path = quantum_dir / subdir
        if subdir_path.exists():
            for filepath in subdir_path.glob("**/*.py"):
                result = add_template_reference(filepath)
                if result:
                    added += 1
                else:
                    skipped += 1

    print("=" * 50)
    print(f"✅ Added reference to: {added} files")
    print(f"⏭️  Skipped: {skipped} files")
    print("\n📚 Template references have been added! 📚")


if __name__ == "__main__":
    main()
