#!/usr/bin/env bash
set -euo pipefail
OUT=reports/deep_search
mkdir -p "$OUT"

# Indexes
find . -type f -not -path "./.git/*" -print | sort > "$OUT/FILE_INDEX.txt"
find . -type f -name "*.py" -not -path "./.git/*" | sort > "$OUT/PY_INDEX.txt"
# First 3 import lines per file
: > "$OUT/IMPORT_SAMPLES.txt"
while IFS= read -r f; do
  printf ">>> %s\n" "$f" >> "$OUT/IMPORT_SAMPLES.txt"
  grep -E "^\s*(from|import)\s+" "$f" | head -3 >> "$OUT/IMPORT_SAMPLES.txt" || true
  printf "\n" >> "$OUT/IMPORT_SAMPLES.txt"
done < "$OUT/PY_INDEX.txt"

# Sanity/health flags
# Wrong core imports (legacy pattern)
grep -Rn "from core\." -n -- */*.py 2>/dev/null | sort > "$OUT/WRONG_CORE_IMPORTS.txt" || true
# candidate used by lukhas
grep -Rn "from candidate\." lukhas/ 2>/dev/null | sort > "$OUT/CANDIDATE_USED_BY_LUKHAS.txt" || true
# symlinks
find . -type l -not -path "./.git/*" -exec ls -l {} \; | sort > "$OUT/SYMLINKS.txt" || true
# zero-byte files
find . -type f -size 0c -not -path "./.git/*" | sort > "$OUT/ZERO_BYTES.txt" || true
# import cycles
python tools/ci/find_import_cycles.py >/dev/null || true

echo "Deep search preparation complete. Outputs in $OUT/"
