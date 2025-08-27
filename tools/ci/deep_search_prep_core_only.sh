#!/usr/bin/env bash
set -euo pipefail
OUT=reports/deep_search
mkdir -p "$OUT"

echo "🎯 Creating LUKHAS CORE module indexes only (~3000 files expected)"

# Define ONLY the core LUKHAS source directories (no node_modules, no build outputs, no test artifacts)
CORE_DIRS="lukhas candidate core consciousness memory identity governance quantum bio creativity emotion orchestration visualization api bridge security"

# 1. LUKHAS Core Source Files Only
echo "📁 Indexing LUKHAS core source files..."
{
    for dir in $CORE_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f \
                -not -path "*/__pycache__/*" \
                -not -path "*/node_modules/*" \
                -not -path "*/.pytest_cache/*" \
                -not -path "*/dist/*" \
                -not -path "*/build/*" \
                -not -name "*.pyc" \
                -not -name ".DS_Store"
        fi
    done
    # Add key root files
    find . -maxdepth 1 -type f -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.json" | grep -v node_modules
} | sort > "$OUT/FILE_INDEX.txt"

# 2. Python Files Only (core source)
echo "🐍 Indexing LUKHAS core Python files..."
{
    for dir in $CORE_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f -name "*.py" \
                -not -path "*/__pycache__/*" \
                -not -path "*/node_modules/*" \
                -not -name "*.pyc"
        fi
    done
    # Add root Python files
    find . -maxdepth 1 -type f -name "*.py"
} | sort > "$OUT/PY_INDEX.txt"

# 3. Directory-specific indexes (fixed bash syntax)
echo "📂 Creating directory-specific indexes..."
for dir in $CORE_DIRS; do
    if [ -d "$dir" ]; then
        echo "  Indexing $dir..."
        DIR_UPPER=$(echo "$dir" | tr '[:lower:]' '[:upper:]')
        find "$dir" -type f -name "*.py" -not -path "*/__pycache__/*" | sort > "$OUT/DIR_${DIR_UPPER}_PY.txt" 2>/dev/null || true
        find "$dir" -type f -not -path "*/__pycache__/*" -not -name "*.pyc" | sort > "$OUT/DIR_${DIR_UPPER}_ALL.txt" 2>/dev/null || true
    fi
done

# 4. Import samples (first 3 import lines per CORE Python file)
echo "📥 Analyzing imports for core files..."
: > "$OUT/IMPORT_SAMPLES.txt"
while IFS= read -r f; do
  if [ -f "$f" ]; then
    printf ">>> %s\n" "$f" >> "$OUT/IMPORT_SAMPLES.txt"
    grep -E "^\s*(from|import)\s+" "$f" | head -3 >> "$OUT/IMPORT_SAMPLES.txt" 2>/dev/null || true
    printf "\n" >> "$OUT/IMPORT_SAMPLES.txt"
  fi
done < "$OUT/PY_INDEX.txt"

# 5. Import analysis (core files only)
echo "🔍 Running import analysis..."
# Wrong core imports (legacy pattern) - only in core dirs
{
    for dir in lukhas candidate; do
        if [ -d "$dir" ]; then
            find "$dir" -name "*.py" -not -path "*/__pycache__/*" -exec grep -Hn "from core\." {} \; 2>/dev/null || true
        fi
    done
} | sort > "$OUT/WRONG_CORE_IMPORTS.txt"

# candidate used by lukhas
find lukhas/ -name "*.py" -not -path "*/__pycache__/*" -exec grep -Hn "from candidate\." {} \; 2>/dev/null | sort > "$OUT/CANDIDATE_USED_BY_LUKHAS.txt" || true

# 6. Health flags (core scope only)
echo "🏥 Checking core module health..."
# symlinks in core dirs only
{
    for dir in $CORE_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type l -exec ls -l {} \; 2>/dev/null || true
        fi
    done
} | sort > "$OUT/SYMLINKS.txt"

# zero-byte files in core dirs only
{
    for dir in $CORE_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f -size 0c 2>/dev/null || true
        fi
    done
} | sort > "$OUT/ZERO_BYTES.txt"

# 7. Import cycles (update the Python script to only scan core dirs)
echo "🔄 Detecting import cycles in core modules..."
python -c "
import sys
sys.path.insert(0, 'tools/ci')
import find_import_cycles
find_import_cycles.ROOT_DIRS = ['lukhas', 'candidate', 'core', 'consciousness', 'memory', 'identity', 'governance']
" 2>/dev/null || python tools/ci/find_import_cycles.py >/dev/null 2>&1 || true

# Statistics
echo "
📊 LUKHAS Core Module Index Statistics:
- Total files: $(wc -l < "$OUT/FILE_INDEX.txt")
- Python files: $(wc -l < "$OUT/PY_INDEX.txt")  
- Symlinks: $(wc -l < "$OUT/SYMLINKS.txt")
- Zero-byte files: $(wc -l < "$OUT/ZERO_BYTES.txt")
- Wrong core imports: $(wc -l < "$OUT/WRONG_CORE_IMPORTS.txt")
- Candidate->Lukhas imports: $(wc -l < "$OUT/CANDIDATE_USED_BY_LUKHAS.txt")

✅ LUKHAS core module preparation complete. Outputs in $OUT/
"