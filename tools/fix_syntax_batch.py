#!/usr/bin/env python3
"""
Batch syntax error fixer for LUKHAS codebase.
"""

import re
import subprocess
import json
import os


def get_syntax_errors():
    """Get files with syntax errors from ruff output."""
    try:
        result = subprocess.run([
            'python3', '-m', 'ruff', 'check', '.', 
            '--output-format=json'
        ], capture_output=True, text=True, cwd='/Users/agi_dev/LOCAL-REPOS/Lukhas')
        
        if result.stdout:
            violations = json.loads(result.stdout)
            syntax_errors = []
            
            for violation in violations:
                message = violation.get('message', '').lower()
                if ('syntax' in message or 
                    'expected' in message or 
                    'unexpected' in message or
                    'cannot follow' in message or
                    'positional argument' in message):
                    syntax_errors.append(violation)
            
            return syntax_errors
    except Exception as e:
        print(f"Error getting syntax errors: {e}")
    
    return []


def fix_common_syntax_patterns(file_path):
    """Apply common syntax fixes to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Remove malformed timezone parameters
        content = re.sub(r',\s*,\s*timezone\)', r')', content)
        content = re.sub(r'= None,\s*timezone\)', r'= None, timezone=None)', content)
        
        # Fix 2: Fix logger calls with incorrect timezone params
        content = re.sub(r'logger\.getLogger\([^)]+,\s*timezone\)', 
                        lambda m: m.group(0).replace(', timezone', ''), content)
        
        # Fix 3: Fix incomplete f-strings
        content = re.sub(r'f"[^"]*\{[^}]*:\s*$', lambda m: m.group(0) + '}', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function."""
    print("🔧 Fixing syntax errors in batch...")
    
    syntax_errors = get_syntax_errors()
    files_with_errors = set()
    
    for error in syntax_errors:
        if error.get('filename'):
            files_with_errors.add(error['filename'])
    
    print(f"Found {len(files_with_errors)} files with syntax errors")
    
    fixed_count = 0
    for file_path in list(files_with_errors)[:50]:  # Process first 50 files
        if fix_common_syntax_patterns(file_path):
            fixed_count += 1
            short_path = file_path.replace('/Users/agi_dev/LOCAL-REPOS/Lukhas/', '')
            print(f"✅ Fixed: {short_path}")
    
    print(f"\n🎉 Fixed {fixed_count} files")


if __name__ == "__main__":
    main()