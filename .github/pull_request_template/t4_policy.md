## Summary
Replace T4 Unused Imports policy with T4 Platform (structured annotations + Intent Registry).

## Changes
- docs/policies/T4_UNUSED_IMPORTS_PLATFORM.md (new canonical policy)
- Updated tools/ci/unused_imports.py (annotator)
- Updated tools/ci/check_unused_imports_todo.py (validator)
- New tools/ci/intent_registry.py
- GitHub Action: .github/workflows/t4-policy-validation.yml
- Migration script: scripts/replace_t4_policy.sh

## How to test
1. Run: `python3 tools/ci/check_unused_imports_todo.py --paths lukhas core api consciousness memory identity MATRIZ --json-only`
2. Dry-run: `python3 tools/ci/unused_imports.py --paths lukhas MATRIZ --dry-run`
3. Ingest logs: `python3 tools/ci/intent_registry.py`

## Rollback plan
- Restore files from `docs/backup_t4/` which were moved.

## Notes
This change keeps backwards-compatibility: the annotator will accept old free-text tags but will prefer structured JSON. Start the validator in dry-run for 2–4 weeks to review quality issues, then enable strict CI enforcement.
