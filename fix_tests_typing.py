#!/usr/bin/env python3
"""
Fix UP035 violations in tests/ directory.
Simplified version for test files only.
"""
import re
import subprocess
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix typing imports in a single file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content

        # Check if file has deprecated typing imports
        if not re.search(r'from typing import.*\b(Dict|List|Tuple|Set)\b', content):
            return False

        # Remove Dict, List, Tuple, Set from typing imports - multiple passes
        for deprecated_type in ['Dict', 'List', 'Tuple', 'Set']:
            # Remove from middle of import list
            content = re.sub(
                rf'from typing import ([^()\n]*?),\s*{deprecated_type}\b,\s*',
                r'from typing import \1, ',
                content
            )
            # Remove from start of import list
            content = re.sub(
                rf'from typing import {deprecated_type}\b,\s*',
                r'from typing import ',
                content
            )
            # Remove from end of import list
            content = re.sub(
                rf'from typing import ([^()\n]*?),\s*{deprecated_type}\b',
                r'from typing import \1',
                content
            )
            # Remove if it's the only import
            content = re.sub(
                rf'from typing import {deprecated_type}\b\s*\n',
                '',
                content
            )

        # Clean up malformed imports and extra commas
        content = re.sub(r'from typing import\s*,\s*', 'from typing import ', content)
        content = re.sub(r'from typing import\s*\n', '', content)
        content = re.sub(r',\s*,', ',', content)
        content = re.sub(r'from typing import ([^()\n]*?),\s*\n', r'from typing import \1\n', content)

        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Fix all test files with UP035 violations."""
    # Get files with UP035 in tests/
    result = subprocess.run(
        ['ruff', 'check', 'tests/', '--select', 'UP035', '--output-format=concise'],
        capture_output=True,
        text=True,
        cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
    )

    files = set()
    for line in result.stdout.splitlines():
        if 'UP035' in line:
            filepath = line.split(':')[0]
            if filepath.startswith('tests/'):
                files.add(Path('/Users/agi_dev/LOCAL-REPOS/Lukhas') / filepath)

    print(f"Found {len(files)} test files with UP035 violations")

    fixed_count = 0
    for filepath in sorted(files):
        if filepath.exists() and fix_file(filepath):
            fixed_count += 1
            print(f"✅ {filepath.relative_to('/Users/agi_dev/LOCAL-REPOS/Lukhas')}")

    print(f"\n🎯 Fixed {fixed_count} test files")


if __name__ == '__main__':
    main()
