# Integration Guide - Batch 7/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~192 hours
**Average Priority**: 62.5
**Complexity**: 9 low, 11 medium
**Strategic Focus**: Integration Coordination & Security

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
  "task": "Hidden Gems Integration - Batch 7",
  "batch": 7,
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

## Batch 7 Overview

### Complexity Distribution
- **Low Complexity**: 9 modules (2-4 hours each)
- **Medium Complexity**: 11 modules (6-12 hours each)

### Recommended Execution Strategy

**High Complexity Batch** - Majority are medium complexity. Recommended approach:
1. Review all modules before starting
2. Tackle highest priority modules first
3. One module at a time with full testing
4. Target: 1-2 modules per day
5. Expected completion: 12 work days (8h/day)

### Priority Range
- **Highest**: 64.0 (system_coordinator)
- **Lowest**: 60.0 (symbolic_weaver)

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

### 1. core.integration.system_coordinator

**Priority Score**: 64.0 | **Quality Score**: 72.5 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `core/integration/system_coordinator.py`
**Target**: `core/integration/system_coordinator.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/integration/system_coordinator.py and understand architecture (650 LOC, 6 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_system_coordinator.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/integration/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.governance.identity.deployment_package

**Priority Score**: 64.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/governance/identity/deployment_package.py`
**Target**: `core/governance/identity/deployment_package.py`

**Why**: 7 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/deployment_package.py and understand architecture (615 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_deployment_package.py
4. **MOVE**: git mv labs/governance/identity/deployment_package.py core/governance/identity/deployment_package.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.governance.identity.lambda_id_auth

**Priority Score**: 64.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/governance/identity/lambda_id_auth.py`
**Target**: `core/governance/identity/lambda_id_auth.py`

**Why**: 8 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/lambda_id_auth.py and understand architecture (506 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_lambda_id_auth.py
4. **MOVE**: git mv labs/governance/identity/lambda_id_auth.py core/governance/identity/lambda_id_auth.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.governance.security.consent_manager

**Priority Score**: 64.0 | **Quality Score**: 70.0 | **Complexity**: medium (12h) | **Risk**: medium-high

**Current**: `labs/governance/security/consent_manager.py`
**Target**: `core/governance/security/consent_manager.py`

**Why**: standard module

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/security/consent_manager.py and understand architecture (998 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_consent_manager.py
4. **MOVE**: git mv labs/governance/security/consent_manager.py core/governance/security/consent_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.consciousness.reflection.practical_optimizations

**Priority Score**: 63.8 | **Quality Score**: 72.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/practical_optimizations.py`
**Target**: `matriz/consciousness/reflection/practical_optimizations.py`

**Why**: 11 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/practical_optimizations.py and understand architecture (937 LOC, 11 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_practical_optimizations.py
4. **MOVE**: git mv labs/consciousness/reflection/practical_optimizations.py matriz/consciousness/reflection/practical_optimizations.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.core.symbolic.dream_delivery_manager

**Priority Score**: 63.7 | **Quality Score**: 71.7 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/core/symbolic/dream_delivery_manager.py`
**Target**: `core/symbolic/dream_delivery_manager.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/symbolic/dream_delivery_manager.py and understand architecture (693 LOC, 3 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dream_delivery_manager.py
4. **MOVE**: git mv labs/core/symbolic/dream_delivery_manager.py core/symbolic/dream_delivery_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.governance.security.access_control

**Priority Score**: 63.0 | **Quality Score**: 80.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/governance/security/access_control.py`
**Target**: `core/governance/security/access_control.py`

**Why**: 1102 LOC, 14 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/security/access_control.py and understand architecture (1102 LOC, 14 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_access_control.py
4. **MOVE**: git mv labs/governance/security/access_control.py core/governance/security/access_control.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.core.identity.lambda_id_core

**Priority Score**: 63.0 | **Quality Score**: 70.0 | **Complexity**: medium (10h) | **Risk**: medium-high

**Current**: `labs/core/identity/lambda_id_core.py`
**Target**: `core/identity/lambda_id_core.py`

**Why**: 11 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/identity/lambda_id_core.py and understand architecture (717 LOC, 11 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_lambda_id_core.py
4. **MOVE**: git mv labs/core/identity/lambda_id_core.py core/identity/lambda_id_core.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.core.endocrine.hormone_system

**Priority Score**: 63.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/core/endocrine/hormone_system.py`
**Target**: `core/endocrine/hormone_system.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/endocrine/hormone_system.py and understand architecture (430 LOC, 4 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_hormone_system.py
4. **MOVE**: git mv labs/core/endocrine/hormone_system.py core/endocrine/hormone_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. core.constellation_alignment_system

**Priority Score**: 63.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `core/constellation_alignment_system.py`
**Target**: `core/constellation_alignment_system.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/constellation_alignment_system.py and understand architecture (701 LOC, 7 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_constellation_alignment_system.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. core.integration.neuro_symbolic_fusion_layer

**Priority Score**: 63.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/integration/neuro_symbolic_fusion_layer.py`
**Target**: `core/integration/neuro_symbolic_fusion_layer.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/integration/neuro_symbolic_fusion_layer.py and understand architecture (605 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_neuro_symbolic_fusion_layer.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/integration/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. core.symbolic.neuro_symbolic_fusion_layer

**Priority Score**: 63.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/symbolic/neuro_symbolic_fusion_layer.py`
**Target**: `core/symbolic/neuro_symbolic_fusion_layer.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/symbolic/neuro_symbolic_fusion_layer.py and understand architecture (508 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_neuro_symbolic_fusion_layer.py
4. **MOVE**: git mv core/symbolic/neuro_symbolic_fusion_layer.py core/symbolic/neuro_symbolic_fusion_layer.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.core.colonies.ethics_swarm_colony

**Priority Score**: 62.3 | **Quality Score**: 93.2 | **Complexity**: medium (14h) | **Risk**: low

**Current**: `labs/core/colonies/ethics_swarm_colony.py`
**Target**: `core/colonies/ethics_swarm_colony.py`

**Why**: 1195 LOC, 14 classes, already imports production code, high quality score

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/colonies/ethics_swarm_colony.py and understand architecture (1195 LOC, 14 classes, 5 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_ethics_swarm_colony.py
4. **MOVE**: git mv labs/core/colonies/ethics_swarm_colony.py core/colonies/ethics_swarm_colony.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.memory.systems.neurosymbolic_integration

**Priority Score**: 62.0 | **Quality Score**: 70.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/memory/systems/neurosymbolic_integration.py`
**Target**: `core/memory/neurosymbolic_integration.py`

**Why**: 1601 LOC, 8 classes

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/systems/neurosymbolic_integration.py and understand architecture (1601 LOC, 8 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_neurosymbolic_integration.py
4. **MOVE**: git mv labs/memory/systems/neurosymbolic_integration.py core/memory/neurosymbolic_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.core.orchestration.brain.canadian_awareness_engine

**Priority Score**: 61.0 | **Quality Score**: 70.0 | **Complexity**: medium (10h) | **Risk**: medium-high

**Current**: `labs/core/orchestration/brain/canadian_awareness_engine.py`
**Target**: `core/orchestration/brain/canadian_awareness_engine.py`

**Why**: 11 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/canadian_awareness_engine.py and understand architecture (591 LOC, 11 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_canadian_awareness_engine.py
4. **MOVE**: git mv labs/core/orchestration/brain/canadian_awareness_engine.py core/orchestration/brain/canadian_awareness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.core.orchestration.brain.das_awareness_engine

**Priority Score**: 61.0 | **Quality Score**: 70.0 | **Complexity**: medium (10h) | **Risk**: medium-high

**Current**: `labs/core/orchestration/brain/das_awareness_engine.py`
**Target**: `core/orchestration/brain/das_awareness_engine.py`

**Why**: 15 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/das_awareness_engine.py and understand architecture (523 LOC, 15 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_das_awareness_engine.py
4. **MOVE**: git mv labs/core/orchestration/brain/das_awareness_engine.py core/orchestration/brain/das_awareness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. labs.core.orchestration.brain.uk_awareness_engine

**Priority Score**: 61.0 | **Quality Score**: 70.0 | **Complexity**: medium (10h) | **Risk**: medium-high

**Current**: `labs/core/orchestration/brain/uk_awareness_engine.py`
**Target**: `core/orchestration/brain/uk_awareness_engine.py`

**Why**: 11 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/uk_awareness_engine.py and understand architecture (564 LOC, 11 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_uk_awareness_engine.py
4. **MOVE**: git mv labs/core/orchestration/brain/uk_awareness_engine.py core/orchestration/brain/uk_awareness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. bridge.api.orchestration_endpoints

**Priority Score**: 61.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `bridge/api/orchestration_endpoints.py`
**Target**: `core/bridge/orchestration_endpoints.py`

**Why**: 6 classes

**Location Reasoning**: Default placement in core/bridge/ - review manually

**Integration Steps**:

1. **REVIEW**: Read bridge/api/orchestration_endpoints.py and understand architecture (688 LOC, 6 classes, 11 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_orchestration_endpoints.py
4. **MOVE**: git mv bridge/api/orchestration_endpoints.py core/bridge/orchestration_endpoints.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.consciousness.reflection.cognitive_architecture_controller

**Priority Score**: 60.5 | **Quality Score**: 76.2 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/cognitive_architecture_controller.py`
**Target**: `matriz/consciousness/reflection/cognitive_architecture_controller.py`

**Why**: 1584 LOC, 18 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/cognitive_architecture_controller.py and understand architecture (1584 LOC, 18 classes, 4 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_cognitive_architecture_controller.py
4. **MOVE**: git mv labs/consciousness/reflection/cognitive_architecture_controller.py matriz/consciousness/reflection/cognitive_architecture_controller.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.consciousness.reflection.symbolic_weaver

**Priority Score**: 60.0 | **Quality Score**: 75.0 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/symbolic_weaver.py`
**Target**: `matriz/consciousness/reflection/symbolic_weaver.py`

**Why**: 1832 LOC, 11 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/symbolic_weaver.py and understand architecture (1832 LOC, 11 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_weaver.py
4. **MOVE**: git mv labs/consciousness/reflection/symbolic_weaver.py matriz/consciousness/reflection/symbolic_weaver.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 7 Completion Checklist

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

**Estimated Effort**: ~192 hours (~24 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_08.md (if batch 7 < 8)
**Previous Batch**: INTEGRATION_GUIDE_06.md (if batch 7 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
