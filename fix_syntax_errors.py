#!/usr/bin/env python3
"""
Surgical syntax error fixer for LUKHAS codebase.
Focuses on the most common patterns:
1. F-string missing closing braces
2. Misplaced timezone imports
"""

import re
import ast
from pathlib import Path
import subprocess


def fix_fstring_errors(content):
    """Fix common f-string errors like missing closing braces."""
    # Pattern 1: Fix f"...{expr" -> f"...{expr}"
    # Look for f-strings missing closing brace
    pattern1 = r'(f"[^"]*\{[^}"{]*)"'
    content = re.sub(pattern1, r'\1}"', content)

    # Pattern 2: Fix f'...{expr' -> f'...{expr}'
    pattern2 = r"(f'[^']*\{[^}'{]*)''"
    content = re.sub(pattern2, r"\1}'", content)

    # Pattern 3: Fix format specifier placement: {value:.3f} not {value:.3f}
    # This fixes cases like get('key', 0.0:.3f) -> get('key', 0.0):.3f}
    pattern3 = r"\{([^}]*\.get\([^)]+,\s*[0-9.]+)(:[^}]+)\}"
    content = re.sub(pattern3, r"{\1)\2}", content)

    return content


def fix_timezone_import(content):
    """Fix misplaced timezone imports inside parenthesized imports."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a parenthesized import
        if "import (" in line and i + 1 < len(lines):
            # Look ahead for misplaced timezone import
            next_line = lines[i + 1]
            if "from datetime import timezone" in next_line:
                # Found the issue - extract the timezone import
                # Skip the misplaced line
                i += 1
                # Add timezone import before the current import
                if not any("from datetime import timezone" in fl for fl in fixed_lines):
                    fixed_lines.insert(len(fixed_lines), "from datetime import timezone")
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        elif line.strip() == "from datetime import timezone" and i > 0:
            # Check if previous line has unclosed parenthesis
            prev_line = lines[i - 1] if i > 0 else ""
            if "(" in prev_line and ")" not in prev_line:
                # This is a misplaced import, skip it
                pass
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Apply fixes
        content = fix_fstring_errors(content)
        content = fix_timezone_import(content)

        if content != original:
            # Test if the fixed content is valid Python
            try:
                ast.parse(content)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except SyntaxError:
                # Don't write if it's still broken
                return False
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def find_syntax_errors():
    """Find all Python files with syntax errors using ruff."""
    result = subprocess.run(
        [".venv/bin/ruff", "check", "--select", "E999", "--output-format=json"], capture_output=True, text=True
    )

    import json

    try:
        errors = json.loads(result.stdout)
        # Get unique filenames
        files_with_errors = set()
        for error in errors:
            if "filename" in error:
                files_with_errors.add(error["filename"])
        return list(files_with_errors)
    except:
        # Fallback to finding files manually
        return []


def main():
    print("🔧 Surgical Syntax Error Fixer")
    print("=" * 50)

    # Get list of files with syntax errors
    print("Finding files with syntax errors...")

    # First try ruff, then fallback to manual search
    error_files = find_syntax_errors()

    if not error_files:
        # Manual fallback - check specific directories
        paths = ["candidate/", "examples/", "branding/", "products/"]

        error_files = []
        for path in paths:
            for py_file in Path(path).rglob("*.py"):
                try:
                    with open(py_file, "r") as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError:
                    error_files.append(str(py_file))
                except:
                    pass

    print(f"Found {len(error_files)} files with syntax errors")

    fixed_count = 0
    for filepath in error_files[:100]:  # Process first 100 files
        if fix_file(filepath):
            fixed_count += 1
            print(f"✅ Fixed: {filepath}")

    print(f"\n✨ Fixed {fixed_count} files")

    # Run ruff again to see remaining errors
    print("\n📊 Checking remaining errors...")
    subprocess.run([".venv/bin/ruff", "check", "--statistics"])


if __name__ == "__main__":
    main()
