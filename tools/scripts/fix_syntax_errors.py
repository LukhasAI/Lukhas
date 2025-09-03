#!/usr/bin/env python3
"""Fix syntax errors in Python files - specifically EOL string literals"""

import ast
import os
from pathlib import Path

# List of files with known EOL string literal issues
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
    "tools/scripts/consolidate_modules.py",
]

base_dir = Path(os.getenv("LUKHAS_ROOT", "/Users/agi_dev/LOCAL-REPOS/Lukhas"))


def find_syntax_error_line(file_path):
    """Find the line with syntax error"""
    try:
        with open(file_path) as f:
            content = f.read()
            ast.parse(content)
        return None
    except SyntaxError as e:
        return e.lineno, e.msg


def fix_eol_string_literal(file_path):
    """Fix EOL string literal errors in a file"""
    error_info = find_syntax_error_line(file_path)
    if not error_info:
        return False

    line_no, msg = error_info
    if (
        "EOL while scanning string literal" not in msg
        and "unterminated string literal" not in msg
    ):
        # ΛTAG: error_message_normalization
        return False

    with open(file_path) as f:
        lines = f.readlines()

    if line_no <= len(lines):
        # Fix the line with the unclosed string
        problem_line = lines[line_no - 1]

        # Check if it's a multiline string that needs closing
        if (
            ('"content":' in problem_line or "'content':" in problem_line)
            and '": "' in problem_line
            and not problem_line.rstrip().endswith('",')
        ):
            # ΛTAG: condition_simplify
            lines[line_no - 1] = problem_line.rstrip() + '"\n'
            if line_no < len(lines):
                next_line = lines[line_no]
                # If next line is a continuation, merge it
                if not next_line.strip().startswith(
                    '"'
                ) and not next_line.strip().startswith("}"):
                    lines[line_no - 1] = (
                        problem_line.rstrip() + " " + next_line.strip() + '",\n'
                    )
                    lines[line_no] = ""

        # Write fixed content back
        with open(file_path, "w") as f:
            f.writelines(lines)

        return True

    return False


def main():
    fixed_count = 0
    error_count = 0

    for file_path in files_to_fix:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"Checking {file_path}...")
            if fix_eol_string_literal(full_path):
                print(f"  ✓ Fixed EOL string literal in {file_path}")
                fixed_count += 1
            else:
                error_info = find_syntax_error_line(full_path)
                if error_info:
                    print(
                        f"  ✗ Error in {file_path} at line {error_info[0]}: {error_info[1]}"
                    )
                    error_count += 1

    print(
        f"\nSummary: Fixed {fixed_count} files, {error_count} files still have errors"
    )


if __name__ == "__main__":
    main()
