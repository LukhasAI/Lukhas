#!/usr/bin/env python3
"""
Fix Streamlit (st) import issues across LUKHAS codebase
Resolves F821 violations for st usage
"""
import os
import json
from pathlib import Path

def fix_streamlit_imports():
    """Fix streamlit import issues by adding proper import statements"""
    
    # Load F821 violations
    with open('/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/idx_F821.json') as f:
        data = json.load(f)
    
    # Find files with 'st' F821 violations
    st_files = set()
    for violation in data['violations']:
        if violation['message'] == "Undefined name `st`":
            st_files.add(violation['filename'])
    
    print(f"Found {len(st_files)} files with st F821 violations")
    
    fixes_applied = 0
    for file_path in st_files:
        abs_path = Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{file_path}")
        
        if not abs_path.exists():
            print(f"⚠️ File not found: {file_path}")
            continue
            
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file already imports streamlit
            if 'import streamlit as st' in content or 'import streamlit' in content:
                continue
                
            # Check if file uses st.something
            if 'st.' in content:
                # Find the best place to add the import (after other imports)
                lines = content.split('\n')
                import_line_index = 0
                
                # Find the last import line or first non-docstring line
                in_docstring = False
                docstring_quotes = None
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Handle docstrings
                    if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                        in_docstring = True
                        docstring_quotes = stripped[:3]
                        continue
                    elif in_docstring and docstring_quotes in stripped:
                        in_docstring = False
                        continue
                    elif in_docstring:
                        continue
                        
                    # Skip comments and empty lines
                    if stripped.startswith('#') or not stripped:
                        continue
                        
                    # Found an import line
                    if (stripped.startswith('import ') or stripped.startswith('from ')) and 'streamlit' not in stripped:
                        import_line_index = i
                        
                    # Found a non-import line, stop searching
                    elif stripped and not stripped.startswith('import ') and not stripped.startswith('from '):
                        break
                
                # Insert streamlit import after the last import line
                if import_line_index > 0:
                    lines.insert(import_line_index + 1, 'import streamlit as st')
                else:
                    # If no imports found, add at the top after docstring
                    for i, line in enumerate(lines):
                        if not line.strip().startswith('"""') and not line.strip().startswith("'''") and line.strip():
                            lines.insert(i, 'import streamlit as st')
                            break
                
                new_content = '\n'.join(lines)
                
                # Write back the fixed content
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Fixed streamlit import in: {file_path}")
                fixes_applied += 1
                        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Applied {fixes_applied} streamlit import fixes")
    return fixes_applied

if __name__ == "__main__":
    fix_streamlit_imports()