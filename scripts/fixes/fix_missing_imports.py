#!/usr/bin/env python3
"""
Automatically fix F821 undefined name violations by adding missing imports.

This script identifies files with missing typing imports and adds them.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, Set


def get_f821_violations() -> Dict[str, Set[str]]:
    """Get all F821 violations and group by file."""
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'F821'],
        capture_output=True, text=True
    )
    
    files_needing_imports = {}
    for line in result.stdout.split('\n'):
        if 'F821 Undefined name' in line:
            # Extract file and undefined name
            match = re.search(r'F821 Undefined name `([^`]+)`.*--> ([^:]+):', line)
            if match:
                undefined_name, file_path = match.groups()
                if file_path not in files_needing_imports:
                    files_needing_imports[file_path] = set()
                files_needing_imports[file_path].add(undefined_name)
    
    return files_needing_imports


def add_missing_imports(file_path: str, missing_names: Set[str]) -> bool:
    """Add missing typing imports to a file."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Find typing imports to extend
        typing_imports = set()
        typing_line_idx = None
        
        for i, line in enumerate(lines):
            if line.startswith('from typing import'):
                # Extract existing imports
                import_part = line[len('from typing import'):].strip()
                existing_imports = [imp.strip() for imp in import_part.split(',')]
                typing_imports.update(existing_imports)
                typing_line_idx = i
                break
        
        # Determine which imports we need to add
        needed_imports = missing_names & {'List', 'Dict', 'Tuple', 'Optional', 'Any', 'Union'}
        if not needed_imports:
            return False  # No standard typing imports needed
        
        # Add missing imports to existing set
        typing_imports.update(needed_imports)
        
        # Create new import line
        sorted_imports = sorted(typing_imports)
        new_import_line = f"from typing import {', '.join(sorted_imports)}"
        
        if typing_line_idx is not None:
            # Replace existing typing import
            lines[typing_line_idx] = new_import_line
        else:
            # Find where to insert typing import
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_idx = i + 1
                elif line.strip() == '' and i < 10:  # Skip initial empty lines
                    continue
                elif not line.startswith('#') and line.strip():  # First non-comment, non-import line
                    break
            
            lines.insert(insert_idx, new_import_line)
        
        # Write back to file
        new_content = '\n'.join(lines)
        path.write_text(new_content, encoding='utf-8')
        
        print(f"✅ Fixed {file_path}: added {needed_imports}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main execution function."""
    print("🔍 Analyzing F821 undefined name violations...")
    
    violations = get_f821_violations()
    
    if not violations:
        print("✅ No F821 violations found!")
        return
    
    print(f"\n📊 Found F821 violations in {len(violations)} files")
    
    fixed_count = 0
    for file_path, missing_names in violations.items():
        if add_missing_imports(file_path, missing_names):
            fixed_count += 1
    
    print(f"\n📈 Results:")
    print(f"  Fixed: {fixed_count}/{len(violations)} files")
    
    # Check remaining violations
    print(f"\n🔍 Checking remaining F821 violations...")
    remaining = get_f821_violations()
    print(f"  Remaining: {sum(len(names) for names in remaining.values())} violations")


if __name__ == "__main__":
    main()