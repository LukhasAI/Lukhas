            # Integration Guide - Batch 1/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~146 hours
**Average Priority**: 84.5
**Complexity**: 20 low, 0 medium
**Strategic Focus**: Core Infrastructure & Orchestration (Pure Quick Wins)

**Doctrine**: **Zero Guesswork.** Every action must be based on explicit reads, verified state, or a defined pattern. No assumptions.

---

## Context Integrity Check (run once per session)

```bash
pwd; git status --porcelain || true
test "$(pwd)" = "/Users/agi_dev/LOCAL-REPOS/Lukhas" || { echo "wrong repo root"; exit 1; }
test -f docs/audits/INTEGRATION_MANIFEST_SUMMARY.md && test -f docs/audits/integration_manifest.json || { echo "missing integration context"; exit 1; }
# Optional: capture baseline smoke before any changes
make smoke | tee .baseline_smoke.txt || true
```

---

## Mission Trace (short-term objective memory)

When starting this batch, create/update `.codex_trace.json`:

```json
{
  "session_id": "<auto>",
  "task": "Hidden Gems Integration - Batch 1",
  "batch": 1,
  "total_modules": 20,
  "completed_modules": 0,
  "phase": "integration",
  "last_verified_state": "<timestamp>",
  "expected_artifacts": ["tests/integration/*", "docs/architecture/*", "moved modules with updated imports"]
}
```

---

## Acceptance Gates — Integration

1. Module relocated to target lane/path with history preserved (`git mv`)
2. Imports updated; `make lane-guard` and `make imports-guard` pass
3. New or adapted **integration tests** added and passing
4. Smoke suite unchanged or improved (≥ baseline; baseline recorded pre-changes)
5. Registry/exports wired; module discoverable by MATRIZ/core
6. Docs updated (architecture notes, registry references)
7. No circular imports or runtime import errors
8. Commit message matches T4 standard with diagnostic self-report

---

## Batch 1 Overview

### Complexity Distribution
- **Low Complexity**: 20 modules (2-12 hours each)
- **Medium Complexity**: 0 modules (6-12 hours each)

### Recommended Execution Strategy

**Pure Quick Wins Batch** - All modules are low complexity. Recommended approach:
1. Execute in sequential order (priority-ranked)
2. Batch commits every 5 modules for efficiency
3. Target: 4-5 modules per day
4. Expected completion: 4 work days (8h/day)

### Priority Range
- **Highest**: 92.5 (async_orchestrator)
- **Lowest**: 83.0 (dream_reflection_loop)

---

## Modules in This Batch (20 total)

Note:
- After any **UPDATE_IMPORTS** step, run `make lint && make format`.
- Typical registry/exports touchpoints: `matriz/core/__init__.py`, module registries/catalogs, and package `__init__.py` files.
- Use T4 commit messages with a short diagnostic body (gates, baseline deltas, registry updates).

### 1. matriz.core.async_orchestrator

**Priority Score**: 92.5 | **Quality Score**: 86.2 | **Complexity**: low (6h) | **Risk**: low

**Current**: `matriz/core/async_orchestrator.py`
**Target**: `matriz/core/async_orchestrator.py`

**Why**: 6 classes, already imports production code, high quality score

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read matriz/core/async_orchestrator.py and understand architecture (543 LOC, 6 classes, 10 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_async_orchestrator.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `matriz/core/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules; then run `make lint && make format`
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config; e.g., update `matriz/core/__init__.py`, registries/catalogs)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

Example commit:
```
feat(matriz): integrate async_orchestrator from labs

- Gates: lane-guard ✅ imports-guard ✅ smoke Δ0
- Registry: added to matriz.core registry catalog
- Tests: +1 integration
```

---

### 2. matriz.core.memory_system

**Priority Score**: 85.0 | **Quality Score**: 80.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `matriz/core/memory_system.py`
**Target**: `matriz/core/memory_system.py`

**Why**: 1034 LOC, 6 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read matriz/core/memory_system.py and understand architecture (1034 LOC, 6 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_memory_system.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `matriz/core/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules; then run `make lint && make format`
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config; e.g., update `matriz/core/__init__.py`, registries/catalogs)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.consciousness.unified.symbolic_bio_symbolic_orchestrator

**Priority Score**: 85.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py`
**Target**: `core/consciousness/symbolic_bio_symbolic_orchestrator.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py and understand architecture (697 LOC, 3 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_bio_symbolic_orchestrator.py
4. **MOVE**: git mv labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py core/consciousness/symbolic_bio_symbolic_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules; then run `make lint && make format`
6. **INTEGRATE**: Wire into appropriate system component (update `__init__.py`, add exports; update relevant package registry)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.consciousness.systems.unified_consciousness_engine

**Priority Score**: 85.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/consciousness/systems/unified_consciousness_engine.py`
**Target**: `core/consciousness/unified_consciousness_engine.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/systems/unified_consciousness_engine.py and understand architecture (748 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_unified_consciousness_engine.py
4. **MOVE**: git mv labs/consciousness/systems/unified_consciousness_engine.py core/consciousness/unified_consciousness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules; then run `make lint && make format`
6. **INTEGRATE**: Wire into appropriate system component (update `__init__.py`, add exports; update relevant package registry)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.consciousness.reflection.visionary_orchestrator

**Priority Score**: 85.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/visionary_orchestrator.py`
**Target**: `matriz/consciousness/reflection/visionary_orchestrator.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/visionary_orchestrator.py and understand architecture (783 LOC, 5 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_visionary_orchestrator.py
4. **MOVE**: git mv labs/consciousness/reflection/visionary_orchestrator.py matriz/consciousness/reflection/visionary_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules; then run `make lint && make format`
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config; e.g., update `matriz/core/__init__.py`, registries/catalogs)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.consciousness.reflection.master_orchestrator

**Priority Score**: 85.0 | **Quality Score**: 75.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/master_orchestrator.py`
**Target**: `matriz/consciousness/reflection/master_orchestrator.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/master_orchestrator.py and understand architecture (989 LOC, 6 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_master_orchestrator.py
4. **MOVE**: git mv labs/consciousness/reflection/master_orchestrator.py matriz/consciousness/reflection/master_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config; e.g., update `matriz/core/__init__.py`, registries/catalogs)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.consciousness.reflection.actor_system

**Priority Score**: 85.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/actor_system.py`
**Target**: `matriz/consciousness/reflection/actor_system.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/actor_system.py and understand architecture (628 LOC, 7 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_actor_system.py
4. **MOVE**: git mv labs/consciousness/reflection/actor_system.py matriz/consciousness/reflection/actor_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.consciousness.systems.integrator

**Priority Score**: 84.9 | **Quality Score**: 74.8 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/consciousness/systems/integrator.py`
**Target**: `core/consciousness/integrator.py`

**Why**: 11 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/systems/integrator.py and understand architecture (565 LOC, 11 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_integrator.py
4. **MOVE**: git mv labs/consciousness/systems/integrator.py core/consciousness/integrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update `__init__.py`, add exports; update relevant package registry)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.consciousness.reflection.colony_orchestrator

**Priority Score**: 84.8 | **Quality Score**: 74.4 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/colony_orchestrator.py`
**Target**: `matriz/consciousness/reflection/colony_orchestrator.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/colony_orchestrator.py and understand architecture (847 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_colony_orchestrator.py
4. **MOVE**: git mv labs/consciousness/reflection/colony_orchestrator.py matriz/consciousness/reflection/colony_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. labs.consciousness.reflection.openai_core_service

**Priority Score**: 84.6 | **Quality Score**: 73.9 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/openai_core_service.py`
**Target**: `matriz/consciousness/reflection/openai_core_service.py`

**Why**: 9 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/openai_core_service.py and understand architecture (760 LOC, 9 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_openai_core_service.py
4. **MOVE**: git mv labs/consciousness/reflection/openai_core_service.py matriz/consciousness/reflection/openai_core_service.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.consciousness.systems.advanced_consciousness_engine

**Priority Score**: 84.3 | **Quality Score**: 73.3 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/systems/advanced_consciousness_engine.py`
**Target**: `core/consciousness/advanced_consciousness_engine.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/systems/advanced_consciousness_engine.py and understand architecture (836 LOC, 5 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_advanced_consciousness_engine.py
4. **MOVE**: git mv labs/consciousness/systems/advanced_consciousness_engine.py core/consciousness/advanced_consciousness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate advanced_consciousness_engine from labs"

---

### 12. labs.consciousness.dream.reality_synthesis_engine

**Priority Score**: 84.0 | **Quality Score**: 72.5 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/consciousness/dream/reality_synthesis_engine.py`
**Target**: `matriz/consciousness/dream//reality_synthesis_engine.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/dream/reality_synthesis_engine.py and understand architecture (637 LOC, 5 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_reality_synthesis_engine.py
4. **MOVE**: git mv labs/consciousness/dream/reality_synthesis_engine.py matriz/consciousness/dream//reality_synthesis_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate reality_synthesis_engine from labs"

---

### 13. labs.consciousness.reflection.metalearningenhancementsystem

**Priority Score**: 84.0 | **Quality Score**: 72.5 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/metalearningenhancementsystem.py`
**Target**: `matriz/consciousness/reflection/metalearningenhancementsystem.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/metalearningenhancementsystem.py and understand architecture (983 LOC, 3 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_metalearningenhancementsystem.py
4. **MOVE**: git mv labs/consciousness/reflection/metalearningenhancementsystem.py matriz/consciousness/reflection/metalearningenhancementsystem.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate metalearningenhancementsystem from labs"

---

### 14. core.matriz_signal_emitters

**Priority Score**: 83.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `core/matriz_signal_emitters.py`
**Target**: `core/matriz_signal_emitters.py`

**Why**: 9 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/matriz_signal_emitters.py and understand architecture (576 LOC, 9 classes, 6 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_matriz_signal_emitters.py
4. **MOVE**: git mv core/matriz_signal_emitters.py core/matriz_signal_emitters.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate matriz_signal_emitters from labs"

---

### 15. labs.core.identity.matriz_consciousness_identity

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/core/identity/matriz_consciousness_identity.py`
**Target**: `core/identity/matriz_consciousness_identity.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/identity/matriz_consciousness_identity.py and understand architecture (948 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_matriz_consciousness_identity.py
4. **MOVE**: git mv labs/core/identity/matriz_consciousness_identity.py core/identity/matriz_consciousness_identity.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate matriz_consciousness_identity from labs"

---

### 16. labs.core.identity.test_consciousness_identity_patterns

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/core/identity/test_consciousness_identity_patterns.py`
**Target**: `core/identity/test_consciousness_identity_patterns.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/identity/test_consciousness_identity_patterns.py and understand architecture (753 LOC, 7 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_test_consciousness_identity_patterns.py
4. **MOVE**: git mv labs/core/identity/test_consciousness_identity_patterns.py core/identity/test_consciousness_identity_patterns.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate test_consciousness_identity_patterns from labs"

---

### 17. labs.core.identity.consciousness_namespace_isolation

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/core/identity/consciousness_namespace_isolation.py`
**Target**: `core/identity/consciousness_namespace_isolation.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/identity/consciousness_namespace_isolation.py and understand architecture (749 LOC, 7 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_consciousness_namespace_isolation.py
4. **MOVE**: git mv labs/core/identity/consciousness_namespace_isolation.py core/identity/consciousness_namespace_isolation.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate consciousness_namespace_isolation from labs"

---

### 18. labs.core.governance.matriz_consciousness_governance

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/core/governance/matriz_consciousness_governance.py`
**Target**: `core/governance/matriz_consciousness_governance.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/governance/matriz_consciousness_governance.py and understand architecture (690 LOC, 5 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_matriz_consciousness_governance.py
4. **MOVE**: git mv labs/core/governance/matriz_consciousness_governance.py core/governance/matriz_consciousness_governance.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.consciousness.expansion.consciousness_expansion_engine

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/consciousness/expansion/consciousness_expansion_engine.py`
**Target**: `core/consciousness/consciousness_expansion_engine.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/expansion/consciousness_expansion_engine.py and understand architecture (641 LOC, 3 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_consciousness_expansion_engine.py
4. **MOVE**: git mv labs/consciousness/expansion/consciousness_expansion_engine.py core/consciousness/consciousness_expansion_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.consciousness.systems.dream_engine.dream_reflection_loop

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/systems/dream_engine/dream_reflection_loop.py`
**Target**: `core/consciousness/dream_reflection_loop.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/systems/dream_engine/dream_reflection_loop.py and understand architecture (885 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dream_reflection_loop.py
4. **MOVE**: git mv labs/consciousness/systems/dream_engine/dream_reflection_loop.py core/consciousness/dream_reflection_loop.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 1 Completion Checklist

- [ ] All 20 modules moved to target locations
- [ ] All integration tests written and passing
- [ ] All imports updated and verified (`make lane-guard` and `make imports-guard`)
- [ ] Smoke tests passing (≥ baseline)
- [ ] Baseline smoke captured pre-changes (`.baseline_smoke.txt`)
- [ ] Documentation updated for all modules
- [ ] All commits follow T4 standard
- [ ] Lint/format clean (`make lint && make format`)
- [ ] No circular dependencies introduced
- [ ] Registry/exports properly wired
- [ ] Architecture diagrams updated if needed
- [ ] `.codex_trace.json` updated with completion status

**Estimated Effort**: ~146 hours (~18 work days at 8h/day)

---

## Quick Reference Commands

```bash
# Run integration tests
pytest tests/integration/ -v

# Run smoke tests
make smoke

# Validate lane boundaries
make lane-guard

# Validate imports health
make imports-guard

# Lint and format
make lint && make format

# Check for circular imports
python3 -m scripts.check_circular_imports

# Update architecture docs
# Edit docs/architecture/README.md with new module locations
```

---

**Next Batch**: INTEGRATION_GUIDE_02.md (if batch 1 < 8)
**Previous Batch**: INTEGRATION_GUIDE_00.md (if batch 1 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
