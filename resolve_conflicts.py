#!/usr/bin/env python3
"""
Script to systematically resolve merge conflicts in PR #118.
The conflicts appear to be Jules adding parentheses to tuple unpacking,
and main branch already has the improved syntax.
"""

import os
import re
import subprocess
from pathlib import Path


def find_conflict_files():
    """Find all files with merge conflicts."""
    result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, text=True)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def resolve_conflict_file(filepath):
    """Resolve conflicts in a single file by accepting main branch version."""
    print(f"Resolving conflicts in {filepath}")

    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Pattern to match conflict blocks
        conflict_pattern = r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/main"

        def replace_conflict(match):
            # Always take the main branch version (group 2)
            return match.group(2)

        # Replace all conflicts with main branch version
        resolved_content = re.sub(conflict_pattern, replace_conflict, content, flags=re.DOTALL)

        # Write back the resolved content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(resolved_content)

        # Check if conflicts are fully resolved
        if "<<<<<<< HEAD" not in resolved_content:
            print(f"✓ Successfully resolved all conflicts in {filepath}")
            return True
        else:
            print(f"⚠ Some conflicts may remain in {filepath}")
            return False

    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False


def main():
    """Main resolution process."""
    print("Starting systematic conflict resolution for PR #118...")

    # Find files with conflicts
    conflict_files = find_conflict_files()

    if not conflict_files:
        print("No conflict files found.")
        return

    print(f"Found {len(conflict_files)} files with conflicts:")
    for f in conflict_files:
        print(f"  - {f}")

    print("\nResolving conflicts (accepting main branch versions)...")

    resolved_count = 0
    for filepath in conflict_files:
        if filepath and os.path.exists(filepath):
            if resolve_conflict_file(filepath):
                resolved_count += 1

    print(f"\nResolved {resolved_count}/{len(conflict_files)} files")

    # Add resolved files to staging
    if resolved_count > 0:
        print("\nAdding resolved files to staging area...")
        for filepath in conflict_files:
            if filepath and os.path.exists(filepath):
                result = subprocess.run(["git", "add", filepath], capture_output=True)
                if result.returncode == 0:
                    print(f"✓ Added {filepath}")
                else:
                    print(f"✗ Failed to add {filepath}")


if __name__ == "__main__":
    main()
