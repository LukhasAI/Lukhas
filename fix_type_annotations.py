#!/usr/bin/env python3
"""Script to fix Python 3.9 compatibility issues in test files."""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def fix_type_annotations(content: str) -> Tuple[str, int]:
    """Fix type annotations to be Python 3.9 compatible.

    Returns:
        Tuple of (fixed_content, num_changes)
    """
    changes = 0
    original = content

    # Fix dict[...] -> Dict[...]
    if re.search(r'\bdict\[', content):
        content = re.sub(r'\bdict\[', 'Dict[', content)
        changes += 1

    # Fix list[...] -> List[...]
    if re.search(r'\blist\[', content):
        content = re.sub(r'\blist\[', 'List[', content)
        changes += 1

    # Fix tuple[...] -> Tuple[...]
    if re.search(r'\btuple\[', content):
        content = re.sub(r'\btuple\[', 'Tuple[', content)
        changes += 1

    # Fix set[...] -> Set[...]
    if re.search(r'\bset\[', content):
        content = re.sub(r'\bset\[', 'Set[', content)
        changes += 1

    # Fix "X | None" -> "Optional[X]" (but not in comments or strings)
    # This is more complex, so we'll use a careful regex
    # Match patterns like "str | None", "int | None", etc.
    union_none_pattern = r'(\w+(?:\[[^\]]+\])?)\s*\|\s*None'
    if re.search(union_none_pattern, content):
        # Only replace in type annotation contexts (after : or ->)
        content = re.sub(
            r'([:>])\s*' + union_none_pattern,
            r'\1 Optional[\2]',
            content
        )
        changes += 1

    # Ensure typing imports are present if we made changes
    if changes > 0 and content != original:
        # Check if we need to add typing imports
        needs_dict = 'Dict[' in content and 'Dict' not in re.findall(r'from typing import.*', content)[0] if re.findall(r'from typing import.*', content) else 'Dict[' in content
        needs_list = 'List[' in content and 'List' not in re.findall(r'from typing import.*', content)[0] if re.findall(r'from typing import.*', content) else 'List[' in content
        needs_tuple = 'Tuple[' in content and 'Tuple' not in re.findall(r'from typing import.*', content)[0] if re.findall(r'from typing import.*', content) else 'Tuple[' in content
        needs_set = 'Set[' in content and 'Set' not in re.findall(r'from typing import.*', content)[0] if re.findall(r'from typing import.*', content) else 'Set[' in content
        needs_optional = 'Optional[' in content and 'Optional' not in re.findall(r'from typing import.*', content)[0] if re.findall(r'from typing import.*', content) else 'Optional[' in content

        # If there's already a typing import, update it
        typing_import_match = re.search(r'from typing import ([^\n]+)', content)
        if typing_import_match:
            existing_imports = set(i.strip() for i in typing_import_match.group(1).split(','))
            new_imports = existing_imports.copy()

            if needs_dict and 'Dict' not in existing_imports:
                new_imports.add('Dict')
            if needs_list and 'List' not in existing_imports:
                new_imports.add('List')
            if needs_tuple and 'Tuple' not in existing_imports:
                new_imports.add('Tuple')
            if needs_set and 'Set' not in existing_imports:
                new_imports.add('Set')
            if needs_optional and 'Optional' not in existing_imports:
                new_imports.add('Optional')

            if new_imports != existing_imports:
                new_import_line = 'from typing import ' + ', '.join(sorted(new_imports))
                content = content.replace(typing_import_match.group(0), new_import_line)
        else:
            # Add typing import after other imports
            imports_needed = []
            if needs_dict:
                imports_needed.append('Dict')
            if needs_list:
                imports_needed.append('List')
            if needs_tuple:
                imports_needed.append('Tuple')
            if needs_set:
                imports_needed.append('Set')
            if needs_optional:
                imports_needed.append('Optional')

            if imports_needed:
                # Find the last import statement
                import_pattern = r'^(from __future__ import.*?\n|import .*?\n|from .*? import .*?\n)'
                imports = list(re.finditer(import_pattern, content, re.MULTILINE))
                if imports:
                    last_import_end = imports[-1].end()
                    typing_import = f'from typing import {", ".join(sorted(imports_needed))}\n'
                    content = content[:last_import_end] + typing_import + content[last_import_end:]

    return content, changes


def process_file(file_path: Path) -> bool:
    """Process a single file and return True if changes were made."""
    try:
        content = file_path.read_text(encoding='utf-8')
        fixed_content, changes = fix_type_annotations(content)

        if changes > 0:
            file_path.write_text(fixed_content, encoding='utf-8')
            print(f"Fixed {file_path}: {changes} type(s) of changes")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to process all test files."""
    tests_dir = Path('/home/user/Lukhas/tests')

    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}", file=sys.stderr)
        return 1

    # Find all Python test files
    test_files = list(tests_dir.rglob('*.py'))
    print(f"Found {len(test_files)} test files")

    fixed_count = 0
    for test_file in test_files:
        if process_file(test_file):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")
    return 0


if __name__ == '__main__':
    sys.exit(main())
