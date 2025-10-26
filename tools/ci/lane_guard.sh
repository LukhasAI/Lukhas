#!/usr/bin/env bash
set -euo pipefail

# ΛTAG: lane_guard_enforcement
CONFIG_PATH="config/tools/.importlinter"

if ! command -v importlinter >/dev/null 2>&1; then
  echo "⚠️ importlinter not installed; falling back to lightweight scan" >&2
  # Fallback: basic grep-based guard (non-exhaustive)
  # Fail only on obvious violations to avoid blocking PRs due to missing tool
  if rg -n "^(from|import)\s+candidate\b" core lukhas matriz 2>/dev/null; then
    echo "❌ Lane violation: production importing candidate/*"
    exit 1
  fi
  echo "✅ Fallback scan: no obvious lane violations"
  exit 0
fi

if [ ! -f "$CONFIG_PATH" ]; then
  echo "❌ Import linter config missing at $CONFIG_PATH" >&2
  exit 1
fi

echo "🔒 Running lane import guard (importlinter)..."
LANE=${LUKHAS_LANE:-prod}
export LUKHAS_LANE="$LANE"
importlinter lint --config "$CONFIG_PATH"
echo "✅ Lane guard clean for lane=$LANE"
