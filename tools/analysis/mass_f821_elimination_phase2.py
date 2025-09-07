#!/usr/bin/env python3
"""
LUKHAS F821 Mass Elimination Script - Phase 2
Elite surgical F821 undefined-name violation elimination

Target: Reduce 5,407 F821 violations by 1,500-2,000 using pattern-based fixes
Focus: timezone, st, log, VisualSymbol, and other high-frequency patterns
"""

import os
import re
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast


class F821MassEliminatorPhase2:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.fixes_applied = 0
        self.files_modified = 0
        self.errors = []
        
        # High-frequency violation patterns and their fixes
        self.violation_patterns = {
            'timezone': {
                'import_fix': 'from datetime import timezone',
                'expected_count': 3213,
                'priority': 1
            },
            'st': {
                'import_fix': 'import streamlit as st',
                'expected_count': 427,
                'priority': 2
            },
            'log': {
                'import_fix': 'import logging\nlog = logging.getLogger(__name__)',
                'expected_count': 368,
                'priority': 3
            },
            'VisualSymbol': {
                'import_fix': 'from core.symbolic import VisualSymbol',
                'expected_count': 236,
                'priority': 4
            },
            'VoiceSymbol': {
                'import_fix': 'from core.symbolic import VoiceSymbol',
                'expected_count': 66,
                'priority': 5
            },
            'random': {
                'import_fix': 'import random',
                'expected_count': 50,
                'priority': 6
            },
            'QuantumCreativeComponent': {
                'import_fix': 'from quantum.creative import QuantumCreativeComponent',
                'expected_count': 44,
                'priority': 7
            },
            'qi': {
                'import_fix': 'from consciousness.qi import qi',
                'expected_count': 41,
                'priority': 8
            },
            'lukhas_pb2': {
                'import_fix': 'import lukhas_pb2',
                'expected_count': 35,
                'priority': 9
            },
            'logging': {
                'import_fix': 'import logging',
                'expected_count': 34,
                'priority': 10
            },
            'time': {
                'import_fix': 'import time',
                'expected_count': 22,
                'priority': 11
            },
            'Dict': {
                'import_fix': 'from typing import Dict',
                'expected_count': 8,
                'priority': 12
            },
            'List': {
                'import_fix': 'from typing import List',
                'expected_count': 5,
                'priority': 13
            },
            'Optional': {
                'import_fix': 'from typing import Optional',
                'expected_count': 5,
                'priority': 14
            }
        }
        
        # Class name correction patterns (Lambda symbol issues)
        self.class_name_fixes = {
            'ΛBotClickActions': 'LambdaBotClickActions',
            'ΛBotCustomizer': 'LambdaBotCustomizer', 
            'ΛBotStatusDesigner': 'LambdaBotStatusDesigner',
            'CoreΛBot': 'CoreLambdaBot'
        }

    def get_current_violations(self) -> List[Dict]:
        """Get current F821 violations using ruff"""
        try:
            cmd = [
                '.venv/bin/ruff', 'check', 
                'branding/', 'candidate/', 'tools/', 'products/', 
                'matriz/', 'next_gen/', 'lukhas/',
                '--select=F821', '--output-format=json', '--quiet'
            ]
            result = subprocess.run(cmd, cwd=self.project_root, 
                                    capture_output=True, text=True)
            
            if result.returncode in [0, 1]:  # 1 means violations found
                violations = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            violations.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                return violations
            return []
        except Exception as e:
            self.errors.append(f"Error getting violations: {e}")
            return []

    def analyze_file_content(self, file_path: Path) -> Tuple[str, Set[str], List[str]]:
        """Analyze file content and extract imports and violations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract existing imports
            existing_imports = set()
            import_lines = []
            
            for line in content.split('\n'):
                stripped = line.strip()
                if (stripped.startswith('import ') or 
                    stripped.startswith('from ') and ' import ' in stripped):
                    existing_imports.add(stripped)
                    import_lines.append(line)
            
            return content, existing_imports, import_lines
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return "", set(), []

    def add_import_safely(self, content: str, import_statement: str, file_path: Path) -> str:
        """Add import statement safely, avoiding duplicates"""
        lines = content.split('\n')
        
        # Check if import already exists (handle variations)
        existing_imports = [line.strip() for line in lines 
                           if line.strip().startswith(('import ', 'from '))]
        
        # Parse the import we want to add
        import_parts = import_statement.strip().split('\n')
        
        for import_part in import_parts:
            import_part = import_part.strip()
            if not import_part:
                continue
                
            # Check for duplicate imports
            should_add = True
            for existing in existing_imports:
                if self.imports_equivalent(existing, import_part):
                    should_add = False
                    break
            
            if should_add:
                # Find the right place to insert the import
                insert_idx = self.find_import_insertion_point(lines)
                lines.insert(insert_idx, import_part)
        
        return '\n'.join(lines)

    def imports_equivalent(self, existing: str, new: str) -> bool:
        """Check if two import statements are equivalent"""
        # Normalize imports for comparison
        existing = existing.strip()
        new = new.strip()
        
        if existing == new:
            return True
            
        # Handle common variations
        patterns = [
            (r'from datetime import timezone', r'from datetime import.*timezone'),
            (r'import streamlit as st', r'import streamlit'),
            (r'import logging', r'import logging'),
            (r'from typing import Dict', r'from typing import.*Dict'),
        ]
        
        for pattern, check in patterns:
            if re.match(pattern, new) and re.search(check, existing):
                return True
                
        return False

    def find_import_insertion_point(self, lines: List[str]) -> int:
        """Find the appropriate place to insert an import"""
        # Look for existing imports
        last_import_idx = -1
        in_docstring = False
        docstring_end = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track docstrings
            if '"""' in stripped or "'''" in stripped:
                if not in_docstring:
                    in_docstring = True
                else:
                    in_docstring = False
                    docstring_end = i
            
            # Track imports
            if (stripped.startswith('import ') or 
                (stripped.startswith('from ') and ' import ' in stripped)):
                last_import_idx = i
            elif stripped and not stripped.startswith('#') and not in_docstring:
                # Found first non-comment, non-import line
                break
        
        # Insert after last import, or after docstring, or at beginning
        if last_import_idx >= 0:
            return last_import_idx + 1
        elif docstring_end >= 0:
            return docstring_end + 1
        else:
            # Insert after shebang and encoding if they exist
            insert_idx = 0
            for i, line in enumerate(lines[:5]):  # Check first 5 lines
                if line.strip().startswith('#') and ('coding' in line or 'encoding' in line or line.startswith('#!')):
                    insert_idx = i + 1
            return insert_idx

    def fix_class_names(self, content: str) -> str:
        """Fix Lambda symbol class name issues"""
        for wrong_name, correct_name in self.class_name_fixes.items():
            if wrong_name in content:
                # Replace in class definitions and usage
                content = re.sub(rf\'\b{re.escape(wrong_name)}\b\', correct_name, content)
        return content

    def fix_function_signatures(self, content: str) -> str:
        """Fix corrupted function signatures like def __init__(self):"""
        # Fix timezone parameter corruption
        content = re.sub(
            r'def __init__\(self,\s*timezone\s*\):',
            'def __init__(self):',
            content
        )
        
        # Fix other common parameter corruptions
        content = re.sub(
            r'def __init__\(self,\s*(Dict|List|Optional|log|st)\s*\):',
            'def __init__(self):',
            content
        )
        
        return content

    def process_file(self, file_path: Path, violations: List[str]) -> bool:
        """Process a single file to fix F821 violations"""
        try:
            content, existing_imports, import_lines = self.analyze_file_content(file_path)
            
            if not content:
                return False
            
            original_content = content
            modified = False
            
            # Add missing imports based on violations found in this file
            for violation in violations:
                if violation in self.violation_patterns:
                    import_fix = self.violation_patterns[violation]['import_fix']
                    content = self.add_import_safely(content, import_fix, file_path)
                    modified = True
            
            # Fix class name issues
            fixed_content = self.fix_class_names(content)
            if fixed_content != content:
                content = fixed_content
                modified = True
            
            # Fix function signature corruptions
            fixed_content = self.fix_function_signatures(content)
            if fixed_content != content:
                content = fixed_content
                modified = True
            
            # Write back if modified
            if modified and content != original_content:
                # Validate syntax before writing
                if self.validate_python_syntax(content):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.files_modified += 1
                    return True
                else:
                    self.errors.append(f"Syntax validation failed for {file_path}")
            
            return False
            
        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {e}")
            return False

    def validate_python_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def run_targeted_elimination(self):
        """Run targeted elimination of F821 violations"""
        print("🎯 LUKHAS F821 Mass Elimination - Phase 2")
        print("=" * 60)
        
        # Get current violations
        print("📊 Analyzing current F821 violations...")
        violations = self.get_current_violations()
        
        if not violations:
            print("❌ Could not retrieve violations")
            return
        
        print(f"📈 Found {len(violations)} F821 violations")
        
        # Group violations by file
        violations_by_file = {}
        violation_counts = {}
        
        for violation in violations:
            file_path = Path(violation['filename'])
            message = violation.get('message', '')
            
            # Extract violation type from message
            match = re.search(r"Undefined name `([^`]+)`", message)
            if match:
                violation_type = match.group(1)
                violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
                
                if file_path not in violations_by_file:
                    violations_by_file[file_path] = []
                violations_by_file[file_path].append(violation_type)
        
        # Print violation summary
        print("\n🔍 Top violation patterns:")
        for violation_type, count in sorted(violation_counts.items(), 
                                           key=lambda x: x[1], reverse=True)[:15]:
            expected = self.violation_patterns.get(violation_type, {}).get('expected_count', '?')
            print(f"   {violation_type}: {count} (expected: {expected})")
        
        # Process files with high-priority violations
        processed_files = 0
        target_violations = set(self.violation_patterns.keys())
        
        print(f"\n🚀 Processing {len(violations_by_file)} files...")
        
        for file_path, file_violations in violations_by_file.items():
            # Only process if file has target violations
            relevant_violations = [v for v in file_violations if v in target_violations]
            
            if relevant_violations:
                if self.process_file(file_path, relevant_violations):
                    processed_files += 1
                    self.fixes_applied += len(relevant_violations)
        
        print(f"\n✅ Processing complete!")
        print(f"📁 Files modified: {self.files_modified}")
        print(f"🔧 Fixes applied: {self.fixes_applied}")
        
        if self.errors:
            print(f"\n⚠️ Errors encountered: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   {error}")

    def verify_elimination(self):
        """Verify the elimination results"""
        print("\n🔍 Verifying elimination results...")
        
        # Get new violation count
        violations = self.get_current_violations()
        new_count = len(violations)
        
        print(f"📊 New violation count: {new_count}")
        print(f"📈 Estimated reduction: {5407 - new_count}")
        
        return new_count


def main():
    eliminator = F821MassEliminatorPhase2()
    
    try:
        eliminator.run_targeted_elimination()
        new_count = eliminator.verify_elimination()
        
        print(f"\n🎯 PHASE 2 ELIMINATION COMPLETE")
        print(f"📈 Target: Reduce 1,500-2,000 violations")
        print(f"✅ Files modified: {eliminator.files_modified}")
        print(f"🔧 Fixes applied: {eliminator.fixes_applied}")
        print(f"📊 New violation count: {new_count}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Elimination interrupted by user")
    except Exception as e:
        print(f"\n❌ Elimination failed: {e}")


if __name__ == "__main__":
    main()