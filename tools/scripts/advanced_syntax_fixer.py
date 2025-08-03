#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Syntax Fixer - Handles complex syntax errors
"""

import os
import re
import ast
import shutil
from datetime import datetime
from pathlib import Path

class AdvancedSyntaxFixer:
    """Advanced fixer for complex syntax errors"""
    
    def __init__(self):
        self.fixed_count = 0
        self.failed_count = 0
        self.backup_dir = Path('healing/advanced_backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def fix_nested_quotes(self, content):
        """Fix nested triple quotes and string issues"""
        lines = content.split('\n')
        fixed_lines = []
        in_triple_quote = False
        quote_type = None
        
        for i, line in enumerate(lines):
            # Detect problematic nested quotes pattern
            if 'f.write(""""""' in line or 'f.write(\'\'\'\'\'\'':
                # This is a common pattern where someone tries to write triple quotes
                fixed_lines.append(line.replace('""""""', 'r"""'))
                fixed_lines.append('"""')  # Close the string properly
                continue
            
            # Handle unclosed triple quotes
            if '"""' in line:
                count = line.count('"""')
                if count % 2 == 1:  # Odd number means unclosed
                    in_triple_quote = not in_triple_quote
                    quote_type = '"""'
            elif "'''" in line:
                count = line.count("'''")
                if count % 2 == 1:
                    in_triple_quote = not in_triple_quote
                    quote_type = "'''"
            
            fixed_lines.append(line)
        
        # If still in triple quote at end, close it
        if in_triple_quote:
            fixed_lines.append(quote_type)
        
        return '\n'.join(fixed_lines)
    
    def fix_duplicate_statements(self, content):
        """Fix duplicate statements on same line"""
        # Fix pattern like: statement()    statement()
        pattern = r'(\w+\([^)]*\))\s+(\1)'
        content = re.sub(pattern, r'\1', content)
        return content
    
    def fix_string_escapes(self, content):
        """Fix string escape issues"""
        # Fix backslash at end of line in strings
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for string with backslash at end
            if line.rstrip().endswith('\\') and ('"' in line or "'" in line):
                # Check if it's inside a string
                if line.count('"') % 2 == 1 or line.count("'") % 2 == 1:
                    line = line.rstrip('\\').rstrip() + '"'
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_encoding_issues(self, content):
        """Fix encoding and special character issues"""
        # Replace problematic characters
        replacements = {
            '\u039b': 'Lambda',  # Greek Lambda
            '\u2014': '-',       # Em dash
            '\u2013': '-',       # En dash
            '\u201c': '"',       # Left double quote
            '\u201d': '"',       # Right double quote
            '\u2018': "'",       # Left single quote
            '\u2019': "'",       # Right single quote
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        return content
    
    def fix_file(self, filepath):
        """Fix a file with advanced techniques"""
        # Create backup
        backup_path = self.backup_dir / (Path(filepath).name + f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.backup')
        
        try:
            # Try to copy file for backup
            shutil.copy2(filepath, backup_path)
        except:
            print(f"Warning: Could not backup {filepath}")
        
        try:
            # Read with error handling
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Apply fixes in order
            content = self.fix_encoding_issues(content)
            content = self.fix_nested_quotes(content)
            content = self.fix_duplicate_statements(content)
            content = self.fix_string_escapes(content)
            
            # Write fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Verify fix
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                ast.parse(test_content)
                self.fixed_count += 1
                return True
            except:
                # Restore backup if still broken
                if backup_path.exists():
                    shutil.copy2(backup_path, filepath)
                self.failed_count += 1
                return False
                
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
            # Restore backup
            if backup_path.exists():
                shutil.copy2(backup_path, filepath)
            self.failed_count += 1
            return False
    
    def find_syntax_errors(self):
        """Find all Python files with syntax errors"""
        errors = []
        
        for root, dirs, files in os.walk('.'):
            # Skip virtual environments and git
            if any(skip in root for skip in ['.venv', '.git', '__pycache__', '.pwm_cleanup_archive']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        ast.parse(content)
                    except:
                        errors.append(filepath)
        
        return errors

def main():
    """Run the advanced syntax fixer"""
    print("[Advanced Syntax Fixer] Starting...")
    print("=" * 50)
    
    fixer = AdvancedSyntaxFixer()
    
    # Find all syntax errors
    print("[Scanning] Looking for syntax errors...")
    errors = fixer.find_syntax_errors()
    
    if not errors:
        print("[OK] No syntax errors found!")
        return
    
    print(f"Found {len(errors)} files with syntax errors")
    
    # Fix errors
    print(f"\n[Fixing] Attempting advanced fixes on {len(errors)} files...")
    
    for i, filepath in enumerate(errors):
        print(f"Fixing {i+1}/{len(errors)}: {filepath}...", end='')
        success = fixer.fix_file(filepath)
        print(" [OK]" if success else " [FAILED]")
    
    # Summary
    print("\n" + "=" * 50)
    print("[ADVANCED FIXING COMPLETE]")
    print("=" * 50)
    print(f"[Fixed] {fixer.fixed_count} files")
    print(f"[Failed] {fixer.failed_count} files")
    
    # Rescan to confirm
    print("\n[Rescanning] Verifying fixes...")
    remaining = fixer.find_syntax_errors()
    print(f"[Status] Remaining syntax errors: {len(remaining)}")
    
    if remaining:
        print("\n[Files Still With Errors]")
        for f in remaining[:10]:
            print(f"  - {f}")
        if len(remaining) > 10:
            print(f"  ... and {len(remaining) - 10} more")

if __name__ == "__main__":
    main()