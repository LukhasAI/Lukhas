#!/usr/bin/env python3
"""
Final RUF012 Cleanup Script
===========================

Handles remaining edge cases for RUF012 violations.
"""

import json
import os
import re
import subprocess


def fix_remaining_ruf012():
    """Fix remaining RUF012 violations with advanced pattern matching"""

    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--output-format=json', '.'],
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        print("No RUF012 violations found!")
        return

    violations = json.loads(result.stdout)
    files_to_fix = {}

    for violation in violations:
        if violation.get('filename'):
            file_path = violation['filename']
            line_num = violation['location']['row']

            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(line_num)

    print(f"Found {len(violations)} remaining violations in {len(files_to_fix)} files")

    fixed_count = 0

    for file_path, line_numbers in files_to_fix.items():
        print(f"\n🔧 Processing: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            modified = False

            # Check if we need to add ClassVar import
            needs_classvar = 'ClassVar' not in content and ('from typing import' in content)

            if needs_classvar:
                for i, line in enumerate(lines):
                    if line.strip().startswith('from typing import'):
                        # Add ClassVar to existing import
                        if 'ClassVar' not in line:
                            imports = line.replace('from typing import ClassVar, ', '').strip().split(',')
                            imports = [imp.strip() for imp in imports]
                            imports.append('ClassVar')
                            imports.sort()
                            lines[i] = f"from typing import {', '.join(imports)}"
                            modified = True
                            break

            # Fix specific patterns
            for line_num in sorted(line_numbers, reverse=True):
                line_idx = line_num - 1
                if line_idx < len(lines):
                    line = lines[line_idx]

                    # Pattern 1: Dict/dict in variable annotations
                    if re.search(r'^\s*\w+\s*:\s*(Dict|dict)\s*=', line):
                        new_line = re.sub(r'(\w+)\s*:\s*(Dict|dict)\s*=', r'\1: ClassVar[\2] =', line)
                        if new_line != line:
                            lines[line_idx] = new_line
                            modified = True

                    # Pattern 2: Lists/sets that need ClassVar
                    elif re.search(r'^\s*\w+\s*:\s*(List|list|Set|set)\s*=', line):
                        new_line = re.sub(r'(\w+)\s*:\s*(List|list|Set|set)\s*=', r'\1: ClassVar[\2] =', line)
                        if new_line != line:
                            lines[line_idx] = new_line
                            modified = True

                    # Pattern 3: json_schema_extra multiline - more aggressive
                    elif 'json_schema_extra' in line and '=' in line and 'ClassVar' not in line:
                        new_line = re.sub(
                            r'(json_schema_extra)\s*=\s*\{',
                            r'\1: ClassVar[dict] = {',
                            line
                        )
                        if new_line != line:
                            lines[line_idx] = new_line
                            modified = True

                    # Pattern 4: Simple assignment patterns
                    elif re.search(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[\{\[\(]', line):
                        # Variable assignment to mutable type
                        match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
                        if match:
                            indent, var_name, value = match.groups()

                            # Determine type
                            if value.strip().startswith('{'):
                                type_hint = 'dict'
                            elif value.strip().startswith('['):
                                type_hint = 'list'
                            elif value.strip().startswith('set('):
                                type_hint = 'set'
                            else:
                                continue

                            new_line = f"{indent}{var_name}: ClassVar[{type_hint}] = {value}"
                            lines[line_idx] = new_line
                            modified = True

            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

                fixed_count += 1
                print(f"  ✅ Applied fixes to {file_path}")

        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")

    print(f"\n🎯 Fixed {fixed_count} files")

def main():
    print("🛠️ Final RUF012 Cleanup")
    print("=" * 30)

    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')
    fix_remaining_ruf012()

    # Check final status
    print("\n📊 Checking final results...")
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--statistics'],
        capture_output=True,
        text=True
    )

    if 'RUF012' in result.stdout:
        remaining = int(re.search(r'(\d+)\s+RUF012', result.stdout).group(1))
        print(f"📊 {remaining} RUF012 violations remaining")
    else:
        print("🎉 All RUF012 violations eliminated!")

if __name__ == "__main__":
    main()