# Integration Guide - Batch 6/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~166 hours
**Average Priority**: 66.6
**Complexity**: 15 low, 5 medium
**Strategic Focus**: Bio-Inspired Systems & Memory

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
  "task": "Hidden Gems Integration - Batch 6",
  "batch": 6,
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

## Batch 6 Overview

### Complexity Distribution
- **Low Complexity**: 15 modules (2-4 hours each)
- **Medium Complexity**: 5 modules (6-12 hours each)

### Recommended Execution Strategy

**Mixed Complexity Batch** - Combination of low and medium. Recommended approach:
1. Start with low-complexity modules for momentum
2. Intersperse medium-complexity modules
3. Target: 2-3 modules per day
4. Expected completion: 6 work days (8h/day)

### Priority Range
- **Highest**: 68.6 (symbolic_proteome)
- **Lowest**: 64.0 (core_hub)

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

### 1. labs.bio.memory.symbolic_proteome

**Priority Score**: 68.6 | **Quality Score**: 74.0 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/bio/memory/symbolic_proteome.py`
**Target**: `matriz/bio/memory/symbolic_proteome.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Matches pattern 'bio' - move to matriz/bio/

**Integration Steps**:

1. **REVIEW**: Read labs/bio/memory/symbolic_proteome.py and understand architecture (835 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_proteome.py
4. **MOVE**: git mv labs/bio/memory/symbolic_proteome.py matriz/bio/memory/symbolic_proteome.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.memory.repair.advanced_trauma_repair

**Priority Score**: 68.6 | **Quality Score**: 74.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/memory/repair/advanced_trauma_repair.py`
**Target**: `core/memory/advanced_trauma_repair.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/repair/advanced_trauma_repair.py and understand architecture (777 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_advanced_trauma_repair.py
4. **MOVE**: git mv labs/memory/repair/advanced_trauma_repair.py core/memory/advanced_trauma_repair.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.consciousness.reflection.unified_memory_manager

**Priority Score**: 68.0 | **Quality Score**: 70.0 | **Complexity**: medium (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/unified_memory_manager.py`
**Target**: `matriz/consciousness/reflection/unified_memory_manager.py`

**Why**: 1425 LOC

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/unified_memory_manager.py and understand architecture (1425 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_unified_memory_manager.py
4. **MOVE**: git mv labs/consciousness/reflection/unified_memory_manager.py matriz/consciousness/reflection/unified_memory_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. serve.reference_api.public_api_reference

**Priority Score**: 67.5 | **Quality Score**: 83.8 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `serve/reference_api/public_api_reference.py`
**Target**: `serve/reference_api/public_api_reference.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read serve/reference_api/public_api_reference.py and understand architecture (530 LOC, 7 classes, 16 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_public_api_reference.py
4. **MOVE**: git mv serve/reference_api/public_api_reference.py serve/reference_api/public_api_reference.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.core.governance.constitutional_compliance_engine

**Priority Score**: 67.5 | **Quality Score**: 78.8 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/core/governance/constitutional_compliance_engine.py`
**Target**: `core/governance/constitutional_compliance_engine.py`

**Why**: 1310 LOC, 12 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/governance/constitutional_compliance_engine.py and understand architecture (1310 LOC, 12 classes, 4 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_constitutional_compliance_engine.py
4. **MOVE**: git mv labs/core/governance/constitutional_compliance_engine.py core/governance/constitutional_compliance_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.core.governance.guardian_system_2

**Priority Score**: 67.5 | **Quality Score**: 78.7 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/core/governance/guardian_system_2.py`
**Target**: `core/governance/guardian_system_2.py`

**Why**: 1127 LOC, 15 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/governance/guardian_system_2.py and understand architecture (1127 LOC, 15 classes, 4 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_guardian_system_2.py
4. **MOVE**: git mv labs/core/governance/guardian_system_2.py core/governance/guardian_system_2.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. core.oracle_nervous_system

**Priority Score**: 67.0 | **Quality Score**: 80.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `core/oracle_nervous_system.py`
**Target**: `core/oracle_nervous_system.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/oracle_nervous_system.py and understand architecture (705 LOC, 6 classes, 6 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_oracle_nervous_system.py
4. **MOVE**: git mv core/oracle_nervous_system.py core/oracle_nervous_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. core.symbolic.symbolic_anomaly_explorer

**Priority Score**: 67.0 | **Quality Score**: 80.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `core/symbolic/symbolic_anomaly_explorer.py`
**Target**: `core/symbolic/symbolic_anomaly_explorer.py`

**Why**: 1112 LOC, 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/symbolic/symbolic_anomaly_explorer.py and understand architecture (1112 LOC, 7 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_anomaly_explorer.py
4. **MOVE**: git mv core/symbolic/symbolic_anomaly_explorer.py core/symbolic/symbolic_anomaly_explorer.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.memory.learning.meta_learning.federated_integration

**Priority Score**: 67.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/memory/learning/meta_learning/federated_integration.py`
**Target**: `core/memory/federated_integration.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/learning/meta_learning/federated_integration.py and understand architecture (685 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_federated_integration.py
4. **MOVE**: git mv labs/memory/learning/meta_learning/federated_integration.py core/memory/federated_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. labs.memory.learning.federated.FederatedIntegration

**Priority Score**: 67.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/memory/learning/federated/FederatedIntegration.py`
**Target**: `core/memory/FederatedIntegration.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/learning/federated/FederatedIntegration.py and understand architecture (685 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_FederatedIntegration.py
4. **MOVE**: git mv labs/memory/learning/federated/FederatedIntegration.py core/memory/FederatedIntegration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.memory.dna_helix.dna_healix

**Priority Score**: 67.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/memory/dna_helix/dna_healix.py`
**Target**: `core/memory/dna_healix.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/dna_helix/dna_healix.py and understand architecture (554 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dna_healix.py
4. **MOVE**: git mv labs/memory/dna_helix/dna_healix.py core/memory/dna_healix.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.memory.neocortical.neocortical_network

**Priority Score**: 67.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/memory/neocortical/neocortical_network.py`
**Target**: `core/memory/neocortical_network.py`

**Why**: already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/neocortical/neocortical_network.py and understand architecture (646 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_neocortical_network.py
4. **MOVE**: git mv labs/memory/neocortical/neocortical_network.py core/memory/neocortical_network.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.orchestration.openai_modulated_service

**Priority Score**: 66.9 | **Quality Score**: 72.2 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/orchestration/openai_modulated_service.py`
**Target**: `core/orchestration/openai_modulated_service.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Default placement in core/orchestration/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/orchestration/openai_modulated_service.py and understand architecture (589 LOC, 10 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_openai_modulated_service.py
4. **MOVE**: git mv labs/orchestration/openai_modulated_service.py core/orchestration/openai_modulated_service.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.governance.identity.core.sent.policy_engine

**Priority Score**: 66.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/governance/identity/core/sent/policy_engine.py`
**Target**: `core/governance/identity/core/sent/policy_engine.py`

**Why**: 1015 LOC, 7 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/sent/policy_engine.py and understand architecture (1015 LOC, 7 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_policy_engine.py
4. **MOVE**: git mv labs/governance/identity/core/sent/policy_engine.py core/governance/identity/core/sent/policy_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.orchestration.context_bus

**Priority Score**: 66.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/orchestration/context_bus.py`
**Target**: `core/orchestration/context_bus.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/orchestration/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/orchestration/context_bus.py and understand architecture (540 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_context_bus.py
4. **MOVE**: git mv labs/orchestration/context_bus.py core/orchestration/context_bus.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.core.symbolic.vision_vocabulary

**Priority Score**: 65.0 | **Quality Score**: 75.0 | **Complexity**: low (10h) | **Risk**: medium

**Current**: `labs/core/symbolic/vision_vocabulary.py`
**Target**: `core/symbolic/vision_vocabulary.py`

**Why**: 1047 LOC, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/symbolic/vision_vocabulary.py and understand architecture (1047 LOC, 2 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_vision_vocabulary.py
4. **MOVE**: git mv labs/core/symbolic/vision_vocabulary.py core/symbolic/vision_vocabulary.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. core.tier_aware_colony_proxy

**Priority Score**: 65.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `core/tier_aware_colony_proxy.py`
**Target**: `core/tier_aware_colony_proxy.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/tier_aware_colony_proxy.py and understand architecture (517 LOC, 4 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_tier_aware_colony_proxy.py
4. **MOVE**: git mv core/tier_aware_colony_proxy.py core/tier_aware_colony_proxy.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.core.orchestration.brain.GlobalInstitutionalCompliantEngine

**Priority Score**: 64.8 | **Quality Score**: 79.4 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py`
**Target**: `core/orchestration/brain/GlobalInstitutionalCompliantEngine.py`

**Why**: 1180 LOC, 9 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py and understand architecture (1180 LOC, 9 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_GlobalInstitutionalCompliantEngine.py
4. **MOVE**: git mv labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py core/orchestration/brain/GlobalInstitutionalCompliantEngine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.core.resource_optimization_integration

**Priority Score**: 64.0 | **Quality Score**: 72.5 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/core/resource_optimization_integration.py`
**Target**: `core/resource_optimization_integration.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/resource_optimization_integration.py and understand architecture (516 LOC, 5 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_resource_optimization_integration.py
4. **MOVE**: git mv labs/core/resource_optimization_integration.py core/resource_optimization_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.core.core_hub

**Priority Score**: 64.0 | **Quality Score**: 72.5 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/core/core_hub.py`
**Target**: `core/core_hub.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/core_hub.py and understand architecture (601 LOC, 2 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_core_hub.py
4. **MOVE**: git mv labs/core/core_hub.py core/core_hub.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 6 Completion Checklist

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

**Estimated Effort**: ~166 hours (~20 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_07.md (if batch 6 < 8)
**Previous Batch**: INTEGRATION_GUIDE_05.md (if batch 6 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
