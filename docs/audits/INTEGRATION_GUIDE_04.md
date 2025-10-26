# Integration Guide - Batch 4/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~150 hours
**Average Priority**: 73.0
**Complexity**: 20 low, 0 medium
**Strategic Focus**: Identity & Governance Systems

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
  "task": "Hidden Gems Integration - Batch 4",
  "batch": 4,
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

## Batch 4 Overview

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
- **Highest**: 74.0 (MetaLearningEnhancement)
- **Lowest**: 71.0 (qrg_generators)

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

### 1. labs.consciousness.reflection.MetaLearningEnhancement

**Priority Score**: 74.0 | **Quality Score**: 72.5 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/MetaLearningEnhancement.py`
**Target**: `matriz/consciousness/reflection/MetaLearningEnhancement.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/MetaLearningEnhancement.py and understand architecture (944 LOC, 3 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_MetaLearningEnhancement.py
4. **MOVE**: git mv labs/consciousness/reflection/MetaLearningEnhancement.py matriz/consciousness/reflection/MetaLearningEnhancement.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.governance.identity.zkproof.multimodal_zk_engine

**Priority Score**: 74.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/zkproof/multimodal_zk_engine.py`
**Target**: `core/governance/identity/zkproof/multimodal_zk_engine.py`

**Why**: standard module

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/zkproof/multimodal_zk_engine.py and understand architecture (566 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_multimodal_zk_engine.py
4. **MOVE**: git mv labs/governance/identity/zkproof/multimodal_zk_engine.py core/governance/identity/zkproof/multimodal_zk_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.governance.identity.core.unified_auth_manager

**Priority Score**: 74.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/unified_auth_manager.py`
**Target**: `core/governance/identity/core/unified_auth_manager.py`

**Why**: 8 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/unified_auth_manager.py and understand architecture (799 LOC, 8 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_unified_auth_manager.py
4. **MOVE**: git mv labs/governance/identity/core/unified_auth_manager.py core/governance/identity/core/unified_auth_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.governance.identity.biometric.biometric_fusion_engine

**Priority Score**: 74.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/biometric/biometric_fusion_engine.py`
**Target**: `core/governance/identity/biometric/biometric_fusion_engine.py`

**Why**: standard module

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/biometric/biometric_fusion_engine.py and understand architecture (712 LOC, 5 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_biometric_fusion_engine.py
4. **MOVE**: git mv labs/governance/identity/biometric/biometric_fusion_engine.py core/governance/identity/biometric/biometric_fusion_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.governance.identity.quantum.dynamic_qrglyph_engine

**Priority Score**: 74.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/governance/identity/quantum/dynamic_qrglyph_engine.py`
**Target**: `core/governance/identity/quantum/dynamic_qrglyph_engine.py`

**Why**: 6 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/quantum/dynamic_qrglyph_engine.py and understand architecture (553 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dynamic_qrglyph_engine.py
4. **MOVE**: git mv labs/governance/identity/quantum/dynamic_qrglyph_engine.py core/governance/identity/quantum/dynamic_qrglyph_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. core.bio_symbolic_processor

**Priority Score**: 74.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/bio_symbolic_processor.py`
**Target**: `core/bio_symbolic_processor.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/bio_symbolic_processor.py and understand architecture (532 LOC, 5 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_bio_symbolic_processor.py
4. **MOVE**: git mv core/bio_symbolic_processor.py core/bio_symbolic_processor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.memory.access.tier_system

**Priority Score**: 73.5 | **Quality Score**: 73.8 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/memory/access/tier_system.py`
**Target**: `core/memory/tier_system.py`

**Why**: 7 classes

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/access/tier_system.py and understand architecture (596 LOC, 7 classes, 8 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_tier_system.py
4. **MOVE**: git mv labs/memory/access/tier_system.py core/memory/tier_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.core.api.api_system

**Priority Score**: 73.0 | **Quality Score**: 72.5 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/core/api/api_system.py`
**Target**: `core/api/api_system.py`

**Why**: 14 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/api/api_system.py and understand architecture (631 LOC, 14 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_api_system.py
4. **MOVE**: git mv labs/core/api/api_system.py core/api/api_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.core.identity.manager

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/core/identity/manager.py`
**Target**: `core/identity/manager.py`

**Why**: standard module

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/identity/manager.py and understand architecture (716 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_manager.py
4. **MOVE**: git mv labs/core/identity/manager.py core/identity/manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. labs.consciousness.reasoning.decision.bridge

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/reasoning/decision/bridge.py`
**Target**: `core/consciousness/bridge.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reasoning/decision/bridge.py and understand architecture (805 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_bridge.py
4. **MOVE**: git mv labs/consciousness/reasoning/decision/bridge.py core/consciousness/bridge.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.consciousness.states.world_models

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/consciousness/states/world_models.py`
**Target**: `core/consciousness/world_models.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/states/world_models.py and understand architecture (543 LOC, 7 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_world_models.py
4. **MOVE**: git mv labs/consciousness/states/world_models.py core/consciousness/world_models.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.consciousness.states.qi_mesh_integrator

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/consciousness/states/qi_mesh_integrator.py`
**Target**: `core/consciousness/qi_mesh_integrator.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/states/qi_mesh_integrator.py and understand architecture (624 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_qi_mesh_integrator.py
4. **MOVE**: git mv labs/consciousness/states/qi_mesh_integrator.py core/consciousness/qi_mesh_integrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.consciousness.dream.parallel_reality_simulator

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/dream/parallel_reality_simulator.py`
**Target**: `matriz/consciousness/dream//parallel_reality_simulator.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/dream/parallel_reality_simulator.py and understand architecture (849 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_parallel_reality_simulator.py
4. **MOVE**: git mv labs/consciousness/dream/parallel_reality_simulator.py matriz/consciousness/dream//parallel_reality_simulator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.consciousness.reflection.federated_meta_learning

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/federated_meta_learning.py`
**Target**: `matriz/consciousness/reflection/federated_meta_learning.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/federated_meta_learning.py and understand architecture (927 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_federated_meta_learning.py
4. **MOVE**: git mv labs/consciousness/reflection/federated_meta_learning.py matriz/consciousness/reflection/federated_meta_learning.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.consciousness.reflection.meta_learning

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/meta_learning.py`
**Target**: `matriz/consciousness/reflection/meta_learning.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/meta_learning.py and understand architecture (927 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_meta_learning.py
4. **MOVE**: git mv labs/consciousness/reflection/meta_learning.py matriz/consciousness/reflection/meta_learning.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.consciousness.reflection.agent_coordination

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/agent_coordination.py`
**Target**: `matriz/consciousness/reflection/agent_coordination.py`

**Why**: 13 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/agent_coordination.py and understand architecture (690 LOC, 13 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_agent_coordination.py
4. **MOVE**: git mv labs/consciousness/reflection/agent_coordination.py matriz/consciousness/reflection/agent_coordination.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. consciousness.__init__

**Priority Score**: 73.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `consciousness/__init__.py`
**Target**: `core/consciousness/__init__.py`

**Why**: 17 classes, already imports production code

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read consciousness/__init__.py and understand architecture (400 LOC, 17 classes, 6 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test___init__.py
4. **MOVE**: git mv consciousness/__init__.py core/consciousness/__init__.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.governance.identity.unified_login_interface

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/governance/identity/unified_login_interface.py`
**Target**: `core/governance/identity/unified_login_interface.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/unified_login_interface.py and understand architecture (790 LOC, 7 classes, 2 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_unified_login_interface.py
4. **MOVE**: git mv labs/governance/identity/unified_login_interface.py core/governance/identity/unified_login_interface.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.governance.identity.auth_backend.websocket_server

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/governance/identity/auth_backend/websocket_server.py`
**Target**: `core/governance/identity/auth_backend/websocket_server.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/auth_backend/websocket_server.py and understand architecture (628 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_websocket_server.py
4. **MOVE**: git mv labs/governance/identity/auth_backend/websocket_server.py core/governance/identity/auth_backend/websocket_server.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.governance.identity.auth.qrg_generators

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/governance/identity/auth/qrg_generators.py`
**Target**: `core/governance/identity/auth/qrg_generators.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/auth/qrg_generators.py and understand architecture (770 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_qrg_generators.py
4. **MOVE**: git mv labs/governance/identity/auth/qrg_generators.py core/governance/identity/auth/qrg_generators.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 4 Completion Checklist

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

**Estimated Effort**: ~150 hours (~18 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_05.md (if batch 4 < 8)
**Previous Batch**: INTEGRATION_GUIDE_03.md (if batch 4 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
