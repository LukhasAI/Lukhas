# Tier 1 CI Workflow Verification Report

This report verifies the presence of `concurrency` and `retention-days` settings in the Tier 1 CI workflows.

| Workflow File | `concurrency` Status | `retention-days` Status |
|---|---|---|
| [`ci.yml`](../../.github/workflows/ci.yml) | ✅ Present | ✅ Present |
| [`architectural-guardian.yml`](../../.github/workflows/architectural-guardian.yml) | ✅ Present | N/A |
| [`auto-codex-review.yml`](../../.github/workflows/auto-codex-review.yml) | ✅ Present | N/A |
| [`auto-copilot-review.yml`](../../.github/workflows/auto-copilot-review.yml) | ✅ Present | N/A |
| [`codeql-analysis.yml`](../../.github/workflows/codeql-analysis.yml) | ✅ Present | N/A |
| [`coverage-gates.yml`](../../.github/workflows/coverage-gates.yml) | ✅ Present | ✅ Present |
| [`dependency-review.yml`](../../.github/workflows/dependency-review.yml) | ✅ Present | N/A |
| [`labot_audit.yml`](../../.github/workflows/labot_audit.yml) | ✅ Present | N/A |

## Summary

All Tier 1 workflows have been updated to include a `concurrency` setting to cancel in-progress runs on the same branch. The `retention-days` setting has been verified and is present where applicable (i.e., in workflows that produce artifacts).
