#!/usr/bin/env python3
"""
Fix Python 3.9 compatibility by converting Python 3.10+ union type syntax.

Converts: Optional[str]  ->  Optional[str]
    int | None  ->  Optional[int]
    SomeType | None  ->  Optional[SomeType]
    
Also ensures proper imports are added.
"""

import re
import sys
from pathlib import Path
from typing import Set, Tuple


def has_union_syntax(content: str) -> bool:
    """Check if file has Python 3.10+ union syntax."""
    # Pattern: type annotation with | union operator
    pattern = r':\s*\w+(\[\w+\])?\s*\|\s*None'
    return bool(re.search(pattern, content))


def has_optional_import(content: str) -> bool:
    """Check if Optional is already imported."""
    patterns = [
        r'from typing import.*Optional',
        r'from typing import.*\(\s*.*Optional',
    ]
    return any(re.search(p, content) for p in patterns)


def add_optional_import(content: str) -> str:
    """Add Optional to typing imports if not present."""
    
    # Pattern 1: from typing import X, Y, Z
    single_line = r'(from typing import )([^(\n]+)'
    match = re.search(single_line, content)
    if match:
        imports = match.group(2).strip()
        if 'Optional' not in imports:
            # Add Optional to the import list
            new_imports = imports.rstrip(',') + ', Optional'
            content = content.replace(match.group(0), f'from typing import {new_imports}')
            return content
    
    # Pattern 2: from typing import (...)
    multi_line = r'from typing import \((.*?)\)'
    match = re.search(multi_line, content, re.DOTALL)
    if match:
        imports = match.group(1)
        if 'Optional' not in imports:
            # Add Optional to the import list
            new_imports = imports.rstrip().rstrip(',') + ',\n    Optional'
            content = content.replace(match.group(0), f'from typing import ({new_imports}\n)')
            return content
    
    # If no typing import exists, add one at the top after any module docstring
    lines = content.split('\n')
    insert_pos = 0
    in_docstring = False
    
    for i, line in enumerate(lines):
        if i == 0 and (line.startswith('"""') or line.startswith("'''")):
            in_docstring = True
        elif in_docstring and (line.endswith('"""') or line.endswith("'''")):
            in_docstring = False
            insert_pos = i + 1
            break
        elif not in_docstring and line.strip() and not line.startswith('#'):
            insert_pos = i
            break
    
    lines.insert(insert_pos, 'from typing import Optional\n')
    return '\n'.join(lines)


def convert_union_to_optional(content: str) -> Tuple[str, int]:
    """Convert X | None to Optional[X]."""
    
    # Pattern to match type annotations with union syntax
    # Captures: Optional[type_name]
    pattern = r':\s*(\w+(?:\[[\w\[\], ]+\])?)\s*\|\s*None'
    
    count = 0
    
    def replacer(match):
        nonlocal count
        type_name = match.group(1)
        count += 1
        return f': Optional[{type_name}]'
    
    content = re.sub(pattern, replacer, content)
    
    # Also handle return type annotations: -> Optional[Type]
    pattern_return = r'->\s*(\w+(?:\[[\w\[\], ]+\])?)\s*\|\s*None'
    
    def replacer_return(match):
        nonlocal count
        type_name = match.group(1)
        count += 1
        return f'-> Optional[{type_name}]'
    
    content = re.sub(pattern_return, replacer_return, content)
    
    return content, count


def fix_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """Fix a single file. Returns (modified, count)."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not has_union_syntax(content):
            return False, 0
        
        # Convert union syntax
        new_content, count = convert_union_to_optional(content)
        
        if count == 0:
            return False, 0
        
        # Add Optional import if needed
        if not has_optional_import(new_content):
            new_content = add_optional_import(new_content)
        
        if dry_run:
            print(f"Would fix {file_path}: {count} conversions")
            return True, count
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Fixed {file_path}: {count} conversions")
        return True, count
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}", file=sys.stderr)
        return False, 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix Python 3.9 compatibility')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--paths', nargs='+', help='Specific paths to fix')
    parser.add_argument('--batch-size', type=int, default=50, help='Files per batch')
    
    args = parser.parse_args()
    
    # Find all Python files with union syntax
    if args.paths:
        files = [Path(p) for p in args.paths if Path(p).suffix == '.py']
    else:
        import subprocess
        result = subprocess.run(
            ['rg', r':\s*\w+\s*\|', '--type', 'py', '-l'],
            capture_output=True,
            text=True
        )
        files = [Path(line.strip()) for line in result.stdout.split('\n') if line.strip()]
    
    total_files = len(files)
    total_conversions = 0
    modified_files = 0
    
    print(f"Found {total_files} files with potential union syntax")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY FIXES'}")
    print("=" * 60)
    
    # Process in batches
    for i in range(0, total_files, args.batch_size):
        batch = files[i:i + args.batch_size]
        print(f"\nBatch {i // args.batch_size + 1}/{(total_files - 1) // args.batch_size + 1}:")
        
        for file_path in batch:
            if file_path.exists():
                modified, count = fix_file(file_path, args.dry_run)
                if modified:
                    modified_files += 1
                    total_conversions += count
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Files scanned: {total_files}")
    print(f"  Files modified: {modified_files}")
    print(f"  Total conversions: {total_conversions}")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()
