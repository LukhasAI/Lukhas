#!/usr/bin/env python3
"""Fix UP035 violations: Replace typing.Dict/List/Tuple/Set with builtins (PEP 585)."""
import re
from pathlib import Path


def fix_typing_in_annotations(content: str) -> str:
    """Replace Dict/List/Tuple/Set with dict/list/tuple/set in type annotations."""
    # Replace in type annotations (after : or ->)
    content = re.sub(r'\bDict\[', 'dict[', content)
    content = re.sub(r'\bList\[', 'list[', content)
    content = re.sub(r'\bTuple\[', 'tuple[', content)
    content = re.sub(r'\bSet\[', 'set[', content)
    
    # Replace standalone usage in annotations
    content = re.sub(r':\s*Dict\b', ': dict', content)
    content = re.sub(r':\s*List\b', ': list', content)
    content = re.sub(r':\s*Tuple\b', ': tuple', content)
    content = re.sub(r':\s*Set\b', ': set', content)
    content = re.sub(r'->\s*Dict\b', '-> dict', content)
    content = re.sub(r'->\s*List\b', '-> list', content)
    content = re.sub(r'->\s*Tuple\b', '-> tuple', content)
    content = re.sub(r'->\s*Set\b', '-> set', content)
    
    return content


def remove_from_import_line(line: str) -> str:
    """Remove Dict, List, Tuple, Set from a 'from typing import' line."""
    if 'from typing import' not in line:
        return line
    
    # Extract the import list
    match = re.match(r'(from typing import\s+)(.+)', line)
    if not match:
        return line
    
    prefix, imports = match.groups()
    
    # Split by comma, remove Dict/List/Tuple/Set, rejoin
    items = [item.strip() for item in imports.split(',')]
    items = [item for item in items if item not in ('Dict', 'List', 'Tuple', 'Set')]
    
    if not items:
        # If no imports left, comment out the line
        return f"# {line.strip()}  # All imports converted to builtins (PEP 585)"
    
    # Rejoin
    return f"{prefix}{', '.join(items)}"


def fix_file(filepath: Path) -> bool:
    """Fix UP035 violations in a file. Returns True if changes were made."""
    try:
        content = filepath.read_text()
        original = content
        
        # Step 1: Fix type annotations
        content = fix_typing_in_annotations(content)
        
        # Step 2: Fix import lines
        lines = content.split('\n')
        new_lines = [remove_from_import_line(line) for line in lines]
        content = '\n'.join(new_lines)
        
        if content != original:
            filepath.write_text(content)
            return True
        return False
    except Exception as e:
        print(f"❌ Error in {filepath}: {e}")
        return False


def main():
    """Process all test files."""
    test_dir = Path("tests")
    if not test_dir.exists():
        print("❌ tests/ directory not found")
        return
    
    fixed_count = 0
    error_count = 0
    
    for pyfile in sorted(test_dir.rglob("*.py")):
        try:
            if fix_file(pyfile):
                fixed_count += 1
                print(f"✓ {pyfile.relative_to(test_dir)}")
        except Exception as e:
            error_count += 1
            print(f"❌ {pyfile.relative_to(test_dir)}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} files")
    if error_count:
        print(f"❌ Errors in {error_count} files")


if __name__ == "__main__":
    main()
