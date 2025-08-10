#!/usr/bin/env bash
set -euo pipefail

: "${BACKUP_S3_BUCKET:?Set BACKUP_S3_BUCKET (e.g., s3://bucket)}"
BACKUP_PREFIX="${BACKUP_PREFIX:-pwm}"
OUTDIR="${OUTDIR:-out}"
INCLUDE=${BACKUP_INCLUDE:-".lukhas_feedback .lukhas_audit .lukhas_analytics .lukhas_migration .lukhas_legacy"}
EXCLUDE=${BACKUP_EXCLUDE:-"*.tmp *.log .cache node_modules __pycache__"}
KMS="${BACKUP_KMS_KEY_ID:-}"

mkdir -p "${OUTDIR}"

python3 scripts/backup_create.py \
  --include ${INCLUDE} \
  --exclude ${EXCLUDE} \
  --outdir "${OUTDIR}" | tee "${OUTDIR}/backup_create.out.json"

TARBALL=$(jq -r '.tarball' "${OUTDIR}/backup_create.out.json")
MANIFEST=$(jq -r '.manifest' "${OUTDIR}/backup_create.out.json")

# Derive S3 key name, optionally append GitHub run id for traceability
TARBALL_FN="$(basename "${TARBALL}")"
KEY_FILE="$TARBALL_FN"
if [[ -n "${GITHUB_RUN_ID:-}" ]]; then
  if [[ "$TARBALL_FN" =~ ^(.*)\.tar\.(gz|zst)$ ]]; then
    KEY_FILE="${BASH_REMATCH[1]}_${GITHUB_RUN_ID}.tar.${BASH_REMATCH[2]}"
  else
    BASE_NOEXT="${TARBALL_FN%.*}"
    EXT_ONLY="${TARBALL_FN##*.}"
    KEY_FILE="${BASE_NOEXT}_${GITHUB_RUN_ID}.${EXT_ONLY}"
  fi
fi
KEY_BASE="${BACKUP_PREFIX}/${KEY_FILE}"

echo "Uploading to ${BACKUP_S3_BUCKET}/${KEY_BASE}"
if [[ -n "${KMS}" ]]; then
  aws s3 cp "${TARBALL}"   "${BACKUP_S3_BUCKET}/${KEY_BASE}"                --sse aws:kms --sse-kms-key-id "${KMS}"
  aws s3 cp "${MANIFEST}"  "${BACKUP_S3_BUCKET}/${KEY_BASE}.manifest.json"  --sse aws:kms --sse-kms-key-id "${KMS}"
else
  aws s3 cp "${TARBALL}"   "${BACKUP_S3_BUCKET}/${KEY_BASE}"
  aws s3 cp "${MANIFEST}"  "${BACKUP_S3_BUCKET}/${KEY_BASE}.manifest.json"
fi

mkdir -p .lukhas_backup
jq -n --arg k "${BACKUP_S3_BUCKET}/${KEY_BASE}" \
      --arg m "${BACKUP_S3_BUCKET}/${KEY_BASE}.manifest.json" \
      --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      '{last_s3_tar:$k, last_s3_manifest:$m, last_success_utc:$ts}' \
      > .lukhas_backup/last_success.json

echo "✅ Backup complete"
