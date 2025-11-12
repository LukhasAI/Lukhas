#!/usr/bin/env bash
# scripts/migration/matriz_inventory.sh
# List all files importing matriz or MATRIZ
set -euo pipefail

echo "=== MATRIZ Import Inventory ==="
echo "Searching for (from|import) (matriz|MATRIZ) patterns..."
echo ""

git grep -nE "(from|import) (matriz|MATRIZ)" > /tmp/matriz_imports.lst || true

if [[ -s /tmp/matriz_imports.lst ]]; then
    echo "Found $(wc -l < /tmp/matriz_imports.lst) import occurrences"
    echo "Results saved to: /tmp/matriz_imports.lst"
    echo ""
    echo "Top 10 files:"
    cut -d: -f1 /tmp/matriz_imports.lst | sort | uniq -c | sort -rn | head -10
else
    echo "No MATRIZ imports found (or git grep failed)"
fi
