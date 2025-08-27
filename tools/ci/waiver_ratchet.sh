#!/usr/bin/env bash
set -euo pipefail

# Prevent waiver creep: fail if ops/lane_waivers.txt grows vs origin/main

git fetch origin main --depth=1 >/dev/null 2>&1 || true

base=$(git show origin/main:ops/lane_waivers.txt 2>/dev/null | wc -l | tr -d ' ' || true)
if [ -f ops/lane_waivers.txt ]; then
  cur=$(wc -l < ops/lane_waivers.txt | tr -d ' ')
else
  cur=0
fi

if [ -n "${base:-}" ] && [ -n "${cur:-}" ] && [ "${cur}" -gt "${base}" ]; then
  echo "❌ waiver ratchet: grew from ${base} to ${cur} lines"
  exit 1
fi

echo "✅ waiver ratchet: ${cur:-0} (base ${base:-0})"
