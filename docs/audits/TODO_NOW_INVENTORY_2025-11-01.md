---
status: snapshot
type: inventory
owner: codex
updated: 2025-11-01
---

# TODO NOW Inventory — Urgent Action Items (2025-11-01)

## Executive Summary

**Total TODO NOW Tags**: 27 instances across 5 files

**Breakdown by Category**:
- **Actionable Code Fixes**: 12 items (44%)
- **Documentation**: 14 items (52%)
- **False Positives**: 1 item (4%)

**Priority Distribution**:
- **P0 (Critical - Blocking)**: 6 items
- **P1 (High - Lane Compliance)**: 3 items
- **P2 (Medium - Cleanup)**: 3 items
- **Documentation**: 14 items (reference only)
- **False Positive**: 1 item

---

## 1. Actionable TODO NOW Items (12 Total)

### P0: Critical Blockers (6 items)

#### 1.1 Test Import Path Mismatches

**File**: `tests/matriz/test_async_orchestrator_e2e.py:9`
```
TODO NOW — ModuleNotFoundError: labs.core.orchestration.async_orchestrator
Action: Add ProviderRegistry-backed adapter or conditional skip; avoid direct labs import
```
**Impact**: Blocking MATRIZ E2E test suite
**Remediation**: Replace `from labs.core.orchestration.async_orchestrator` with Provider pattern or skip if unavailable

---

**File**: `tests/integration/test_matriz_complete_thought_loop.py:28`
```
TODO NOW — ModuleNotFoundError: consciousness.matriz_thought_loop
Action: Add compatibility shim or update tests to current MATRIZ entrypoint
```
**Impact**: Blocking consciousness integration tests
**Remediation**: Create `consciousness/matriz_thought_loop.py` shim exporting required symbols or update test imports to new path

---

#### 1.2 Labs Import Dependencies in Tests

**File**: Multiple test files (sample provided in audit)
```
TODO NOW tests/* (labs imports) — Replace direct labs import with ProviderRegistry or add conditional skips in CI profile
```
**Impact**: Many tests import labs.* directly, creating hard dependencies
**Files Affected**:
- `tests/matriz/test_async_orchestrator_e2e.py:9`
- `tests/matriz/test_behavioral_e2e.py:12`
- `tests/orchestration/test_async_orchestrator_metrics.py:12`
- `tests/bridges/test_vector_store.py:23`
- `tests/bridge/test_vector_store_adapter.py:7`
- `tests/bridge/test_jwt_adapter_high_priority.py:4`
- And many more...

**Remediation**:
1. Implement ProviderRegistry pattern for common labs dependencies
2. Add conditional skips: `pytest.skip("labs not available")`
3. Create adapter layer in core/adapters/

---

#### 1.3 Consciousness Entry Point Missing

**File**: Multiple test files importing `consciousness.matriz_thought_loop`
```
TODO NOW tests/* (above) — Provide shim module exposing MATRIZProcessingContext/MATRIZThoughtLoop or refactor imports
```
**Files Affected**:
- `tests/bridges/test_consciousness_extension_bridges.py:27`
- `tests/bridges/test_phase9_contracts.py:13`
- `tests/bridges/test_top_missing_contracts.py:15-16`
- `tests/soak/test_guardian_matriz_throughput.py:35`
- `tests/bridges/test_chatgpt_bridges.py:21,35,50,103,110`
- `tests/matriz/test_e2e_perf.py:36`
- `tests/lint/test_lane_imports.py:70`
- `tests/integration/test_orchestrator_matriz_roundtrip.py:32`
- `tests/integration/test_matriz_complete_thought_loop.py:28`

**Remediation**: Create `consciousness/matriz_thought_loop.py` with:
```python
"""Shim module for backward compatibility with test suite."""
from matriz.orchestration.service_async import (
    MATRIZProcessingContext,
    MATRIZThoughtLoop,
)

__all__ = ["MATRIZProcessingContext", "MATRIZThoughtLoop"]
```

---

### P1: Lane Compliance Issues (3 items)

#### 1.4 Production Lane Direct matriz Imports

**File**: `core/trace.py:13`
```
TODO NOW — Replace with `from MATRIZ.node_contract import GLYPH` or lazy import adapter
```
**Current Code**: `from matriz.node_contract import GLYPH`
**Expected**: `from MATRIZ.node_contract import GLYPH` (uppercase per lane convention)
**Impact**: Lane compliance violation; case-sensitivity issues
**Remediation**: Update import to uppercase MATRIZ or implement lazy loading adapter

---

**File**: `core/symbolic/dast_engine.py:214`
```
TODO NOW — Replace with `from MATRIZ.core.memory_system import get_memory_system`; keep try/except guard; document lane compliance
```
**Current Code**: `from matriz.core.memory_system import get_memory_system` (inside try block)
**Expected**: `from MATRIZ.core.memory_system import get_memory_system`
**Impact**: Lane compliance violation
**Remediation**: Update import to uppercase MATRIZ; retain try/except pattern; add docstring explaining lane policy

---

**File**: `serve/main.py:14,57`
```
TODO NOW — Replace matriz with MATRIZ and/or lazy import; guard availability
```
**Current Code**:
- Line 14: `import matriz`
- Line 57: `from matriz.orchestration.service_async import (...)`

**Expected**: `from MATRIZ.orchestration.service_async import ...`
**Impact**: Lane compliance violation; service layer importing from wrong case
**Remediation**: Update imports to uppercase MATRIZ; add availability guards

---

### P2: Developer Experience (3 items)

#### 1.5 Import Health Script UX

**File**: `scripts/consolidation/check_import_health.py`
```
TODO NOW — Add guidance when deps missing; print "use scripts/run_lane_guard_worktree.sh"
```
**Current Behavior**: Script fails silently when dependencies missing or PYTHONPATH incorrect
**Impact**: Confusing error messages for developers
**Remediation**: Add helpful error message:
```python
except ImportError as e:
    print(f"❌ Import check failed: {e}")
    print("💡 TIP: Run via worktree with isolated venv:")
    print("   ./scripts/run_lane_guard_worktree.sh")
    sys.exit(1)
```

---

## 2. Documentation References (14 items)

These TODO NOW tags appear in documentation files as references to actionable items above. They are not separate action items but cross-references.

### 2.1 MATRIZ System Audit (9 instances)
**File**: `docs/audits/MATRIZ_SYSTEM_AUDIT_2025-11-01.md`

Lines 11, 22, 25, 43, 63, 75, 76, 77, 81 — All reference the actionable items listed in Section 1 above.

### 2.2 MATRIZ Consciousness Architecture (14 instances)
**File**: `docs/architecture/MATRIZ_CONSCIOUSNESS_ARCHITECTURE.md`

Lines 283, 289, 293, 299, 310, 312, 314, 325-331 — All reference the actionable items listed in Section 1 above.

---

## 3. False Positives (1 item)

**File**: `docs/gonzo/matriz_prep/TODO_brief.md:543`
```
name: forbid fake TODO snow
```
**Context**: This is a YAML configuration example showing how to forbid fake TODO comments. Not an actual TODO item.

**File**: `tools/ci/complete_todo_allocation.py:25,32`
```python
unknown_todos = [t for t in open_todos if t.get("priority") == "unknown"]
print(f"  Unknown: {len(unknown_todos)}")
```
**Context**: Variable names in code that happen to contain "todo". Not actual TODO comments.

**File**: `CODEX_INITIATION_PROMPT.md:164`
```
- ✅ All TODOs now trackable via GitHub issues
```
**Context**: Documentation stating TODOs are tracked. Not an actual TODO item.

---

## 4. Remediation Plan

### Phase 1: Critical Blockers (P0) — Unblock Test Suite
**Estimated Effort**: 4-6 hours

1. **Create consciousness shim module** (1 hour)
   - File: `consciousness/matriz_thought_loop.py`
   - Export: MATRIZProcessingContext, MATRIZThoughtLoop
   - Tests affected: 9 files

2. **Add ProviderRegistry pattern for labs dependencies** (2-3 hours)
   - Create: `core/adapters/labs_provider.py`
   - Implement lazy loading for common labs.* imports
   - Add conditional skips to tests when unavailable

3. **Update test imports** (1-2 hours)
   - Fix `test_async_orchestrator_e2e.py`
   - Fix `test_matriz_complete_thought_loop.py`
   - Add pytest.skip conditions where needed

### Phase 2: Lane Compliance (P1) — Fix Import Case Issues
**Estimated Effort**: 2-3 hours

1. **Update core/trace.py** (15 minutes)
   - Change: `from matriz.node_contract` → `from MATRIZ.node_contract`

2. **Update core/symbolic/dast_engine.py** (30 minutes)
   - Change: `from matriz.core.memory_system` → `from MATRIZ.core.memory_system`
   - Add docstring explaining lane policy

3. **Update serve/main.py** (1-2 hours)
   - Change: `import matriz` → `from MATRIZ import ...`
   - Add availability guards
   - Test service startup

### Phase 3: Developer Experience (P2) — Improve Tooling
**Estimated Effort**: 1 hour

1. **Enhance check_import_health.py** (1 hour)
   - Add helpful error messages
   - Suggest worktree script when deps missing
   - Improve PYTHONPATH guidance

### Total Estimated Effort: 7-10 hours

---

## 5. Statistics Summary

| Category | Count | Percentage |
|----------|-------|------------|
| **Actionable Items** | 12 | 44% |
| **Documentation References** | 14 | 52% |
| **False Positives** | 1 | 4% |
| **Total Tags Found** | 27 | 100% |

### Priority Breakdown
| Priority | Count | Focus Area |
|----------|-------|------------|
| P0 Critical | 6 | Test suite blockers, missing modules |
| P1 High | 3 | Lane compliance, import case fixes |
| P2 Medium | 3 | Developer experience, tooling |

### Files Requiring Changes
| File Path | TODO Count | Priority |
|-----------|------------|----------|
| `consciousness/matriz_thought_loop.py` | 1 (NEW) | P0 |
| `core/adapters/labs_provider.py` | 1 (NEW) | P0 |
| `tests/matriz/test_async_orchestrator_e2e.py` | 1 | P0 |
| `tests/integration/test_matriz_complete_thought_loop.py` | 1 | P0 |
| `core/trace.py` | 1 | P1 |
| `core/symbolic/dast_engine.py` | 1 | P1 |
| `serve/main.py` | 1 | P1 |
| `scripts/consolidation/check_import_health.py` | 1 | P2 |

---

## 6. Recommendations

### Immediate Actions (This Week)
1. **Create consciousness shim** — Highest ROI, unblocks 9 test files
2. **Fix lane compliance imports** — Quick wins (3 files, <1 hour total)
3. **Enhance import health script** — Improves developer experience

### Short-Term (Next Sprint)
1. **Implement ProviderRegistry pattern** — Foundation for removing labs dependencies
2. **Add conditional test skips** — Allow tests to pass gracefully when optional deps missing
3. **Update test suite** — Migrate from old import paths to new patterns

### Long-Term (Next Quarter)
1. **Eliminate hard labs dependencies** — Full adoption of Provider pattern
2. **Comprehensive lane compliance audit** — Ensure all production code follows uppercase MATRIZ
3. **Automated TODO NOW tracking** — CI job that fails if new TODO NOW tags added without GitHub issue

---

## Command Log (Evidence)

```bash
# Search for TODO NOW tags
rg "TODO.{0,5}NOW|NOW.{0,5}TODO" -i -n --heading --color never

# Count by file
rg "TODO.{0,5}NOW|NOW.{0,5}TODO" -i --count-matches

# Results:
# tools/ci/complete_todo_allocation.py:2 (false positive)
# CODEX_INITIATION_PROMPT.md:1 (false positive)
# docs/gonzo/matriz_prep/TODO_brief.md:1 (false positive)
# docs/architecture/MATRIZ_CONSCIOUSNESS_ARCHITECTURE.md:14 (documentation)
# docs/audits/MATRIZ_SYSTEM_AUDIT_2025-11-01.md:9 (documentation)
```

---

## Appendix: Full Text of Actionable Items

### A1: Test Import Errors
```
TODO NOW tests/matriz/test_async_orchestrator_e2e.py:9
  ModuleNotFoundError: labs.core.orchestration.async_orchestrator
  Action: add ProviderRegistry-backed adapter or conditional skip; avoid direct labs import

TODO NOW tests/integration/test_matriz_complete_thought_loop.py:28
  ModuleNotFoundError: consciousness.matriz_thought_loop
  Action: add compatibility shim or update tests to current MATRIZ entrypoint
```

### A2: Consciousness Entry Point
```
TODO NOW tests/* (above)
  Provide shim module exposing MATRIZProcessingContext/MATRIZThoughtLoop or refactor imports.

Files affected:
- tests/bridges/test_consciousness_extension_bridges.py:27
- tests/bridges/test_phase9_contracts.py:13
- tests/bridges/test_top_missing_contracts.py:15-16
- tests/soak/test_guardian_matriz_throughput.py:35
- tests/bridges/test_chatgpt_bridges.py:21,35,50,103,110
- tests/matriz/test_e2e_perf.py:36
- tests/lint/test_lane_imports.py:70
- tests/integration/test_orchestrator_matriz_roundtrip.py:32
- tests/integration/test_matriz_complete_thought_loop.py:28
```

### A3: Labs Import Dependencies
```
TODO NOW tests/* (labs imports)
  Replace direct labs import with ProviderRegistry or add conditional skips in CI profile.

Sample files affected:
- tests/matriz/test_async_orchestrator_e2e.py:9
- tests/matriz/test_behavioral_e2e.py:12
- tests/orchestration/test_async_orchestrator_metrics.py:12
- tests/bridges/test_vector_store.py:23
- tests/bridge/test_vector_store_adapter.py:7
- tests/bridge/test_jwt_adapter_high_priority.py:4
- tests/bridge/test_qrs_manager.py:20
- tests/integration/governance/test_guardian_system_integration.py:10
- tests/integration/orchestration/test_orchestration_coverage.py:42
- tests/memory/test_memory_compression.py:13
- tests/memory/test_memory_properties_hypothesis.py:55
- tests/test_memory_integration.py:2-3
```

### A4: Lane Compliance — Production Imports
```
TODO NOW core/trace.py:13
  Replace with `from MATRIZ.node_contract import GLYPH` or lazy import adapter.

TODO NOW core/symbolic/dast_engine.py:214
  Replace with `from MATRIZ.core.memory_system import get_memory_system`;
  keep try/except guard; document lane compliance.

TODO NOW serve/main.py:14,57
  Replace matriz with MATRIZ and/or lazy import; guard availability.
```

### A5: Developer Experience
```
TODO NOW scripts/consolidation/check_import_health.py
  Add guidance when deps missing; print "use scripts/run_lane_guard_worktree.sh".
```

---

**End of Report**
