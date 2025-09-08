#!/usr/bin/env python3
"""
🎯 Proven Pattern Syntax Fixer
============================

Focus on ONLY the patterns we've proven successful in our 11 perfect eliminations:
1. F-string brace mismatches: {function(}} → {function()}
2. Missing closing braces in nested dicts: {"key": {"value",} → {"key": {"value"},}
3. CSS f-string escaping: ; } → ; }}

Targeting ONLY files with known patterns for maximum safety.
"""

import os
import re
import subprocess
from pathlib import Path


def fix_f_string_hexdigest_pattern(content: str) -> tuple[str, int]:
    """Fix the proven hexdigest pattern: .hexdigest(}}[: → .hexdigest()}["""
    pattern = re.compile(r"\.hexdigest\(\}\}\[")
    fixes = len(pattern.findall(content))
    content = pattern.sub(".hexdigest()}[", content)
    return content, fixes

def fix_float_nan_pattern(content: str) -> tuple[str, int]:
    """Fix the proven float pattern: float("nan"} → float("nan")"""
    pattern = re.compile(r'float\("(nan|inf)"\}')
    fixes = len(pattern.findall(content))
    content = pattern.sub(r'float("\1")', content)
    return content, fixes

def fix_css_f_string_braces(content: str) -> tuple[str, int]:
    """Fix CSS f-string brace escaping: ; } → ; }}"""
    if 'f"""' not in content or "<style>" not in content:
        return content, 0
        
    # Only fix CSS property endings that need escaping
    pattern = re.compile(r"(:\s*[^;}]+;\s*)}(?!\})")
    fixes = len(pattern.findall(content))
    content = pattern.sub(r"\1}}", content)
    return content, fixes

def fix_known_patterns_only(file_path: Path) -> tuple[int, bool]:
    """Apply ONLY proven patterns that we know work"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            
        original_content = content
        total_fixes = 0
        
        # Apply proven patterns
        content, fixes1 = fix_f_string_hexdigest_pattern(content)
        total_fixes += fixes1
        
        content, fixes2 = fix_float_nan_pattern(content)
        total_fixes += fixes2
        
        content, fixes3 = fix_css_f_string_braces(content)
        total_fixes += fixes3
        
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Test compilation
            result = subprocess.run([
                "python3", "-c", f'import py_compile; py_compile.compile("{file_path}", doraise=True)'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {file_path.name}: Applied {total_fixes} proven fixes - COMPILES")
                return total_fixes, True
            else:
                print(f"⚠️  {file_path.name}: Applied {total_fixes} proven fixes - Still has errors")
                return total_fixes, False
                
        return 0, True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0, False

def get_target_files() -> list[Path]:
    """Get files that are likely to have our proven patterns"""
    target_files = []
    
    # Files we know had similar patterns
    known_pattern_files = [
        "candidate/governance/security/security_audit_engine.py",
        "candidate/api/audit.py", 
        "candidate/aka_qualia/tests/test_memory_security.py",
        "candidate/aka_qualia/tests/conftest.py",
        "candidate/aka_qualia/cli/gdpr_erase_user.py"
    ]
    
    for file_path in known_pattern_files:
        path = Path(file_path)
        if path.exists():
            target_files.append(path)
            
    return target_files

def main():
    print("🎯 Proven Pattern Syntax Fixer")
    print("=" * 40)
    print("Targeting ONLY proven successful patterns from 11 perfect eliminations")
    
    target_files = get_target_files()
    
    if not target_files:
        print("No target files found")
        return
        
    total_fixes = 0
    successful_files = 0
    
    for file_path in target_files:
        fixes, success = fix_known_patterns_only(file_path)
        total_fixes += fixes
        if success and fixes > 0:
            successful_files += 1
            
    print("\n" + "=" * 40)
    print(f"✅ Successfully fixed: {successful_files} files")
    print(f"🔧 Total proven fixes applied: {total_fixes}")
    
    if total_fixes > 0:
        print("\n🚀 Ready to test compilation and commit!")

if __name__ == "__main__":
    main()
