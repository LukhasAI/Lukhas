# Integration Guide - Batch 3/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~172 hours
**Average Priority**: 75.8
**Complexity**: 17 low, 3 medium
**Strategic Focus**: Advanced Consciousness & Testing

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
  "task": "Hidden Gems Integration - Batch 3",
  "batch": 3,
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

## Batch 3 Overview

### Complexity Distribution
- **Low Complexity**: 17 modules (2-12 hours each)
- **Medium Complexity**: 3 modules (6-12 hours each)

### Recommended Execution Strategy

**Mixed Complexity Batch** - Combination of low and medium. Recommended approach:
1. Start with low-complexity modules for momentum
2. Intersperse medium-complexity modules
3. Target: 2-3 modules per day
4. Expected completion: 7 work days (8h/day)

### Priority Range
- **Highest**: 78.0 (chaos_engineering_framework)
- **Lowest**: 74.0 (awareness_engine_elevated)

---

## Modules in This Batch (20 total)

Note:
- After any **UPDATE_IMPORTS** step, run `make lint && make format`.
- Typical registry/exports touchpoints: `matriz/core/__init__.py`, module registries/catalogs, and package `__init__.py` files.
- Use T4 commit messages with a short diagnostic body (gates, baseline deltas, registry updates).

T4 commit example:
```
feat(core): integrate <module_name> from labs

- Gates: lane-guard ✅ imports-guard ✅ smoke Δ0
- Tests: +1 integration; smoke unchanged
- Registry: updated <registry/catalog files>
- Docs: docs/architecture updated
```

Lane-specific subjects:
- `feat(matriz): integrate <module_name> from labs`
- `feat(core): integrate <module_name> from labs`
- `feat(serve): integrate <module_name> from labs`

### 1. labs.consciousness.testing.chaos_engineering_framework

**Priority Score**: 78.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/consciousness/testing/chaos_engineering_framework.py`
**Target**: `core/consciousness/chaos_engineering_framework.py`

**Why**: 10 classes

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/testing/chaos_engineering_framework.py and understand architecture (669 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_chaos_engineering_framework.py
4. **MOVE**: git mv labs/consciousness/testing/chaos_engineering_framework.py core/consciousness/chaos_engineering_framework.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.consciousness.quantum.collapse_governance_system

**Priority Score**: 78.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/consciousness/quantum/collapse_governance_system.py`
**Target**: `core/consciousness/collapse_governance_system.py`

**Why**: 9 classes

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/quantum/collapse_governance_system.py and understand architecture (742 LOC, 9 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_collapse_governance_system.py
4. **MOVE**: git mv labs/consciousness/quantum/collapse_governance_system.py core/consciousness/collapse_governance_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi

**Priority Score**: 77.8 | **Quality Score**: 81.9 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py`
**Target**: `matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py`

**Why**: 13 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py and understand architecture (804 LOC, 13 classes, 10 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dream_engine_fastapi.py
4. **MOVE**: git mv labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.core.orchestration.async_orchestrator

**Priority Score**: 77.0 | **Quality Score**: 72.5 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/core/orchestration/async_orchestrator.py`
**Target**: `core/orchestration/async_orchestrator.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/async_orchestrator.py and understand architecture (936 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_async_orchestrator.py
4. **MOVE**: git mv labs/core/orchestration/async_orchestrator.py core/orchestration/async_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.memory.learning.adaptive_meta_learning_system

**Priority Score**: 77.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/memory/learning/adaptive_meta_learning_system.py`
**Target**: `core/memory/adaptive_meta_learning_system.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/learning/adaptive_meta_learning_system.py and understand architecture (534 LOC, 1 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_adaptive_meta_learning_system.py
4. **MOVE**: git mv labs/memory/learning/adaptive_meta_learning_system.py core/memory/adaptive_meta_learning_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.memory.fold_system.distributed_memory_fold

**Priority Score**: 77.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/memory/fold_system/distributed_memory_fold.py`
**Target**: `core/memory/distributed_memory_fold.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/fold_system/distributed_memory_fold.py and understand architecture (792 LOC, 6 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_distributed_memory_fold.py
4. **MOVE**: git mv labs/memory/fold_system/distributed_memory_fold.py core/memory/distributed_memory_fold.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.memory.systems.simple_store

**Priority Score**: 77.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/memory/systems/simple_store.py`
**Target**: `core/memory/simple_store.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/systems/simple_store.py and understand architecture (526 LOC, 5 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_simple_store.py
4. **MOVE**: git mv labs/memory/systems/simple_store.py core/memory/simple_store.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. core.orchestration.brain.demo

**Priority Score**: 76.5 | **Quality Score**: 71.2 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/orchestration/brain/demo.py`
**Target**: `core/orchestration/brain/demo.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/orchestration/brain/demo.py and understand architecture (515 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_demo.py
4. **MOVE**: git mv core/orchestration/brain/demo.py core/orchestration/brain/demo.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. core.orchestration.brain.brain_integration

**Priority Score**: 76.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/orchestration/brain/brain_integration.py`
**Target**: `core/orchestration/brain/brain_integration.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/orchestration/brain/brain_integration.py and understand architecture (633 LOC, 3 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_brain_integration.py
4. **MOVE**: git mv core/orchestration/brain/brain_integration.py core/orchestration/brain/brain_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. matriz.interfaces.api_server

**Priority Score**: 75.0 | **Quality Score**: 80.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `matriz/interfaces/api_server.py`
**Target**: `matriz/interfaces/api_server.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read matriz/interfaces/api_server.py and understand architecture (622 LOC, 6 classes, 20 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_api_server.py
4. **MOVE**: git mv matriz/interfaces/api_server.py matriz/interfaces/api_server.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.consciousness.creativity.haiku_generator

**Priority Score**: 75.0 | **Quality Score**: 75.0 | **Complexity**: low (10h) | **Risk**: medium

**Current**: `labs/consciousness/creativity/haiku_generator.py`
**Target**: `core/consciousness/haiku_generator.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/creativity/haiku_generator.py and understand architecture (912 LOC, 4 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_haiku_generator.py
4. **MOVE**: git mv labs/consciousness/creativity/haiku_generator.py core/consciousness/haiku_generator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.consciousness.states.simulation_controller

**Priority Score**: 75.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/consciousness/states/simulation_controller.py`
**Target**: `core/consciousness/simulation_controller.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/states/simulation_controller.py and understand architecture (515 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_simulation_controller.py
4. **MOVE**: git mv labs/consciousness/states/simulation_controller.py core/consciousness/simulation_controller.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.consciousness.states.async_client

**Priority Score**: 75.0 | **Quality Score**: 75.0 | **Complexity**: low (10h) | **Risk**: medium

**Current**: `labs/consciousness/states/async_client.py`
**Target**: `core/consciousness/async_client.py`

**Why**: 3365 LOC, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/states/async_client.py and understand architecture (3365 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_async_client.py
4. **MOVE**: git mv labs/consciousness/states/async_client.py core/consciousness/async_client.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.consciousness.interfaces.natural_language_interface

**Priority Score**: 75.0 | **Quality Score**: 75.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `labs/consciousness/interfaces/natural_language_interface.py`
**Target**: `core/consciousness/natural_language_interface.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/interfaces/natural_language_interface.py and understand architecture (897 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_natural_language_interface.py
4. **MOVE**: git mv labs/consciousness/interfaces/natural_language_interface.py core/consciousness/natural_language_interface.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.consciousness.reflection.content_enterprise_orchestrator

**Priority Score**: 75.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/content_enterprise_orchestrator.py`
**Target**: `matriz/consciousness/reflection/content_enterprise_orchestrator.py`

**Why**: 13 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/content_enterprise_orchestrator.py and understand architecture (868 LOC, 13 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_content_enterprise_orchestrator.py
4. **MOVE**: git mv labs/consciousness/reflection/content_enterprise_orchestrator.py matriz/consciousness/reflection/content_enterprise_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.consciousness.reflection.event_replay_snapshot

**Priority Score**: 74.8 | **Quality Score**: 74.4 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/event_replay_snapshot.py`
**Target**: `matriz/consciousness/reflection/event_replay_snapshot.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/event_replay_snapshot.py and understand architecture (673 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_event_replay_snapshot.py
4. **MOVE**: git mv labs/consciousness/reflection/event_replay_snapshot.py matriz/consciousness/reflection/event_replay_snapshot.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. labs.consciousness.states.shared_state

**Priority Score**: 74.7 | **Quality Score**: 74.3 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/states/shared_state.py`
**Target**: `core/consciousness/shared_state.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/states/shared_state.py and understand architecture (986 LOC, 7 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_shared_state.py
4. **MOVE**: git mv labs/consciousness/states/shared_state.py core/consciousness/shared_state.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.consciousness.reflection.circuit_breaker

**Priority Score**: 74.7 | **Quality Score**: 74.3 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/circuit_breaker.py`
**Target**: `matriz/consciousness/reflection/circuit_breaker.py`

**Why**: 14 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/circuit_breaker.py and understand architecture (760 LOC, 14 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_circuit_breaker.py
4. **MOVE**: git mv labs/consciousness/reflection/circuit_breaker.py matriz/consciousness/reflection/circuit_breaker.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.consciousness.dream.colony_dream_coordinator

**Priority Score**: 74.2 | **Quality Score**: 73.1 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/dream/colony_dream_coordinator.py`
**Target**: `matriz/consciousness/dream/colony_dream_coordinator.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/dream/colony_dream_coordinator.py and understand architecture (899 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_colony_dream_coordinator.py
4. **MOVE**: git mv labs/consciousness/dream/colony_dream_coordinator.py matriz/consciousness/dream/colony_dream_coordinator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.consciousness.awareness.awareness_engine_elevated

**Priority Score**: 74.0 | **Quality Score**: 85.0 | **Complexity**: medium (16h) | **Risk**: low

**Current**: `labs/consciousness/awareness/awareness_engine_elevated.py`
**Target**: `matriz/consciousness/awareness/awareness_engine_elevated.py`

**Why**: 1288 LOC, 21 classes, high quality score

**Location Reasoning**: Matches pattern 'consciousness.awareness' - move to matriz/consciousness/awareness/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/awareness/awareness_engine_elevated.py and understand architecture (1288 LOC, 21 classes, 5 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_awareness_engine_elevated.py
4. **MOVE**: git mv labs/consciousness/awareness/awareness_engine_elevated.py matriz/consciousness/awareness/awareness_engine_elevated.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 3 Completion Checklist

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

**Estimated Effort**: ~172 hours (~21 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_04.md (if batch 3 < 8)
**Previous Batch**: INTEGRATION_GUIDE_02.md (if batch 3 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
