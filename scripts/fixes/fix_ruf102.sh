#!/bin/bash

# T4: RUF102 Import Cleanup Script
# Fix trailing commas and malformed import statements

cd /Users/agi_dev/LOCAL-REPOS/Lukhas

echo "Fixing RUF102 violations..."

# Function to clean up import formatting
fix_imports() {
    local file="$1"
    
    # Skip if file doesn't exist or isn't regular file
    [[ -f "$file" ]] || return
    
    python3 << EOF
import re

file_path = "$file"
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix trailing commas in typing imports
    content = re.sub(r'from typing import ([^,\n]*,)*\s*,\s*$', 
                     lambda m: f"from typing import {m.group(1)}".rstrip(', '), 
                     content, flags=re.MULTILINE)
    
    # Fix double commas in imports
    content = re.sub(r'from typing import ([^,\n]*),\s*,\s*([^,\n]*)', 
                     r'from typing import \1, \2', content)
    
    # Fix empty typing imports
    content = re.sub(r'from typing import\s*,?\s*$', '', content, flags=re.MULTILINE)
    
    # Fix trailing commas in other imports
    content = re.sub(r'from ([^,\n]+) import ([^,\n]*,)*\s*,\s*$',
                     lambda m: f"from {m.group(1)} import {m.group(2)}".rstrip(', '),
                     content, flags=re.MULTILINE)
    
    # Clean up extra whitespace and empty lines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
except Exception as e:
    print(f"Error processing {file_path}: {e}")

EOF
}

# Get all Python files with RUF102 violations
python3 -m ruff check --select RUF102 --output-format=json . 2>/dev/null | \
jq -r '.[] | select(.filename != null) | .filename' | \
sort -u | \
while read -r file; do
    echo "Fixing: $file"
    fix_imports "$file"
done

echo "RUF102 cleanup completed!"