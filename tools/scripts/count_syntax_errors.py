#!/usr/bin/env python3
import streamlit as st
"""Count remaining syntax errors in Python files"""

import ast
import os
from pathlib import Path


def count_syntax_errors(base_path=None):
    if base_path is None:
        base_path = os.getenv("LUKHAS_ROOT", os.getcwd())
    base_dir = Path(base_path)
    total_errors = 0
    error_details = []

    for py_file in base_dir.rglob("*.py"):
        # Skip archive and backup directories
        if any(part in str(py_file).lower() for part in ["archive", "backup", "_cleanup", ".git"]):
            continue

        try:
            with open(py_file, encoding="utf-8", errors="ignore") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            total_errors += 1
            if total_errors <= 30:
                error_details.append(f"{py_file.relative_to(base_dir)}:{e.lineno}: {e.msg}")

    return total_errors, error_details


if __name__ == "__main__":
    import sys

    # Allow path to be specified as command line argument
    base_path = sys.argv[1] if len(sys.argv) > 1 else None
    errors, details = count_syntax_errors(base_path)

    print(f"Total Python files with syntax errors: {errors}")
    if details:
        print("\nErrors found:")
        for d in details:
            print(f"  {d}")

    if errors > 0:
        sys.exit(1)  # Exit with error code if syntax errors found
