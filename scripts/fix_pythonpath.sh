#!/usr/bin/env bash
# fix_pythonpath.sh - Suggest PYTHONPATH additions for local dev

REPO_ROOT="${1:-.}"
echo "🔍 Scanning for Python packages under ${REPO_ROOT} ..."

# Find all __init__.py files and extract package directories
PKGS=()
while IFS= read -r dir; do
  PKGS+=("$dir")
done < <(find "$REPO_ROOT" -type f -name "__init__.py" -exec dirname {} \; 2>/dev/null | sort -u)

if [ ${#PKGS[@]} -eq 0 ]; then
  echo "⚠️  No packages found. Add repo root to PYTHONPATH:"
  echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
  exit 0
fi

# Extract unique top-level directories
declare -A TOPS
for p in "${PKGS[@]}"; do
  rel=$(python3 -c "import os; print(os.path.relpath('$p', '$REPO_ROOT'))" 2>/dev/null || echo "$p")
  top=$(echo "$rel" | cut -d'/' -f1)
  TOPS["$top"]=1
done

echo ""
echo "✅ Suggested PYTHONPATH entries (paste into shell or .env):"
for t in "${!TOPS[@]}"; do
  echo "export PYTHONPATH=\"\$(pwd)/$t:\$PYTHONPATH\""
done

echo ""
echo "💡 Or add repository root:"
echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
