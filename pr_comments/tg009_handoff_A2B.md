## HANDOFF A→B: Claude→GPT5 (Integration test + CI smoke)

**Artifact**: `scripts/batch_next.sh` with `detect_and_handle_noop()` guard (lines 70-113)

**Status**: ✅ Guard logic implemented, bash syntax valid, audit log configured

**Required for Agent B (GPT-5 Pro)**:
1. **Integration Test**: Create `services/registry/tests/test_noop_guard_integration.py`
   - Initialize temp git repo
   - Create file, commit seed
   - Stage chmod-only change (`chmod +x file.py`)
   - Invoke guard logic (extract function or simulate)
   - Assert: `.done` file appended, no new commit, audit log updated

2. **CI Smoke Job**: Add job to `.github/workflows/t4-pr-ci.yml`
   - Job name: `batch-noop-smoke` (already stubbed, needs enhancement)
   - Create temp repo with chmod-only scenario
   - Run guard detection logic
   - Assert guard prevents commit

3. **Edge Case Testing**: Document edge cases in test
   - Content + mode change → should proceed with commit
   - Mode-only → should block and log
   - No staged changes → should exit gracefully

**Guard Behavior** (for reference):
```bash
1. No staged changes → exit with NO_STAGED_CHANGES
2. Chmod-only → revert, log to docs/audits/noop_guard.log, mark done, exit 0
3. Content + mode → proceed with commit
4. Content-only → proceed with commit
```

**Deliverable**:
- `tests/integration/test_noop_guard_integration.py` (or in services/registry/tests/)
- Enhanced CI job in `t4-pr-ci.yml` (batch-noop-smoke)
- Edge case documentation in test docstring

**Validation Commands**:
```bash
# Syntax check (already passing)
bash -n scripts/batch_next.sh

# Integration test (after B creates it)
pytest tests/integration/test_noop_guard_integration.py -v
```

**Next**: `HANDOFF B→C` after integration test + CI smoke complete
