#!/usr/bin/env python3
"""
Batch fix UP035 deprecated typing imports
"""
import subprocess
import re
import sys
from pathlib import Path

def fix_file_up035(filepath):
    """Fix UP035 violations in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Pattern for typing imports
        patterns = [
            (r'from typing import ([^,\n]*,\s*)*Dict([^,\n]*,\s*)*([^,\n]*)', 
             lambda m: f'from typing import {", ".join([x.strip() for x in m.group(0).replace("from typing import ", "").split(",") if x.strip() not in ["Dict", "List", "Tuple", "Set"]])}'),
            (r'from typing import ([^,\n]*,\s*)*List([^,\n]*,\s*)*([^,\n]*)', 
             lambda m: f'from typing import {", ".join([x.strip() for x in m.group(0).replace("from typing import ", "").split(",") if x.strip() not in ["Dict", "List", "Tuple", "Set"]])}'),
            (r'from typing import ([^,\n]*,\s*)*Tuple([^,\n]*,\s*)*([^,\n]*)', 
             lambda m: f'from typing import {", ".join([x.strip() for x in m.group(0).replace("from typing import ", "").split(",") if x.strip() not in ["Dict", "List", "Tuple", "Set"]])}'),
        ]
        
        # Simple replacement
        replacements = {
            'from typing import Dict, List, Optional': 'from typing import Optional',
            'from typing import Any, Dict, List, Optional': 'from typing import Any, Optional', 
            'from typing import Any, Dict, List, Optional, Tuple': 'from typing import Any, Optional',
            'from typing import Dict, List': '# UP035: Use built-in dict, list',
            'from typing import Dict': '# UP035: Use built-in dict',
            'from typing import List': '# UP035: Use built-in list',
            'from typing import Tuple': '# UP035: Use built-in tuple',
            'from typing import Dict, List, Tuple': '# UP035: Use built-in dict, list, tuple',
            'from typing import Any, Dict': 'from typing import Any',
            'from typing import Dict, Optional': 'from typing import Optional',
            'from typing import List, Optional': 'from typing import Optional',
        }
        
        modified = False
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                modified = True
                print(f"  ✓ Fixed: {old} → {new}")
        
        if modified:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  ✗ Error fixing {filepath}: {e}")
        return False

def main():
    # Get files with UP035 violations
    result = subprocess.run([
        'python3', '-m', 'ruff', 'check', '.', '--select=UP035', '--output-format=json'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Getting UP035 violations...")
    
    try:
        import json
        data = json.loads(result.stdout) if result.stdout.strip() else []
        files = {item['filename'] for item in data if item.get('rule_id') == 'UP035'}
        
        print(f"Found {len(files)} files with UP035 violations")
        
        fixed_count = 0
        for filepath in sorted(files)[:10]:  # Process first 10 files
            print(f"\nFixing: {filepath}")
            if fix_file_up035(filepath):
                fixed_count += 1
        
        print(f"\n✅ Fixed {fixed_count} files")
        return fixed_count
        
    except Exception as e:
        print(f"Error processing: {e}")
        return 0

if __name__ == "__main__":
    main()
