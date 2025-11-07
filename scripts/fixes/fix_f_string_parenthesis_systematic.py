#!/usr/bin/env python3
"""
🔧 SYSTEMATIC F-STRING PARENTHESIS ERROR FIXER
Fixes f-string errors where } comes after ( without matching )
Pattern: f"text{var}" → f"text{var()}" when there's a ( without )
"""

import ast
import re
from pathlib import Path


def fix_fstring_parentheses(content: str) -> tuple[str, int]:
    """Fix f-string parenthesis mismatches systematically"""
    fixes_count = 0

    # Pattern 1: f"...{var}" where var has unmatched parenthesis
    # Look for: {word(}  ->  {word()}
    pattern1 = re.compile(r"\{([^{}]+)\(([^)]*)\}")

    def fix_pattern1(match):
        nonlocal fixes_count
        var_part = match.group(1)
        params_part = match.group(2)

        # Only fix if params_part is clearly incomplete (no closing paren expected)
        if not params_part.strip() or params_part.count("(") > params_part.count(")"):
            fixes_count += 1
            return f"{{{var_part}({params_part})}}"
        return match.group(0)

    content = pattern1.sub(fix_pattern1, content)

    # Pattern 2: Direct f-string syntax fixes for specific common patterns
    common_fixes = [
        # timestamp() patterns
        (r'f"([^"]*)\{([^}]+)\.timestamp\(\}([^"]*)"', r'f"\1{\2.timestamp()}\3"'),
        (r"f'([^']*)\\{([^}]+)\\.timestamp\\(\\}([^']*)'", r"f'\1{\2.timestamp()}\3'"),
        # len() patterns
        (r'f"([^"]*)\{len\(([^}]+)\}([^"]*)"', r'f"\1{len(\2)}\3"'),
        (r"f'([^']*)\\{len\\(([^}]+)\\}([^']*)'", r"f'\1{len(\2)}\3'"),
        # hash() patterns
        (r'f"([^"]*)\{hash\(([^}]+)\}([^"]*)"', r'f"\1{hash(\2)}\3"'),
        (r"f'([^']*)\\{hash\\(([^}]+)\\}([^']*)'", r"f'\1{hash(\2)}\3'"),
        # time() patterns
        (r'f"([^"]*)\{time\.time\(\}([^"]*)}"', r'f"\1{time.time()}\2"'),
        # int() patterns
        (r'f"([^"]*)\{int\(([^}]+)\}([^"]*)"', r'f"\1{int(\2)}\3"'),
    ]

    for pattern, replacement in common_fixes:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            fixes_count += len(re.findall(pattern, content))
            content = new_content

    return content, fixes_count


def validate_syntax(file_path: str, content: str) -> bool:
    """Check if the fixed content has valid syntax"""
    try:
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax validation failed for {file_path}: {e}")
        return False


def main():
    """Fix f-string parenthesis errors systematically"""

    print("🔧 SYSTEMATIC F-STRING PARENTHESIS ERROR FIXER")
    print("=" * 60)
    print()

    # Get all Python files that have f-string syntax errors
    error_files = []

    def check_fstring_errors(file_path):
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return False
        except SyntaxError as e:
            if "f-string" in str(e) and ("closing parenthesis" in str(e) or "parenthesis" in str(e)):
                return True
        except Exception as e:
            logger.debug(f"Expected optional failure: {e}")
            pass
        return False

    # Scan for files with f-string errors
    python_files = list(Path(".").rglob("*.py"))
    for file_path in python_files:
        if check_fstring_errors(str(file_path)):
            error_files.append(str(file_path))

    print(f"🔍 Found {len(error_files)} files with f-string parenthesis errors")
    print()

    total_fixes = 0
    successful_fixes = 0

    for file_path in error_files[:20]:  # Fix first 20 files
        print(f"🔧 Fixing: {file_path}")

        try:
            # Read original content
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Apply fixes
            fixed_content, fixes_count = fix_fstring_parentheses(original_content)

            if fixes_count > 0:
                # Validate syntax before writing
                if validate_syntax(file_path, fixed_content):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content)

                    print(f"   ✅ Applied {fixes_count} fixes")
                    total_fixes += fixes_count
                    successful_fixes += 1
                else:
                    print("   ❌ Syntax validation failed, skipped")
            else:
                print("   ⚠️  No automatic fixes applied")

        except Exception as e:
            print(f"   ❌ Error processing file: {e}")

    print()
    print("📊 F-STRING PARENTHESIS FIX RESULTS:")
    print("=" * 40)
    print(f"Files with errors: {len(error_files)}")
    print(f"Files processed: {min(20, len(error_files))}")
    print(f"Files successfully fixed: {successful_fixes}")
    print(f"Total fixes applied: {total_fixes}")

    if len(error_files) > 20:
        print(f"⚠️  {len(error_files) - 20} more files need fixing")


if __name__ == "__main__":
    main()
