#!/usr/bin/env python3
"""
Mass F821 Elimination - Phase 2: Targeted File-by-File Mechanical Fixing
========================================================================

This script applies the proven mechanical approach to fix specific files
with high error counts, using the exact rules that worked for demo.py.

MECHANICAL APPROACH RULES:
A.1) Drop f-prefix when no expressions exist  
A.2) Escape literal braces (} → }}, { → {{)
A.3) Close strings and balance fields
A.4) Never alter expression semantics
"""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple


def apply_mechanical_fixes(content: str) -> str:
    """Apply mechanical f-string fixes using proven patterns"""
    
    # Rule A.2 & A.3: Fix common f-string bracket mismatches
    fixes = [
        # Pattern 1: Extra closing brace in nested f-strings
        (r"f'([^']*\{[^}]*)\}'", r"f'\1}'"),
        (r'f"([^"]*\{[^}]*)\}"', r'f"\1}"'),
        
        # Pattern 2: Extra closing brace before colon
        (r"(\{[^}]+)\}:", r"\1:"),
        
        # Pattern 3: Fix bracket mismatches in hashlib patterns
        (r"f'([^']*)\}'", r"f'\1'"),
        (r'f"([^"]*)\}"', r'f"\1"'),
        
        # Pattern 4: Fix unclosed strings
        (r'startswith\("\)  # ":', r'startswith("#"):'),
    ]
    
    fixed_content = content
    total_fixes = 0
    
    for pattern, replacement in fixes:
        matches = len(re.findall(pattern, fixed_content))
        if matches > 0:
            fixed_content = re.sub(pattern, replacement, fixed_content)
            total_fixes += matches
            print(f"Applied fix: {pattern} -> {replacement} ({matches} matches)")
    
    return fixed_content

def fix_file_mechanically(file_path: str) -> bool:
    """Fix a single file using mechanical approach"""
    print(f"\n🔧 Applying mechanical fixes to {file_path}")
    
    try:
        # Read original content
        with open(file_path, encoding="utf-8") as f:
            original_content = f.read()
        
        # Apply fixes
        fixed_content = apply_mechanical_fixes(original_content)
        
        if fixed_content != original_content:
            # Write fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            
            # Test compilation
            result = subprocess.run([".venv/bin/python", "-m", "py_compile", file_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully fixed {file_path}")
                return True
            else:
                # Revert if compilation failed
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
                print(f"❌ Compilation failed for {file_path}, reverted")
                print(f"Error: {result.stderr}")
                return False
        else:
            print(f"ℹ️  No fixes needed for {file_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Fix top error files using mechanical approach"""
    
    # Target the highest error files first
    target_files = [
        "candidate/governance/security/security_audit_engine.py",
        "candidate/core/orchestration/brain/brain_integration_broken.py", 
        "candidate/bridge/cognitive_bridge.py",
    ]
    
    print("🚀 Mass F821 Elimination - Phase 2: Mechanical File Fixing")
    print("=" * 60)
    
    fixed_count = 0
    
    for file_path in target_files:
        if Path(file_path).exists():
            if fix_file_mechanically(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Phase 2 Complete: {fixed_count}/{len(target_files)} files fixed")

if __name__ == "__main__":
    main()