#!/usr/bin/env python3
"""
Fix real linting issues - not just formatting.
Focuses on undefined names, imports, and actual errors.
"""

import subprocess
from pathlib import Path
from collections import defaultdict


def get_flake8_issues(directory: str) -> dict:
    """Get all flake8 issues for a directory"""
    cmd = ["flake8", directory, "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    issues = defaultdict(list)
    for line in result.stdout.splitlines():
        if ':' in line:
            try:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    filepath = parts[0]
                    line_num = int(parts[1])
                    col = int(parts[2])
                    error = parts[3].strip()
                    
                    # Parse error code and message
                    error_parts = error.split(' ', 1)
                    if len(error_parts) >= 2:
                        code = error_parts[0]
                        msg = error_parts[1]
                        
                        issues[filepath].append({
                            'line': line_num,
                            'col': col,
                            'code': code,
                            'msg': msg
                        })
            except (ValueError, IndexError):
                continue
    
    return issues


def fix_undefined_names(filepath: Path, issues: list) -> bool:
    """Fix undefined name errors (F821) by adding imports"""
    
    # Common imports for undefined names
    import_map = {
        'logging': 'import logging',
        'time': 'import time',
        'uuid': 'import uuid',
        'json': 'import json',
        'asyncio': 'import asyncio',
        'np': 'import numpy as np',
        'pd': 'import pandas as pd',
        'datetime': 'from datetime import datetime',
        'timezone': 'from datetime import timezone',
        'Dict': 'from typing import Dict',
        'List': 'from typing import List',
        'Optional': 'from typing import Optional',
        'Any': 'from typing import Any',
        'Union': 'from typing import Union',
        'Tuple': 'from typing import Tuple',
        'Set': 'from typing import Set',
        'Type': 'from typing import Type',
        'Callable': 'from typing import Callable',
        'TypeVar': 'from typing import TypeVar',
        'cast': 'from typing import cast',
        'dataclass': 'from dataclasses import dataclass',
        'field': 'from dataclasses import field',
        'asdict': 'from dataclasses import asdict',
        'Path': 'from pathlib import Path',
        'defaultdict': 'from collections import defaultdict',
        'deque': 'from collections import deque',
        'Counter': 'from collections import Counter',
        'ABC': 'from abc import ABC',
        'abstractmethod': 'from abc import abstractmethod',
    }
    
    undefined_names = set()
    for issue in issues:
        if issue['code'] == 'F821':
            # Extract undefined name from message
            msg = issue['msg']
            if 'undefined name' in msg:
                name = msg.split("'")[1] if "'" in msg else None
                if name:
                    undefined_names.add(name)
    
    if not undefined_names:
        return False
    
    try:
        content = filepath.read_text()
        lines = content.splitlines()
        
        # Find where to insert imports (after module docstring)
        insert_idx = 0
        if lines and lines[0].startswith('"""'):
            for i, line in enumerate(lines):
                if i > 0 and '"""' in line:
                    insert_idx = i + 1
                    break
        
        # Add imports for undefined names
        imports_added = []
        for name in undefined_names:
            if name in import_map:
                import_stmt = import_map[name]
                # Check if import already exists
                if import_stmt not in content:
                    imports_added.append(import_stmt)
        
        if imports_added:
            # Insert imports
            for import_stmt in sorted(imports_added):
                lines.insert(insert_idx, import_stmt)
                insert_idx += 1
            
            # Add blank line after imports
            if insert_idx < len(lines) and lines[insert_idx].strip():
                lines.insert(insert_idx, '')
            
            # Write back
            filepath.write_text('\n'.join(lines))
            return True
    
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
    
    return False


def fix_syntax_errors(filepath: Path, issues: list) -> bool:
    """Fix common syntax errors"""
    
    syntax_issues = [i for i in issues if i['code'] in ['E999', 'E901', 'E902']]
    if not syntax_issues:
        return False
    
    try:
        content = filepath.read_text()
        original = content
        
        # Fix unclosed strings
        for issue in syntax_issues:
            if 'EOL while scanning string' in issue['msg']:
                lines = content.splitlines()
                if issue['line'] <= len(lines):
                    line_idx = issue['line'] - 1
                    line = lines[line_idx]
                    
                    # Count quotes
                    single_quotes = line.count("'") - line.count("\\'")
                    double_quotes = line.count('"') - line.count('\\"')
                    
                    # Add closing quote if needed
                    if single_quotes % 2 == 1:
                        lines[line_idx] = line + "'"
                    elif double_quotes % 2 == 1:
                        lines[line_idx] = line + '"'
                    
                    content = '\n'.join(lines)
        
        if content != original:
            filepath.write_text(content)
            return True
    
    except Exception as e:
        print(f"Error fixing syntax in {filepath}: {e}")
    
    return False


def main():
    """Main function"""
    
    # Directories to fix
    dirs_to_fix = ['core', 'bridge', 'lukhas_pwm', 'serve', 'orchestration', 
                   'governance', 'consciousness', 'memory']
    
    print("🔧 Fixing real linting issues (not just formatting)...")
    
    total_fixed = 0
    
    for directory in dirs_to_fix:
        if not Path(directory).exists():
            continue
        
        print(f"\n📁 Processing {directory}...")
        
        # Get all issues
        issues = get_flake8_issues(directory)
        
        # Fix each file
        for filepath_str, file_issues in issues.items():
            filepath = Path(filepath_str)
            if not filepath.exists():
                continue
            
            # Group issues by type
            undefined_issues = [i for i in file_issues if i['code'] == 'F821']
            syntax_issues = [i for i in file_issues if i['code'] in ['E999', 'E901', 'E902']]
            
            fixed = False
            
            # Fix undefined names
            if undefined_issues:
                if fix_undefined_names(filepath, undefined_issues):
                    fixed = True
                    print(f"  ✓ Fixed undefined names in {filepath.name}")
            
            # Fix syntax errors
            if syntax_issues:
                if fix_syntax_errors(filepath, syntax_issues):
                    fixed = True
                    print(f"  ✓ Fixed syntax errors in {filepath.name}")
            
            if fixed:
                total_fixed += 1
    
    print(f"\n✅ Fixed {total_fixed} files")
    
    # Check final count
    result = subprocess.run(["flake8", ".", "--count"], capture_output=True, text=True)
    count = result.stdout.strip()
    if count.isdigit():
        print(f"📊 Remaining issues: {count}")


if __name__ == "__main__":
    main()