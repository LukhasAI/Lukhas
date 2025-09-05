#!/usr/bin/env bash
set -euo pipefail

# --- Config (pin tool versions to match CI) ---
PY=python3
RUFF_VER=0.6.9
PYTEST_VER=8.4.2
MYPY_VER=1.17.1

# Flags
DRY_RUN=0
NO_PR=0
ALL_TESTS=0

usage() {
  cat <<'EOF'
Usage: scripts/codex_lint_sweep.sh [--dry-run] [--no-pr] [--all-tests]

  --dry-run   : run tools, show diffs; do not commit/push
  --no-pr     : commit locally; do not open a PR
  --all-tests : run full pytest suite (default runs tests/contract only)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --no-pr) NO_PR=1; shift ;;
    --all-tests) ALL_TESTS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

# --- Preconditions ---
git rev-parse --is-inside-work-tree >/dev/null
BASE_BRANCH=${BASE_BRANCH:-main}
git fetch origin --prune
git checkout "${BASE_BRANCH}"
git pull --ff-only origin "${BASE_BRANCH}"

BR="chore/auto-lint-$(date +%Y%m%d)"
git checkout -b "${BR}"

# --- venv setup (local only; non-invasive) ---
if [[ ! -d .lintvenv ]]; then
  ${PY} -m venv .lintvenv
fi
# shellcheck disable=SC1091
source .lintvenv/bin/activate
pip install -q --upgrade pip
pip install -q "ruff==${RUFF_VER}" "pytest==${PYTEST_VER}" "mypy==${MYPY_VER}"

echo "== Tools =="
ruff --version
pytest --version
mypy --version

# --- Ruff: fix + format (repo config) ---
echo "== Ruff check --fix =="
ruff check . --fix --exit-non-zero-on-fix --config pyproject.toml || true

echo "== Ruff format =="
ruff format .

# --- Show diff summary ---
echo "== Diff summary after Ruff =="
git status --porcelain
CHANGED=$(git status --porcelain | wc -l | tr -d ' ')
if [[ "${CHANGED}" -eq 0 ]]; then
  echo "No changes from Ruff/format."
else
  git --no-pager diff --staged || true
  git --no-pager diff || true
fi

# --- Tests (lane-local by default) ---
TEST_PATH="tests/contract"
if [[ "${ALL_TESTS}" -eq 1 ]]; then
  TEST_PATH=""
fi

echo "== Pytest =="
if [[ -z "${TEST_PATH}" ]]; then
  pytest -q --disable-warnings
else
  pytest -q "${TEST_PATH}" --disable-warnings
fi

# --- Scoped mypy (report-only) ---
echo "== MyPy (scoped) =="
set +e
mypy --follow-imports=skip --ignore-missing-imports serve/main.py
MYPY_RC=$?
set -e

# --- Commit / Push / PR ---
if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "(dry-run) Skipping commit/PR."
  exit 0
fi

if [[ "${CHANGED}" -gt 0 ]]; then
  ADDED=$(git status --porcelain | awk '{print $2}' | wc -l | tr -d ' ')
  git add -A
  git commit -m "style: ruff format + lint fixes (auto)

Tools:
- ruff ${RUFF_VER}
- pytest ${PYTEST_VER}
- mypy ${MYPY_VER} (rc=${MYPY_RC})

Notes:
- Auto-applied import order / whitespace / simple style fixes.
- No behavior changes."
  git push -u origin "${BR}"
else
  echo "Nothing to commit."
fi

if [[ "${NO_PR}" -eq 1 ]]; then
  echo "(no-pr) Done."
  exit 0
fi

if command -v gh >/dev/null 2>&1; then
  gh pr create \
    --title "style: ruff/format sweep (auto)" \
    --body "Automated lint/format sweep.

- Ruff ${RUFF_VER} (repo config)
- Pytest ${PYTEST_VER} ($( [[ -z "${TEST_PATH}" ]] && echo "full suite" || echo "${TEST_PATH}" ))
- MyPy ${MYPY_VER} (scoped; rc=${MYPY_RC})

No behavior changes; safe fixes only." \
    --base "${BASE_BRANCH}" \
    --head "${BR}" \
    --label lint --label tech-debt || true
  echo "PR opened."
else
  echo "gh not installed; skipping PR creation."
fi