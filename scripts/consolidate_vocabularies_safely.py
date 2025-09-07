#!/usr/bin/env python3
"""
Safe vocabulary consolidation script.
Analyzes all vocabulary files and creates a unified, deduplicated set.
"""

import hashlib
import os
from pathlib import Path


def get_file_hash(filepath):
    """Get hash of file content, ignoring TAG comments."""
    with open(filepath) as f:
        lines = [line for line in f if not line.startswith("# TAG:")]
        content = "".join(lines)
        return hashlib.sha256(content.encode()).hexdigest()


def analyze_vocabularies():
    """Analyze all vocabulary files for duplicates."""
    vocab_dirs = [
        "core/symbolic",
        "symbolic/vocabularies",
        "core/symbolic_core/vocabularies",
        "branding/unified/vocabularies",
    ]

    vocab_files = {}

    for dir_path in vocab_dirs:
        if os.path.exists(dir_path):
            for file in Path(dir_path).glob("*vocabulary*.py"):
                if file.is_file():
                    file_hash = get_file_hash(file)
                    file_name = file.name

                    if file_name not in vocab_files:
                        vocab_files[file_name] = []

                    vocab_files[file_name].append({"path": str(file), "hash": file_hash, "size": file.stat().st_size})

    # Report findings
    print("\n=== Vocabulary File Analysis ===\n")

    for filename, locations in vocab_files.items():
        print(f"{filename}:")

        # Group by hash
        hash_groups = {}
        for loc in locations:
            if loc["hash"] not in hash_groups:
                hash_groups[loc["hash"]] = []
            hash_groups[loc["hash"]].append(loc)

        if len(hash_groups) == 1:
            print(f"  ✓ All {len(locations)} copies are identical")
            for loc in locations:
                print(f"    - {loc['path']} ({loc['size']} bytes)")
        else:
            print(f"  ⚠ Found {len(hash_groups)} different versions:")
            for hash_val, locs in hash_groups.items():
                print(f"    Version {hash_val[:8]}...:")
                for loc in locs:
                    print(f"      - {loc['path']} ({loc['size']} bytes)")
        print()


if __name__ == "__main__":
    analyze_vocabularies()
