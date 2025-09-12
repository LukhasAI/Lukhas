#!/usr/bin/env bash
set -euo pipefail

# Feature flag (default off in CI until confident)
: "${T4_AUTOFIX:=1}"

mkdir -p reports/lints reports/autofix

# ——— Pre: print tool versions into ledger-friendly file
{
  echo "ruff $(ruff --version 2>/dev/null || echo 'n/a')"
  echo "black $(black --version 2>/dev/null || echo 'n/a')"
  echo "isort $(isort --version-number 2>/dev/null || echo 'n/a')"
  python -V
} > reports/autofix/tool_versions.txt || true

# Files staged now
STAGED=$(git diff --name-only --cached --diff-filter=ACM | grep -E '\.py$' || true)
if [ -z "${STAGED}" ]; then
  echo "ℹ️  No staged Python files. Skipping autofix."
  exit 0
fi

# 0) Hard blocker: secrets (pre-commit handles exit != 0)
pre-commit run detect-private-key --files ${STAGED} || {
  echo "❌ Secret detected. Fix manually."
  exit 1
}

# 1) Reality tests (pre) — narrow to imports/integration/golden if present
REALITY_OK=0
if [ -d tests ]; then
  pytest -q tests/test_imports.py tests/test_integration.py tests/golden/ 2>/dev/null && REALITY_OK=1 || REALITY_OK=0
fi
if [ $REALITY_OK -eq 0 ]; then
  echo "❌ Reality pre-check failed. Skipping autofix; fix code first."
  exit 1
fi

if [ "${T4_AUTOFIX}" != "1" ]; then
  echo "⏩ T4_AUTOFIX disabled; exiting."
  exit 0
fi

# 2) Lint reports (no fail): JSON + SARIF for CI
ruff check --fix --output-format json --output-file reports/lints/ruff.json ${STAGED} || true
ruff check --output-format sarif --output-file reports/lints/ruff.sarif ${STAGED} || true

# 3) Apply safe CST fixes against staged subset
python tools/ci/auto_fix_safe.py || true

# 4) Reformat after edits (idempotent)
ruff format ${STAGED} || true
black ${STAGED} || true
isort ${STAGED} --profile black || true

# 5) Re-stage and amend if changed
if ! git diff --quiet; then
  git add -A
  git commit --amend -m "$(git log -1 --pretty=%B)
chore(autofix): apply safe fixes per .t4autofix.toml" || true
fi

# 6) Reality tests (post). If fail, revert edits and branch off
set +e
pytest -q tests/test_imports.py tests/test_integration.py tests/golden/
POST=$?
set -e
if [ $POST -ne 0 ]; then
  echo "❌ Reality post-check failed. Reverting autofix edits to keep tree green."
  git reset --hard HEAD~1 || true
  git checkout -b "autofix/$(git rev-parse --short HEAD)" || true
  echo "ℹ️ Open a PR from the autofix branch for review."
  exit 1
fi

# 7) (Placeholder) anti-fake-tests hook — later swap to real script/command
if [ -x tools/ci/anti_fake_tests.sh ]; then
  tools/ci/anti_fake_tests.sh || true
else
  echo "ℹ️ anti-fake-tests not present yet; skipping."
fi

echo "✅ Autofix loop complete."
