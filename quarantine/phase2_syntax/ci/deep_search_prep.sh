#!/usr/bin/env bash
set -euo pipefail
OUT=reports/deep_search
mkdir -p "$OUT"

# LUKHAS source directories only (~4500 files expected)
LUKHAS_DIRS="lukhas candidate core consciousness memory identity governance quantum bio creativity emotion orchestration visualization api bridge security branding config scripts tests docs agents"

echo "Creating per-directory indexes for LUKHAS source directories..."

# Per-directory indexes - create separate index for each directory
for dir in $LUKHAS_DIRS; do
    if [ -d "$dir" ]; then
        echo "  Indexing $dir..."
        DIR_UPPER=$(echo "$dir" | tr '[:lower:]' '[:upper:]')

        # All files in this directory
        find "$dir" -type f -not -path "*/__pycache__/*" -not -path "*/node_modules/*" -not -name "*.pyc" -not -name ".DS_Store" | sort > "$OUT/DIR_${DIR_UPPER}_ALL.txt"

        # Python files in this directory
        find "$dir" -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/node_modules/*" -not -name "*.pyc" | sort > "$OUT/DIR_${DIR_UPPER}_PY.txt"

        # Import samples for this directory only
        : > "$OUT/DIR_${DIR_UPPER}_IMPORTS.txt"
        while IFS= read -r f; do
            printf ">>> %s\n" "$f" >> "$OUT/DIR_${DIR_UPPER}_IMPORTS.txt"
            grep -E "^\s*(from|import)\s+" "$f" | head -3 >> "$OUT/DIR_${DIR_UPPER}_IMPORTS.txt" 2>/dev/null || true
            printf "\n" >> "$OUT/DIR_${DIR_UPPER}_IMPORTS.txt"
        done < "$OUT/DIR_${DIR_UPPER}_PY.txt"
    fi
done

# Master indexes - consolidated but manageable
echo "Creating master indexes..."

# Master file index (all LUKHAS source)
{
    for dir in $LUKHAS_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f -not -path "*/__pycache__/*" -not -path "*/node_modules/*" -not -name "*.pyc" -not -name ".DS_Store"
        fi
    done
    # Add key root files
    find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.json" -o -name "*.txt" \)
} | sort > "$OUT/FILE_INDEX_MASTER.txt"

# Master Python index
{
    for dir in $LUKHAS_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/node_modules/*" -not -name "*.pyc"
        fi
    done
    # Add root Python files
    find . -maxdepth 1 -type f -name "*.py"
} | sort > "$OUT/PY_INDEX_MASTER.txt"

# Health flags - focused analysis
echo "Running health analysis..."

# Wrong core imports (legacy pattern)
{
    for dir in lukhas candidate; do
        if [ -d "$dir" ]; then
            find "$dir" -name "*.py" -not -path "*/__pycache__/*" -exec grep -Hn "from core\." {} \; 2>/dev/null || true
        fi
    done
} | sort > "$OUT/WRONG_CORE_IMPORTS.txt"

# candidate used by lukhas
find lukhas/ -name "*.py" -not -path "*/__pycache__/*" -exec grep -Hn "from candidate\." {} \; 2>/dev/null | sort > "$OUT/CANDIDATE_USED_BY_LUKHAS.txt" || true

# symlinks - LUKHAS source only
{
    for dir in $LUKHAS_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type l -exec ls -l {} \; 2>/dev/null || true
        fi
    done
    # Check for important root symlinks
    find . -maxdepth 1 -type l -exec ls -l {} \; 2>/dev/null || true
} | sort > "$OUT/SYMLINKS.txt"

# zero-byte files - LUKHAS source only
{
    for dir in $LUKHAS_DIRS; do
        if [ -d "$dir" ]; then
            find "$dir" -type f -size 0c 2>/dev/null || true
        fi
    done
} | sort > "$OUT/ZERO_BYTES.txt"

# import cycles
python tools/ci/find_import_cycles.py >/dev/null || true

# Summary statistics
echo ""
echo "📊 Per-Directory Index Summary:"
for dir in $LUKHAS_DIRS; do
    if [ -d "$dir" ] && [ -f "$OUT/DIR_$(echo "$dir" | tr '[:lower:]' '[:upper:]')_ALL.txt" ]; then
        DIR_UPPER=$(echo "$dir" | tr '[:lower:]' '[:upper:]')
        ALL_COUNT=$(wc -l < "$OUT/DIR_${DIR_UPPER}_ALL.txt")
        PY_COUNT=$(wc -l < "$OUT/DIR_${DIR_UPPER}_PY.txt")
        printf "  %-15s: %4d files (%4d Python)\n" "$dir" "$ALL_COUNT" "$PY_COUNT"
    fi
done

echo ""
echo "📋 Master Index Summary:"
echo "  Total files: $(wc -l < "$OUT/FILE_INDEX_MASTER.txt")"
echo "  Python files: $(wc -l < "$OUT/PY_INDEX_MASTER.txt")"
echo "  Symlinks: $(wc -l < "$OUT/SYMLINKS.txt")"
echo "  Zero-byte files: $(wc -l < "$OUT/ZERO_BYTES.txt")"
echo "  Wrong core imports: $(wc -l < "$OUT/WRONG_CORE_IMPORTS.txt")"
echo "  Candidate->Lukhas imports: $(wc -l < "$OUT/CANDIDATE_USED_BY_LUKHAS.txt")"
echo ""
echo "✅ Per-directory deep search preparation complete. Outputs in $OUT/"
