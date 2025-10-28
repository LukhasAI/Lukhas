# TODO Cleanup Audit — CODEX Run — 2025-10-28

## Summary
**Run date:** 2025-10-28  
**Agent / Runner:** Codex (automation)  
**Outcome:** Replaced **78** TODOs with GitHub issue links across **38** files. Changes were committed and merged via PR #631.

**PR:** https://github.com/LukhasAI/Lukhas/pull/631  
**Mapping artifact:** artifacts/todo_to_issue_map.json  
**Post-apply log:** artifacts/replace_todos_log.json  
**Completion report:** CODEX_TODO_REPLACEMENT_COMPLETE.md (committed to `main`)

## Counts
- TODOs replaced: **78**
- Files modified: **38**
- Pre-existing files skipped for syntax: *2* (unrelated, surfaced by Python compile)
- Issues created: range **#552–#629** (78 issues; see mapping file above)

## Notable security-related items
The following security-related TODOs were converted to issues and labeled/flagged accordingly:
- Issue **#552** — `.semgrep/lukhas-security.yaml:547` — *implement authentication* (SCOPE: SECURITY)
- Issue **#600** — `qi/bio/oscillators/oscillator.py:263` — *Validate against token store* (SCOPE: SECURITY)
*(See artifacts/todo_to_issue_map.json for full list.)*

## Validation performed
- Dry-run verified: `artifacts/todo_to_issue_map.json` and `artifacts/replace_todos_log.json`
- Spot-checked diffs to ensure replacements were comment/string-only and formatted as:
  `# See: https://github.com/LukhasAI/Lukhas/issues/<n>`
- Confirmed generated issues include `Location`, `Priority`, optional `Owner`, and original TODO text for traceability.
- Confirmed that security/privacy/model-safety TODOs were converted to issues (not deleted).
- Python `compile` surfaced unrelated pre-existing syntax issues in lab/test files; **no logic changes** were made by the replacer.

## Artifacts & Links
- Mapping: `artifacts/todo_to_issue_map.json`  
- Post-apply log: `artifacts/replace_todos_log.json`  
- Completion PR: https://github.com/LukhasAI/Lukhas/pull/631  
- Completion report: `CODEX_TODO_REPLACEMENT_COMPLETE.md`

## Next steps
1. (Optional) Run `make smoke` to provide an extra safety check across changed test files.  
2. Monitor issues **#552–#629** and assign owners/labels where missing. Prioritize security TODOs for triage.  
3. Add this audit entry to `TRANSPARENCY_SCORECARD.md` (see suggested entry below).
4. Record any follow-ups in `CODEX_TODO_REPLACEMENT_COMPLETE.md` (already included).

**Prepared by:** LUKHAS Autonomous Infrastructure
**Date:** 2025-10-28
