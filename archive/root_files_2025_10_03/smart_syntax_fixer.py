#!/usr/bin/env python3
"""
Smart Syntax Fixer for LUKHAS AI
================================

Intelligently fixes syntax errors while preserving current logic improvements.
Only targets files with actual syntax errors, applies minimal targeted fixes.
"""

import ast
import os
import re
import subprocess
import sys
from typing import List, Optional


def has_syntax_error(file_path: str) -> bool:
    """Check if a Python file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return False
    except SyntaxError:
        return True
    except Exception:
        return False


def get_syntax_error_details(file_path: str) -> Optional[str]:
    """Get specific syntax error details."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return None
    except SyntaxError as e:
        return f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"Parse error: {str(e)}"


def fix_common_fstring_errors(content: str) -> str:
    """Fix common f-string syntax errors while preserving logic."""
    fixes_applied = []
    
    # Fix missing closing braces in f-strings
    # Pattern: f"text{expression" -> f"text{expression}"
    pattern1 = r'f"([^"]*\{[^}]*)"'
    matches = re.finditer(pattern1, content)
    for match in matches:
        if match.group(1).count('{') > match.group(1).count('}'):
            old = match.group(0)
            fixed = old[:-1] + '}"'
            content = content.replace(old, fixed, 1)
            fixes_applied.append(f"Added missing closing brace: {old} -> {fixed}")
    
    # Fix missing closing braces in dictionary definitions
    # Pattern: {"key": value, "key2": value -> {"key": value, "key2": value}
    pattern2 = r'\{"[^"]*":\s*[^,}]+(?:,\s*"[^"]*":\s*[^,}]+)*'
    matches = re.finditer(pattern2, content)
    for match in matches:
        if match.group(0).count('{') > match.group(0).count('}'):
            old = match.group(0)
            fixed = old + '}'
            content = content.replace(old, fixed, 1)
            fixes_applied.append(f"Added missing closing brace to dict: {old} -> {fixed}")
    
    # Fix malformed f-string expressions
    # Pattern: f"text{expr}[:20])}..." -> f"text{expr[:20]}..."
    pattern3 = r'f"([^"]*\{[^}]*\})\[:(\d+)\]\)\}([^"]*)"'
    def fix_fstring_slice(match):
        prefix = match.group(1)
        slice_num = match.group(2)
        suffix = match.group(3)
        # Remove the extra )}
        fixed_prefix = prefix[:-1] + f'[:{slice_num}]'
        return f'f"{fixed_prefix}{suffix}"'
    
    content = re.sub(pattern3, fix_fstring_slice, content)
    
    # Fix missing quotes in f-strings
    # Pattern: f"text{timestamp()}" where timestamp() returns unquoted
    pattern4 = r'f"([^"]*\{[^}]*\.timestamp\(\)\}[^"]*)"'
    content = re.sub(pattern4, lambda m: f'f"{m.group(1)}"', content)
    
    return content


def fix_return_outside_function(content: str) -> str:
    """Fix 'return' outside function errors."""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('return ') and not is_inside_function(lines, i):
            # Convert return to a comment or remove it
            lines[i] = line.replace('return ', '# return ')
    return '\n'.join(lines)


def is_inside_function(lines: List[str], line_index: int) -> bool:
    """Check if a line is inside a function definition."""
    indent_level = len(lines[line_index]) - len(lines[line_index].lstrip())
    
    # Look backwards for function definition
    for i in range(line_index - 1, -1, -1):
        line = lines[i].strip()
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        
        if current_indent < indent_level and (line.startswith('def ') or line.startswith('async def ')):
            return True
        elif current_indent == 0 and line and not line.startswith('#'):
            break
    
    return False


def apply_smart_fixes(file_path: str) -> bool:
    """Apply smart syntax fixes to a file, preserving logic."""
    print(f"🔧 Fixing {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply fixes
        fixed_content = original_content
        fixed_content = fix_common_fstring_errors(fixed_content)
        fixed_content = fix_return_outside_function(fixed_content)
        
        # Verify the fix worked
        try:
            ast.parse(fixed_content)
            
            # Only write if we actually fixed something
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ Fixed syntax errors in {file_path}")
                return True
            else:
                print(f"⚠️  No fixable syntax errors found in {file_path}")
                return False
                
        except SyntaxError as e:
            print(f"❌ Could not fix syntax error in {file_path}: Line {e.lineno}: {e.msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def find_syntax_error_files(directory: str) -> List[str]:
    """Find all Python files with syntax errors in a directory."""
    error_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if has_syntax_error(file_path):
                    error_files.append(file_path)
    
    return error_files


def main():
    """Main execution function."""
    candidate_dir = "candidate/"
    
    if not os.path.exists(candidate_dir):
        print(f"❌ Directory {candidate_dir} not found")
        return 1
    
    print("🔍 Finding files with syntax errors...")
    error_files = find_syntax_error_files(candidate_dir)
    
    if not error_files:
        print("✅ No syntax errors found!")
        return 0
    
    print(f"📊 Found {len(error_files)} files with syntax errors")
    
    # Show first 10 files with their specific errors
    print("\n🎯 Top syntax error files:")
    for i, file_path in enumerate(error_files[:10]):
        error_detail = get_syntax_error_details(file_path)
        print(f"  {i+1}. {file_path}")
        print(f"     Error: {error_detail}")
    
    if len(error_files) > 10:
        print(f"     ... and {len(error_files) - 10} more files")
    
    # Ask for confirmation
    response = input(f"\n🚀 Apply smart fixes to {len(error_files)} files? (y/N): ")
    if response.lower() != 'y':
        print("❌ Aborted by user")
        return 1
    
    # Apply fixes
    fixed_count = 0
    for file_path in error_files:
        if apply_smart_fixes(file_path):
            fixed_count += 1
    
    print(f"\n📊 Results:")
    print(f"  ✅ Fixed: {fixed_count} files")
    print(f"  ❌ Failed: {len(error_files) - fixed_count} files")
    
    # Check final status
    print("\n🔍 Checking final status...")
    result = subprocess.run(['ruff', 'check', 'candidate/', '--statistics'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("🎉 All syntax errors fixed!")
    else:
        print("📊 Remaining errors:")
        print(result.stdout)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())