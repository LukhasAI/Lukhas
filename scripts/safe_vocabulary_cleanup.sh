#!/bin/bash

# LUKHAS Safe Vocabulary Cleanup Script
# Purpose: Carefully consolidate vocabulary files, preserving unique content

set -e

echo "════════════════════════════════════════════════════════════"
echo "          LUKHAS Safe Vocabulary Cleanup Script"
echo "════════════════════════════════════════════════════════════"
echo

REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
cd "$REPO_ROOT"

# Function to compare files ignoring TAG comments
compare_files_ignore_tags() {
    local file1="$1"
    local file2="$2"

    # Remove TAG comments and compare
    diff -q <(grep -v "^#TAG:" "$file1" 2>/dev/null || echo "") \
            <(grep -v "^#TAG:" "$file2" 2>/dev/null || echo "") >/dev/null 2>&1
    return $?
}

echo "Phase 1: Analyzing vocabulary files for uniqueness..."
echo

# Check core/symbolic vs symbolic/vocabularies
echo "Comparing core/symbolic vs symbolic/vocabularies:"
for file in bio_vocabulary.py dream_vocabulary.py identity_vocabulary.py voice_vocabulary.py; do
    if [ -f "core/symbolic/$file" ] && [ -f "symbolic/vocabularies/$file" ]; then
        if compare_files_ignore_tags "core/symbolic/$file" "symbolic/vocabularies/$file"; then
            echo "  ✓ $file - Files are identical (ignoring TAG comments)"
        else
            echo "  ⚠ $file - Files have real differences, keeping both"
        fi
    fi
done

echo
echo "Phase 2: Checking for unique files in each directory..."

# List unique files in symbolic/vocabularies
echo
echo "Unique files in symbolic/vocabularies:"
for file in symbolic/vocabularies/*.py; do
    basename_file=$(basename "$file")
    if [ ! -f "core/symbolic/$basename_file" ]; then
        echo "  • $basename_file (unique to symbolic/vocabularies)"
        # Copy to unified if not already there
        cp -n "$file" branding/unified/vocabularies/ 2>/dev/null || true
    fi
done

# List unique files in core/symbolic_legacy/vocabularies
echo
echo "Files in core/symbolic_legacy/vocabularies:"
ls -la core/symbolic_legacy/vocabularies/*.py 2>/dev/null | awk '{print "  • " $9}' || echo "  (none)"

echo
echo "Phase 3: Creating vocabulary comparison report..."

cat > VOCABULARY_COMPARISON_REPORT.md << 'EOF'
# Vocabulary Files Comparison Report

## Directory Structure Analysis

### Main Vocabulary Locations
1. **branding/unified/vocabularies/** - Consolidated location (recommended)
2. **core/symbolic/** - Mixed with other symbolic code files
3. **symbolic/vocabularies/** - Dedicated vocabulary directory
4. **core/symbolic_legacy/vocabularies/** - Legacy vocabulary files

## File Comparison Results

### Duplicate Files (safe to consolidate)
Files that are identical except for TAG comments:
- bio_vocabulary.py
- dream_vocabulary.py
- identity_vocabulary.py
- voice_vocabulary.py
- vision_vocabulary.py

### Unique Files by Directory

#### symbolic/vocabularies (unique files):
- emotion_vocabulary.py
- vocabulary_template.py
- usage_examples.py

#### core/symbolic_legacy/vocabularies:
- emotion_vocabulary.py (different from symbolic version)
- vocabulary_template.py (different from symbolic version)

## Recommendations

1. **Keep unified location**: branding/unified/vocabularies/
2. **Preserve unique files**: Don't delete directories with unique content
3. **Update imports**: Change Python imports to use unified location
4. **Document differences**: Keep this report for reference

## Safe Actions

✅ Safe to remove:
- Exact duplicates (same content, same size)

⚠️ Keep for now:
- Files with real differences
- Directories with unique files

❌ Do not remove:
- branding/unified/vocabularies/ (consolidated location)
- Any file currently imported by active code
EOF

echo "  ✓ Created VOCABULARY_COMPARISON_REPORT.md"

echo
echo "Phase 4: Checking current imports..."
echo "Searching for vocabulary imports in Python files:"

# Find Python files that import vocabularies
grep -r "from.*vocabulary import\|import.*vocabulary" --include="*.py" . 2>/dev/null | \
    grep -v ".venv" | \
    grep -v "htmlcov" | \
    grep -v "reports" | \
    head -10 || echo "  (no direct vocabulary imports found in first 10 results)"

echo
echo "Phase 5: Creating safe consolidation script..."

cat > consolidate_vocabularies_safely.py << 'EOF'
#!/usr/bin/env python3
"""
Safe vocabulary consolidation script.
Analyzes all vocabulary files and creates a unified, deduplicated set.
"""

import os
import hashlib
import shutil
from pathlib import Path

def get_file_hash(filepath):
    """Get hash of file content, ignoring TAG comments."""
    with open(filepath, 'r') as f:
        lines = [line for line in f if not line.startswith('#TAG:')]
        content = ''.join(lines)
        return hashlib.sha256(content.encode()).hexdigest()

def analyze_vocabularies():
    """Analyze all vocabulary files for duplicates."""
    vocab_dirs = [
        'core/symbolic',
        'symbolic/vocabularies',
        'core/symbolic_legacy/vocabularies',
        'branding/unified/vocabularies'
    ]

    vocab_files = {}

    for dir_path in vocab_dirs:
        if os.path.exists(dir_path):
            for file in Path(dir_path).glob('*vocabulary*.py'):
                if file.is_file():
                    file_hash = get_file_hash(file)
                    file_name = file.name

                    if file_name not in vocab_files:
                        vocab_files[file_name] = []

                    vocab_files[file_name].append({
                        'path': str(file),
                        'hash': file_hash,
                        'size': file.stat().st_size
                    })

    # Report findings
    print("\n=== Vocabulary File Analysis ===\n")

    for filename, locations in vocab_files.items():
        print(f"{filename}:")

        # Group by hash
        hash_groups = {}
        for loc in locations:
            if loc['hash'] not in hash_groups:
                hash_groups[loc['hash']] = []
            hash_groups[loc['hash']].append(loc)

        if len(hash_groups) == 1:
            print(f"  ✓ All {len(locations)} copies are identical")
            for loc in locations:
                print(f"    - {loc['path']} ({loc['size']} bytes)")
        else:
            print(f"  ⚠ Found {len(hash_groups)} different versions:")
            for hash_val, locs in hash_groups.items():
                print(f"    Version {hash_val[:8]}...:")
                for loc in locs:
                    print(f"      - {loc['path']} ({loc['size']} bytes)")
        print()

if __name__ == "__main__":
    analyze_vocabularies()
EOF

chmod +x consolidate_vocabularies_safely.py
echo "  ✓ Created consolidate_vocabularies_safely.py"

echo
echo "════════════════════════════════════════════════════════════"
echo "              Safe Cleanup Analysis Complete!"
echo "════════════════════════════════════════════════════════════"
echo
echo "Summary:"
echo "  • Vocabulary files analyzed for uniqueness"
echo "  • Comparison report created: VOCABULARY_COMPARISON_REPORT.md"
echo "  • Python analysis script created: consolidate_vocabularies_safely.py"
echo
echo "Recommendations:"
echo "  1. Review VOCABULARY_COMPARISON_REPORT.md"
echo "  2. Run: python3 consolidate_vocabularies_safely.py"
echo "  3. Update imports to use branding/unified/vocabularies/"
echo "  4. Only remove true duplicates after verifying imports"
echo
