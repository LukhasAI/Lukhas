#!/usr/bin/env python3

"""
Utility script to remove trailing whitespace from Python files
"""

from pathlib import Path


def clean_trailing_whitespace(file_path):
    """Remove trailing whitespace from a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Remove trailing whitespace from each line
        lines = content.split("\n")
        cleaned_lines = [line.rstrip() for line in lines]
        cleaned_content = "\n".join(cleaned_lines)

        # Only write if changes were made
        if content != cleaned_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Clean trailing whitespace from all Python files."""
    repo_root = Path(__file__).parent.parent
    cleaned_count = 0

    # Find all Python files
    for py_file in repo_root.rglob("*.py"):
        # Skip archived and venv files
        if "archived" in str(py_file) or ".venv" in str(py_file):
            continue

        if clean_trailing_whitespace(py_file):
            cleaned_count += 1
            print(f"Cleaned: {py_file.relative_to(repo_root)}")

    print(f"\nTotal files cleaned: {cleaned_count}")


if __name__ == "__main__":
    main()
