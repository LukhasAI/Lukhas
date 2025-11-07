#!/usr/bin/env python3
"""
Fix UP035: Convert deprecated typing imports to built-ins (PEP 585)

Dict → dict, List → list, Tuple → tuple, Set → set, etc.
"""
import re
import sys
from pathlib import Path


# Mapping of deprecated typing names to built-in equivalents
TYPING_REPLACEMENTS = {
    'Dict': 'dict',
    'List': 'list',
    'Tuple': 'tuple',
    'Set': 'set',
    'FrozenSet': 'frozenset',
    'Deque': 'collections.deque',
    'DefaultDict': 'collections.defaultdict',
    'OrderedDict': 'collections.OrderedDict',
    'Counter': 'collections.Counter',
    'ChainMap': 'collections.ChainMap',
}


def needs_collections_import(replacements: set[str]) -> bool:
    """Check if any replacement requires collections import."""
    collections_types = {'collections.deque', 'collections.defaultdict', 
                        'collections.OrderedDict', 'collections.Counter', 
                        'collections.ChainMap'}
    return bool(replacements & collections_types)


def fix_typing_imports_in_file(filepath: Path) -> tuple[int, bool]:
    """Fix deprecated typing imports in a file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        changes = 0
        types_found = set()
        
        # Track what types we're replacing
        for old_type in TYPING_REPLACEMENTS:
            if re.search(rf'\b{old_type}\[', content):
                types_found.add(old_type)
        
        # Replace type annotations (e.g., Dict[str, int] → dict[str, int])
        for old_type, new_type in TYPING_REPLACEMENTS.items():
            pattern = rf'\b{old_type}\['
            if re.search(pattern, content):
                content = re.sub(pattern, f'{new_type}[', content)
                changes += content.count(f'{new_type}[') - original.count(f'{new_type}[')
        
        # Remove deprecated types from typing imports if no longer used
        if changes > 0:
            # Check which types are still used (not in annotations)
            unused_types = []
            for old_type in types_found:
                # Check if type is used outside of annotations (rare but possible)
                if not re.search(rf'\b{old_type}\b(?!\[)', content):
                    unused_types.append(old_type)
            
            # Remove unused types from imports
            for old_type in unused_types:
                # Remove from comma-separated imports
                content = re.sub(
                    rf'from typing import ([^()\n]*?){old_type},\s*([^()\n]*)',
                    r'from typing import \1\2',
                    content
                )
                content = re.sub(
                    rf'from typing import ([^()\n]*?),\s*{old_type}\b([^()\n]*)',
                    r'from typing import \1\2',
                    content
                )
                # Remove if it's the only import
                content = re.sub(
                    rf'from typing import {old_type}\s*\n',
                    '',
                    content
                )
            
            # Clean up double commas and trailing commas
            content = re.sub(r',\s*,', ',', content)
            content = re.sub(r'from typing import\s*,', 'from typing import ', content)
            content = re.sub(r'from typing import ([^()\n]*?),\s*\n', r'from typing import \1\n', content)
            
            # Add collections import if needed
            replacements_used = {TYPING_REPLACEMENTS[t] for t in types_found}
            if needs_collections_import(replacements_used):
                # Check if collections is already imported
                if 'import collections' not in content and 'from collections import' not in content:
                    # Add after typing import
                    content = re.sub(
                        r'(from typing import [^\n]+\n)',
                        r'\1from collections.abc import deque, defaultdict, OrderedDict, Counter, ChainMap\n',
                        content,
                        count=1
                    )
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return changes, True
        return 0, False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return 0, False


def main():
    """Fix all files with UP035 violations."""
    import subprocess
    
    # Get files with UP035 from ruff
    result = subprocess.run(
        ['ruff', 'check', '.', '--select', 'UP035', '--output-format=concise'],
        capture_output=True,
        text=True,
        cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
    )
    
    # Extract unique file paths
    files = set()
    for line in result.stdout.splitlines():
        if 'UP035' in line and 'invalid-syntax' not in line:
            filepath = line.split(':')[0]
            files.add(Path('/Users/agi_dev/LOCAL-REPOS/Lukhas') / filepath)
    
    print(f"Found {len(files)} files with UP035 violations")
    
    total_changes = 0
    fixed_files = 0
    
    for filepath in sorted(files):
        if not filepath.exists():
            continue
        changes, modified = fix_typing_imports_in_file(filepath)
        if modified:
            fixed_files += 1
            total_changes += changes
            print(f"✅ {filepath.name}: {changes} changes")
    
    print(f"\n🎯 Summary: Fixed {total_changes} deprecated type imports in {fixed_files} files")
    

if __name__ == '__main__':
    main()
