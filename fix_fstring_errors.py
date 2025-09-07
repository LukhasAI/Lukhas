#!/usr/bin/env python3
"""
Fix F-string Formatting Errors
Fix issues where I accidentally changed { to ( in f-strings during mass fixes
"""

import re
import os
from pathlib import Path

def fix_fstring_patterns(content):
    """Fix f-string formatting errors"""
    fixes = 0
    
    # Pattern 1: f"...{variable}..." -> f"...{variable}..."
    pattern1 = r'f"([^"]*)\{([^}]+)\)([^"]*)"'
    matches = re.findall(pattern1, content)
    if matches:
        content = re.sub(pattern1, r'f"\1{\2}\3"', content)
        fixes += len(matches)
    
    # Pattern 2: f'...{variable}...' -> f'...{variable}...'
    pattern2 = r"f'([^']*)\{([^}]+)\)([^']*)'"
    matches = re.findall(pattern2, content)
    if matches:
        content = re.sub(pattern2, r"f'\1{\2}\3'", content)
        fixes += len(matches)
    
    return content, fixes

def process_files():
    """Process all Python files to fix f-string errors"""
    total_files_fixed = 0
    total_fixes = 0
    
    print("🔧 Fixing f-string formatting errors...")
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        skip_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = Path(root) / file
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                fixed_content, fixes_made = fix_fstring_patterns(original_content)
                
                if fixes_made > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    total_files_fixed += 1
                    total_fixes += fixes_made
                    
                    print(f"✅ {file_path}: {fixes_made} f-string fixes")
                
            except Exception as e:
                continue
    
    return total_files_fixed, total_fixes

if __name__ == "__main__":
    print("🔧 F-STRING ERROR FIXER")
    print("=" * 50)
    
    files_fixed, total_fixes = process_files()
    
    print("=" * 50)
    print("📊 F-STRING FIX RESULTS:")
    print(f"  📁 Files fixed: {files_fixed}")
    print(f"  🔧 Total fixes: {total_fixes}")
    print("=" * 50)