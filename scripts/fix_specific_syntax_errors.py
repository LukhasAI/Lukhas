#!/usr/bin/env python3
"""
🔧 LUKHAS Specific Syntax Error Fixer
Targets specific common syntax errors found in the codebase.
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_malformed_function_definitions(content: str) -> Tuple[str, List[str]]:
    """Fix function definitions with syntax errors like 'def function(:'."""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        # Pattern: def function_name(:
        match = re.match(r'^(\s*)def\s+(\w+)\(:$', line)
        if match:
            indent, func_name = match.groups()
            fixed_line = f"{indent}def {func_name}(self):"
            fixed_lines.append(fixed_line)
            fixes.append(f"Line {i}: Fixed malformed function definition")
            continue
            
        # Pattern: def _function(:
        match = re.match(r'^(\s*)def\s+(_\w+)\(:$', line)
        if match:
            indent, func_name = match.groups()
            fixed_line = f"{indent}def {func_name}(self):"
            fixed_lines.append(fixed_line)
            fixes.append(f"Line {i}: Fixed malformed method definition")
            continue
            
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_unclosed_f_strings(content: str) -> Tuple[str, List[str]]:
    """Fix unclosed f-strings in multiline statements."""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    in_f_string = False
    brace_count = 0
    f_string_start_line = 0
    
    for i, line in enumerate(lines, 1):
        # Check if we're starting an f-string
        if ('f"' in line or "f'" in line) and not in_f_string:
            in_f_string = True
            f_string_start_line = i
            brace_count = line.count('{') - line.count('}')
            
            # Check if it's a complete f-string on one line
            if brace_count == 0:
                in_f_string = False
            
            fixed_lines.append(line)
        elif in_f_string:
            # We're in a multiline f-string
            brace_count += line.count('{') - line.count('}')
            
            # Check if the string ends on this line
            if ('"' in line or "'" in line) and brace_count > 0:
                # Add closing braces before the quote
                quote_pos = max(line.rfind('"'), line.rfind("'"))
                if quote_pos > 0:
                    fixed_line = line[:quote_pos] + '}' * brace_count + line[quote_pos:]
                    fixed_lines.append(fixed_line)
                    fixes.append(f"Lines {f_string_start_line}-{i}: Fixed unclosed f-string braces")
                    in_f_string = False
                    brace_count = 0
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
                
            # Reset if we've balanced the braces
            if brace_count <= 0:
                in_f_string = False
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_conditional_expressions(content: str) -> Tuple[str, List[str]]:
    """Fix conditional expressions with incorrect colons."""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        # Pattern: if condition: else value:
        # Should be: if condition else value
        if re.search(r'\sif\s+.+:\s+else\s+.+:', line):
            # This is likely an incorrect ternary operator
            fixed_line = re.sub(r'(\sif\s+[^:]+):\s+else\s+([^:]+):', r'\1 else \2', line)
            fixed_lines.append(fixed_line)
            fixes.append(f"Line {i}: Fixed conditional expression syntax")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_multiline_conditionals(content: str) -> Tuple[str, List[str]]:
    """Fix multiline conditional statements with syntax errors."""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for conditional statements
        if re.match(r'^\s*(if|elif|for|while)\s+', line):
            # Check if it's missing a colon
            if not line.rstrip().endswith(':'):
                # Look ahead to see if this is a multiline condition
                if i + 1 < len(lines) and lines[i + 1].strip().startswith(('and ', 'or ')):
                    # Collect the full condition
                    condition_lines = [line]
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith(('and ', 'or ')):
                        condition_lines.append(lines[j])
                        j += 1
                    
                    # Join and add colon
                    full_condition = ' '.join(l.strip() for l in condition_lines)
                    if not full_condition.endswith(':'):
                        full_condition += ':'
                    
                    fixed_lines.append(full_condition)
                    fixes.append(f"Lines {i+1}-{j}: Fixed multiline conditional")
                    i = j
                    continue
                else:
                    # Single line missing colon
                    fixed_lines.append(line + ':')
                    fixes.append(f"Line {i+1}: Added missing colon to conditional")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines), fixes

def process_file(file_path: Path) -> bool:
    """Process a single file and fix syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        all_fixes = []
        
        # Apply fixes in order
        content, fixes = fix_malformed_function_definitions(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_unclosed_f_strings(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_conditional_expressions(content)
        all_fixes.extend(fixes)
        
        content, fixes = fix_multiline_conditionals(content)
        all_fixes.extend(fixes)
        
        if all_fixes:
            print(f"\n📝 {file_path.name}")
            for fix in all_fixes[:5]:
                print(f"   {fix}")
            if len(all_fixes) > 5:
                print(f"   ... and {len(all_fixes) - 5} more fixes")
            
            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main entry point."""
    # Files with known issues from the previous run
    problem_files = [
        'tools/journal/learning_assistant.py',
        'tools/analysis/2030_full_consolidator.py',
        'tools/analysis/import_success_summary.py',
        'tools/analysis/generate_function_index.py',
        'tools/analysis/operational_summary.py',
        'tools/analysis/security_gap_analysis.py',
        'tools/analysis/validate_lukhas_concepts.py',
        'tools/analysis/duplicate_analysis.py',
        'tools/scripts/generate_final_research_report.py',
        'tools/scripts/comprehensive_system_report.py',
        'tools/scripts/system_status_comprehensive_report.py',
        'tools/scripts/research_report_generator.py',
        'tools/scripts/system_diagnostic.py',
        'tools/scripts/consolidate_modules.py',
        'core/fallback_services.py',
    ]
    
    print("🔧 LUKHAS Specific Syntax Error Fixer")
    print("=" * 50)
    print(f"Processing {len(problem_files)} files with known issues...")
    
    fixed_count = 0
    for file_str in problem_files:
        file_path = Path(file_str)
        if file_path.exists():
            if process_file(file_path):
                fixed_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Fixed {fixed_count}/{len(problem_files)} files")
    
    return fixed_count == len(problem_files)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)