#!/usr/bin/env python3
"""
Fix Specific F-String Patterns - Surgical Approach
==================================================

Target the exact f-string bracket mismatch patterns identified in error files.
"""

import re
import subprocess
from pathlib import Path


def fix_specific_patterns(content: str) -> str:
    """Fix specific f-string bracket patterns"""
    
    # Pattern 1: f'{variable}}' -> f'{variable}'  (extra closing brace)
    content = re.sub(r"f'([^']*\{[^}]*)\}'", r"f'\1'", content)
    content = re.sub(r'f"([^"]*\{[^}]*)\}"', r'f"\1"', content)
    
    # Pattern 2: {variable}} -> {variable} (inside f-strings)
    content = re.sub(r"(\{[^{}]*)\}([^}]*)", r"\1\2", content)
    
    return content

def fix_file(file_path: str) -> bool:
    """Fix a file with specific f-string patterns"""
    print(f"🔧 Fixing f-string patterns in {file_path}")
    
    try:
        # Read original
        with open(file_path, encoding="utf-8") as f:
            original = f.read()
        
        # Apply fixes
        fixed = fix_specific_patterns(original)
        
        if fixed != original:
            # Write fixed version
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed)
            
            # Test compilation
            result = subprocess.run([".venv/bin/python", "-m", "py_compile", file_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully fixed {file_path}")
                return True
            else:
                # Revert and try manual approach
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original)
                print(f"❌ Pattern fixes failed, trying manual approach...")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    file_path = "candidate/governance/security/security_audit_engine.py"
    fix_file(file_path)
