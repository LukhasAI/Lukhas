#!/usr/bin/env bash
set -euo pipefail
OUT=reports/deep_search
mkdir -p "$OUT"

echo "🔍 Creating LUKHAS-specific indexes (excluding external packages, .venv, etc.)"

# Define LUKHAS project directories (exclude .venv, .git, __pycache__, external packages)
PROJECT_DIRS="lukhas candidate core matriz branding tools api orchestration consciousness memory identity governance quantum bio creativity emotion visualization agents config docs scripts tests archive enterprise security analytics dashboard demos deployment"

# 1. LUKHAS Project Files Only (exclude .venv, .git, external packages)
echo "📁 Indexing LUKHAS project files..."
find . -type f \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -path "./*/__pycache__/*" \
    -not -path "./node_modules/*" \
    -not -path "./.DS_Store" \
    -not -path "./*.egg-info/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./.coverage*" \
    -not -path "./.mypy_cache/*" \
    | grep -v "__pycache__" \
    | sort > "$OUT/FILE_INDEX.txt"

# 2. Python Files Only (project files)
echo "🐍 Indexing LUKHAS Python files..."
find . -type f -name "*.py" \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -path "./*/__pycache__/*" \
    -not -path "./node_modules/*" \
    -not -path "./*.egg-info/*" \
    | sort > "$OUT/PY_INDEX.txt"

# 3. Directory-specific indexes
echo "📂 Creating directory-specific indexes..."
for dir in $PROJECT_DIRS; do
    if [ -d "$dir" ]; then
        echo "  Indexing $dir..."
        find "$dir" -type f -name "*.py" | sort > "$OUT/DIR_${dir^^}_PY.txt" 2>/dev/null || true
        find "$dir" -type f | sort > "$OUT/DIR_${dir^^}_ALL.txt" 2>/dev/null || true
    fi
done

# 4. Import samples (first 3 import lines per PROJECT Python file)
echo "📥 Analyzing imports for project files..."
: > "$OUT/IMPORT_SAMPLES.txt"
while IFS= read -r f; do
  if [ -f "$f" ]; then
    printf ">>> %s\n" "$f" >> "$OUT/IMPORT_SAMPLES.txt"
    grep -E "^\s*(from|import)\s+" "$f" | head -3 >> "$OUT/IMPORT_SAMPLES.txt" 2>/dev/null || true
    printf "\n" >> "$OUT/IMPORT_SAMPLES.txt"
  fi
done < "$OUT/PY_INDEX.txt"

# 5. Sanity/health flags (project files only)
echo "🔍 Running import analysis..."
# Wrong core imports (legacy pattern) - only in project files
find lukhas/ candidate/ -name "*.py" -exec grep -Hn "from core\." {} \; 2>/dev/null | sort > "$OUT/WRONG_CORE_IMPORTS.txt" || true
# candidate used by lukhas
find lukhas/ -name "*.py" -exec grep -Hn "from candidate\." {} \; 2>/dev/null | sort > "$OUT/CANDIDATE_USED_BY_LUKHAS.txt" || true

# 6. Health flags (project scope only)
echo "🏥 Checking project health..."
# symlinks in project
find . -type l \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -exec ls -l {} \; | sort > "$OUT/SYMLINKS.txt" || true
# zero-byte files in project
find . -type f -size 0c \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -path "./*/__pycache__/*" \
    | sort > "$OUT/ZERO_BYTES.txt" || true

# 7. Import cycles (project files only)
echo "🔄 Detecting import cycles..."
python tools/ci/find_import_cycles.py >/dev/null 2>&1 || true

# Statistics
echo "
📊 LUKHAS Deep Search Index Statistics:
- Total files: $(wc -l < "$OUT/FILE_INDEX.txt")
- Python files: $(wc -l < "$OUT/PY_INDEX.txt")  
- Symlinks: $(wc -l < "$OUT/SYMLINKS.txt")
- Zero-byte files: $(wc -l < "$OUT/ZERO_BYTES.txt")
- Wrong core imports: $(wc -l < "$OUT/WRONG_CORE_IMPORTS.txt")
- Candidate->Lukhas imports: $(wc -l < "$OUT/CANDIDATE_USED_BY_LUKHAS.txt")

✅ Deep search preparation complete. Outputs in $OUT/
"