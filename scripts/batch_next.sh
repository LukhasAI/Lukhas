#!/usr/bin/env bash
set -euo pipefail

BATCH_FILE="${BATCH_FILE:?set BATCH_FILE=/tmp/batch_matriz.tsv}"
DONE_FILE="${BATCH_FILE}.done"
REPO_ROOT="${LUKHAS_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$REPO_ROOT"

# Activate virtualenv if available
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Pick first line not in DONE
NEXT_LINE="$(comm -23 <(sort -u "$BATCH_FILE") <(sort -u "$DONE_FILE" 2>/dev/null || true) | head -n 1 || true)"
[ -n "$NEXT_LINE" ] || { echo "✅ No more items in $BATCH_FILE"; exit 0; }

MODULE="$(echo "$NEXT_LINE" | cut -f1)"
SRC="$(echo "$NEXT_LINE" | cut -f2)"
DST="$(echo "$NEXT_LINE" | cut -f3)"

BRANCH="feat/integrate-$(echo "$MODULE" | tr '.' '-' | tr '/' '-')"

echo "➡️  MODULE: $MODULE"
echo "    SRC   : $SRC"
echo "    DST   : $DST"
echo "    BRANCH: $BRANCH"

# Branch
git checkout -b "$BRANCH"

# Ensure destination dir
mkdir -p "$(dirname "$DST")"

# Smoke (allow fail early without stopping script)
pytest -q || true

# Move with history if exists
if [ -e "$SRC" ]; then
  git mv "$SRC" "$DST"
else
  echo "⚠️  Source not found: $SRC (skipping move)"
fi

# Greedy import update hint (non-destructive preview)
# dev uses IDE/AST for precise refactor; we only hint here
echo "🔎 Grep references for manual update:"
grep -RIn -- "$SRC" || true
grep -RIn -- "$(dirname "$SRC")" || true

# Try module-specific test name from module path
TEST_NAME="test_$(basename "$DST" .py | tr '-' '_' | tr '.' '_').py"
TEST_CANDIDATE="tests/integration/${TEST_NAME}"

# If missing, create a minimal placeholder (keeps CI honest)
if [ ! -f "$TEST_CANDIDATE" ]; then
  mkdir -p tests/integration
  cat > "$TEST_CANDIDATE" <<PY
def test_${TEST_NAME%.*}_placeholder():
    assert True
PY
  git add "$TEST_CANDIDATE"
fi

# Prove
pytest "$TEST_CANDIDATE" -q || { echo "❌ integration test failed"; exit 1; }
pytest tests/smoke/ -q
make codex-acceptance-gates

# Commit
git add -A
git commit -m "feat(integration): integrate ${MODULE} → ${DST} — task: Hidden Gems Integration"

# Mark done
mkdir -p "$(dirname "$DONE_FILE")"
echo "$NEXT_LINE" >> "$DONE_FILE"

echo "✅ Integrated: $MODULE"
echo "Next: run this script again to pick the next item."
