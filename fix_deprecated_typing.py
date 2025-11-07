#!/usr/bin/env python3
"""
Fix UP035: Convert deprecated typing imports to built-ins (PEP 585)

Dict → dict, List → list, Tuple → tuple, Set → set, etc.
"""

import re
import sys
from pathlib import Path

# Mapping of deprecated typing names to built-in equivalents
TYPING_REPLACEMENTS = {
    "Dict": "dict",
    "List": "list",
    "Tuple": "tuple",
    "Set": "set",
    "FrozenSet": "frozenset",
    "Deque": "collections.deque",
    "DefaultDict": "collections.defaultdict",
    "OrderedDict": "collections.OrderedDict",
    "Counter": "collections.Counter",
    "ChainMap": "collections.ChainMap",
}


def needs_collections_import(replacements: set[str]) -> bool:
    """Check if any replacement requires collections import."""
    collections_types = {
        "collections.deque",
        "collections.defaultdict",
        "collections.OrderedDict",
        "collections.Counter",
        "collections.ChainMap",
    }
    return bool(replacements & collections_types)


def fix_typing_imports_in_file(filepath: Path, cleanup_only: bool = False) -> tuple[int, bool]:
    """Fix deprecated typing imports in a file.

    Args:
        filepath: Path to file to fix
        cleanup_only: If True, only remove imports, don't fix annotations
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content
        changes = 0
        types_found = set()

        if not cleanup_only:
            # Track what types we're replacing
            for old_type in TYPING_REPLACEMENTS:
                if re.search(rf"\b{old_type}\[", content):
                    types_found.add(old_type)

            # Replace type annotations (e.g., Dict[str, int] → dict[str, int])
            for old_type, new_type in TYPING_REPLACEMENTS.items():
                pattern = rf"\b{old_type}\["
                if re.search(pattern, content):
                    content = re.sub(pattern, f"{new_type}[", content)
                    changes += content.count(f"{new_type}[") - original.count(f"{new_type}[")

        # Always check for unused imports
        unused_types = []
        for old_type in TYPING_REPLACEMENTS:
            # Check if type is still used anywhere in the file
            if not re.search(rf"\b{old_type}\b", content.replace(f"import {old_type}", "")):
                unused_types.append(old_type)

        # Remove unused types from typing imports
        if unused_types:
            for old_type in unused_types:
                # Handle multi-line imports with parentheses
                content = re.sub(rf"(\([\s\S]*?)\s*{old_type}\s*,\s*([\s\S]*?\))", r"\1\2", content)
                content = re.sub(rf"(\([\s\S]*?),\s*{old_type}\s*([\s\S]*?\))", r"\1\2", content)
                # Single-line imports
                content = re.sub(
                    rf"from typing import ([^()\n]*?){old_type},\s*",
                    r"from typing import \1",
                    content,
                )
                content = re.sub(
                    rf"from typing import ([^()\n]*?),\s*{old_type}\b",
                    r"from typing import \1",
                    content,
                )
                # Only import
                content = re.sub(rf"from typing import {old_type}\s*\n", "", content)
                changes += 1

        # Clean up malformed imports
        content = re.sub(r",\s*,", ",", content)
        content = re.sub(r"from typing import\s*,\s*", "from typing import ", content)
        content = re.sub(r"from typing import\s*\([\s,]*\)", "", content)
        content = re.sub(r"from typing import\s*\n", "", content)

        # Add collections import if needed (only if not cleanup_only)
        if not cleanup_only and types_found:
            replacements_used = {TYPING_REPLACEMENTS[t] for t in types_found}
            if needs_collections_import(replacements_used):
                if "import collections" not in content and "from collections import" not in content:
                    content = re.sub(
                        r"(from typing import [^\n]+\n)",
                        r"\1from collections.abc import deque, defaultdict, OrderedDict, Counter, ChainMap\n",
                        content,
                        count=1,
                    )

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return changes, True
        return 0, False

    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return 0, False


def main():
    """Fix all files with UP035 violations."""
    import subprocess

    cleanup_only = "--cleanup-only" in sys.argv

    # Get files with UP035 from ruff
    result = subprocess.run(
        ["ruff", "check", ".", "--select", "UP035", "--output-format=concise"],
        capture_output=True,
        text=True,
        cwd="/Users/agi_dev/LOCAL-REPOS/Lukhas",
    )

    # Extract unique file paths
    files = set()
    for line in result.stdout.splitlines():
        if "UP035" in line and "invalid-syntax" not in line:
            filepath = line.split(":")[0]
            files.add(Path("/Users/agi_dev/LOCAL-REPOS/Lukhas") / filepath)

    mode = "cleanup" if cleanup_only else "fix+cleanup"
    print(f"Found {len(files)} files with UP035 violations (mode: {mode})")

    total_changes = 0
    fixed_files = 0

    for filepath in sorted(files):
        if not filepath.exists():
            continue
        changes, modified = fix_typing_imports_in_file(filepath, cleanup_only=cleanup_only)
        if modified:
            fixed_files += 1
            total_changes += changes
            if changes > 0:
                print(f"✅ {filepath.name}: {changes} changes")

    print(f"\n🎯 Summary: Fixed {total_changes} items in {fixed_files} files")


if __name__ == "__main__":
    main()
