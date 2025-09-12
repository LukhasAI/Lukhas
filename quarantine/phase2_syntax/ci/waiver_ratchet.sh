#!/usr/bin/env bash
set -euo pipefail
git fetch Github.com/Lukhas main --depth=1 2>/dev/null || true
base=$(git show Github.com/Lukhas/main:ops/lane_waivers.txt 2>/dev/null | wc -l | tr -d ' \n' || echo "0")
cur=$(wc -l < ops/lane_waivers.txt 2>/dev/null | tr -d ' \n' || echo "0")
if [ "$cur" -gt "$base" ]; then
  echo "❌ waiver ratchet: grew from $base to $cur"; exit 1
fi
echo "✅ waiver ratchet: $cur (base $base)"
