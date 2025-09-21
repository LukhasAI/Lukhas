#!/usr/bin/env bash
set -euo pipefail
# allow existing lines under tests/ and core/__init__.py
if git diff --cached -U0 | grep -E '^\+.*\b(from|import)\s+core(\.|$)' \
  | grep -v 'tests/' | grep -v 'core/__init__.py'; then
  echo "Blocked: new legacy 'core' imports detected. Use 'lukhas.core'." >&2
  exit 1
fi