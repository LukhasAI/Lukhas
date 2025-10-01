#!/usr/bin/env python3
"""
Guard script to enforce canonical module naming conventions.
Ensures all module directories follow ^[a-z0-9_]+$ pattern.
"""

import sys
import pathlib
import re

def main():
    """Check all directories for naming violations."""
    bad_names = []
    ignore_patterns = {
        ".", "..", ".git", ".claude", "__pycache__", ".pytest_cache",
        ".venv", "venv", "node_modules", ".DS_Store"
    }

    # Special files/dirs that don't need to follow module naming
    special_patterns = {
        r".*\.code-workspace$",  # VS Code workspace files
        r".*\.egg-info$",        # Python package info
        r"mcp-.*",               # MCP server directories
        r"requirements-.*\.(txt|in)$",  # Requirements files
        r".*\.(json|xml|yaml|yml|md|txt|in)$",  # Regular files
        r"\..*",                 # Hidden files/dirs
    }

    root_path = pathlib.Path(".")

    for item in root_path.iterdir():
        if not item.is_dir():
            continue

        name = item.name

        # Skip ignored patterns
        if name in ignore_patterns:
            continue

        # Skip special patterns
        is_special = any(re.match(pattern, name) for pattern in special_patterns)
        if is_special:
            continue

        # Check if name follows canonical pattern
        if not re.fullmatch(r"[a-z0-9_]+", name):
            bad_names.append(name)

    if bad_names:
        print("❌ Invalid module directory names found:")
        for name in sorted(bad_names):
            print(f"  • {name}")
        print("\nModule directories must follow pattern: ^[a-z0-9_]+$")
        print("Use: git mv {old_name} {new_name}")
        sys.exit(1)

    print("✅ All module directory names are canonical")
    return 0

if __name__ == "__main__":
    main()