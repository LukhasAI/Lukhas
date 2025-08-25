#!/usr/bin/env python3
"""
Test Import Path Migration Script
Systematically fixes lukhas -> candidate imports in test files
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: from lukhas.module import ...
        content = re.sub(r'from lukhas\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'from candidate.\1', content)
        
        # Pattern 2: import lukhas.module
        content = re.sub(r'import lukhas\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'import candidate.\1', content)
        
        # Pattern 3: lukhas.module.function() calls
        content = re.sub(r'\blukhas\.([a-zA-Z_][a-zA-Z0-9_.]*)', r'candidate.\1', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main migration function"""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("tests/ directory not found")
        return
    
    fixed_files = []
    total_files = 0
    
    # Find all Python files in tests directory
    for py_file in tests_dir.rglob("*.py"):
        if py_file.is_file():
            total_files += 1
            if fix_imports_in_file(py_file):
                fixed_files.append(str(py_file))
    
    print(f"✅ Import Migration Complete!")
    print(f"📊 Files processed: {total_files}")
    print(f"🔧 Files modified: {len(fixed_files)}")
    
    if fixed_files:
        print(f"\n📋 Modified files:")
        for file_path in sorted(fixed_files):
            print(f"  - {file_path}")
    
    print(f"\n🧪 Next steps:")
    print(f"1. Review the changes: git diff tests/")
    print(f"2. Test a few key files: python -m pytest tests/[specific_test] -v")
    print(f"3. Run full test suite: python -m pytest tests/ --co -q")

if __name__ == "__main__":
    main()