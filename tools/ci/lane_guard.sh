#!/usr/bin/env bash
set -euo pipefail
# block candidate->lukhas imports
if rg -n "from\s+candidate\." lukhas/ -g '!**/__init__.py' >/dev/null; then
  echo "❌ lane_guard: candidate imports in lukhas/"
  rg -n "from\s+candidate\." lukhas/ -g '!**/__init__.py'
  exit 1
fi
echo "✅ lane_guard: OK"
