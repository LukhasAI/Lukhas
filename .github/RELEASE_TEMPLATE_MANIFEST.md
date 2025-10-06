---
status: wip
type: documentation
---
# Manifest System Release Notes

## What's new
- LUKHAS Manifest System is now **operational** with a living registry, lockfiles, and conformance tests.

## Key metrics
- Modules indexed: **147**
- Conformance: **490/490 passing**
- Schema: **v3.1.0** (aliases + deprecations)
- Restored entrypoints: **39**

## Why it matters
- Prevents drift with CI enforcement
- Verifies manifests with executable tests
- Tracks provenance via lockfiles

## Upgrade notes
- New CI workflow: `manifest-system.yml`
- Pre-commit hooks: manifest validate + lock hydrate
- Registry baseline committed to `artifacts/`

## Next
- Add signing (GPG/cosign)
- Extend conformance with OTEL spans
- Publish module catalog and badges
