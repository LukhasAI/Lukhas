#!/usr/bin/env python3
"""
Future Import Positioning Fixer
===============================
Systematically fixes __future__ import positioning issues across the codebase.

__future__ imports MUST be at the very beginning of the file (after docstring)
before any other imports or code.
"""
import ast
import re
from pathlib import Path
from typing import List


class FutureImportFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors = []
    
    def has_future_import_issue(self, content: str) -> bool:
        """Check if file has __future__ import positioning issue"""
        if 'from __future__ import' not in content:
            return False
            
        lines = content.split('\n')
        future_line_idx = -1
        
        # Find __future__ import line
        for i, line in enumerate(lines):
            if line.strip().startswith('from __future__ import'):
                future_line_idx = i
                break
                
        if future_line_idx == -1:
            return False
            
        # Check if there are non-docstring, non-comment lines before it
        in_docstring = False
        docstring_closed = False
        
        for i in range(future_line_idx):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Handle docstrings
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    # Check if docstring opens and closes on same line
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        in_docstring = False
                        docstring_closed = True
                else:
                    in_docstring = False
                    docstring_closed = True
                continue
                    
            if in_docstring:
                continue
                
            # Skip shebang and encoding
            if line.startswith('#!') or 'coding' in line or 'encoding' in line:
                continue
                
            # Skip regular comments
            if line.startswith('#'):
                continue
                
            # If we found any import or code before __future__, it's a problem
            if line.startswith(('import ', 'from ')) or any(c.isalpha() for c in line):
                return True
                
        return False
    
    def fix_future_import_positioning(self, content: str) -> str:
        """Fix __future__ import positioning"""
        if not self.has_future_import_issue(content):
            return content
            
        lines = content.split('\n')
        future_imports = []
        other_lines = []
        
        # Extract all __future__ imports
        for line in lines:
            if line.strip().startswith('from __future__ import'):
                future_imports.append(line)
            else:
                other_lines.append(line)
        
        if not future_imports:
            return content
            
        # Find insertion point (after docstring, before any other code)
        insert_idx = 0
        in_docstring = False
        
        for i, line in enumerate(other_lines):
            stripped = line.strip()
            
            # Handle docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                    if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                        in_docstring = False
                        insert_idx = i + 1
                else:
                    in_docstring = False
                    insert_idx = i + 1
                continue
                    
            if in_docstring:
                continue
                
            # Skip shebang and encoding
            if stripped.startswith('#!') or 'coding' in stripped or 'encoding' in stripped:
                insert_idx = i + 1
                continue
                
            # Found first non-docstring, non-shebang line
            if stripped and not stripped.startswith('#'):
                break
                
        # Insert __future__ imports at the correct position
        result_lines = other_lines[:insert_idx]
        
        # Add empty line before __future__ if needed
        if result_lines and result_lines[-1].strip():
            result_lines.append('')
            
        result_lines.extend(future_imports)
        
        # Add empty line after __future__ if needed
        if insert_idx < len(other_lines) and other_lines[insert_idx].strip():
            result_lines.append('')
            
        result_lines.extend(other_lines[insert_idx:])
        
        self.fixes_applied += 1
        return '\n'.join(result_lines)
    
    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix __future__ imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            if not self.has_future_import_issue(original_content):
                return False
                
            fixed_content = self.fix_future_import_positioning(original_content)
            
            # Validate syntax
            if not self.validate_syntax(fixed_content):
                self.errors.append(f"Syntax validation failed: {file_path}")
                return False
                
            # Only write if content changed
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True
                
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            
        return False
    
    def process_directory(self, directory: Path):
        """Process all Python files in directory"""
        print(f"📂 Processing: {directory}")
        fixed_count = 0
        
        for py_file in directory.rglob("*.py"):
            # Skip certain directories
            if any(skip in str(py_file) for skip in ['__pycache__', '.venv', 'node_modules']):
                continue
                
            self.files_processed += 1
                
            if self.fix_file(py_file):
                print(f"✅ Fixed: {py_file}")
                fixed_count += 1
                
        print(f"   Files processed: {self.files_processed}")
        print(f"   Files fixed: {fixed_count}")
    
    def run_future_import_fixes(self, target_dirs: List[str]):
        """Run __future__ import fixes on target directories"""
        print("🔮 FUTURE IMPORT POSITIONING FIXER")
        print("=" * 50)
        
        for dir_name in target_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                self.process_directory(dir_path)
        
        print(f"\n🎯 FUTURE IMPORT FIXES COMPLETE!")
        print(f"📁 Files processed: {self.files_processed}")
        print(f"✅ Files fixed: {self.fixes_applied}")
        
        if self.errors:
            print(f"\n⚠️ Errors: {len(self.errors}")
            for error in self.errors[:5]:
                print(f"   {error}")


def main():
    fixer = FutureImportFixer()
    
    # Focus on core consciousness and system directories
    target_directories = [
        'candidate/consciousness',
        'candidate/memory',
        'candidate/core', 
        'lukhas',
        'consciousness'
    ]
    
    fixer.run_future_import_fixes(target_directories)


if __name__ == "__main__":
    main()