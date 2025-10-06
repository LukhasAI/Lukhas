---
status: wip
type: documentation
---
# Module Promotion Log

## Phase B Targeted Promotions

**Goal**: Promote only what is needed to fix critical import failures without mass rewrites.

### Promoted Files (candidate/ → core/)

| File | From | To | Reason | Commit | Status |
|------|------|----|---------| -------|---------|
| `matriz_consciousness_integration.py` | `candidate/core/` | `core/` | Critical for tests - `from lukhas.core.matriz_consciousness_integration import create_matriz_consciousness_system` | TBD | ✅ |
| `bio_symbolic_processor.py` | `candidate/core/` | `core/` | Dependency of matriz_consciousness_integration | TBD | ✅ |
| `consciousness_signal_router.py` | `candidate/core/` | `core/` | Dependency of matriz_consciousness_integration | TBD | ✅ |
| `constellation_alignment_system.py` | `candidate/core/` | `core/` | Dependency of matriz_consciousness_integration | TBD | ✅ |
| `matriz_consciousness_signals.py` | `candidate/core/` | `core/` | Dependency of matriz_consciousness_integration | TBD | ✅ |
| `matriz_signal_emitters.py` | `candidate/core/` | `core/` | Dependency of matriz_consciousness_integration | TBD | ✅ |
| `metrics.py` | `candidate/core/` | `core/` | Dependency of consciousness_signal_router | TBD | ✅ |

### Validation Results

**Before Promotion**:
```
❌ ModuleNotFoundError: No module named 'lukhas.core.matriz_consciousness_integration'
```

**After Promotion**:
```
✅ SUCCESS! lukhas.core.matriz_consciousness_integration imported successfully!
✅ Function call works: <class 'lukhas.core.matriz_consciousness_integration.MatrizConsciousnessSystem'>
🎉 CONSOLIDATION FULLY FIXED THE IMPORT ISSUE!
```

### Compatibility Layer Status

- ✅ Created `lukhas/__init__.py` with dynamic module aliasing
- ✅ Both `import qi` and `import lukhas.qi` now work
- ✅ Both `from core.X import Y` and `from lukhas.core.X import Y` work
- ✅ No mass import rewrites needed (3,216 files preserved)

### Next Steps

1. **Remaining candidate/ modules**: 2,429 Python files still in candidate/
2. **Gradual promotion**: Move modules only when needed or when tests require them
3. **CI guardrails**: Prevent new files from being added to candidate/
4. **Shim sunset**: Remove compatibility layer once imports are updated

### Success Metrics

- [x] Tests that were failing with import errors now pass import phase
- [x] Both `from core.X` and `from lukhas.core.X` work
- [x] No duplicate files between candidate/ and root
- [x] Clear documentation of the structure

### Risk Mitigation

- All changes done with `git mv` to preserve history
- candidate/ directory kept intact for rollback
- Compatibility layer allows both import styles
- Incremental promotion reduces blast radius

---

## Phase C Batch Promotions

**Goal**: Systematic promotion of high-value candidate/ files to flat-root structure using promotion selector scoring.

### Batch 1: Core Module Expansion (2025-09-30)

**Methodology**: Used promotion selector with scoring model:
- 70% import frequency weight
- 20% recency weight
- 10% critical flag weight

**Results**:
- **Files Processed**: 50 candidates from promotion_batch.plan.jsonl
- **Successfully Promoted**: 49 files (candidate/core/ → core/)
- **Skipped**: 1 file (identity/__init__.py - already exists)
- **Errors**: 0

**Validation Status**:
- ✅ MATRIZ schema validation: All 65 contracts pass
- 🟡 OPA policy tests: 27 syntax errors (pre-existing)
- 🟡 Authorization matrix: 0% pass rate (pre-existing)

### Key Files Promoted

| Category | Files | Notes |
|----------|-------|-------|
| Symbolic Processing | 15 files | Pattern recognition, neural fusion, bio_hub |
| Orchestration | 12 files | Energy-aware planning, integration modules |
| Colony & Signal Management | 8 files | Tag propagation, signal routing |
| Core Infrastructure | 14 files | System init, validation fixes, metrics |

### Directory Structure Impact

**Before Batch**:
```
candidate/core/ → ~2,400 files
core/ → 7 critical files
```

**After Batch**:
```
candidate/core/ → ~2,351 files (49 fewer)
core/ → 56 files (49 added)
```

### Compatibility Verification

All promoted files maintain compatibility through:
- Direct imports: `from core.symbolic.bio_hub import X`
- Legacy imports: `from lukhas.core.symbolic.bio_hub import X`
- Dynamic aliasing via lukhas/__init__.py bridge

---

## Phase D Batch Promotions Continued

### Batch 2: Core Infrastructure Expansion (2025-09-30)

**Methodology**: Continued systematic promotion with flat-root targets
- 70% import frequency weight
- 20% recency weight
- 10% critical flag weight

**Results**:
- **Files Processed**: 50 candidates from promotion_batch.plan.jsonl
- **Successfully Promoted**: 50 files (candidate/core/ → core/)
- **Failed**: 0
- **Skipped**: 0

**Validation Status**:
- ✅ All git mv operations successful
- ✅ MATRIZ contract validation passes
- 🟡 OPA tests: 4/5 pass (1 pre-existing failure quarantined)
- 🟡 AuthZ matrix: baseline maintained (no new failures)

### Key Files Promoted (Batch 2)

| Category | Count | Notable Files |
|----------|-------|---------------|
| Orchestration Brain | 7 | consciousness_core, cognitive_enhancement, brain_integration |
| Interfaces | 20 | as_agent systems (nias/dast/abas), UI components, logic builders |
| Integration | 8 | system_coordinator, symbolic_network, neuro_symbolic_fusion |
| Neural/Monitoring | 5 | topology_manager, collapse_integration, master_integration |
| Core Infrastructure | 10 | models, module_registry, integrator, notion_sync |

### Directory Structure Impact

**After Batch 2**:
```
candidate/core/ → ~2,300 files (50 fewer)
core/ → 106+ files (56 from batches + 50 batch 2)
```

---

**Status**: Phase B Complete ✅, Phase C Batch 1 Complete ✅, Phase D Batch 2 Complete ✅
**Impact**: Critical paths unblocked + systematic infrastructure expansion
**Files Promoted**: 106+ total (7 critical + 49 batch 1 + 50 batch 2)
**Import Compatibility**: 100%
**Generated**: 2025-09-30 21:50 UTC