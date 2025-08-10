#!/usr/bin/env python3
"""Count remaining syntax errors in Python files"""

import ast
from pathlib import Path

def count_syntax_errors():
    base_dir = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")
    total_errors = 0
    error_details = []
    
    for py_file in base_dir.rglob("*.py"):
        # Skip archive and backup directories
        if any(part in str(py_file).lower() for part in ['archive', 'backup', 'pwm_cleanup', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                ast.parse(f.read())
        except SyntaxError as e:
            total_errors += 1
            if total_errors <= 30:
                error_details.append(f"{py_file.relative_to(base_dir)}:{e.lineno}: {e.msg}")
    
    return total_errors, error_details

if __name__ == "__main__":
    errors, details = count_syntax_errors()
    print(f"Total Python files with syntax errors: {errors}")
    if details:
        print("\nErrors found:")
        for d in details:
            print(f"  {d}")