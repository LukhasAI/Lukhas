# Integration Guide - Batch 2/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~144 hours
**Average Priority**: 80.4
**Complexity**: 20 low, 0 medium
**Strategic Focus**: Consciousness Systems Foundation

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
  "task": "Hidden Gems Integration - Batch 2",
  "batch": 2,
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

## Batch 2 Overview

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
- **Highest**: 83.0 (system)
- **Lowest**: 78.0 (interface)

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

### 1. labs.consciousness.reflection.system

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/system.py`
**Target**: `matriz/consciousness/reflection/system.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/system.py and understand architecture (936 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_system.py
4. **MOVE**: git mv labs/consciousness/reflection/system.py matriz/consciousness/reflection/system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.consciousness.reflection.awareness_system

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/awareness_system.py`
**Target**: `matriz/consciousness/reflection/awareness_system.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/awareness_system.py and understand architecture (995 LOC, 3 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_awareness_system.py
4. **MOVE**: git mv labs/consciousness/reflection/awareness_system.py matriz/consciousness/reflection/awareness_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.consciousness.reflection.distributed_state_manager

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/distributed_state_manager.py`
**Target**: `matriz/consciousness/reflection/distributed_state_manager.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/distributed_state_manager.py and understand architecture (577 LOC, 5 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_distributed_state_manager.py
4. **MOVE**: git mv labs/consciousness/reflection/distributed_state_manager.py matriz/consciousness/reflection/distributed_state_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.consciousness.reflection.learning_system

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/learning_system.py`
**Target**: `matriz/consciousness/reflection/learning_system.py`

**Why**: 9 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/learning_system.py and understand architecture (848 LOC, 9 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_learning_system.py
4. **MOVE**: git mv labs/consciousness/reflection/learning_system.py matriz/consciousness/reflection/learning_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.governance.identity.core.colonies.consciousness_verification_colony

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/colonies/consciousness_verification_colony.py`
**Target**: `core/governance/identity/core/colonies/consciousness_verification_colony.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/colonies/consciousness_verification_colony.py and understand architecture (907 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_consciousness_verification_colony.py
4. **MOVE**: git mv labs/governance/identity/core/colonies/consciousness_verification_colony.py core/governance/identity/core/colonies/consciousness_verification_colony.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. core.matriz_consciousness_integration

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `core/matriz_consciousness_integration.py`
**Target**: `core/matriz_consciousness_integration.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/matriz_consciousness_integration.py and understand architecture (522 LOC, 1 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_matriz_consciousness_integration.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. core.consciousness_signal_router

**Priority Score**: 83.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `core/consciousness_signal_router.py`
**Target**: `core/consciousness_signal_router.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/consciousness_signal_router.py and understand architecture (733 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_consciousness_signal_router.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.governance.security.audit_system

**Priority Score**: 81.0 | **Quality Score**: 75.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `labs/governance/security/audit_system.py`
**Target**: `core/governance/security/audit_system.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/security/audit_system.py and understand architecture (973 LOC, 10 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_audit_system.py
4. **MOVE**: git mv labs/governance/security/audit_system.py core/governance/security/audit_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. core.utils.orchestration_energy_aware_execution_planner

**Priority Score**: 80.0 | **Quality Score**: 80.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `core/utils/orchestration_energy_aware_execution_planner.py`
**Target**: `core/utils/orchestration_energy_aware_execution_planner.py`

**Why**: 1254 LOC, 10 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read core/utils/orchestration_energy_aware_execution_planner.py and understand architecture (1254 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_orchestration_energy_aware_execution_planner.py
4. **VERIFY**: Placement already correct; ensure registry/exports wiring (e.g., update `core/utils/__init__.py`)
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. labs.governance.identity.core.brain_identity_integration

**Priority Score**: 79.2 | **Quality Score**: 70.5 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/brain_identity_integration.py`
**Target**: `core/governance/identity/core/brain_identity_integration.py`

**Why**: 10 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/brain_identity_integration.py and understand architecture (528 LOC, 10 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_brain_identity_integration.py
4. **MOVE**: git mv labs/governance/identity/core/brain_identity_integration.py core/governance/identity/core/brain_identity_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.memory.systems.replay_system

**Priority Score**: 79.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/memory/systems/replay_system.py`
**Target**: `core/memory/replay_system.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/systems/replay_system.py and understand architecture (573 LOC, 8 classes, 5 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_replay_system.py
4. **MOVE**: git mv labs/memory/systems/replay_system.py core/memory/replay_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.governance.identity.core.colonies.biometric_verification_colony

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/colonies/biometric_verification_colony.py`
**Target**: `core/governance/identity/core/colonies/biometric_verification_colony.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/colonies/biometric_verification_colony.py and understand architecture (601 LOC, 6 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_biometric_verification_colony.py
4. **MOVE**: git mv labs/governance/identity/core/colonies/biometric_verification_colony.py core/governance/identity/core/colonies/biometric_verification_colony.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.governance.identity.core.colonies.dream_verification_colony

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/colonies/dream_verification_colony.py`
**Target**: `core/governance/identity/core/colonies/dream_verification_colony.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/colonies/dream_verification_colony.py and understand architecture (912 LOC, 5 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dream_verification_colony.py
4. **MOVE**: git mv labs/governance/identity/core/colonies/dream_verification_colony.py core/governance/identity/core/colonies/dream_verification_colony.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.governance.identity.core.health.identity_health_monitor

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/health/identity_health_monitor.py`
**Target**: `core/governance/identity/core/health/identity_health_monitor.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/health/identity_health_monitor.py and understand architecture (713 LOC, 5 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_identity_health_monitor.py
4. **MOVE**: git mv labs/governance/identity/core/health/identity_health_monitor.py core/governance/identity/core/health/identity_health_monitor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.governance.identity.core.tagging.identity_tag_resolver

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/tagging/identity_tag_resolver.py`
**Target**: `core/governance/identity/core/tagging/identity_tag_resolver.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/tagging/identity_tag_resolver.py and understand architecture (556 LOC, 6 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_identity_tag_resolver.py
4. **MOVE**: git mv labs/governance/identity/core/tagging/identity_tag_resolver.py core/governance/identity/core/tagging/identity_tag_resolver.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.governance.identity.core.glyph.distributed_glyph_generation

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/core/glyph/distributed_glyph_generation.py`
**Target**: `core/governance/identity/core/glyph/distributed_glyph_generation.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/core/glyph/distributed_glyph_generation.py and understand architecture (753 LOC, 7 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_distributed_glyph_generation.py
4. **MOVE**: git mv labs/governance/identity/core/glyph/distributed_glyph_generation.py core/governance/identity/core/glyph/distributed_glyph_generation.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. labs.governance.guardian.system_health_monitor

**Priority Score**: 79.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/guardian/system_health_monitor.py`
**Target**: `core/governance/guardian/system_health_monitor.py`

**Why**: 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/guardian/system_health_monitor.py and understand architecture (766 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_system_health_monitor.py
4. **MOVE**: git mv labs/governance/guardian/system_health_monitor.py core/governance/guardian/system_health_monitor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.core.orchestration.golden_trio.trio_orchestrator

**Priority Score**: 78.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/core/orchestration/golden_trio/trio_orchestrator.py`
**Target**: `core/orchestration/golden_trio/trio_orchestrator.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/golden_trio/trio_orchestrator.py and understand architecture (552 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_trio_orchestrator.py
4. **MOVE**: git mv labs/core/orchestration/golden_trio/trio_orchestrator.py core/orchestration/golden_trio/trio_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.core.orchestration.brain.autonomous_github_manager

**Priority Score**: 78.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/core/orchestration/brain/autonomous_github_manager.py`
**Target**: `core/orchestration/brain/autonomous_github_manager.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/autonomous_github_manager.py and understand architecture (582 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_autonomous_github_manager.py
4. **MOVE**: git mv labs/core/orchestration/brain/autonomous_github_manager.py core/orchestration/brain/autonomous_github_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.core.orchestration.brain.abstract_reasoning.interface

**Priority Score**: 78.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/core/orchestration/brain/abstract_reasoning/interface.py`
**Target**: `core/orchestration/brain/abstract_reasoning/interface.py`

**Why**: already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/abstract_reasoning/interface.py and understand architecture (571 LOC, 1 classes, 6 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_interface.py
4. **MOVE**: git mv labs/core/orchestration/brain/abstract_reasoning/interface.py core/orchestration/brain/abstract_reasoning/interface.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 2 Completion Checklist

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

**Estimated Effort**: ~144 hours (~18 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_03.md (if batch 2 < 8)
**Previous Batch**: INTEGRATION_GUIDE_01.md (if batch 2 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
