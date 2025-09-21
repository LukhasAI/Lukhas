#!/usr/bin/env bash
set -euo pipefail

# ΛTAG: lane_guard_enforcement
CONFIG_PATH="config/tools/.importlinter"

if ! command -v importlinter >/dev/null 2>&1; then
  echo "⚠️ importlinter not installed. Install via 'pip install import-linter'." >&2
  exit 1
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
