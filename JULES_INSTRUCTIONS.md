# JULES Agent Instructions

## Main Entry Point
**File**: `docs/audits/JULES_RUNBOOK.md` (Complete technical runbook)
**Quick Start**: This file (minimal instructions)

## Your Mission
1. **Critical Test Coverage**: Create tests for `lukhas/` and `serve/` modules (serve/ has ZERO tests)
2. **TODO[T4-AUTOFIX] Resolution**: Fix remaining syntax issues in system status report
3. **Surgical Code Fixes**: Apply safe Ruff/MyPy fixes (≤20 lines per file)

## Priority Queue (Start Here)

### ✅ COMPLETED: TODO[T4-AUTOFIX] Items (PRs #100 & #101)
1. ✅ `tools/dev/t4_test_validation.py` - All 3 items fixed (DONE)
2. ✅ `tools/scripts/system_status_comprehensive_report.py` - Syntax errors fixed (DONE)
3. ✅ `archive/.../fold_lineage_tracker.py` - Added missing logger (DONE)
4. ✅ `tests/bridge/test_unified_openai_client.py` - Comprehensive test suite added (DONE)

### 🚨 HIGH PRIORITY: serve/ API Test Coverage (ZERO TESTS)
**Critical Gap**: 19 `serve/` modules have no test coverage

**Immediate Test Tasks for Jules**:
1. **serve/ APIs** (highest impact - complete gap):
   - `tests/serve/test_main.py` - Main FastAPI application
   - `tests/serve/test_consciousness_api.py` - Consciousness endpoints
   - `tests/serve/test_identity_api.py` - Identity/auth endpoints
   - `tests/serve/test_guardian_api.py` - Guardian security endpoints
   - `tests/serve/test_routes.py` - General route testing

2. **lukhas/bridge/** (missing tests):
   - `tests/bridge/test_bridge_wrapper.py` - Bridge wrapper component
   - `tests/bridge/test_anthropic_wrapper.py` - Anthropic API wrapper

3. **lukhas/core/** and **lukhas/matriz/**:
   - `tests/core/test_distributed_tracing.py` - Tracing system
   - `tests/matriz/test_runtime_policy.py` - Policy runtime

### 🔴 REMAINING: TODO[T4-AUTOFIX] Item
**Location**: `tools/scripts/system_status_comprehensive_report.py:1`
- Fix extensive syntax errors throughout file
- Missing colons, malformed f-strings, broken list comprehensions
- Apply surgical fixes (≤20 lines per section)

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
- serve/ directory has basic test coverage (5+ test files minimum)
- lukhas/bridge/ missing components tested
- Final TODO[T4-AUTOFIX] item resolved
- Coverage +15% on stable lukhas/ and serve/ modules
- Zero lane violations (import-linter passes)
- All quality gates green

## Documentation References
- **Complete Guide**: `docs/audits/JULES_RUNBOOK.md`
- **TODO Batches**: `docs/project_status/JULES_TODO_BATCHES.md`
- **Architecture**: `CLAUDE.md` (Trinity Framework: ⚛️🧠🛡️)

---
*Start with serve/ API tests for maximum impact - 19 modules with zero coverage*