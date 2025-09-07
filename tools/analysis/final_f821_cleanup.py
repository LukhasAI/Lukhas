#!/usr/bin/env python3
"""
Final F821 Cleanup - Phase 3
Target the remaining 1,638 violations with surgical precision

Remaining patterns:
- 427 st violations (streamlit)
- 274 log violations (logger declarations)  
- 51 logging violations
- 17 timezone violations
- Other specific patterns
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set
import subprocess


class FinalF821Cleanup:
    def __init__(self):
        self.fixes_applied = 0
        self.files_modified = 0
        self.errors = []
        
        # Remaining violation patterns and fixes
        self.remaining_fixes = {
            'st': {
                'import_statement': 'import streamlit as st',
                'check_patterns': [r'st\.', r'\bst\b'],
                'import_patterns': [r'import streamlit', r'import streamlit as st']
            },
            'log': {
                'import_statement': 'import logging\nlog = logging.getLogger(__name__)',
                'check_patterns': [r'log\.(info|debug|warning|error|critical|exception)'],
                'import_patterns': [r'log\s*=\s*logging\.getLogger']
            },
            'logging': {
                'import_statement': 'import logging',
                'check_patterns': [r'logging\.'],
                'import_patterns': [r'import logging']
            },
            'timezone': {
                'import_statement': 'from datetime import timezone',
                'check_patterns': [r'timezone\.utc', r'timezone\('],
                'import_patterns': [r'from datetime import.*timezone', r'import datetime.*timezone']
            },
            'time': {
                'import_statement': 'import time',
                'check_patterns': [r'time\.(sleep|time|perf_counter)'],
                'import_patterns': [r'import time']
            },
            'os': {
                'import_statement': 'import os',
                'check_patterns': [r'os\.(path|environ|getcwd)'],
                'import_patterns': [r'import os']
            },
            're': {
                'import_statement': 'import re',
                'check_patterns': [r're\.(match|search|sub|findall)'],
                'import_patterns': [r'import re']
            }
        }

    def get_violations_for_file(self, file_path: Path) -> List[str]:
        """Get F821 violations for a specific file"""
        try:
            result = subprocess.run([
                '.venv/bin/ruff', 'check', str(file_path), 
                '--select=F821', '--output-format=concise'
            ], capture_output=True, text=True)
            
            violations = []
            for line in result.stdout.split('\n'):
                if 'F821 Undefined name' in line:
                    match = re.search(r'Undefined name `([^`]+)`', line)
                    if match:
                        violations.append(match.group(1))
            
            return violations
        except Exception as e:
            self.errors.append(f"Error getting violations for {file_path}: {e}")
            return []

    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze file content and determine needed fixes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'content': '', 'needed_fixes': []}
        
        needed_fixes = []
        
        # Check each remaining violation pattern
        for violation_name, fix_info in self.remaining_fixes.items():
            # Check if violation is used in code
            has_usage = any(re.search(pattern, content) for pattern in fix_info['check_patterns'])
            
            if has_usage:
                # Check if appropriate import already exists
                has_import = any(re.search(pattern, content) for pattern in fix_info['import_patterns'])
                
                if not has_import:
                    needed_fixes.append(violation_name)
        
        return {
            'content': content,
            'needed_fixes': needed_fixes,
            'error': None
        }

    def apply_fixes(self, file_path: Path, analysis: Dict) -> bool:
        """Apply fixes to file"""
        if analysis.get('error') or not analysis.get('needed_fixes'):
            return False
        
        content = analysis['content']
        original_content = content
        
        # Apply fixes for each needed violation
        for fix_name in analysis['needed_fixes']:
            if fix_name in self.remaining_fixes:
                import_statement = self.remaining_fixes[fix_name]['import_statement']
                content = self.add_import_safely(content, import_statement)
        
        # Additional cleanup fixes
        content = self.apply_specific_fixes(content)
        
        # Validate syntax
        if not self.validate_syntax(content):
            self.errors.append(f"Syntax validation failed for {file_path}")
            return False
        
        # Write back if modified
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                self.errors.append(f"Error writing {file_path}: {e}")
                return False
        
        return False

    def apply_specific_fixes(self, content: str) -> str:
        """Apply specific fixes for common issues"""
        
        # Fix logger parameter corruption
        content = re.sub(
            r'logger = logging\.getLogger\([^,)]+,\s*st\)',
            'logger = logging.getLogger(__name__)',
            content
        )
        
        # Fix function parameter corruption  
        content = re.sub(
            r'def __init__\(self,\s*(st|log|logging|timezone|time|os|re)\s*\):',
            'def __init__(self):',
            content
        )
        
        # Fix sys.path.append parameter corruption
        content = re.sub(
            r'sys\.path\.append\([^,)]+,\s*(st|log|logging|timezone)\)',
            'sys.path.append(".")',
            content
        )
        
        return content

    def add_import_safely(self, content: str, import_statement: str) -> str:
        """Add import statement safely"""
        lines = content.split('\n')
        
        # Check if import already exists (handle variations)
        import_parts = import_statement.strip().split('\n')
        
        for import_part in import_parts:
            import_part = import_part.strip()
            if not import_part:
                continue
            
            # Check for existing import
            if any(import_part in line or self.imports_similar(line.strip(), import_part) 
                   for line in lines):
                continue
            
            # Find insertion point
            insert_idx = self.find_import_insertion_point(lines)
            lines.insert(insert_idx, import_part)
        
        return '\n'.join(lines)

    def imports_similar(self, existing: str, new: str) -> bool:
        """Check if imports are similar/equivalent"""
        # Handle common variations
        patterns = [
            (r'import streamlit as st', r'import streamlit'),
            (r'import logging', r'import logging'),
            (r'from datetime import timezone', r'from datetime import.*timezone'),
        ]
        
        for pattern, check in patterns:
            if re.match(pattern, new) and re.search(check, existing):
                return True
        
        return False

    def find_import_insertion_point(self, lines: List[str]) -> int:
        """Find appropriate insertion point for imports"""
        insert_idx = 0
        
        # Skip shebang and encoding
        for i, line in enumerate(lines[:5]):
            if line.strip().startswith('#') and ('coding' in line or 'encoding' in line or line.startswith('#!')):
                insert_idx = i + 1
        
        # Skip docstrings and find last import
        in_docstring = False
        last_import_idx = insert_idx - 1
        
        for i in range(insert_idx, len(lines)):
            line = lines[i].strip()
            
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                if not in_docstring:
                    insert_idx = max(insert_idx, i + 1)
            elif in_docstring:
                continue
            elif line.startswith(('import ', 'from ')) and ' import ' in line:
                last_import_idx = i
            elif line and not line.startswith('#'):
                break
        
        return last_import_idx + 1

    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def process_files(self, file_paths: List[Path]):
        """Process multiple files"""
        print(f"🎯 Processing {len(file_paths} files with F821 violations...")
        
        for file_path in file_paths:
            try:
                # Get current violations for this file
                violations = self.get_violations_for_file(file_path)
                if not violations:
                    continue
                
                # Analyze file content
                analysis = self.analyze_file_content(file_path)
                
                # Apply fixes
                if self.apply_fixes(file_path, analysis):
                    self.files_modified += 1
                    self.fixes_applied += len(analysis.get('needed_fixes', []))
                    print(f"  ✅ {file_path}")
                    
            except Exception as e:
                self.errors.append(f"Error processing {file_path}: {e}")

    def get_files_with_violations(self) -> List[Path]:
        """Get all Python files with F821 violations"""
        try:
            result = subprocess.run([
                '.venv/bin/ruff', 'check', 
                'branding/', 'candidate/', 'tools/', 'products/',
                'matriz/', 'next_gen/', 'lukhas/',
                '--select=F821', '--output-format=concise'
            ], capture_output=True, text=True)
            
            files = set()
            for line in result.stdout.split('\n'):
                if 'F821' in line and ':' in line:
                    file_path = line.split(':')[0]
                    if file_path.endswith('.py'):
                        files.add(Path(file_path))
            
            return sorted(files)
            
        except Exception as e:
            self.errors.append(f"Error getting files with violations: {e}")
            return []

    def run_final_cleanup(self):
        """Run final F821 cleanup"""
        print("🧹 LUKHAS Final F821 Cleanup - Phase 3")
        print("=" * 60)
        
        # Get baseline count
        print("📊 Getting current F821 count...")
        try:
            result = subprocess.run([
                '.venv/bin/ruff', 'check', '.', '--select=F821', '--statistics'
            ], capture_output=True, text=True)
            
            baseline_count = 1638  # From previous output
            for line in result.stdout.split('\n'):
                if 'F821' in line and 'undefined-name' in line:
                    baseline_count = int(line.split()[0])
                    break
            
            print(f"📈 Current F821 violations: {baseline_count}")
        except:
            baseline_count = 1638
        
        # Get files with violations
        files_with_violations = self.get_files_with_violations()
        print(f"📁 Files with violations: {len(files_with_violations}")
        
        # Process files
        self.process_files(files_with_violations)
        
        print(f"\n✅ FINAL CLEANUP COMPLETE!")
        print(f"📁 Files modified: {self.files_modified}")
        print(f"🔧 Fixes applied: {self.fixes_applied}")
        
        if self.errors:
            print(f"\n⚠️ Errors: {len(self.errors}")
            for error in self.errors[:5]:
                print(f"   {error}")
        
        # Get final count
        print("\n📊 Getting final F821 count...")
        try:
            result = subprocess.run([
                '.venv/bin/ruff', 'check', '.', '--select=F821', '--statistics'
            ], capture_output=True, text=True)
            
            final_count = 0
            for line in result.stdout.split('\n'):
                if 'F821' in line and 'undefined-name' in line:
                    final_count = int(line.split()[0])
                    break
            
            reduction = baseline_count - final_count
            total_reduction = 5364 - final_count  # From original 5364
            
            print(f"📊 Final F821 violations: {final_count}")
            print(f"📉 Phase 3 reduction: {reduction}")
            print(f"🎯 TOTAL REDUCTION: {total_reduction} ({((total_reduction/5364)*100}:.1f}%)")
            
            if total_reduction >= 3500:
                print("🏆 MASSIVE SUCCESS! Exceeded all targets!")
            elif total_reduction >= 2000:
                print("🎯 EXCELLENT! Major elimination achieved!")
                
        except:
            print("⚠️ Could not get final count")


def main():
    cleanup = FinalF821Cleanup()
    cleanup.run_final_cleanup()


if __name__ == "__main__":
    main()