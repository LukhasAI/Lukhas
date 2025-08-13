#!/usr/bin/env python3
"""Check for syntax errors in all Python files"""

import ast
from pathlib import Path


def check_all_syntax_errors():
    base_dir = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
    error_count = 0
    files_with_errors = []

    # Check all Python files
    for py_file in base_dir.rglob("*.py"):
        # Skip archive and backup directories
        if any(part in str(py_file).lower() for part in ['archive', 'backup', '_cleanup']):
            continue

        try:
            with open(py_file) as f:
                content = f.read()
                ast.parse(content)
        except SyntaxError as e:
            error_count += 1
            files_with_errors.append((str(py_file.relative_to(base_dir)), e.lineno, e.msg))
            if error_count <= 20:  # Show first 20 errors
                print(f"{py_file.relative_to(base_dir)}:{e.lineno}: {e.msg}")

    print(f"\nTotal files with syntax errors: {error_count}")
    return error_count

if __name__ == "__main__":
    check_all_syntax_errors()
