# JULES Agent Instructions

## Main Entry Point
**File**: `docs/audits/JULES_RUNBOOK.md` (Complete technical runbook)
**Quick Start**: This file (minimal instructions)

## Your Mission
1. **TODO[T4-AUTOFIX] Resolution**: Fix 3 items in `tools/dev/t4_test_validation.py`
2. **Test Generation**: Create tests for `lukhas/` and `serve/` modules
3. **Surgical Code Fixes**: Apply safe Ruff/MyPy fixes (≤20 lines per file)

## Priority Queue (Start Here)

### ✅ COMPLETED: TODO[T4-AUTOFIX] Items (PR #100)
1. ✅ `tools/dev/t4_test_validation.py:10` - Use list comprehension (DONE)
2. ✅ `tools/dev/t4_test_validation.py:16` - Use pathlib.Path (DONE)  
3. ✅ `tools/dev/t4_test_validation.py:21` - Remove unused variable (DONE)
4. ✅ `tools/scripts/system_status_comprehensive_report.py` - Fixed syntax errors (DONE)
5. ✅ `archive/.../fold_lineage_tracker.py` - Added missing logger (DONE)

### 🟡 SAFE PARALLEL WORK: Test Creation Only
**Note**: Wave C files (`candidate/aka_qualia/`) under active development by parallel Claude Code agent

**Safe Test Tasks for Jules**:
- Create missing tests for existing `lukhas/` modules
- Add unit tests for `lukhas/bridge/` components  
- Create integration tests for stable APIs
- Add smoke tests for existing functionality

### 🔵 IMPORT FIXES: Batch Processing
See `docs/project_status/JULES_TODO_BATCHES.md` - BATCH 1 (15 items)

## Quality Gates (Must Pass)
```bash
make jules-gate
# Runs: ruff check --fix . && ruff format . && mypy . && pytest
```

## Working Constraints
- **Branch**: `feat/jules-tests-and-autofix`
- **Edit Only**: `tests/`, `docs/`, `lukhas/`, `serve/` 
- **⚠️ AVOID**: `candidate/aka_qualia/` (Wave C parallel development)
- **Don't Touch**: `enterprise/`, `MATRIZ/`
- **Patch Budget**: ≤20 lines per file
- **No Behavior Changes**: Only safe fixes

## Environment Setup
```bash
source .venv/bin/activate
make test           # 85% pass rate minimum
make lint           # Code quality check
```

## Key Commands
- `make jules-gate` - Run all quality checks
- `pytest -m "smoke"` - Run smoke tests only
- `ruff check --fix .` - Auto-fix safe issues

## Success Criteria
- All 3 TODO[T4-AUTOFIX] items resolved
- Coverage +10% on lukhas/ modules
- Zero lane violations (import-linter passes)
- All quality gates green

## Documentation References
- **Complete Guide**: `docs/audits/JULES_RUNBOOK.md`
- **TODO Batches**: `docs/project_status/JULES_TODO_BATCHES.md`
- **Architecture**: `CLAUDE.md` (Trinity Framework: ⚛️🧠🛡️)

---
*Start with the 3 TODO[T4-AUTOFIX] items for immediate impact*