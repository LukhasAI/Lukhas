#!/usr/bin/env python3
"""Fix all remaining syntax errors in Python files"""

import ast
from pathlib import Path


def fix_multiline_string_error(file_path):
    """Fix multiline string EOL errors"""
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return False

    # Try to find and fix the error
    for i in range(len(lines)):
        line = lines[i]

        # Pattern 1: String split across lines without proper closing
        # Look for lines with odd number of quotes
        quote_count = line.count('"') - line.count('\\"')
        if quote_count % 2 != 0:
            # Check if it's a line that starts a string but doesn't close it
            if '": "' in line or '= "' in line or 'return "' in line:
                # Check if the line doesn't end with a quote
                stripped = line.rstrip()
                if not stripped.endswith('"') and not stripped.endswith('",'):
                    # Look ahead to see if next line continues the string
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # If next line is indented continuation, merge it
                        if next_line.startswith('    '):
                            # Merge the lines
                            lines[i] = stripped + ' ' + next_line.strip()
                            if lines[i].rstrip()[-1] not in '",\'':
                                lines[i] = lines[i].rstrip() + '"\n'
                            lines[i + 1] = ''
                        else:
                            # Just close the string
                            lines[i] = stripped + '"\n'

    # Write back the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines([l for l in lines if l])  # Skip empty lines we created

    # Verify the fix
    try:
        with open(file_path, encoding='utf-8') as f:
            ast.parse(f.read())
        return True
    except:
        return False

def get_syntax_error(file_path):
    """Get the syntax error details for a file"""
    try:
        with open(file_path, encoding='utf-8', errors='ignore') as f:
            ast.parse(f.read())
        return None
    except SyntaxError as e:
        return (e.lineno, e.msg)

def main():
    """Fix all syntax errors"""
    base_dir = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")

    # List of directories to fix
    dirs_to_fix = [
        "tools/analysis",
        "tools/scripts",
        "tools/journal"
    ]

    fixed_count = 0
    failed_files = []

    for dir_path in dirs_to_fix:
        full_dir = base_dir / dir_path
        if not full_dir.exists():
            continue

        for py_file in full_dir.glob("*.py"):
            error = get_syntax_error(py_file)
            if error:
                print(f"Fixing {py_file.relative_to(base_dir)}: Line {error[0]} - {error[1]}")
                if fix_multiline_string_error(py_file):
                    print("  ✓ Fixed")
                    fixed_count += 1
                else:
                    # Try again with manual inspection
                    error = get_syntax_error(py_file)
                    if error:
                        print(f"  ✗ Still has error: Line {error[0]} - {error[1]}")
                        failed_files.append(str(py_file.relative_to(base_dir)))
                    else:
                        print("  ✓ Fixed on second attempt")
                        fixed_count += 1

    print("\n📊 Summary:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Failed: {len(failed_files)} files")

    if failed_files:
        print("\n❌ Files still with errors:")
        for f in failed_files[:10]:
            print(f"    {f}")

if __name__ == "__main__":
    main()
