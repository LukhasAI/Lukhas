#!/usr/bin/env python3
"""
LUKHAS AI RUF012 ClassVar Fix Script - Targeted Approach
======================================================

Fixes RUF012 violations with precise pattern matching:
1. Pydantic Config classes with json_schema_extra
2. Simple mutable class attributes (lists, dicts, sets)
3. Ensures proper typing imports are added
"""

import json
import os
import re
import subprocess
from typing import Dict, List


def get_ruf012_violations() -> Dict[str, List[int]]:
    """Get RUF012 violations grouped by file"""
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--output-format=json', '.'],
        capture_output=True,
        text=True
    )

    violations = {}
    if result.stdout.strip():
        data = json.loads(result.stdout)
        for item in data:
            if item.get('filename'):
                file_path = item['filename']
                line_num = item['location']['row']

                if file_path not in violations:
                    violations[file_path] = []
                violations[file_path].append(line_num)

    return violations

def add_typing_imports(lines: List[str]) -> bool:
    """Add necessary typing imports"""
    content = '\n'.join(lines)
    needs_imports = set()

    if 'ClassVar' in content and not re.search(r'from typing import.*ClassVar|import.*ClassVar', content):
        needs_imports.add('ClassVar')

    if not needs_imports:
        return False

    # Find existing typing import
    typing_line_idx = None
    for i, line in enumerate(lines[:25]):
        if re.match(r'^from typing import', line.strip()):
            typing_line_idx = i
            break

    if typing_line_idx is not None:
        # Extend existing import
        current_line = lines[typing_line_idx]
        import_match = re.match(r'from typing import (.+)', current_line.strip())
        if import_match:
            current_imports = {imp.strip() for imp in import_match.group(1).split(',')}
            all_imports = current_imports | needs_imports
            lines[typing_line_idx] = f"from typing import {', '.join(sorted(all_imports))}"
            return True
    else:
        # Find best insertion point
        insert_idx = 0
        for i, line in enumerate(lines[:20]):
            if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                insert_idx = i + 1

        new_import = f"from typing import {', '.join(sorted(needs_imports))}"
        lines.insert(insert_idx, new_import)
        return True

    return False

def fix_specific_violation(lines: List[str], line_num: int) -> bool:
    """Fix a specific RUF012 violation at given line number"""
    line_idx = line_num - 1

    if line_idx >= len(lines):
        return False

    line = lines[line_idx].strip()
    original_line = lines[line_idx]

    # Pattern 1: Pydantic Config json_schema_extra (multiline)
    if 'json_schema_extra' in line and '=' in line:
        # Extract indentation and fix
        indent_match = re.match(r'^(\s*)', original_line)
        indent = indent_match.group(1) if indent_match else ''

        if 'ClassVar' not in line:
            new_line = re.sub(
                r'(json_schema_extra)\s*=\s*\{',
                r'\1: ClassVar[dict] = {',
                original_line
            )
            lines[line_idx] = new_line
            return True

    # Pattern 2: Simple list assignment
    elif re.search(r'^\s*\w+\s*=\s*\[', line):
        var_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', original_line)
        if var_match:
            indent, var_name, value = var_match.groups()
            lines[line_idx] = f"{indent}{var_name}: ClassVar[list] = {value}"
            return True

    # Pattern 3: Simple dict assignment
    elif re.search(r'^\s*\w+\s*=\s*\{', line):
        var_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', original_line)
        if var_match:
            indent, var_name, value = var_match.groups()
            lines[line_idx] = f"{indent}{var_name}: ClassVar[dict] = {value}"
            return True

    # Pattern 4: Simple set assignment
    elif re.search(r'^\s*\w+\s*=\s*(set\(|{\w)', line):
        var_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', original_line)
        if var_match:
            indent, var_name, value = var_match.groups()
            lines[line_idx] = f"{indent}{var_name}: ClassVar[set] = {value}"
            return True

    return False

def process_file(file_path: str, line_numbers: List[int]) -> int:
    """Process a single file to fix RUF012 violations"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove trailing newlines for processing
        lines = [line.rstrip('\n') for line in lines]

        fixes_applied = 0

        # Process violations in reverse order to avoid line number shifts
        for line_num in sorted(line_numbers, reverse=True):
            if fix_specific_violation(lines, line_num):
                fixes_applied += 1

        # Add typing imports if we made fixes
        if fixes_applied > 0:
            add_typing_imports(lines)

        # Write back to file
        if fixes_applied > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

        return fixes_applied

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    print("🛡️ LUKHAS AI Targeted RUF012 ClassVar Fix")
    print("=" * 50)

    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')

    # Get all violations
    violations = get_ruf012_violations()
    print(f"Found RUF012 violations in {len(violations)} files")

    total_fixes = 0

    # Process each file
    for file_path, line_numbers in violations.items():
        print(f"\n🔧 Processing: {file_path}")
        fixes = process_file(file_path, line_numbers)

        if fixes > 0:
            total_fixes += fixes
            print(f"  ✅ Applied {fixes} ClassVar fixes")
        else:
            print(f"  ⚠️  No fixes applied (may need manual review)")

    print(f"\n🎯 Total fixes applied: {total_fixes}")

    # Check final status
    print("\n📊 Checking remaining violations...")
    final_violations = get_ruf012_violations()
    remaining_count = sum(len(lines) for lines in final_violations.values())

    print(f"📊 {remaining_count} RUF012 violations remaining")

    if remaining_count == 0:
        print("🎉 All RUF012 violations eliminated!")
    elif remaining_count < 20:
        print("\n🔍 Remaining violations (need manual review):")
        result = subprocess.run(
            ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '.'],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout[:1500])

if __name__ == "__main__":
    main()