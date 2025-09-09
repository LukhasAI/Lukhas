#!/usr/bin/env python3
"""
Fix specific f-string closing parenthesis issues
Patterns like {time.time()} missing closing }
"""

import re
import subprocess
import sys


def fix_fstring_specific_issues(content):
    """Fix specific f-string patterns with missing closing braces"""

    # Pattern 1: {function()} missing closing }
    # Look for {function(...)} where the } is missing after )
    patterns = [
        # {time.time()" -> {time.time()}"
        (r'(\{[^{}]*?\([^)]*?\))"', r'\1}"'),
        # {function(" -> {function()}"
        (r'(\{[^{}]*?\([^)]*?\))"', r'\1}"'),
        # More general: {something(" where closing } is missing
        (r'(\{[^{}]*?\([^)]*?\))"', r'\1}"'),
        # {something(} -> {something()}
        (r'(\{[^{}]*?\()}"', r'\1)}"'),
    ]

    original_content = content

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def find_and_fix_files():
    """Find files with specific f-string errors and fix them"""

    # Find files with the specific error pattern
    cmd = ["find", ".", "-name", "*.py", "-not", "-path", "./.venv*", "-not", "-path", "./.cleanenv*"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Error finding Python files")
        return

    python_files = result.stdout.strip().split("\n")
    fixed_files = []

    for file_path in python_files:
        if not file_path or not file_path.endswith(".py"):
            continue

        # Check if file has the specific error
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", file_path],
            capture_output=True, text=True
        )

        if compile_result.returncode != 0 and "closing parenthesis" in compile_result.stderr and "does not match" in compile_result.stderr:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                fixed_content = fix_fstring_specific_issues(content)

                if fixed_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)

                    # Test if fix worked
                    test_result = subprocess.run(
                        [sys.executable, "-m", "py_compile", file_path],
                        capture_output=True, text=True
                    )

                    if test_result.returncode == 0:
                        print(f"✅ Fixed: {file_path}")
                        fixed_files.append(file_path)
                    else:
                        print(f"❌ Still has errors: {file_path}")
                        # Try manual inspection for this specific case
                        if "closing parenthesis" in test_result.stderr:
                            manual_fix_file(file_path)

            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    print(f"\n✅ Fixed {len(fixed_files)} files with closing parenthesis issues")
    return fixed_files


def manual_fix_file(file_path):
    """Manual fix for specific f-string closing parenthesis issues"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        for i, line in enumerate(lines):
            # Look for patterns like {function(}" or {function(}
            if 'f"' in line or "f'" in line:
                # Pattern: {something(}" should be {something()}"
                if re.search(r'\{[^{}]*?\(}"', line):
                    lines[i] = re.sub(r'(\{[^{}]*?\(})"', r'\1)"', line)
                    modified = True
                # Pattern: {something(} should be {something()}
                elif re.search(r"\{[^{}]*?\(}", line):
                    lines[i] = re.sub(r"(\{[^{}]*?\()}}", r"\1)}", line)
                    modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"🔧 Manual fix attempted: {file_path}")

    except Exception as e:
        print(f"❌ Manual fix failed for {file_path}: {e}")


if __name__ == "__main__":
    print("🔧 Fixing specific f-string closing parenthesis issues...")
    find_and_fix_files()