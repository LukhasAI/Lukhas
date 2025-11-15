#!/usr/bin/env python3
"""Fix misplaced 'from typing import Optional' statements."""

import re
import sys
from pathlib import Path


def fix_misplaced_imports(file_path: Path) -> bool:
    """Fix Optional imports that were placed inside classes/functions."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Pattern 1: Import after class docstring
        # class Foo:
        #     """Docstring."""
        # from typing import Optional
        pattern1 = r'(class\s+\w+.*?:\s*\n\s+""".*?"""\s*\n)(from typing import Optional\s*\n)'
        content = re.sub(pattern1, r'\2\1', content, flags=re.DOTALL)
        
        # Pattern 2: Import inside class body (indented)
        # class Foo:
        #     """Docstring."""
        # from typing import Optional
        #
        #     def __init__...
        pattern2 = r'(class\s+\w+[^:]*:\s*\n(?:\s+"""[^"]*"""\s*\n)?)(from typing import Optional\s*\n)(\s*\n\s+def )'
        
        def fix_indent(match):
            class_def = match.group(1)
            import_stmt = 'from typing import Optional\n\n'
            method_def = match.group(3)
            return import_stmt + class_def + method_def
        
        content = re.sub(pattern2, fix_indent, content, flags=re.DOTALL)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}", file=sys.stderr)
        return False


def main():
    # Files with known issues
    problem_files = [
        'bridge/api/__init__.py',
        'bridge/external_adapters/__init__.py',
        'memory/embedding_index.py',
        'memory/lifecycle.py',
        'security_reports/aggregator.py',
        'serve/webauthn_routes.py',
        'lukhas_website/lukhas/memory/embedding_index.py',
    ]
    
    fixed = 0
    for file_str in problem_files:
        file_path = Path(file_str)
        if file_path.exists():
            if fix_misplaced_imports(file_path):
                fixed += 1
    
    print(f"\nFixed {fixed} files")


if __name__ == '__main__':
    main()
