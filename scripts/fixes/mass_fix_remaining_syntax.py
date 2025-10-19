#!/usr/bin/env python3
"""
Module: mass_fix_remaining_syntax.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Mass Fix Remaining Syntax Errors
Fix all remaining syntax errors identified in final verification
"""

import ast
import os
import re
from pathlib import Path


def get_syntax_error_files():
    """Get all files with syntax errors"""
    error_files = []

    for root, dirs, files in os.walk("."):
        # Skip certain directories
        skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file

            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Try to parse with AST
                ast.parse(content, filename=str(filepath))

            except SyntaxError as e:
                error_files.append({"file": str(filepath), "line": e.lineno, "error": str(e)})

            except Exception:
                continue

    return error_files


def fix_syntax_patterns(content):
    """Fix common syntax error patterns"""
    fixes = 0

    # Pattern 1: def function(: -> def function(
    pattern1 = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*:"
    if re.search(pattern1, content):
        content = re.sub(pattern1, r"def \1(", content)
        fixes += 1

    # Pattern 2: Unmatched parentheses - fix common cases
    # Fix: }' -> )'
    pattern2 = r"(\w+)\s*\}\s*'"
    if re.search(pattern2, content):
        content = re.sub(pattern2, r"\1)'", content)
        fixes += 1

    # Pattern 3: Fix unmatched brackets
    # Fix: ]' -> )'
    pattern3 = r"(\w+)\s*\]\s*'"
    if re.search(pattern3, content):
        content = re.sub(pattern3, r"\1)'", content)
        fixes += 1

    # Pattern 4: Fix double commas
    pattern4 = r",,+"
    if re.search(pattern4, content):
        content = re.sub(pattern4, ",", content)
        fixes += 1

    # Pattern 5: Fix trailing commas in function definitions
    pattern5 = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*,\s*\):"
    matches = re.findall(pattern5, content)
    if matches:
        # Remove trailing comma before closing parenthesis
        content = re.sub(r",(\s*\):)", r"\1", content)
        fixes += len(matches)

    # Pattern 6: Fix function definitions with missing parameters
    pattern6 = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*([^,)]+),\s*([^,)]+)\s*=\s*([^,)]+),?\s*\):"
    matches = re.findall(pattern6, content)
    if matches:
        for match in matches:
            func_name, param1, param2, default = match
            old = f"def {func_name}({param1}, {param2} = {default}"
            new = f"def {func_name}({param1}, {param2}={default}"
            content = content.replace(old, new)
            fixes += 1

    # Pattern 7: Fix non-default argument follows default argument
    # This is complex, let's try a simple case
    pattern7 = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*=\s*[^,)]+),\s*([^=,)]+)\s*\):"
    matches = re.findall(pattern7, content)
    if matches:
        for match in matches:
            func_name, default_param, non_default_param = match
            # Swap the parameter order
            old_def = f"def {func_name}({default_param}, {non_default_param}):"
            new_def = f"def {func_name}({non_default_param.strip()}, {default_param.strip()}):"
            content = content.replace(old_def, new_def)
            fixes += 1

    return content, fixes


def process_error_files():
    """Process all files with syntax errors"""
    error_files = get_syntax_error_files()

    if not error_files:
        print("🎉 No syntax errors found!")
        return 0, 0

    total_files_fixed = 0
    total_fixes = 0

    print(f"🔧 Processing {len(error_files)} files with syntax errors...")

    for error_info in error_files[:50]:  # Process first 50 files
        file_path = error_info["file"]

        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            fixed_content, fixes_made = fix_syntax_patterns(original_content)

            if fixes_made > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                total_files_fixed += 1
                total_fixes += fixes_made

                print(f"✅ {file_path}: {fixes_made} fixes")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return total_files_fixed, total_fixes


if __name__ == "__main__":
    print("🔧 MASS FIX REMAINING SYNTAX ERRORS")
    print("=" * 70)

    files_fixed, total_fixes = process_error_files()

    print("=" * 70)
    print("📊 MASS FIX RESULTS:")
    print(f"  📁 Files fixed: {files_fixed}")
    print(f"  🔧 Total fixes: {total_fixes}")
    print("  📋 Pattern: Various syntax error patterns")
    print("=" * 70)
