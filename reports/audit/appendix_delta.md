---
status: wip
type: documentation
---
# Appendix — Delta between `audit-freeze-20250910T122620Z` and `audit-freeze-20250910T143306Z`

## Summary

- Commits: **19**
- File changes: **14927**
- Diff stat: `14927 files changed, 25102 insertions(+), 3042046 deletions(-)`

### Change buckets

| Bucket | Files |
|---|---:|

| code | 155 |
| tests | 27 |
| ci | 1 |
| audit | 4 |
| docs | 11 |
| other | 14729 |

### Change types

| Type | Count |
|---|---:|

| A | 9 |
| M | 4050 |
| D | 10861 |
| R | 0 |

## Key Governance Artifacts Changed

| File | Hash @ old | Hash @ new |
|---|---|---|

| LUKHAS_ARCHITECTURE_MASTER.json | `—` | `sha256:b3c6892541ebc7b8c21067d9efbe4d7e3f72ee6015f450adf79765f0bae5b187` |

## SBOM

- Present @ old: **False**  
- Present @ new: **True**

- **Note:** SBOM added in new tag — add link in SECURITY_ARCHITECTURE.json if missing.

## MATRIZ/GOLDEN Test Additions

- `tests/golden/tier1/governance_policy_enforcement.json`
- `tests/golden/tier1/identity_authentication_lifecycle.json`
- `tests/golden/tier1/orchestration_workflow_management.json`

## CI / Lane Guard Changes

- `.github/workflows/ci.yml`

## Do-Not-Regress Checks (auto-derived)

- Ensure CI job `audit-validate` publishes SBOM artifact; block merges if SBOM step fails.
- Confirm all `module_uid`s exist and lanes match `AUDIT/LANES.yaml`.
- Keep `contracts-smoke` green; add new tests to nightly dashboard counts.
- Verify `SELF_HEALING_DISABLED=1` remains set in CI for safety.

## Commits (compact)

- 6742371c1 style: apply additional ruff-format changes
- f5dfd9e4b style: apply ruff auto-formatting to codebase
- a258fe495 chore: remove test file for pre-commit validation
- 3f5bf7384 test: verify pre-commit hooks are non-blocking
- 037ad1ae9 chore: remove tracked files from deleted virtual environments
- f39496b51 chore: untrack security log (automated file should be gitignored)
- a04765867 chore: final security log sync
- 19e6fa3a6 chore: sync security audit log post-freeze
- 3e5e13fec chore: finalize audit-ready state and sync automated updates
- b0a419cb3 fix(conftest): restore config parameter name for pytest compatibility
- 200541e03 chore(sbom): generate CycloneDX snapshot
- 53cff5d87 chore(git): ignore venv, local Claude settings, dashboard artifacts
- dd5567ba6 fix(init): guard optional streamlit import to unblock Tier-1 tests
- d6862e99c chore: Update security audit log post-merge
- deeddbabe chore: Update Claude settings permissions for git merge
- 2b3fa8712 chore: Update Claude settings configuration
- e50b2cf31 fix: Remove iCloud dependencies for local-only operation
- b090a5110 feat: Complete Tier-1 validation system and audit preparation
- 9adaad58e chore(lanes): quarantine cross-lane imports (audit-safe)