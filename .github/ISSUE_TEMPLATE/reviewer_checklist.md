# Reviewer quick checklist — MATRIZ audit & flattening PRs

Use this when reviewing audit-bootstrap and subsequent flattening PRs.

## Quick facts
- Branch: feature or refactor branch (e.g., `refactor/flatten-vivox-v1`)
- Files: Expect changes under `release_artifacts/matriz_readiness_v1/` for audit PRs.
- Policy: `dry_run=true` for audit/bootstrap PRs. Shims are preferred for high-risk modules.

## Checklist
### Scope & Safety
- [ ] Changes limited to `release_artifacts/matriz_readiness_v1/` (audit/bootstrap) OR a small, well-justified set of module moves (for apply PRs).
- [ ] No unreviewed edits to production code or public APIs without deprecation shim & tests.
- [ ] Backup snapshot exists (e.g., `backup/pre-flatten-YYYY-MM-DD-HHMM`) and is referenced in audit_start.json.

### Artifacts & Repro
- [ ] `flatten_map.csv` present and reviewed.
- [ ] `from_imports.txt` and `simple_imports.txt` present and non-empty.
- [ ] `gptpro_config.json` exists with `dry_run` explicitly set.
- [ ] `verify_and_collect.sh` ran and verification logs attached.

### Tools & Checks
- [ ] `black`/`ruff`/`libcst` presence documented or accessible in CI runner.
- [ ] `ruff` E/F baseline is acceptable. No new global E/F errors introduced.
- [ ] `pytest` smoke tests for MATRIZ pass locally or CI (document failures).

### Shim & API safety
- [ ] Shims preserve `__all__` and re-export original symbols
- [ ] No accidental name shadowing or ambiguous E741 identifiers introduced
- [ ] Public API compatibility tests (if present) pass

### Security & alignment
- [ ] No secrets were accidentally committed
- [ ] External API usage (openai., anthropic., requests.) documented and classified
- [ ] Any HIGH_RISK items are flagged and covered by a mitigation plan

### Patch & Simulation
- [ ] If destructive, a `SIMULATE_SCRIPT` exists and was run to produce a patch
- [ ] Patch reviewed, commands shown, and rollback instructions provided

### Final
- [ ] Approve PR for merge to a draft (if audit/bootstrap) or request changes
- [ ] If approved and safe, create a follow-up action list to run the full patch generation (dry-run) and then apply PRs with `dry_run=false` only after human signoff.

**Notes**: Use `@codex` for code-review focusing on artifacts, and `@LukhasAI` org for policy acceptance.
