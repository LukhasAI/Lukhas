#!/usr/bin/env python3
"""
🔧 LUKHAS Syntax Error Fixer
Automatically detects and fixes common syntax errors in Python files.
Part of the Phase 1.1 Foundation Repair initiative.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Optional


def find_syntax_errors(file_path: Path) -> Optional[tuple[int, str]]:
    """Find syntax error in a Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            ast.parse(content)
        return None  # No syntax error
    except SyntaxError as e:
        return (e.lineno, str(e))
    except Exception as e:
        # Other errors (encoding, etc.)
        return (0, str(e))


def fix_common_syntax_patterns(content: str) -> tuple[str, list[str]]:
    """Fix common syntax error patterns."""
    fixes_applied = []
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines, 1):
        # Pattern 1: Fix self._object.method() -> self._method()
        pattern1 = re.match(r"(\s+)def\s+self\._(\w+)\.(\w+)\((.*?)\):", line)
        if pattern1:
            indent, obj, method, params = pattern1.groups()
            line = f"{indent}def _{method}({params}):"
            fixes_applied.append(f"Line {i}: Fixed method definition syntax")

        # Pattern 2: Fix incomplete f-strings
        if 'f"' in line or "f'" in line:
            # Check for unclosed braces
            if line.count("{") != line.count("}"):
                # Try to fix by closing braces
                if line.count("{") > line.count("}"):
                    line = line + "}" * (line.count("{") - line.count("}"))
                    fixes_applied.append(f"Line {i}: Fixed unclosed f-string braces")

        # Pattern 3: Fix invalid indentation (tabs to spaces)
        if "\t" in line:
            line = line.replace("\t", "    ")
            fixes_applied.append(f"Line {i}: Converted tabs to spaces")

        # Pattern 4: Fix trailing comma in function definitions
        if re.match(r".*\),$", line) and "def " in lines[max(0, i - 2) : i]:
            line = line.rstrip(",")
            fixes_applied.append(f"Line {i}: Removed trailing comma in function definition")

        # Pattern 5: Fix missing colons in control structures
        control_patterns = [r"^\s*(if|elif|else|for|while|try|except|finally|with|def|class)\s+"]
        for pattern in control_patterns:
            if re.match(pattern, line) and not line.rstrip().endswith(":") and not line.rstrip().endswith(","):
                line = line.rstrip() + ":"
                fixes_applied.append(f"Line {i}: Added missing colon")
                break

        fixed_lines.append(line)

    return "\n".join(fixed_lines), fixes_applied


def process_file(file_path: Path, auto_fix: bool = True) -> bool:
    """Process a single Python file."""
    error_info = find_syntax_errors(file_path)

    if error_info is None:
        return True  # No error

    line_no, error_msg = error_info
    print(f"\n❌ {file_path}")
    print(f"   Error on line {line_no}: {error_msg}")

    if not auto_fix:
        return False

    # Try to fix the file
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        fixed_content, fixes = fix_common_syntax_patterns(content)

        if fixes:
            print(f"   Applying {len(fixes} fixes:")
            for fix in fixes[:5]:  # Show first 5 fixes
                print(f"     - {fix}")
            if len(fixes) > 5:
                print(f"     ... and {len(fixes} - 5} more")

            # Write fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            # Check if fixed
            if find_syntax_errors(file_path) is None:
                print("   ✅ Fixed successfully!")
                return True
            else:
                print("   ⚠️  Some errors remain, manual fix needed")
                return False
        else:
            print("   ⚠️  No automatic fix available")
            return False

    except Exception as e:
        print(f"   ⚠️  Error processing file: {e}")
        return False


def main():
    """Main entry point."""
    directories_to_check = ["tools", "core", "consciousness", "memory", "bridge", "api"]

    print("🔧 LUKHAS Syntax Error Fixer")
    print("=" * 50)

    total_files = 0
    error_files = []
    fixed_files = []
    unfixed_files = []

    for dir_name in directories_to_check:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue

        print(f"\n📁 Checking {dir_name}/...")

        for py_file in dir_path.rglob("*.py"):
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            total_files += 1

            # Check for syntax errors
            error_info = find_syntax_errors(py_file)
            if error_info is not None:
                error_files.append(py_file)

                # Try to fix
                if process_file(py_file, auto_fix=True):
                    fixed_files.append(py_file)
                else:
                    unfixed_files.append(py_file)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   Total files scanned: {total_files}")
    print(f"   Files with errors: {len(error_files}")
    print(f"   Files fixed: {len(fixed_files}")
    print(f"   Files need manual fix: {len(unfixed_files}")

    if unfixed_files:
        print("\n⚠️  Files requiring manual intervention:")
        for file in unfixed_files[:10]:
            print(f"   - {file}")
        if len(unfixed_files) > 10:
            print(f"   ... and {len(unfixed_files} - 10} more")

    return len(unfixed_files) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
