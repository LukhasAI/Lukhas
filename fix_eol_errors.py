#!/usr/bin/env python3
"""Fix EOL string literal errors in Python files"""

import ast
import re
from pathlib import Path

def fix_eol_in_file(file_path):
    """Fix EOL string literal errors in a specific file"""
    try:
        # First check if file has syntax error
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines(keepends=True)
        
        # Try to parse and find error
        try:
            ast.parse(content)
            return False  # No error
        except SyntaxError as e:
            if "EOL while scanning string literal" not in str(e):
                return False  # Different error
            
            line_no = e.lineno
            if line_no > len(lines):
                return False
            
            # Fix the problematic line
            problem_line = lines[line_no - 1]
            
            # Common patterns for EOL string errors:
            # 1. Unclosed string with extra comma and quote: "text",",
            # 2. String spanning multiple lines without proper escaping
            # 3. Missing closing quote
            
            # Pattern 1: Fix ",", at end of string
            if '",",\n' in problem_line or "',',\n" in problem_line:
                lines[line_no - 1] = problem_line.replace('",",', '",').replace("',',", "',")
            # Pattern 2: String not closed, check for multiline intention
            elif problem_line.count('"') % 2 != 0:
                # Look for unclosed quotes
                if '": "' in problem_line and not problem_line.rstrip().endswith('",'):
                    # Add closing quote
                    lines[line_no - 1] = problem_line.rstrip() + '",\n'
            elif problem_line.count("'") % 2 != 0:
                if "': '" in problem_line and not problem_line.rstrip().endswith("',"):
                    lines[line_no - 1] = problem_line.rstrip() + "',\n"
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Verify fix
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                return True  # Fixed!
            except:
                return False  # Still broken
                
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all EOL errors in tools directory"""
    files_to_fix = [
        "tools/AiDocumentationGenerator.py",
        "tools/CoreAnalyzer.py",
        "tools/generate_lukhas_ecosystem_documentation.py",
        "tools/command_registry.py",
        "tools/journal/solo_dev_support.py",
        "tools/journal/learning_assistant.py",
        "tools/analysis/2030_full_consolidator.py",
        "tools/analysis/import_success_summary.py",
        "tools/analysis/generate_function_index.py",
        "tools/analysis/operational_summary.py",
        "tools/analysis/security_gap_analysis.py",
        "tools/analysis/validate_lukhas_concepts.py",
        "tools/analysis/duplicate_analysis.py",
        "tools/scripts/generate_final_research_report.py",
        "tools/scripts/comprehensive_system_report.py",
        "tools/scripts/system_status_comprehensive_report.py",
        "tools/scripts/research_report_generator.py",
        "tools/scripts/system_diagnostic.py",
        "tools/scripts/consolidate_modules.py"
    ]
    
    base_dir = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")
    fixed = 0
    failed = 0
    
    for file_path in files_to_fix:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"Fixing {file_path}...")
            if fix_eol_in_file(full_path):
                print(f"  ✓ Fixed")
                fixed += 1
            else:
                # Try to get specific error
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        ast.parse(f.read())
                    print(f"  ✓ No error found")
                except SyntaxError as e:
                    print(f"  ✗ Still has error at line {e.lineno}: {e.msg}")
                    failed += 1
    
    print(f"\nFixed {fixed} files, {failed} still have errors")

if __name__ == "__main__":
    main()