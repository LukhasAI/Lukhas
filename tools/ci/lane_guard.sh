#!/usr/bin/env bash
set -euo pipefail

# Belt-and-suspenders guard: fail if stable lane (lukhas/) imports experimental lane (candidate/).
# Strategy:
#  - Prefer AST-based detection (zero false positives from strings/comments)
#  - Fallback to ripgrep if Python/AST path is unavailable
#  - Emit a concise artifact for humans in reports/lints/

echo "🔒 Lane guard: checking that 'lukhas/' does not import 'candidate/'..."

TMP_DIR="$(mktemp -d)"
HITS_FILE="$TMP_DIR/hits.txt"
FILTERED_FILE="$TMP_DIR/filtered.txt"
FAIL=0

# 1) Try AST-first if python3 is available
if command -v python3 >/dev/null 2>&1; then
  if python3 tools/ci/lane_guard_ast.py >"$HITS_FILE" 2>/dev/null; then
    : # no hits via AST
  else
    # Non-zero means hits or an AST error. We'll inspect hits file; if empty, fall back.
    if [ -s "$HITS_FILE" ]; then
      FAIL=1
      cp "$HITS_FILE" "$FILTERED_FILE"
    else
      # Fall back if AST errored without producing output
      :
    fi
  fi
fi

# 2) Fallback to ripgrep if AST not used or produced no hits but failed
if [ $FAIL -eq 0 ] && [ ! -s "$HITS_FILE" ]; then
  if ! command -v rg >/dev/null 2>&1; then
    echo "ripgrep (rg) is required for lane_guard.sh fallback" >&2
    exit 2
  fi
  PATTERNS=(
    '^\s*from\s+candidate\.'
    '^\s*import\s+candidate\b'
  )
  >"$HITS_FILE"
  for pat in "${PATTERNS[@]}"; do
    RG_RES=$(rg -n --no-heading -g 'lukhas/**/*.py' -e "$pat" 2>/dev/null || true)
    if [ -n "$RG_RES" ]; then
      printf "%s\n" "$RG_RES" >>"$HITS_FILE"
    fi
  done
  if [ -s "$HITS_FILE" ]; then
    FAIL=1
    cp "$HITS_FILE" "$FILTERED_FILE"
  fi
fi

# 3) Finalize result
if [ $FAIL -ne 0 ]; then
  echo "❌ Forbidden import(s) detected:"
  cat "$FILTERED_FILE" || true
  mkdir -p reports/lints
  cp "$FILTERED_FILE" reports/lints/lane_guard_hits.txt || true
  echo "See reports/lints/lane_guard_hits.txt"
  echo
  echo "🚫 Lane guard failed: remove candidate->lukhas imports."
  exit 1
fi

echo "✅ lane_guard: OK"
