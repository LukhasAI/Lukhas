#!/usr/bin/env python3
"""Fix massive indentation corruption in brain_integration.py"""

import re

def fix_brain_integration():
    file_path = 'candidate/core/orchestration/brain/brain_integration.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern replacements for systematic indentation fixes
    # These are the common patterns observed in the corruption
    
    # Fix massively over-indented method definitions (should be 4 spaces for class methods)
    content = re.sub(r'^[ ]{100,}def ', '    def ', content, flags=re.MULTILINE)
    
    # Fix massively over-indented if statements (should be 8 spaces in method body)  
    content = re.sub(r'^[ ]{100,}if ', '        if ', content, flags=re.MULTILINE)
    
    # Fix massively over-indented return statements (should be 8 spaces in method body)
    content = re.sub(r'^[ ]{100,}return ', '        return ', content, flags=re.MULTILINE)
    
    # Fix massively over-indented docstrings (should be 8 spaces in method body)
    content = re.sub(r'^[ ]{100,}"""', '        """', content, flags=re.MULTILINE)
    
    # Fix massively over-indented regular statements (should be 8 spaces in method body)
    content = re.sub(r'^[ ]{100,}([a-zA-Z_])', r'        \1', content, flags=re.MULTILINE)
    
    # Fix moderately over-indented lines that should be standard method body (8 spaces)
    content = re.sub(r'^[ ]{60,80}([a-zA-Z_#])', r'        \1', content, flags=re.MULTILINE)
    
    # Fix class definitions that got over-indented (should be 0 spaces)
    content = re.sub(r'^[ ]{80,}class ', 'class ', content, flags=re.MULTILINE)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed brain_integration.py indentation")

if __name__ == '__main__':
    fix_brain_integration()