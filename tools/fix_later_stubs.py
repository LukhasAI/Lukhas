#!/usr/bin/env python3
"""
Fix fix_later stub issues across LUKHAS codebase
Resolves F821 violations for fix_later placeholders
"""
import os
import json
from pathlib import Path

def fix_later_stubs():
    """Replace fix_later placeholders with proper stub implementations"""
    
    # Load F821 violations
    with open('/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/idx_F821.json') as f:
        data = json.load(f)
    
    # Find files with fix_later F821 violations
    fix_later_files = {}
    for violation in data['violations']:
        if violation['message'] == "Undefined name `fix_later`":
            filename = violation['filename']
            if filename not in fix_later_files:
                fix_later_files[filename] = []
            fix_later_files[filename].append(violation['location']['row'])
    
    print(f"Found {len(fix_later_files)} files with fix_later F821 violations")
    
    fixes_applied = 0
    for file_path, line_numbers in fix_later_files.items():
        abs_path = Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{file_path}")
        
        if not abs_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
            
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace fix_later with proper stub
            if 'fix_later' in content:
                # Add stub function at the top of the file after imports
                lines = content.split('\n')
                
                # Find insertion point (after imports/docstrings)
                insertion_point = 0
                in_docstring = False
                docstring_marker = None
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Handle docstrings
                    if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                        in_docstring = True
                        docstring_marker = stripped[:3]
                        if stripped.count(docstring_marker) >= 2:  # Single line docstring
                            in_docstring = False
                        continue
                    elif in_docstring and docstring_marker in stripped:
                        in_docstring = False
                        continue
                    elif in_docstring:
                        continue
                    
                    # Skip imports and comments
                    if (stripped.startswith('import ') or 
                        stripped.startswith('from ') or 
                        stripped.startswith('#') or 
                        not stripped):
                        insertion_point = i + 1
                    else:
                        break
                
                # Add the stub function definition
                stub_definition = '''
def fix_later(*args, **kwargs):
    """TODO(symbol-resolver): implement missing functionality
    
    This is a placeholder for functionality that needs to be implemented.
    Replace this stub with the actual implementation.
    """
    raise NotImplementedError("fix_later is not yet implemented - replace with actual functionality")
'''
                
                lines.insert(insertion_point, stub_definition)
                new_content = '\n'.join(lines)
                
                # Write back the fixed content
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Added fix_later stub to: {file_path}")
                fixes_applied += 1
                        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Applied {fixes_applied} fix_later stub fixes")
    return fixes_applied

if __name__ == "__main__":
    fix_later_stubs()