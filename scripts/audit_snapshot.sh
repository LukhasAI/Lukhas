#!/usr/bin/env bash
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="docs/audits/live/${STAMP}"
mkdir -p "${OUT_DIR}"

echo "==> Ruff baseline"
python3 -m ruff check lukhas core matriz --no-cache --output-format=full > "${OUT_DIR}/ruff.txt" || true
python3 -m ruff check lukhas core matriz --statistics --no-cache > "${OUT_DIR}/ruff_stats.txt" || true

if [ -f scripts/generate_openapi.py ]; then
  echo "==> OpenAPI"
  python3 scripts/generate_openapi.py || true
  if [ -f docs/openapi/lukhas-openapi.json ]; then
    python3 -m openapi_spec_validator docs/openapi/lukhas-openapi.json || true
  fi
fi

if [ -f scripts/validate_module_manifests.py ]; then
  echo "==> Manifest validation"
  python3 scripts/validate_module_manifests.py --out "${OUT_DIR}/manifest_validation.json" || true
fi

if [ -f scripts/system_health_audit.py ]; then
  echo "==> Health audit (best-effort)"
  python3 scripts/system_health_audit.py --out-json "${OUT_DIR}/health.json" --out-md "${OUT_DIR}/health.md" || true
fi

cat > "${OUT_DIR}/INDEX.md" <<EOF
# 📦 Local Audit Snapshot

- Timestamp: ${STAMP}

## Artifacts
- Ruff (full): \`${OUT_DIR}/ruff.txt\`
- Ruff (stats): \`${OUT_DIR}/ruff_stats.txt\`
- OpenAPI: \`docs/openapi/lukhas-openapi.json\` (if generated)
- Manifest validation: \`${OUT_DIR}/manifest_validation.json\` (if available)
- Health audit: \`${OUT_DIR}/health.{json,md}\` (if available)
EOF

echo "✅ Snapshot written to ${OUT_DIR}"
