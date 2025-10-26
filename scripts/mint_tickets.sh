#!/usr/bin/env bash
set -euo pipefail
JSON="${1:-tickets/matriz_backlog.json}"

if ! command -v gh >/dev/null; then
  echo "gh CLI required (https://cli.github.com/)" >&2; exit 1
fi

if ! command -v jq >/dev/null; then
  echo "jq required (https://stedolan.github.io/jq/)" >&2; exit 1
fi

jq -c '.[]' "$JSON" | while read -r item; do
  id=$(echo "$item" | jq -r '.id')
  title=$(echo "$item" | jq -r '.title')
  body=$(echo "$item" | jq -r '.body')
  labels=$(echo "$item" | jq -r '.labels | join(",")')

  echo "Creating issue: $id - $title"
  gh issue create --title "$id: $title" --body "$body" --label "$labels" || true
done
