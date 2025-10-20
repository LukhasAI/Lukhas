#!/usr/bin/env bash
#
# Run generator for a provided newline-delimited list (manifests or module paths).
#
# This script reads a list of module paths from a file and runs the
# `generate_module_manifests.py` script for each one.
#
# Usage:
#   bash scripts/phase4_run_set.sh <listfile>
#
# Requires:
#   - jq
#   - python3
#
set -euo pipefail

LISTFILE="${1:-}"
if [[ -z "$LISTFILE" || ! -f "$LISTFILE" ]]; then
  echo "Usage: $0 <listfile>" >&2
  exit 2
fi

RULES_DIGEST=$(jq -r '.["star_rules.json"]' docs/audits/phase4_digests.json)
CANON_DIGEST=$(jq -r '.["star_canon.json"]' docs/audits/phase4_digests.json)
SCHEMA_VERSION="1.1.0"

process_line() {
  local line="$1"
  if [[ "$line" == manifests/*/module.manifest.json ]]; then
    line="${line#manifests/}"
    line="${line%/module.manifest.json}"
  fi
  echo "[phase4] regenerating: $line"
  python3 scripts/generate_module_manifests.py \
    --module-path "$line" \
    --schema-version "$SCHEMA_VERSION" \
    --rules-digest "$RULES_DIGEST" \
    --canon-digest "$CANON_DIGEST" \
    --star-from-rules --star-confidence-min 0.70 \
    --preserve-tier --preserve-owner --preserve-contracts \
    --atomic-write --roundtrip-verify \
    --reject-legacy-prefix "lukhas/" \
    --exclude "quarantine/*" --exclude ".venv/*" --exclude "node_modules/*" \
    --write --verbose
}

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  [[ "$line" =~ ^# ]] && continue
  process_line "$line"
done < "$LISTFILE"
