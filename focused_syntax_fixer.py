#!/usr/bin/env python3
"""
LUKHAS Focused Syntax Fixer - Targeted approach for high-frequency errors
"""

import ast
import re
from pathlib import Path


def is_lukhas_project_file(file_path: str) -> bool:
    """Filter to only process LUKHAS project files."""
    exclude_patterns = [
        "site-packages", "lib/python", ".venv", "venv/", "__pycache__",
        "transformers/", "kubernetes/", "scipy/", "numpy/", "pandas/",
        ".git/", "node_modules/", "dist/", "build/", "*.egg-info"
    ]

    return not any(pattern in file_path for pattern in exclude_patterns)

def fix_f_string_braces(content: str) -> str:
    """Fix f-string brace issues."""
    lines = content.split("\n")

    for i, line in enumerate(lines):
        # Fix f-strings with single } that should be escaped
        if 'f"' in line or "f'" in line:
            # Simple pattern: if we see }something} it should probably be }}something}}
            if re.search(r'f["\'][^"\']*\}[^}]', line):
                # This is complex - for now just try doubling single braces
                line = re.sub(r"(?<!})(\})(?!})", r"}}", line)
                lines[i] = line

    return "\n".join(lines)

def fix_eol_strings(content: str) -> str:
    """Fix EOL while scanning string literal errors."""
    lines = content.split("\n")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Count quotes - if odd number, likely unclosed
        double_quotes = line.count('"') - line.count('\\"')
        single_quotes = line.count("'") - line.count("\\'")

        if double_quotes % 2 == 1 and not stripped.endswith("\\"):
            lines[i] = line + '"'
        elif single_quotes % 2 == 1 and not stripped.endswith("\\"):
            lines[i] = line + "'"

    return "\n".join(lines)

def fix_parentheses_mismatch(content: str) -> str:
    """Fix parentheses and bracket mismatches."""
    # Simple fix for common patterns
    content = re.sub(r"\(\}", ")", content)  # (} -> )
    content = re.sub(r"\{\)", "}", content)  # {) -> }
    content = re.sub(r"\(\]\)", ")", content)  # (]) -> )
    content = re.sub(r"\[\)\]", "]", content)  # [)] -> ]

    return content

def fix_unexpected_indent(content: str) -> str:
    """Fix unexpected indent errors."""
    lines = content.split("\n")

    for i in range(1, len(lines)):
        if lines[i].startswith("    "):  # Has indentation
            prev_line = lines[i-1].strip()
            # If previous line doesn't end with : and current is indented, remove indent
            if prev_line and not prev_line.endswith(":") and not prev_line.endswith("\\"):
                lines[i] = lines[i].lstrip()

    return "\n".join(lines)

def fix_invalid_characters(content: str) -> str:
    """Fix invalid Unicode characters."""
    content = content.replace("→", "->")  # Arrow to ->
    content = content.replace("…", "...")  # Ellipsis
    return content

def fix_syntax_errors(file_path: Path) -> bool:
    """Apply targeted syntax fixes to a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return True

        # Apply fixes in order of frequency
        content = fix_f_string_braces(content)
        content = fix_eol_strings(content)
        content = fix_parentheses_mismatch(content)
        content = fix_unexpected_indent(content)
        content = fix_invalid_characters(content)

        # Test if fix worked
        try:
            ast.parse(content)

            # Write fixed content back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Fixed: {file_path}")
            return True

        except SyntaxError as e:
            print(f"⚠️  Still has errors: {file_path} - {e.msg}")
            return False

    except Exception as e:
        print(f"🚨 Error processing {file_path}: {e}")
        return False

def main():
    """Main execution function."""
    workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    # Find all Python files
    python_files = []
    for pattern in ["**/*.py"]:
        python_files.extend(workspace.glob(pattern))

    # Filter to LUKHAS project files only
    lukhas_files = [f for f in python_files if is_lukhas_project_file(str(f))]

    print(f"🎯 Processing {len(lukhas_files)} LUKHAS Python files...")

    fixed_count = 0
    error_count = 0

    for file_path in lukhas_files:
        if fix_syntax_errors(file_path):
            fixed_count += 1
        else:
            error_count += 1

    total = len(lukhas_files)
    success_rate = (fixed_count / total * 100) if total > 0 else 0

    print("\n📊 FOCUSED FIX RESULTS")
    print("==============================")
    print(f"📁 Total files processed: {total}")
    print(f"✅ Files fixed/valid: {fixed_count}")
    print(f"❌ Files with remaining errors: {error_count}")
    print(f"📈 Syntax success rate: {success_rate:.1f}%")

if __name__ == "__main__":
    main()
