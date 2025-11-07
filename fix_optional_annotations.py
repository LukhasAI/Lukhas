#!/usr/bin/env python3
"""
Fix UP045: Convert Optional[X] to X | None (PEP 604)

Similar to UP035 fixes, modernizes type annotations.
"""
import re
import sys
from pathlib import Path


def fix_optional_in_file(filepath: Path) -> tuple[int, bool]:
    """Fix Optional[X] to X | None in a file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        changes = 0
        
        # Pattern 1: Optional[Type] -> Type | None
        pattern1 = r'\bOptional\[([^\]]+)\]'
        
        def replace_optional(match):
            nonlocal changes
            inner_type = match.group(1)
            changes += 1
            return f"{inner_type} | None"
        
        content = re.sub(pattern1, replace_optional, content)
        
        # Remove Optional from imports if no longer needed
        if changes > 0 and 'Optional' not in content:
            # Remove Optional from typing imports
            content = re.sub(
                r'from typing import ([^()\n]*?)Optional,?\s*([^()\n]*)',
                lambda m: f"from typing import {m.group(1)}{m.group(2)}".replace('  ', ' ').rstrip(' ,'),
                content
            )
            content = re.sub(
                r'from typing import ([^()\n]*?),\s*Optional\b([^()\n]*)',
                lambda m: f"from typing import {m.group(1)}{m.group(2)}".rstrip(' ,'),
                content
            )
            # Clean up empty import lines
            content = re.sub(r'from typing import\s*$', '', content, flags=re.MULTILINE)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return changes, True
        return 0, False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return 0, False


def main():
    """Fix all files with UP045 violations."""
    # Get files with UP045 from ruff
    import subprocess
    result = subprocess.run(
        ['ruff', 'check', '.', '--select', 'UP045', '--output-format=concise'],
        capture_output=True,
        text=True,
        cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
    )
    
    # Extract unique file paths
    files = set()
    for line in result.stdout.splitlines():
        if 'UP045' in line:
            filepath = line.split(':')[0]
            files.add(Path('/Users/agi_dev/LOCAL-REPOS/Lukhas') / filepath)
    
    print(f"Found {len(files)} files with UP045 violations")
    
    total_changes = 0
    fixed_files = 0
    
    for filepath in sorted(files):
        changes, modified = fix_optional_in_file(filepath)
        if modified:
            fixed_files += 1
            total_changes += changes
            print(f"✅ {filepath.name}: {changes} changes")
    
    print(f"\n🎯 Summary: Fixed {total_changes} Optional annotations in {fixed_files} files")
    

if __name__ == '__main__':
    main()
