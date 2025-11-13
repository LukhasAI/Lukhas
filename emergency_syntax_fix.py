#!/usr/bin/env python3
"""
Emergency syntax fix for ClassVar modifications
Repairs syntax errors introduced by the ClassVar fix script
"""

import os
import re
import subprocess


def fix_syntax_errors():
    """Fix syntax errors caused by ClassVar modifications"""

    # Get files with syntax errors
    result = subprocess.run(
        ['python3', '-c', '''
import ast
import os
import sys

syntax_error_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError:
                syntax_error_files.append(file_path)
            except Exception:
                pass

for file in syntax_error_files:
    print(file)
'''],
        capture_output=True,
        text=True,
        cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
    )

    error_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    print(f"Found {len(error_files)} files with syntax errors")

    for file_path in error_files:
        if fix_file_syntax(file_path):
            print(f"✅ Fixed syntax in {file_path}")

def fix_file_syntax(file_path: str) -> bool:
    """Fix syntax errors in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixed_lines = []
        i = 0
        modified = False

        while i < len(lines):
            line = lines[i]

            # Fix ClassVar lines that broke multiline assignments
            if ': ClassVar[Dict] = {' in line and '# TODO[T4-ISSUE]' in line:
                # This is a broken multiline assignment
                # Extract the variable name and fix the structure

                match = re.match(r'^(\s*)(\w+): ClassVar\[Dict\] = \{\s*#.*', line)
                if match:
                    indent, var_name = match.groups()

                    # Reconstruct the original multiline assignment with ClassVar
                    fixed_lines.append(f"{indent}{var_name}: ClassVar[Dict] = {{\n")

                    # Copy the rest of the multiline assignment
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('}'):
                        fixed_lines.append(lines[i])
                        i += 1

                    # Add the closing brace
                    if i < len(lines):
                        fixed_lines.append(lines[i])

                    modified = True
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    print("🚨 Emergency Syntax Fix for ClassVar Modifications")
    print("=" * 50)

    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')
    fix_syntax_errors()

if __name__ == "__main__":
    main()