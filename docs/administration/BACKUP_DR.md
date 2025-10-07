---
status: wip
type: documentation
owner: unknown
module: administration
redirect: false
moved_to: null
---

# Backup & DR for LUKHAS

This module provides:
- Snapshot creation with tar + zstd/gzip, per-file and bundle SHA-256
- Optional manifest HMAC
- S3 upload with SSE-KMS
- Health endpoint: `/ops/backup/health`
- Restore utility with checksum verification and safe extraction

## Quick start

1) Local backup

make backup-local

Artifacts land in .lukhas_backup/out and a record is written to .lukhas_backup/last_success.json

2) Upload to S3

export BACKUP_S3_BUCKET=s3://my-bucket/backups
export AWS_REGION=us-east-1
# optional
export AWS_KMS_KEY_ID=alias/my-key

make backup-s3

3) Restore (dry-run)

make dr-drill

4) Restore from a manifest

make restore-local MANIFEST=path/to/manifest.json TARGET=_restore

## Health endpoint

Mounts at /ops/backup/health (requires API key if configured). Returns last_success JSON:

{
  "now_utc": "...",
  "last_success": {"last_s3_manifest": "s3://...", "last_s3_tar": "s3://...", "last_success_utc": "..."},
  "ok": true,
  "fresh": true,
  "age_minutes": 12.3,
  "max_age_minutes": 60
}

Configure freshness window via BACKUP_MAX_AGE_MINUTES.

## S3 lifecycle

See backup/s3_lifecycle.example.json for a recommended starting policy.

## Notes

- Restore utility protects against path traversal and supports .tar.zst/.tar.gz
- For production, enable S3 versioning and lifecycle policies.
- Consider storing manifests in a separate, access-controlled bucket.
