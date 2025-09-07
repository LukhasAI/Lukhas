#!/usr/bin/env python3
"""
Quick F821 fix for branding/engines/lukhas_content_platform/bots/ directory
Targeted surgical fixes for the 49 violations in bots directory
"""
import streamlit as st

import os
import re
from pathlib import Path


def fix_bots_directory():
    """Fix F821 violations in bots directory"""
    bots_dir = Path("branding/engines/lukhas_content_platform/bots/")
    
    if not bots_dir.exists():
        print(f"❌ Directory not found: {bots_dir}")
        return
    
    fixes_applied = 0
    files_modified = 0
    
    print(f"🎯 Processing bots directory: {bots_dir}")
    
    # Process each Python file
    for py_file in bots_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Add missing timezone import
            if 'timezone' in content and 'from datetime import timezone' not in content:
                # Find import section
                lines = content.split('\n')
                import_added = False
                
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')) and not import_added:
                        # Insert after last import or datetime import
                        if 'datetime import' in line:
                            lines.insert(i + 1, 'from datetime import timezone')
                            import_added = True
                            fixes_applied += 1
                            break
                        elif line.strip().startswith('from datetime import'):
                            # Add timezone to existing datetime import
                            if 'timezone' not in line:
                                lines[i] = line.rstrip() + ', timezone'
                                import_added = True
                                fixes_applied += 1
                                break
                
                # If no datetime import found, add it
                if not import_added:
                    insert_idx = 0
                    for i, line in enumerate(lines[:10]):
                        if line.strip().startswith('#'):
                            insert_idx = i + 1
                        else:
                            break
                    lines.insert(insert_idx, 'from datetime import timezone')
                    fixes_applied += 1
                
                content = '\n'.join(lines)
            
            # Fix 2: Add missing Dict import
            if 'Dict' in content and 'from typing import' not in content:
                lines = content.split('\n')
                lines.insert(0, 'from typing import Dict')
                content = '\n'.join(lines)
                fixes_applied += 1
            elif 'Dict' in content and 'Dict' not in [line for line in content.split('\n') if 'from typing import' in line][0] if [line for line in content.split('\n') if 'from typing import' in line] else False:
                # Add Dict to existing typing import
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'from typing import' in line and 'Dict' not in line:
                        lines[i] = line.rstrip() + ', Dict'
                        fixes_applied += 1
                        break
                content = '\n'.join(lines)
            
            # Fix 3: Class name corrections
            class_fixes = {
                'ΛBotClickActions': 'LambdaBotClickActions',
                'ΛBotCustomizer': 'LambdaBotCustomizer',
                'ΛBotStatusDesigner': 'LambdaBotStatusDesigner',
                'CoreΛBot': 'CoreLambdaBot'
            }
            
            for wrong_name, correct_name in class_fixes.items():
                if wrong_name in content:
                    content = re.sub(rf'\b{re.escape(wrong_name}\b', correct_name, content)
                    fixes_applied += 1
            
            # Fix 4: Add missing Quantum imports
            if 'QuantumModuleState' in content and 'QuantumModuleState' not in [line for line in content.split('\n') if 'import' in line]:
                lines = content.split('\n')
                lines.insert(0, 'from quantum.states import QuantumModuleState')
                content = '\n'.join(lines)
                fixes_applied += 1
            
            if 'QuantumAnalysisSession' in content and 'QuantumAnalysisSession' not in [line for line in content.split('\n') if 'import' in line]:
                lines = content.split('\n')
                lines.insert(0, 'from quantum.analysis import QuantumAnalysisSession')
                content = '\n'.join(lines)
                fixes_applied += 1
            
            # Write back if modified
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified += 1
                print(f"✅ Fixed: {py_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
    
    print(f"\n🎯 Bots directory processing complete!")
    print(f"📁 Files modified: {files_modified}")
    print(f"🔧 Fixes applied: {fixes_applied}")


if __name__ == "__main__":
    fix_bots_directory()