#!/usr/bin/env python3
"""
Surgical Syntax Recovery Tool
============================
Future-proof recovery from F821 cleanup syntax corruption.

This tool uses AST parsing and pattern matching to surgically fix
syntax errors introduced during automated import insertion while
preserving the 84% F821 reduction achievement.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class SurgicalSyntaxRecovery:
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        self.errors = []
        
        # Define corruption patterns and their fixes
        self.corruption_patterns = {
            'function_param_timezone': {
                'pattern': r'def\s+(\w+)\s*\([^)]*,\s*timezone\s*\)',
                'description': 'Functions with timezone wrongly added as parameter',
                'fix_type': 'remove_param'
            },
            'logger_getlogger_timezone': {
                'pattern': r'logging\.getLogger\([^,)]+,\s*timezone\)',
                'description': 'Logger calls with timezone as extra parameter',
                'fix_type': 'remove_param'
            },
            'get_logger_timezone': {
                'pattern': r'get_logger\([^,)]+,\s*timezone\)',
                'description': 'get_logger calls with timezone as extra parameter', 
                'fix_type': 'remove_param'
            },
            'import_trailing_timezone': {
                'pattern': r'import\s+[^,\n]+,\s*timezone\)',
                'description': 'Import statements with trailing timezone)',
                'fix_type': 'remove_trailing'
            },
            'from_import_trailing_timezone': {
                'pattern': r'from\s+[^,\n]+\s+import\s+[^,\n]+,\s*timezone\)',
                'description': 'From-import with trailing timezone)',
                'fix_type': 'remove_trailing'
            }
        }
    
    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax using AST"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def fix_function_param_corruption(self, content: str) -> str:
        """Fix function parameters with wrongly added timezone"""
        # Pattern: def func(self, other_param):
        pattern = r'(def\s+\w+\s*\([^)]*),\s*timezone(\s*\):)'
        replacement = r'\1\2'
        
        fixed_content = re.sub(pattern, replacement, content)
        
        if fixed_content != content:
            self.fixes_applied += 1
            
        return fixed_content
    
    def fix_logger_call_corruption(self, content: str) -> str:
        """Fix logger calls with wrongly added timezone parameter"""
        patterns = [
            # logging.getLogger("name", timezone)
            (r'(logging\.getLogger\([^,)]+),\s*timezone\)', r'\1)'),
            # get_logger("name", timezone)  
            (r'(get_logger\([^,)]+),\s*timezone\)', r'\1)'),
        ]
        
        fixed_content = content
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, fixed_content)
            if new_content != fixed_content:
                self.fixes_applied += 1
                fixed_content = new_content
                
        return fixed_content
    
    def fix_import_corruption(self, content: str) -> str:
        """Fix import statements with trailing timezone)"""
        patterns = [
            # import module)
            (r'(import\s+[^,\n]+),\s*timezone\)', r'\1'),
            # from module import item)
            (r'(from\s+[^,\n]+\s+import\s+[^,\n]+),\s*timezone\)', r'\1'),
        ]
        
        fixed_content = content
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, fixed_content)
            if new_content != fixed_content:
                self.fixes_applied += 1
                fixed_content = new_content
                
        return fixed_content
    
    def surgical_fix_file(self, file_path: Path) -> bool:
        """Apply surgical fixes to a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip if already valid
            if self.validate_syntax(original_content):
                return False
                
            content = original_content
            
            # Apply fixes in order
            content = self.fix_function_param_corruption(content)
            content = self.fix_logger_call_corruption(content)  
            content = self.fix_import_corruption(content)
            
            # Only write if we made changes and syntax is now valid
            if content != original_content and self.validate_syntax(content):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            elif content != original_content:
                # We made changes but syntax still invalid - record error
                self.errors.append(f"Fixes applied but syntax still invalid: {file_path}")
                
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            
        return False
    
    def process_directory(self, directory: Path) -> Dict[str, int]:
        """Process all Python files in directory"""
        results = {
            'files_processed': 0,
            'files_fixed': 0,
            'syntax_errors_resolved': 0,
            'fixes_applied': 0
        }
        
        for py_file in directory.rglob("*.py"):
            # Skip certain directories
            if any(skip in str(py_file) for skip in ['__pycache__', '.venv', 'node_modules', 'website_v1']):
                continue
                
            results['files_processed'] += 1
            
            if self.surgical_fix_file(py_file):
                results['files_fixed'] += 1
                print(f"✅ Fixed: {py_file}")
                
        results['fixes_applied'] = self.fixes_applied
        return results
    
    def run_surgical_recovery(self, target_dirs: List[str]) -> None:
        """Run surgical syntax recovery on target directories"""
        print("🔧 SURGICAL SYNTAX RECOVERY - Future-Proof Edition")
        print("=" * 60)
        
        total_results = {
            'files_processed': 0,
            'files_fixed': 0,
            'fixes_applied': 0
        }
        
        for dir_name in target_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue
                
            print(f"\n📂 Processing: {dir_name}")
            results = self.process_directory(dir_path)
            
            # Accumulate totals
            for key in total_results:
                total_results[key] += results[key]
                
            print(f"   Files processed: {results['files_processed']}")
            print(f"   Files fixed: {results['files_fixed']}")
            print(f"   Fixes applied: {results['fixes_applied']}")
        
        print(f"\n🎯 SURGICAL RECOVERY COMPLETE!")
        print(f"📁 Total files processed: {total_results['files_processed']}")
        print(f"✅ Total files fixed: {total_results['files_fixed']}")  
        print(f"🔧 Total fixes applied: {total_results['fixes_applied']}")
        
        if self.errors:
            print(f"\n⚠️ Errors encountered: {len(self.errors}")
            for error in self.errors[:5]:
                print(f"   {error}")


def main():
    """Main recovery execution"""
    recovery = SurgicalSyntaxRecovery()
    
    # Target core directories where consciousness systems are located
    target_directories = [
        'candidate/consciousness',
        'candidate/memory', 
        'candidate/bridge',
        'candidate/governance',
        'candidate/tools',
        'lukhas',
        'branding'
    ]
    
    recovery.run_surgical_recovery(target_directories)


if __name__ == "__main__":
    main()