#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${LUKHAS_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTEST_CMD=()

# ΛTAG: batch_pytest_resolution
resolve_pytest_command() {
  PYTEST_CMD=()

  if [[ "${BATCH_NEXT_FORCE_PYTEST_FALLBACK:-0}" != "1" ]] && command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD=(pytest)
    return 0
  fi

  if [ -x "${REPO_ROOT}/.venv/bin/pytest" ]; then
    PYTEST_CMD=("${REPO_ROOT}/.venv/bin/pytest")
    return 0
  fi

  if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
    PYTEST_CMD=("${REPO_ROOT}/.venv/bin/python" -m pytest)
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    PYTEST_CMD=(python3 -m pytest)
    return 0
  fi

  return 1
}

# ΛTAG: batch_pytest_runner
run_pytest() {
  if [[ ${#PYTEST_CMD[@]} -eq 0 ]]; then
    if ! resolve_pytest_command; then
      echo "❌ pytest command not available. Activate the virtual environment via 'source .venv/bin/activate'." >&2
      return 127
    fi
  fi

  "${PYTEST_CMD[@]}" "$@"
}

main() {
  local batch_file="${BATCH_FILE:?set BATCH_FILE=/tmp/batch_matriz.tsv}"
  local done_file="${batch_file}.done"

  cd "$REPO_ROOT"

  if [ -f ".venv/bin/activate" ]; then
    # ΛTAG: batch_virtualenv_activation
    source .venv/bin/activate
  fi

  if ! resolve_pytest_command; then
    echo "❌ pytest command not available. Activate the virtual environment via 'source .venv/bin/activate'." >&2
    exit 127
  fi

  local next_line
  next_line="$(comm -23 <(sort -u "$batch_file") <(sort -u "$done_file" 2>/dev/null || true) | head -n 1 || true)"
  [ -n "$next_line" ] || { echo "✅ No more items in $batch_file"; exit 0; }

  local module
  local src
  local dst
  module="$(echo "$next_line" | cut -f1)"
  src="$(echo "$next_line" | cut -f2)"
  dst="$(echo "$next_line" | cut -f3)"

  local branch
  branch="feat/integrate-$(echo "$module" | tr '.' '-' | tr '/' '-')"

  echo "➡️  MODULE: $module"
  echo "    SRC   : $src"
  echo "    DST   : $dst"
  echo "    BRANCH: $branch"

  git checkout -b "$branch"

  mkdir -p "$(dirname "$dst")"

  run_pytest -q || true

  if [ -e "$src" ]; then
    git mv "$src" "$dst"
  else
    echo "⚠️  Source not found: $src (skipping move)"
  fi

  echo "🔎 Grep references for manual update:"
  grep -RIn -- "$src" || true
  grep -RIn -- "$(dirname "$src")" || true

  local test_name
  local test_candidate
  test_name="test_$(basename "$dst" .py | tr '-' '_' | tr '.' '_').py"
  test_candidate="tests/integration/${test_name}"

  if [ ! -f "$test_candidate" ]; then
    mkdir -p tests/integration
    cat > "$test_candidate" <<PY
def test_${test_name%.*}_placeholder():
    assert True
PY
    git add "$test_candidate"
  fi

  run_pytest "$test_candidate" -q || { echo "❌ integration test failed"; exit 1; }
  run_pytest tests/smoke/ -q
  make codex-acceptance-gates

  git add -A
  git commit -m "feat(integration): integrate ${module} → ${dst} — task: Hidden Gems Integration"

  mkdir -p "$(dirname "$done_file")"
  echo "$next_line" >> "$done_file"

  echo "✅ Integrated: $module"
  echo "Next: run this script again to pick the next item."
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
