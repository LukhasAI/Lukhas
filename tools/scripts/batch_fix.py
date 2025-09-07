#!/usr/bin/env python3
"""
Batch fix for the most common linting issues
Processes files in batches to avoid overwhelming the system
"""
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st


def fix_directory(directory: str, max_files: int = 10):
    """Fix issues in a specific directory, processing files in batches"""
    print(f"\n🔧 Fixing {directory}...")

    # Find Python files
    py_files = list(Path(directory).rglob("*.py"))

    # Skip certain patterns
    py_files = [
        f
        for f in py_files
        if not any(
            skip in str(f)
            for skip in [
                "__pycache__",
                ".venv",
                "venv",
                "test_metadata",
                "lukhas/flags",
                "node_modules",
            ]
        )
    ]

    if not py_files:
        print(f"  No Python files found in {directory}")
        return

    print(f"  Found {len(py_files)} Python files")

    # Process in batches
    for i in range(0, len(py_files), max_files):
        batch = py_files[i : i + max_files]
        batch_files = [str(f) for f in batch]

        print(f"  Processing batch {i // max_files + 1} ({len(batch)} files)...")

        # 1. Remove unused imports
        subprocess.run(
            [
                "autoflake",
                "--in-place",
                "--remove-unused-variables",
                "--remove-all-unused-imports",
                "--ignore-init-module-imports",
                *batch_files,
            ],
            capture_output=True,
            timeout=30,
        )

        # 2. Sort imports
        subprocess.run(
            [
                "isort",
                "--profile",
                "black",
                "--line-length",
                "88",
                "--force-single-line",
                "--quiet",
                *batch_files,
            ],
            capture_output=True,
            timeout=30,
        )

        # 3. Format with black
        subprocess.run(
            [
                "black",
                "--line-length",
                "88",
                "--target-version",
                "py39",
                "--quiet",
                *batch_files,
            ],
            capture_output=True,
            timeout=30,
        )

        # Small delay to prevent overwhelming the system
        time.sleep(0.1)

    print(f"  ✅ Completed {directory}")


def main():
    """Main function to fix issues directory by directory"""
    print("🚀 Starting Batch Fix Process")
    print("=" * 60)

    # Priority directories (most likely to have issues)
    priority_dirs = [
        "bridge/llm_wrappers",
        "lukhasbridge/api",
        "core",
        "serve",
        "tests",
    ]

    # Fix each directory
    for directory in priority_dirs:
        if Path(directory).exists():
            try:
                fix_directory(directory, max_files=20)
            except subprocess.TimeoutExpired:
                print(f"  ⚠️ Timeout processing {directory}, skipping...")
            except Exception as e:
                print(f"  ⚠️ Error processing {directory}: {e}")

    print("\n" + "=" * 60)
    print("✅ Batch fix complete!")
    print("\nNext steps:")
    print("1. Review changes: git diff")
    print("2. Test critical modules: make test")
    print("3. Commit if satisfied: git add -A && git commit -m 'Fix linting issues'")
    print("4. Or revert if needed: git checkout -- .")


if __name__ == "__main__":
    # Check if tools are available
    tools_check = subprocess.run(["which", "autoflake", "isort", "black"], capture_output=True)

    if tools_check.returncode != 0:
        print("⚠️ Required tools not found. Installing...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "autoflake",
                "isort",
                "black",
                "--quiet",
            ]
        )

    main()
