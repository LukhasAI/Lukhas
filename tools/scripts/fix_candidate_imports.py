#!/usr/bin/env python3
"""
Candidate Internal Import Fix Script
Fixes internal imports within candidate/ modules
"""
import streamlit as st

import re
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix imports in a single candidate file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix common problematic patterns in candidate files
        fixes = [
            # from bridge.module -> from candidate.bridge.module
            (r"from bridge\.([a-zA-Z_][a-zA-Z0-9_.]*)", r"from candidate.bridge.\1"),
            # from orchestration.module -> from candidate.orchestration.module
            (
                r"from orchestration\.([a-zA-Z_][a-zA-Z0-9_.]*)",
                r"from candidate.orchestration.\1",
            ),
            # from core.module -> from candidate.core.module (but avoid lukhas.core)
            (
                r"(?<!lukhas\.)from core\.([a-zA-Z_][a-zA-Z0-9_.]*)",
                r"from candidate.core.\1",
            ),
            # from lukhas.module -> keep as is (these should stay)
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main migration function for candidate files"""
    candidate_dir = Path("candidate")
    if not candidate_dir.exists():
        print("candidate/ directory not found")
        return

    fixed_files = []
    total_files = 0

    # Find all Python files in candidate directory
    for py_file in candidate_dir.rglob("*.py"):
        if py_file.is_file():
            total_files += 1
            if fix_imports_in_file(py_file):
                fixed_files.append(str(py_file))

    print("✅ Candidate Import Fix Complete!")
    print(f"📊 Files processed: {total_files}")
    print(f"🔧 Files modified: {len(fixed_files}")

    if fixed_files:
        print("\n📋 Modified files:")
        for file_path in sorted(fixed_files):
            print(f"  - {file_path}")


if __name__ == "__main__":
    main()
