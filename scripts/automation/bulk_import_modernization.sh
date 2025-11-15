#!/bin/bash

# T4: Bulk UP035 Import Modernization Script
# Efficiently removes deprecated typing imports while preserving needed ones

cd /Users/agi_dev/LOCAL-REPOS/Lukhas

echo "Processing import modernization across all directories..."

# Function to clean up typing imports
clean_imports() {
    local file="$1"
    
    # Skip if file doesn't exist or isn't regular file
    [[ -f "$file" ]] || return
    
    # Create temp file
    temp_file=$(mktemp)
    
    # Process the file line by line to handle imports correctly
    python3 << EOF
import re
import sys

file_path = "$file"
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Handle multi-line imports and single line imports
    # Remove Dict from imports
    content = re.sub(r'from typing import ([^,\n]*,\s*)*Dict(\s*,\s*[^,\n]*)*', 
                     lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(', ,', ',').strip(', '), 
                     content)
    
    # Remove List from imports  
    content = re.sub(r'from typing import ([^,\n]*,\s*)*List(\s*,\s*[^,\n]*)*',
                     lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(', ,', ',').strip(', '),
                     content)
    
    # Remove Set from imports
    content = re.sub(r'from typing import ([^,\n]*,\s*)*Set(\s*,\s*[^,\n]*)*',
                     lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(', ,', ',').strip(', '),
                     content)
    
    # Remove Tuple from imports
    content = re.sub(r'from typing import ([^,\n]*,\s*)*Tuple(\s*,\s*[^,\n]*)*',
                     lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(', ,', ',').strip(', '),
                     content)
                     
    # Remove Type from imports
    content = re.sub(r'from typing import ([^,\n]*,\s*)*Type(\s*,\s*[^,\n]*)*',
                     lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(', ,', ',').strip(', '),
                     content)
    
    # Clean up empty typing imports
    content = re.sub(r'from typing import\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'from typing import\s*,\s*', 'from typing import ', content)
    content = re.sub(r'from typing import\s*,', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
except Exception as e:
    print(f"Error processing {file_path}: {e}", file=sys.stderr)
EOF
}

# Process files in batches
find . -name "*.py" -type f | while read -r file; do
    clean_imports "$file"
done

echo "Bulk import modernization completed!"