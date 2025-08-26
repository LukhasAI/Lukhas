## Summary
Promote `core/<MODULE>` from candidate → lukhas. One module only.

## Checks
- [ ] Candidate smoke: `tests/smoke/test_<MODULE>_candidate_smoke.py` passes
- [ ] Lukhas smoke: `tests/smoke/test_<MODULE>_lukhas_smoke.py` passes
- [ ] Imports updated only in promoted files (core.* → lukhas.core.*)
- [ ] TEMP shim added? (Y/N) — if Y, list dependents
- [ ] ops/matriz.yaml lane updated
- [ ] lanes/<MODULE>/README.md created/updated
- [ ] MATRIZ_PLAN.md updated (Promotion Decisions)

## Notes
- No deletion under candidate/.
- No structural changes beyond the module copy.
