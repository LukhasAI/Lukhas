#!/usr/bin/env bash
set -euo pipefail

echo "Starting LUKHAS Quick Audit..."
mkdir -p reports

# Quick Git status
echo "Checking Git status..."
git status -s > reports/git_status.txt 2>&1 || true

# Quick Python file count
echo "Counting Python files..."
find . -name "*.py" -type f | wc -l > reports/python_file_count.txt 2>&1 || true

# Quick dependency count
echo "Counting dependencies..."
pip list --format=freeze | wc -l > reports/dependency_count.txt 2>&1 || true

# Create summary
{
  echo "# LUKHAS Quick Audit Summary"
  echo ""
  echo "Generated: $(date)"
  echo ""
  echo "- Git Status: $(wc -l < reports/git_status.txt 2>/dev/null || echo 0) modified files"
  echo "- Python Files: $(cat reports/python_file_count.txt 2>/dev/null || echo 0) total"
  echo "- Dependencies: $(cat reports/dependency_count.txt 2>/dev/null || echo 0) packages"
} > reports/INDEX.md

echo "Quick audit complete! Results in reports/INDEX.md"
cat reports/INDEX.md