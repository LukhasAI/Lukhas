#!/usr/bin/env bash
# Ledger Snapshot Integration Helper
# Captures flag state and writes to governance ledger
set -euo pipefail

LEDGER_ENDPOINT="${LEDGER_ENDPOINT:-https://ledger.service/flags/snapshots}"

echo "📸 Capturing feature flag snapshot..."
SNAPSHOT=$(./guardian/flag_snapshot.sh)

echo "🏛️ Writing to governance ledger..."
echo "$SNAPSHOT" | curl -sS -X POST "$LEDGER_ENDPOINT" \
  -H 'Content-Type: application/json' \
  -H 'X-Source: guardian-safety-tags' \
  -d @- | jq .

echo "✅ Flag snapshot recorded for audit trail"