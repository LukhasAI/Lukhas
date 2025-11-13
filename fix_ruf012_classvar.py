#!/usr/bin/env python3
"""
LUKHAS AI RUF012 ClassVar Fix Script
===================================

Fixes RUF012 violations by adding typing.ClassVar annotations to mutable class attributes.
This script processes all files with RUF012 violations and adds proper type annotations.

RUF012 Rule: Mutable class attributes should be annotated with `typing.ClassVar`

Target: 139 violations across multiple domains
Priority: HIGH (#1397)
"""

import json
import os
import re
import subprocess
from typing import Dict, List


def get_ruf012_violations() -> List[Dict]:
    """Get all RUF012 violations from ruff"""
    try:
        result = subprocess.run(
            ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--output-format=json', '.'],
            capture_output=True,
            text=True,
            cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
        )

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            return [v for v in violations if v.get('filename')]
        return []
    except Exception as e:
        print(f"Error getting violations: {e}")
        return []

def detect_mutable_type(line: str) -> str:
    """Detect the type of mutable object being assigned"""
    line_clean = line.strip()

    # Dict patterns
    if (re.search(r':\s*\{', line_clean) or
        re.search(r'=\s*\{', line_clean) or
        re.search(r'=\s*dict\(', line_clean)):
        return 'Dict'

    # List patterns
    if (re.search(r':\s*\[', line_clean) or
        re.search(r'=\s*\[', line_clean) or
        re.search(r'=\s*list\(', line_clean)):
        return 'List'

    # Set patterns
    if (re.search(r'=\s*set\(', line_clean) or
        re.search(r'=\s*\{[^}]*\}', line_clean)):
        return 'Set'

    # Default to generic mutable
    return 'Any'

def fix_classvar_annotation(file_path: str, line_num: int) -> bool:
    """Fix a specific RUF012 violation by adding ClassVar annotation"""
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()

        if line_num > len(lines):
            return False

        # Get the problematic line (1-indexed to 0-indexed)
        target_line_idx = line_num - 1
        original_line = lines[target_line_idx]

        # Skip if already has ClassVar
        if 'ClassVar' in original_line:
            return False

        # Detect the variable name and type
        line_clean = original_line.strip()

        # Pattern: variable_name: annotation = value OR variable_name = value
        var_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::\s*([^=]+))?\s*=\s*(.+)$', line_clean)

        if not var_match:
            return False

        indent, var_name, existing_type, value = var_match.groups()

        # Detect the mutable type
        mutable_type = detect_mutable_type(original_line)

        # Create the ClassVar annotation
        if existing_type:
            # Already has type annotation, wrap it in ClassVar
            existing_type = existing_type.strip()
            if existing_type.lower() in ['dict', 'list', 'set']:
                new_annotation = f"ClassVar[{existing_type}]"
            else:
                new_annotation = f"ClassVar[{existing_type}]"
        else:
            # No existing type, add ClassVar with detected type
            if mutable_type == 'Dict':
                new_annotation = "ClassVar[Dict]"
            elif mutable_type == 'List':
                new_annotation = "ClassVar[List]"
            elif mutable_type == 'Set':
                new_annotation = "ClassVar[Set]"
            else:
                new_annotation = "ClassVar"

        # Reconstruct the line
        new_line = f"{indent}{var_name}: {new_annotation} = {value}\n"
        lines[target_line_idx] = new_line

        # Check if we need to add imports
        needs_classvar_import = 'ClassVar' not in ''.join(lines[:20])  # Check first 20 lines
        needs_typing_imports = set()

        if 'Dict' in new_annotation and not re.search(r'from typing import.*Dict|import.*Dict', ''.join(lines[:20])):
            needs_typing_imports.add('Dict')
        if 'List' in new_annotation and not re.search(r'from typing import.*List|import.*List', ''.join(lines[:20])):
            needs_typing_imports.add('List')
        if 'Set' in new_annotation and not re.search(r'from typing import.*Set|import.*Set', ''.join(lines[:20])):
            needs_typing_imports.add('Set')

        # Add imports if needed
        if needs_classvar_import or needs_typing_imports:
            # Find existing typing imports or add new ones
            typing_import_line = None
            for i, line in enumerate(lines[:20]):
                if re.match(r'^from typing import', line.strip()):
                    typing_import_line = i
                    break

            if typing_import_line is not None:
                # Extend existing import
                current_import = lines[typing_import_line].strip()
                imports_needed = {'ClassVar'} | needs_typing_imports

                # Parse current imports
                import_match = re.match(r'from typing import (.+)', current_import)
                if import_match:
                    current_imports = {imp.strip() for imp in import_match.group(1).split(',')}
                    all_imports = current_imports | imports_needed
                    new_import_line = f"from typing import {', '.join(sorted(all_imports))}\n"
                    lines[typing_import_line] = new_import_line
            else:
                # Add new import after existing imports or at the top
                insert_idx = 0
                for i, line in enumerate(lines[:10]):
                    if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                        insert_idx = i + 1

                imports_needed = {'ClassVar'} | needs_typing_imports
                new_import = f"from typing import {', '.join(sorted(imports_needed))}\n"
                lines.insert(insert_idx, new_import)

        # Write back the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return True

    except Exception as e:
        print(f"Error fixing {file_path}:{line_num}: {e}")
        return False

def main():
    """Main function to fix all RUF012 violations"""
    print("🛡️ LUKHAS AI RUF012 ClassVar Fix Script")
    print("=" * 50)
    print("Target: 139 mutable class attribute violations")
    print("Rule: Add typing.ClassVar annotations to class-level mutable attributes")
    print()

    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')

    # Get all violations
    print("📊 Scanning for RUF012 violations...")
    violations = get_ruf012_violations()

    if not violations:
        print("✅ No RUF012 violations found!")
        return

    print(f"Found {len(violations)} RUF012 violations")

    # Group violations by file
    files_to_fix = {}
    for violation in violations:
        file_path = violation['filename']
        line_num = violation['location']['row']

        if file_path not in files_to_fix:
            files_to_fix[file_path] = []
        files_to_fix[file_path].append(line_num)

    print(f"📁 {len(files_to_fix)} files need fixing")
    print()

    # Fix violations file by file (in reverse line order to avoid offset issues)
    fixed_files = 0
    fixed_violations = 0

    for file_path, line_numbers in files_to_fix.items():
        print(f"🔧 Fixing: {file_path}")

        # Sort line numbers in reverse order to avoid offset issues
        line_numbers.sort(reverse=True)

        file_fixed_count = 0
        for line_num in line_numbers:
            if fix_classvar_annotation(file_path, line_num):
                file_fixed_count += 1

        if file_fixed_count > 0:
            fixed_files += 1
            fixed_violations += file_fixed_count
            print(f"  ✅ Fixed {file_fixed_count} violations")
        else:
            print("  ⚠️  No changes needed")

    print()
    print("🎯 Summary:")
    print(f"  📁 Files processed: {fixed_files}")
    print(f"  🔧 Violations fixed: {fixed_violations}")

    # Check remaining violations
    print()
    print("📊 Checking remaining violations...")
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--statistics'],
        capture_output=True,
        text=True
    )

    if 'RUF012' in result.stdout:
        remaining = int(re.search(r'(\d+)\s+RUF012', result.stdout).group(1))
        print(f"📊 {remaining} RUF012 violations remaining")

        if remaining < 10:
            print("\n🔍 Remaining violations:")
            detail_result = subprocess.run(
                ['python3', '-m', 'ruff', 'check', '--select', 'RUF012'],
                capture_output=True,
                text=True
            )
            print(detail_result.stdout)
    else:
        print("🎉 All RUF012 violations eliminated!")

if __name__ == "__main__":
    main()
