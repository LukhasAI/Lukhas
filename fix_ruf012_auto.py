#!/usr/bin/env python3
"""Automatically fix all RUF012 violations by adding ClassVar annotations."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Set


def get_ruf012_violations():
    """Get all RUF012 violations from ruff."""
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", "--select", "RUF012", ".", "--output-format=json"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return []

    import json
    try:
        violations = json.loads(result.stdout)
        return violations
    except:
        # Parse text output if JSON fails
        violations_by_file = {}
        for line in result.stdout.split('\n'):
            if 'RUF012' in line and '-->' in line:
                match = re.search(r'--> (.+?):(\d+):', line)
                if match:
                    filepath, lineno = match.groups()
                    if filepath not in violations_by_file:
                        violations_by_file[filepath] = []
                    violations_by_file[filepath].append(int(lineno))

        return [{'filename': f, 'location': {'row': ln}}
                for f, lines in violations_by_file.items()
                for ln in lines]


def fix_file(filepath: str, violation_lines: Set[int]):
    """Fix RUF012 violations in a single file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} - file not found")
        return False

    content = path.read_text()
    lines = content.split('\n')

    # Check if ClassVar import exists
    has_classvar = 'from typing import ClassVar' in content or ('from typing import' in content and 'ClassVar' in content)

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        lineno = i + 1

        # Add ClassVar import if needed (after first import or at top)
        if not has_classvar and (line.startswith('import ') or line.startswith('from ')):
            new_lines.append(line)
            # Add ClassVar import after this import block
            if i + 1 < len(lines) and not (lines[i+1].startswith('import ') or lines[i+1].startswith('from ')):
                if 'from typing import' in '\n'.join(lines[:i+1]):
                    # ClassVar should already be in existing typing import
                    pass
                else:
                    new_lines.append('from typing import ClassVar')
                    has_classvar = True
                    modified = True
            i += 1
            continue

        # Check if this line starts a class attribute assignment
        if lineno in violation_lines:
            # Match: ATTR_NAME = {...} or [...] or (...)
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]

            if '=' in stripped and not stripped.strip().startswith('#'):
                attr_name = stripped.split('=')[0].strip()

                # Check if already has type annotation
                if ':' in attr_name:
                    new_lines.append(line)
                    i += 1
                    continue

                # Infer type from value
                rest_of_line = '='.join(stripped.split('=')[1:]).strip()

                if rest_of_line.startswith('{'):
                    type_hint = 'dict'
                elif rest_of_line.startswith('['):
                    type_hint = 'list'
                elif rest_of_line.startswith('('):
                    type_hint = 'tuple'
                elif rest_of_line.startswith('set'):
                    type_hint = 'set'
                else:
                    type_hint = 'Any'

                # Create new line with ClassVar annotation
                new_line = f'{indent}{attr_name}: ClassVar[{type_hint}] = {rest_of_line}'
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    if modified:
        # Ensure ClassVar import is present
        if not has_classvar:
            # Add at top after any __future__ imports
            insert_idx = 0
            for idx, line in enumerate(new_lines):
                if line.startswith('from __future__'):
                    insert_idx = idx + 1
                elif line.startswith('import ') or line.startswith('from '):
                    break
            new_lines.insert(insert_idx, 'from typing import ClassVar')

        path.write_text('\n'.join(new_lines))
        print(f'✅ Fixed {filepath}')
        return True

    return False


def main():
    print("Finding RUF012 violations...")
    violations = get_ruf012_violations()

    if not violations:
        print("✅ No RUF012 violations found!")
        return 0

    # Group by file
    by_file = {}
    for v in violations:
        filepath = v.get('filename') or v.get('path', '')
        lineno = v.get('location', {}).get('row', 0) or v.get('line', 0)

        if filepath not in by_file:
            by_file[filepath] = set()
        by_file[filepath].add(lineno)

    print(f"Found {len(violations)} violations in {len(by_file)} files")
    print("\nFixing files...")

    fixed_count = 0
    for filepath, lines in by_file.items():
        if fix_file(filepath, lines):
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files")

    # Run ruff again to verify
    print("\nVerifying fixes...")
    result = subprocess.run(
        ["python3", "-m", "ruff", "check", "--select", "RUF012", "."],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ All RUF012 violations resolved!")
        return 0
    else:
        remaining = len(result.stdout.split('\n'))
        print(f"⚠️  {remaining} violations remaining - may need manual fixes")
        return 1


if __name__ == '__main__':
    sys.exit(main())
