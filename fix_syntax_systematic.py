#!/usr/bin/env python3
"""
Systematic Syntax Fixer for LUKHAS
Fixes the most common syntax error patterns
"""
import re
import sys
from pathlib import Path


def fix_fstring_errors(content: str) -> tuple[str, int]:
    """Fix f-string syntax errors"""
    fixes = 0

    # Pattern 1: Missing closing parenthesis in f-string expressions
    # f"...{len(something} - 10}" -> f"...{len(something)} - 10}"
    pattern1 = r'(f["\'][^"\']*\{[^}]*\([^)]*)(})'
    def fix_parens(match):
        nonlocal fixes
        expr = match.group(1)
        # Count unmatched parens
        open_parens = expr.count("(") - expr.count(")")
        if open_parens > 0:
            fixes += 1
            return expr + ")" * open_parens + "}"
        return match.group(0)

    content = re.sub(pattern1, fix_parens, content)

    # Pattern 2: Missing closing brace in dict/return statements
    # return {"key": "value", "key2": value
    # Look for lines ending with incomplete dict/list
    pattern2 = r"(\s+return\s+\{[^}]*),?\s*$"
    def fix_incomplete_dict(match):
        nonlocal fixes
        line = match.group(0)
        if not line.strip().endswith("}"):
            fixes += 1
            return line.rstrip() + "}"
        return line

    content = re.sub(pattern2, fix_incomplete_dict, content, flags=re.MULTILINE)

    # Pattern 3: Extra closing brace in f-strings (more conservative)
    # Only fix obvious cases where there's a format specifier
    # f"Value: {variable}:.2f}}" -> f"Value: {variable:.2f}"
    pattern3 = r'(f["\'][^"\']*\{[^}]*):([^}]*)}}'
    def fix_double_brace(match):
        nonlocal fixes
        fixes += 1
        return match.group(1) + ":" + match.group(2) + "}"

    content = re.sub(pattern3, fix_double_brace, content)

    return content, fixes

def fix_import_errors(content: str) -> tuple[str, int]:
    """Fix common missing imports"""
    fixes = 0
    lines = content.split("\n")

    # Track needed imports
    needs_datetime_timezone = False
    needs_asyncio = False

    has_datetime_import = False
    has_asyncio_import = False

    # Scan for usage patterns
    for line in lines:
        if "timezone.utc" in line or "timezone(" in line:
            needs_datetime_timezone = True
        if re.search(r"\basyncio\.\w+", line):
            needs_asyncio = True
        if "from datetime import" in line and "timezone" in line:
            has_datetime_import = True
        if "import asyncio" in line:
            has_asyncio_import = True

    # Add missing imports after existing imports
    import_insertion_point = -1
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            import_insertion_point = i

    if import_insertion_point == -1:
        # No imports found, add after docstring or at top
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Find end of docstring
                for j in range(i+1, len(lines)):
                    if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                        import_insertion_point = j
                        break
                break
        if import_insertion_point == -1:
            import_insertion_point = 0

    # Insert needed imports
    insertions = []
    if needs_datetime_timezone and not has_datetime_import:
        insertions.append("from datetime import timezone")
        fixes += 1
    if needs_asyncio and not has_asyncio_import:
        insertions.append("import asyncio")
        fixes += 1

    if insertions:
        for insert in reversed(insertions):
            lines.insert(import_insertion_point + 1, insert)

    return "\n".join(lines), fixes

def fix_file(filepath: Path) -> dict:
    """Fix a single Python file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            original = f.read()

        content = original
        total_fixes = 0

        # Apply fixes
        content, fstring_fixes = fix_fstring_errors(content)
        total_fixes += fstring_fixes

        content, import_fixes = fix_import_errors(content)
        total_fixes += import_fixes

        if total_fixes > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "status": "fixed",
                "fstring_fixes": fstring_fixes,
                "import_fixes": import_fixes,
                "total_fixes": total_fixes
            }

        return {"status": "unchanged"}

    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_syntax_systematic.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist")
        sys.exit(1)

    python_files = list(directory.rglob("*.py"))
    print(f"Found {len(python_files)} Python files in {directory}")

    stats = {
        "fixed": 0,
        "unchanged": 0,
        "errors": 0,
        "total_fstring_fixes": 0,
        "total_import_fixes": 0,
        "total_fixes": 0
    }

    for i, filepath in enumerate(python_files):
        if i % 100 == 0 and i > 0:
            print(f"Processed {i}/{len(python_files)} files...")

        result = fix_file(filepath)
        stats[result["status"]] += 1

        if result["status"] == "fixed":
            stats["total_fstring_fixes"] += result["fstring_fixes"]
            stats["total_import_fixes"] += result["import_fixes"]
            stats["total_fixes"] += result["total_fixes"]

    print("\nResults:")
    print(f"  Fixed: {stats['fixed']} files")
    print(f"  Unchanged: {stats['unchanged']} files")
    print(f"  Errors: {stats['errors']} files")
    print(f"  Total f-string fixes: {stats['total_fstring_fixes']}")
    print(f"  Total import fixes: {stats['total_import_fixes']}")
    print(f"  Total fixes: {stats['total_fixes']}")

if __name__ == "__main__":
    main()
