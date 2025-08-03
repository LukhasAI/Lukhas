#!/usr/bin/env python3
"""
🔧 PWM Syntax Error Fixer
========================
Fixes common syntax errors in the LUKHAS PWM codebase.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def fix_empty_try_blocks(file_path: Path) -> int:
    """Fix empty try blocks after commented imports"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for try: followed by commented line or except:
        if line == 'try:':
            # Look ahead to see if next non-empty line is commented or except
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
                
            if j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('#') or next_line.startswith('except'):
                    # Insert pass statement
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    lines.insert(i + 1, ' ' * (indent + 4) + 'pass\n')
                    fixed += 1
                    i += 1
        
        i += 1
    
    if fixed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return fixed


def fix_files_with_syntax_errors() -> None:
    """Fix known files with syntax errors"""
    files_to_fix = [
        'core/orchestration/brain/brain_integration_enhanced.py',
        'core/orchestration/brain/enhanced_brain_integration.py',
        'core/orchestration/brain/spine/main_loop.py',
        'orchestration/brain/brain_integration_enhanced.py',
        'orchestration/brain/enhanced_brain_integration.py',
        'orchestration/brain/spine/main_loop.py',
        'creativity/dream_engine/dream_engine_comprehensive.py',
        'creativity/dream_engine/dream_engine_unified.py',
        'memory/neuro_buffer.py',
        'security/encryption/advanced_encryption.py',
    ]
    
    total_fixed = 0
    
    for file_path in files_to_fix:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            fixed = fix_empty_try_blocks(full_path)
            if fixed > 0:
                print(f"   Fixed {fixed} empty try blocks in {file_path}")
                total_fixed += fixed
    
    return total_fixed


def main():
    """Main function"""
    print("🔧 PWM Syntax Error Fixer")
    print("=" * 60)
    
    print("\n📝 Fixing empty try blocks...")
    total_fixed = fix_files_with_syntax_errors()
    
    print(f"\n✅ Fixed {total_fixed} syntax errors!")
    

if __name__ == "__main__":
    main()