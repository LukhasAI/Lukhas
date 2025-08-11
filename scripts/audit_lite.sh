#!/usr/bin/env bash
set -euo pipefail

echo "Starting LUKHAS Audit (Lite Version)..."
mkdir -p reports

# List production Python files
find . -type f -name "*.py" \
  -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" -not -path "*/tests/*" -not -path "*/examples/*" \
  -not -path "*/docs/*" -not -path "*/build/*" -not -path "*/dist/*" \
  -not -name "test_*.py" -not -name "*_test.py" > reports/prod_python_files.txt

echo "### 1. Git Hygiene"
git ls-files --others --exclude-standard > reports/git_untracked.txt || true
git status -s > reports/git_status.txt || true

echo "### 2. Dependency Check"
pip freeze > reports/pip_freeze_env.txt || true

echo "### 3. Static Quality (available tools only)"
if command -v ruff &> /dev/null; then
    ruff check . > reports/ruff.txt 2>&1 || true
    echo "Ruff check completed"
fi

if command -v black &> /dev/null; then
    black --check . > reports/black.txt 2>&1 || true
    echo "Black check completed"
fi

if command -v mypy &> /dev/null; then
    mypy --ignore-missing-imports --exclude "(venv|\\.venv|tests|examples|docs)" . > reports/mypy.txt 2>&1 || true
    echo "MyPy check completed"
fi

echo "### 4. Tests (if pytest available)"
if command -v pytest &> /dev/null; then
    pytest -q --maxfail=1 --disable-warnings --cache-clear > reports/pytest.txt 2>&1 || true
    echo "Pytest completed"
fi

echo "### 5. Summary Index"
{
  echo "# LUKHAS Audit Summary (Lite)"
  echo ""
  echo "Generated: $(date)"
  echo ""
  for f in reports/*; do
    if [ -f "$f" ]; then
        size=$(wc -l < "$f" 2>/dev/null || echo 0)
        echo "- $(basename "$f"): ${size} lines"
    fi
  done
} > reports/INDEX.md

echo "Audit complete! Results in reports/INDEX.md"