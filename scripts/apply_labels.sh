#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null; then
  echo "gh CLI required (https://cli.github.com/)" >&2; exit 1
fi

if ! command -v jq >/dev/null; then
  echo "jq required (https://stedolan.github.io/jq/)" >&2; exit 1
fi

jq -r 'to_entries[] | "\(.key) \(.value)"' .github/labels.json | \
while read -r name color; do
  echo "Creating label: $name with color ${color#\#}"
  gh label create "$name" --color "${color#\#}" --force >/dev/null || true
done

echo "Labels applied successfully"
