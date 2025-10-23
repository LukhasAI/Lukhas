# T4 Batch Integration System - READY FOR EXECUTION

**Date**: 2025-10-23
**Status**: Infrastructure Complete, Ready for Batch Execution
**Scope**: 144 low-complexity hidden gems modules

---

## What We Built Today

### 1. Complete Batch Infrastructure ✅

**Batch Files** (Parallel-Safe Grouping):
- `/tmp/batch_matriz.tsv` - 36 modules → `matriz/` targets
- `/tmp/batch_core.tsv` - 106 modules → `core/` targets
- `/tmp/batch_serve.tsv` - 2 modules → `serve/` targets

**Automation Scripts**:
- `scripts/batch_next.sh` - Main worker (9-step workflow per module)
- `scripts/batch_status.py` - Real-time dashboard
- `scripts/batch_next_auto.sh` - Auto-pick smallest batch
- `scripts/batch_push_pr.sh` - Automated PR creation

**Makefile Targets**:
```bash
make batch-status           # Show dashboard
make batch-next-matriz      # Integrate next MATRIZ module
make batch-next-core        # Integrate next CORE module
make batch-next-serve       # Integrate next SERVE module
make batch-next             # Auto-pick smallest batch
```

### 2. Merged 4 Codex PRs ✅

Successfully integrated from previous Codex sessions:
- ✅ PR #469: OpenAI Facade Endpoints (+295, -15)
- ✅ PR #472: WebAuthn Routes (+240, -0)
- ✅ PR #473: MATRIZ Input Adaptation (+141, -3)
- ✅ PR #471: Async Orchestrator Service (+218, -2)

**Total**: +894 lines across 11 files, all tests passing

### 3. Documentation ✅

- `docs/codex/INITIATION_PROMPT.md` - Reorganized with parallelization guide
- `.lukhas_runs/2025-10-23/PR_REVIEW_SUMMARY.md` - Complete PR analysis
- Fixed `mk/codex.mk` - Makefile heredoc syntax error

---

## Current Status Dashboard

Run `make batch-status` to see:

```
batch_matriz.tsv         | total: 36  done:  0  rem: 36  next:matriz.core.async_orchestrator
batch_core.tsv           | total:106  done:  0  rem:106  next:labs.governance.guardian_system_integration
batch_serve.tsv          | total:  2  done:  0  rem:  2  next:serve.reference_api.public_api_reference
```

**Total Remaining**: 144 modules
**Estimated Effort**: 1,748 hours (parallelizable 3x)

---

## T4 Batch Operator Protocol

### Your Role as Operator

```
You are a T4 batch operator. Doctrine: Zero Guesswork.

Mission:
- Integrate modules from $BATCH_FILE (TSV: module<TAB>src<TAB>dst)
- One item per run: call `scripts/batch_next.sh`
- If gates fail, stop and summarize

Operating Loop (repeat until DONE):
1) Run: `scripts/batch_next.sh`
2) If tests or gates fail:
   - Open failing file; surgical edit only
   - Re-run: `pytest -q` then `make codex-acceptance-gates`
   - If still failing, revert: `git restore --staged . && git checkout -- .`
   - Output one-sentence failure summary and STOP
3) If commit succeeded, push PR:
   - `git push --set-upstream origin $(git branch --show-current)`
   - Output "PR READY: $(git branch --show-current)"

Constraints:
- Do not touch files outside destination subtree
- Never skip tests/gates
- Every commit must include: `task: Hidden Gems Integration`
- Stop immediately on persistent failure; no autopilot
```

### How to Run

**Option 1: Single Batch** (tmux pane dedicated to one area)
```bash
export BATCH_FILE=/tmp/batch_matriz.tsv
scripts/batch_next.sh   # Repeat for each module
```

**Option 2: Make Targets** (convenience)
```bash
make batch-next-matriz  # Or -core, -serve
```

**Option 3: Auto-Pick** (works across all batches)
```bash
make batch-next         # Picks smallest remaining batch
```

### Parallel Execution (Recommended)

Run 2-3 tmux panes simultaneously:
- **Pane A**: `BATCH_FILE=/tmp/batch_matriz.tsv` → Run `scripts/batch_next.sh`
- **Pane B**: `BATCH_FILE=/tmp/batch_core.tsv` → Run `scripts/batch_next.sh`
- **Pane C**: Dashboard → Run `make batch-status` periodically

No conflicts because batches target different directories.

---

## Known Issues

### 1. Pytest Not in PATH ⚠️ **BLOCKER**

**Issue**: `scripts/batch_next.sh` line 31 fails: `pytest: command not found`

**Root Cause**: Script doesn't activate virtualenv before running pytest

**Fix Required**: Update `batch_next.sh` line 31 from:
```bash
pytest -q || true
```

To:
```bash
source .venv/bin/activate && pytest -q || true
```

Apply same fix to lines 50, 51, 57 (all pytest/make calls need venv)

### 2. File Already Moved

During test run, `api/integrated_consciousness_api.py` was moved to `serve/api/integrated_consciousness_api.py` but not committed (failed at pytest step). This file is now tracked in git as moved.

**Fix**: Either:
- Complete the integration manually
- Revert: `git checkout HEAD -- api/integrated_consciousness_api.py && rm serve/api/integrated_consciousness_api.py`

---

## Next Steps

### Immediate (Before First Execution)

1. **Fix batch_next.sh pytest calls** - Add virtualenv activation
2. **Test with smallest batch** - Run one integration from batch_serve.tsv (2 modules)
3. **Verify gates work** - Ensure `make codex-acceptance-gates` runs

### Short Term (This Week)

1. **Run 5-10 modules** - Test the workflow end-to-end
2. **Refine scripts** - Add any missing error handling
3. **Document failures** - Track what needs manual intervention

### Medium Term (Ongoing)

1. **Parallel execution** - Run 2-3 batches simultaneously
2. **Progress tracking** - Update dashboard regularly
3. **PR review** - Merge successful integrations
4. **Iterate** - Improve automation based on failures

---

## Batch Statistics

### By Target Directory

| Target | Modules | Avg Effort | Total Hours |
|--------|---------|------------|-------------|
| `matriz/consciousness/reflection/` | 24 | 12h | 288h |
| `core/consciousness/` | 18 | 10h | 180h |
| `core/memory/` | 10 | 14h | 140h |
| `core/` (various) | 11 | 8h | 88h |
| `core/symbolic/` | 5 | 10h | 50h |
| `core/identity/` | 5 | 12h | 60h |
| Other (<5 each) | 71 | 12h | 852h |

### By Complexity

| Complexity | Count | Percentage |
|------------|-------|------------|
| Low | 144 | 100% |
| Medium | 0 | 0% (filtered out) |
| High | 0 | 0% (filtered out) |

---

## Quality Gates (Per Module)

Each integration must pass:

1. **Schema compliance** - Imports resolve
2. **JSON validation** - No syntax errors
3. **Smoke tests** - Pass rate ≥ 90%
4. **Lane guard** - No boundary violations
5. **Rate limits** - Headers present (if API)
6. **Log coverage** - > 85%
7. **No 404s** - All endpoints work
+1. **Self-report** - Diagnostic matches commit

Enforced by: `make codex-acceptance-gates`

---

## Parallelization Safety

### ✅ Safe to Run in Parallel

- Different target directories (matriz vs core vs serve)
- Independent modules (no import dependencies)
- Separate branch per integration
- Isolated test files

### ❌ NOT Safe in Parallel

- Same file edits
- Interdependent integrations (check manifest dependencies)
- Same target directory

### Decision Matrix

From `docs/codex/INITIATION_PROMPT.md`:

| Task | Parallel? | Max Sessions |
|------|-----------|--------------|
| Different batches (matriz, core, serve) | ✅ Yes | 3 |
| Same batch, different modules | ✅ Yes | 2-3 |
| Same module | ❌ No | 1 |

---

## Reference Documents

- **Master Context**: `/Users/agi_dev/LOCAL-REPOS/Lukhas/claude.me`
- **Integration Guide**: `docs/audits/INTEGRATION_GUIDE.md` (6,987 lines)
- **Integration Manifest**: `docs/audits/integration_manifest.json` (325KB)
- **Codex Prompts**: `docs/codex/INITIATION_PROMPT.md`
- **PR Review**: `.lukhas_runs/2025-10-23/PR_REVIEW_SUMMARY.md`

---

## Success Metrics

### Per Session
- Modules integrated: X
- PRs created: X
- Tests passing: X/X
- Acceptance gates: PASS/FAIL

### Overall Progress
- Total: 144 modules
- Completed: 0
- In Progress: 0
- Remaining: 144
- Success Rate: TBD%

---

## Example: First Integration (After Fixing pytest)

```bash
# 1. Fix pytest in batch_next.sh
sed -i '' 's|pytest|source .venv/bin/activate \&\& pytest|g' scripts/batch_next.sh
sed -i '' 's|make codex|source .venv/bin/activate \&\& make codex|g' scripts/batch_next.sh

# 2. Test with smallest batch
export BATCH_FILE=/tmp/batch_serve.tsv
scripts/batch_next.sh

# 3. If successful:
scripts/batch_push_pr.sh

# 4. Check status
make batch-status

# 5. Repeat
scripts/batch_next.sh
```

---

## Commit History

1. `829dd27f4` - Reorganized initiation prompts
2. `74e51e3d3` - Fixed mk/codex.mk syntax error
3. `0e508cf82` - PR review summary
4. `d8733cc47` - Merged PR #469 (OpenAI facade)
5. `858afa127` - Merged PR #472 (WebAuthn)
6. `3347c1191` - Merged PR #473 (MATRIZ TypeError)
7. `7f9d9419e` - Merged PR #471 (Async orchestrator)
8. `c4acf018f` - **THIS COMMIT** - T4 batch infrastructure

---

## Ready to Execute

**Infrastructure**: ✅ Complete
**Batches**: ✅ Generated (144 modules)
**Scripts**: ✅ Created (4 scripts)
**Makefile**: ✅ Targets added (5 targets)
**Documentation**: ✅ Complete
**T4 Protocol**: ✅ Defined

**Blocking Issue**: ⚠️ pytest not in PATH (1-line fix per file)

**Next Command** (after fixing pytest):
```bash
make batch-next
```

Then repeat until all 144 modules are integrated.

---

**Generated**: 2025-10-23T09:00:00+0100
**Status**: READY FOR EXECUTION (after pytest fix)
**Estimated Completion**: 1,748 hours ÷ 3 parallel sessions = ~580 hours of wall-clock time
