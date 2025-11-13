#!/usr/bin/env python3
"""
LUKHAS AI RUF012 ClassVar Fix Script - Enhanced Version
======================================================

Enhanced script to handle complex patterns including:
- Multiline assignments
- TODO comments in code
- Nested class configurations
- Pydantic Config classes
"""

import os
import re
import subprocess
import json
from typing import List, Dict

def fix_ruf012_violations_enhanced():
    """Enhanced fix for RUF012 violations with better pattern handling"""
    
    # Get all violations
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--output-format=json', '.'],
        capture_output=True,
        text=True,
        cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas'
    )
    
    if not result.stdout.strip():
        print("No RUF012 violations found!")
        return
    
    violations = json.loads(result.stdout)
    files_with_violations = {}
    
    for violation in violations:
        if violation.get('filename'):
            file_path = violation['filename']
            line_num = violation['location']['row']
            
            if file_path not in files_with_violations:
                files_with_violations[file_path] = []
            files_with_violations[file_path].append(line_num)
    
    print(f"Found {len(violations)} violations in {len(files_with_violations)} files")
    
    fixed_count = 0
    
    for file_path, line_numbers in files_with_violations.items():
        print(f"\n🔧 Processing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            modified = False
            
            # Process violations in reverse order to avoid line number shifts
            for line_num in sorted(line_numbers, reverse=True):
                line_idx = line_num - 1
                
                if line_idx >= len(lines):
                    continue
                
                # Look for the problematic pattern
                target_line = lines[line_idx]
                
                # Handle different patterns
                if fix_line_pattern(lines, line_idx):
                    modified = True
                    fixed_count += 1
                    print(f"  ✅ Fixed violation at line {line_num}")
            
            # Ensure typing imports are present if we made changes
            if modified:
                if ensure_typing_imports(lines):
                    print(f"  ✅ Added necessary typing imports")
                
                # Write back the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
        
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Fixed {fixed_count} violations total")
    
    # Check remaining violations
    result = subprocess.run(
        ['python3', '-m', 'ruff', 'check', '--select', 'RUF012', '--statistics'],
        capture_output=True,
        text=True
    )
    
    if 'RUF012' in result.stdout:
        remaining = int(re.search(r'(\d+)\s+RUF012', result.stdout).group(1))
        print(f"📊 {remaining} RUF012 violations remaining")
    else:
        print("🎉 All RUF012 violations eliminated!")

def fix_line_pattern(lines: List[str], line_idx: int) -> bool:
    """Fix a specific line pattern for RUF012 violations"""
    
    # Get the line and context
    line = lines[line_idx].strip()
    
    # Pattern 1: Simple assignment (var = {})
    simple_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', line)
    if simple_match:
        indent, var_name = simple_match.groups()
        # Add ClassVar annotation
        lines[line_idx] = f"{indent}{var_name}: ClassVar[Dict] = {line[len(indent + var_name + ' = '):]}"
        return True
    
    # Pattern 2: Assignment with TODO comments
    todo_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{\s*#.*TODO', line)
    if todo_match:
        indent, var_name = todo_match.groups()
        # Find where the assignment value starts
        value_start = line.find('= {')
        if value_start != -1:
            value_part = line[value_start + 2:].strip()
            lines[line_idx] = f"{indent}{var_name}: ClassVar[Dict] = {value_part}"
            return True
    
    # Pattern 3: List assignments
    list_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[', line)
    if list_match:
        indent, var_name = list_match.groups()
        value_part = line[len(indent + var_name + ' = '):]
        lines[line_idx] = f"{indent}{var_name}: ClassVar[List] = {value_part}"
        return True
    
    # Pattern 4: Set assignments  
    set_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(set\(|{\w)', line)
    if set_match:
        indent, var_name = set_match.groups()[:2]
        value_part = line[len(indent + var_name + ' = '):]
        lines[line_idx] = f"{indent}{var_name}: ClassVar[Set] = {value_part}"
        return True
    
    # Pattern 5: Already has type annotation but needs ClassVar
    typed_match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^=]+)\s*=', line)
    if typed_match:
        indent, var_name, type_hint = typed_match.groups()
        type_hint = type_hint.strip()
        
        if 'ClassVar' not in type_hint:
            # Wrap existing type in ClassVar
            value_start = line.find('=')
            value_part = line[value_start:] if value_start != -1 else '= None'
            lines[line_idx] = f"{indent}{var_name}: ClassVar[{type_hint}] {value_part}"
            return True
    
    return False

def ensure_typing_imports(lines: List[str]) -> bool:
    """Ensure necessary typing imports are present"""
    
    # Check if we need any imports
    content = '\n'.join(lines)
    needs_imports = set()
    
    if 'ClassVar[Dict]' in content and not re.search(r'from typing import.*Dict|import.*Dict', content):
        needs_imports.add('Dict')
    if 'ClassVar[List]' in content and not re.search(r'from typing import.*List|import.*List', content):
        needs_imports.add('List')
    if 'ClassVar[Set]' in content and not re.search(r'from typing import.*Set|import.*Set', content):
        needs_imports.add('Set')
    if 'ClassVar' in content and not re.search(r'from typing import.*ClassVar|import.*ClassVar', content):
        needs_imports.add('ClassVar')
    
    if not needs_imports:
        return False
    
    # Find existing typing import line
    typing_line_idx = None
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
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
        # Add new import line
        insert_idx = 0
        
        # Find the best place to insert (after existing imports or docstrings)
        for i, line in enumerate(lines[:15]):
            if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                insert_idx = i + 1
            elif line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Skip docstrings
                quote = '"""' if line.strip().startswith('"""') else "'''"
                for j in range(i + 1, len(lines)):
                    if quote in lines[j]:
                        insert_idx = j + 1
                        break
                break
        
        new_import = f"from typing import {', '.join(sorted(needs_imports))}"
        lines.insert(insert_idx, new_import)
        return True
    
    return False

def main():
    print("🛡️ LUKHAS AI Enhanced RUF012 ClassVar Fix")
    print("=" * 50)
    
    os.chdir('/Users/agi_dev/LOCAL-REPOS/Lukhas')
    fix_ruf012_violations_enhanced()

if __name__ == "__main__":
    main()