#!/usr/bin/env python3
"""
Comprehensive Syntax Fixer for LUKHAS Project
Fixes the most common syntax errors systematically
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple

def is_lukhas_file(file_path: Path) -> bool:
    """Check if this is a LUKHAS project file"""
    str_path = str(file_path)
    exclude_patterns = [
        'site-packages', 'node_modules', '.git', '__pycache__',
        '.pytest_cache', '.mypy_cache', 'venv', '.venv', '.env',
        'dist', 'build', '.lintvenv', '.cleanenv'
    ]
    return not any(pattern in str_path for pattern in exclude_patterns)

def fix_common_syntax_errors(content: str) -> Tuple[str, List[str]]:
    """Fix common syntax errors"""
    fixes_applied = []
    
    # 1. Fix missing closing parentheses in f-strings
    # Pattern: f"text {expression" -> f"text {expression}"
    pattern1 = r'f(["\'])([^"\']*?)\{([^}]*?)\1'
    if re.search(pattern1, content):
        content = re.sub(pattern1, r'f\1\2{\3}\1', content)
        fixes_applied.append('Fixed missing closing brace in f-string')
    
    # 2. Fix missing closing parenthesis/brace combinations
    # Pattern: f"text {func()}" -> f"text {func()}"
    pattern2 = r'f(["\'])([^"\']*?)\{([^}]*?)\}([^"\']*?)\}([^"\']*?)\1'
    if re.search(pattern2, content):
        content = re.sub(pattern2, r'f\1\2{\3}\4\1', content)
        fixes_applied.append('Fixed double closing brace in f-string')
    
    # 3. Fix single } in f-strings (common error)
    pattern3 = r'f(["\'])([^"\']*?)\{([^}]*?)\}([^}]*?)\}([^"\']*?)\1'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'f\1\2{\3}\4\1', content)
        fixes_applied.append('Fixed extra closing brace')
    
    # 4. Fix missing quotes after expressions
    pattern4 = r'f(["\'])([^"\']*?)\{([^}]*?)\}([^"\']*?)$'
    matches = re.findall(pattern4, content, re.MULTILINE)
    for match in matches:
        quote, prefix, expr, suffix = match
        if suffix and not suffix.endswith(quote):
            old_line = f'f{quote}{prefix}{{{expr}}{suffix}'
            new_line = f'f{quote}{prefix}{{{expr}}{suffix}{quote}'
            content = content.replace(old_line, new_line)
            fixes_applied.append('Fixed missing closing quote')
    
    # 5. Fix missing imports
    if 'timezone' in content and 'from datetime import' not in content:
        if 'import datetime' in content:
            content = content.replace('import datetime', 'import datetime\nfrom datetime import timezone')
            fixes_applied.append('Added timezone import')
        else:
            # Add at the top after existing imports
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
            lines.insert(insert_pos, 'from datetime import timezone')
            content = '\n'.join(lines)
            fixes_applied.append('Added timezone import')
    
    return content, fixes_applied

def check_syntax(content: str) -> bool:
    """Check if content has valid Python syntax"""
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False

def fix_file(file_path: Path) -> bool:
    """Fix syntax errors in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
        
        # Check if already valid
        if check_syntax(original_content):
            return False  # No fix needed
        
        fixed_content, fixes = fix_common_syntax_errors(original_content)
        
        # Verify the fix worked
        if check_syntax(fixed_content) and fixes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed {file_path.name}: {', '.join(fixes)}")
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main execution"""
    print("🔧 COMPREHENSIVE SYNTAX FIXER")
    print("=" * 50)
    
    # Find all Python files
    lukhas_files = [f for f in Path('.').rglob('*.py') if is_lukhas_file(f)]
    print(f"📁 Found {len(lukhas_files)} LUKHAS Python files")
    
    # Process files with highest priority syntax errors
    priority_patterns = [
        'f-string',
        'closing parenthesis',
        'unterminated string',
        'missing closing quote'
    ]
    
    files_to_fix = []
    for file_path in lukhas_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not check_syntax(content):
                files_to_fix.append(file_path)
        except:
            continue
    
    print(f"❌ Files needing fixes: {len(files_to_fix)}")
    
    # Fix files
    fixed_count = 0
    for file_path in files_to_fix[:50]:  # Fix first 50 files
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\n🎯 RESULTS: Fixed {fixed_count}/{min(50, len(files_to_fix)} files")
    
    # Recount working files
    working_files = 0
    for file_path in lukhas_files[:100]:  # Check first 100
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if check_syntax(content):
                working_files += 1
        except:
            continue
    
    print(f"📊 Working files: {working_files}/100 ({working_files}%)")

if __name__ == "__main__":
    main()
