#!/usr/bin/env python3
"""
Fix F-string bracket mismatches
Fixes issues like {uuid.uuid4(}} -> {uuid.uuid4()}
"""

import os
import re
import subprocess
import sys


def fix_fstring_bracket_mismatch(content):
    """Fix f-string bracket mismatches"""

    # Pattern to find f-strings with mismatched parentheses/brackets
    # Looking for patterns like {something(}} or {something[}}
    patterns = [
        # Fix {function(}} -> {function()}
        (r"(\{[^{}]*?\([^()]*?)\}\}", r"\1)}"),
        # Fix {function[}} -> {function]}
        (r"(\{[^{}]*?\[[^\[\]]*?)\}\}", r"\1]}"),
        # Fix other common bracket issues
        (r"(\{[^{}]*?)\}\}", r"\1}"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def process_file(file_path):
    """Process a single file to fix f-string bracket mismatches"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixed_content = fix_fstring_bracket_mismatch(content)

        if fixed_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            # Test compilation
            result = subprocess.run([sys.executable, "-m", "py_compile", file_path],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Fixed: {file_path}")
                return True
            else:
                print(f"❌ Still has errors: {file_path}")
                return False
        return True
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    print("🔧 Fixing f-string bracket mismatches...")

    # Find Python files that have f-string bracket mismatch errors
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip virtual environments
        dirs[:] = [d for d in dirs if not d.startswith(".venv") and not d.startswith(".cleanenv")]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Check if file has f-string bracket mismatch
                result = subprocess.run([sys.executable, "-m", "py_compile", file_path],
                                      capture_output=True, text=True)
                if result.returncode != 0 and "f-string: closing parenthesis" in result.stderr:
                    python_files.append(file_path)

    print(f"Found {len(python_files)} files with f-string bracket mismatches")

    fixed_count = 0
    for file_path in python_files:
        if process_file(file_path):
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count}/{len(python_files)} files")


if __name__ == "__main__":
    main()