# Integration Guide - Batch 8/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 23 modules
**Total Effort**: ~282 hours
**Average Priority**: 53.9
**Complexity**: 4 low, 19 medium
**Strategic Focus**: Complex Multi-Component Systems (Highest Effort)

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
  "task": "Hidden Gems Integration - Batch 8",
  "batch": 8,
  "total_modules": 23,
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

## Batch 8 Overview

### Complexity Distribution
- **Low Complexity**: 4 modules (2-4 hours each)
- **Medium Complexity**: 19 modules (6-12 hours each)

### Recommended Execution Strategy

**High Complexity Batch** - Majority are medium complexity. Recommended approach:
1. Review all modules before starting
2. Tackle highest priority modules first
3. One module at a time with full testing
4. Target: 1-2 modules per day
5. Expected completion: 17 work days (8h/day)

### Priority Range
- **Highest**: 59.0 (service)
- **Lowest**: 48.0 (capability_evaluation_framework)

---

## Modules in This Batch (23 total)

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

### 1. labs.consciousness.reflection.service

**Priority Score**: 59.0 | **Quality Score**: 72.5 | **Complexity**: medium (12h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/service.py`
**Target**: `matriz/consciousness/reflection/service.py`

**Why**: 1211 LOC

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/service.py and understand architecture (1211 LOC, 2 classes, 8 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_service.py
4. **MOVE**: git mv labs/consciousness/reflection/service.py matriz/consciousness/reflection/service.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.consciousness.reflection.client

**Priority Score**: 58.8 | **Quality Score**: 71.9 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/client.py`
**Target**: `matriz/consciousness/reflection/client.py`

**Why**: 1724 LOC, 7 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/client.py and understand architecture (1724 LOC, 7 classes, 3 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_client.py
4. **MOVE**: git mv labs/consciousness/reflection/client.py matriz/consciousness/reflection/client.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.core.id

**Priority Score**: 58.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/core/id.py`
**Target**: `core/id.py`

**Why**: 8 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/id.py and understand architecture (699 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_id.py
4. **MOVE**: git mv labs/core/id.py core/id.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.consciousness.constellation.framework_integration

**Priority Score**: 58.0 | **Quality Score**: 70.0 | **Complexity**: medium (16h) | **Risk**: medium-high

**Current**: `labs/consciousness/constellation/framework_integration.py`
**Target**: `core/consciousness/framework_integration.py`

**Why**: 14 classes

**Location Reasoning**: Default placement in core/consciousness/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/constellation/framework_integration.py and understand architecture (812 LOC, 14 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_framework_integration.py
4. **MOVE**: git mv labs/consciousness/constellation/framework_integration.py core/consciousness/framework_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. labs.consciousness.reflection.controller

**Priority Score**: 58.0 | **Quality Score**: 70.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/controller.py`
**Target**: `matriz/consciousness/reflection/controller.py`

**Why**: 8 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/controller.py and understand architecture (905 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_controller.py
4. **MOVE**: git mv labs/consciousness/reflection/controller.py matriz/consciousness/reflection/controller.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.bridge.api.controllers

**Priority Score**: 57.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/bridge/api/controllers.py`
**Target**: `core/bridge/controllers.py`

**Why**: 6 classes

**Location Reasoning**: Default placement in core/bridge/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/bridge/api/controllers.py and understand architecture (542 LOC, 6 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_controllers.py
4. **MOVE**: git mv labs/bridge/api/controllers.py core/bridge/controllers.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.bridge.api.api

**Priority Score**: 57.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/bridge/api/api.py`
**Target**: `core/bridge/api.py`

**Why**: standard module

**Location Reasoning**: Default placement in core/bridge/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/bridge/api/api.py and understand architecture (571 LOC, 5 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_api.py
4. **MOVE**: git mv labs/bridge/api/api.py core/bridge/api.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.memory.folds.memory_fold

**Priority Score**: 56.0 | **Quality Score**: 80.0 | **Complexity**: medium (12h) | **Risk**: medium

**Current**: `labs/memory/folds/memory_fold.py`
**Target**: `matriz/memory/folds/memory_fold.py`

**Why**: 1256 LOC

**Location Reasoning**: Matches pattern 'memory.folds' - move to matriz/memory/folds/

**Integration Steps**:

1. **REVIEW**: Read labs/memory/folds/memory_fold.py and understand architecture (1256 LOC, 5 classes, 8 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_memory_fold.py
4. **MOVE**: git mv labs/memory/folds/memory_fold.py matriz/memory/folds/memory_fold.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.governance.security.privacy_guardian

**Priority Score**: 56.0 | **Quality Score**: 75.0 | **Complexity**: medium (12h) | **Risk**: medium

**Current**: `labs/governance/security/privacy_guardian.py`
**Target**: `core/governance/security/privacy_guardian.py`

**Why**: 1142 LOC

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/security/privacy_guardian.py and understand architecture (1142 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_privacy_guardian.py
4. **MOVE**: git mv labs/governance/security/privacy_guardian.py core/governance/security/privacy_guardian.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. bridge.api.api

**Priority Score**: 55.9 | **Quality Score**: 79.7 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `bridge/api/api.py`
**Target**: `core/bridge/api.py`

**Why**: 1270 LOC, 13 classes, already imports production code

**Location Reasoning**: Default placement in core/bridge/ - review manually

**Integration Steps**:

1. **REVIEW**: Read bridge/api/api.py and understand architecture (1270 LOC, 13 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_api.py
4. **MOVE**: git mv bridge/api/api.py core/bridge/api.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. memory.fold_lineage_tracker

**Priority Score**: 54.0 | **Quality Score**: 75.0 | **Complexity**: medium (12h) | **Risk**: medium

**Current**: `memory/fold_lineage_tracker.py`
**Target**: `core/memory/fold_lineage_tracker.py`

**Why**: 1066 LOC

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read memory/fold_lineage_tracker.py and understand architecture (1066 LOC, 5 classes, 5 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_fold_lineage_tracker.py
4. **MOVE**: git mv memory/fold_lineage_tracker.py core/memory/fold_lineage_tracker.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.governance.guardian.drift_detector

**Priority Score**: 54.0 | **Quality Score**: 70.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/governance/guardian/drift_detector.py`
**Target**: `core/governance/guardian/drift_detector.py`

**Why**: 1062 LOC, 9 classes

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/guardian/drift_detector.py and understand architecture (1062 LOC, 9 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_drift_detector.py
4. **MOVE**: git mv labs/governance/guardian/drift_detector.py core/governance/guardian/drift_detector.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.governance.monitoring.threat_monitor

**Priority Score**: 54.0 | **Quality Score**: 70.0 | **Complexity**: medium (12h) | **Risk**: medium-high

**Current**: `labs/governance/monitoring/threat_monitor.py`
**Target**: `core/governance/monitoring/threat_monitor.py`

**Why**: 1268 LOC

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/monitoring/threat_monitor.py and understand architecture (1268 LOC, 3 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_threat_monitor.py
4. **MOVE**: git mv labs/governance/monitoring/threat_monitor.py core/governance/monitoring/threat_monitor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.memory.protection.symbolic_quarantine_sanctum

**Priority Score**: 53.0 | **Quality Score**: 72.5 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/memory/protection/symbolic_quarantine_sanctum.py`
**Target**: `core/memory/symbolic_quarantine_sanctum.py`

**Why**: 1467 LOC, 8 classes

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/protection/symbolic_quarantine_sanctum.py and understand architecture (1467 LOC, 8 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_quarantine_sanctum.py
4. **MOVE**: git mv labs/memory/protection/symbolic_quarantine_sanctum.py core/memory/symbolic_quarantine_sanctum.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.emotion.regulation.security_control_validation

**Priority Score**: 53.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/emotion/regulation/security_control_validation.py`
**Target**: `core/emotion/security_control_validation.py`

**Why**: 9 classes, already imports production code

**Location Reasoning**: Default placement in core/emotion/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/emotion/regulation/security_control_validation.py and understand architecture (660 LOC, 9 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_security_control_validation.py
4. **MOVE**: git mv labs/emotion/regulation/security_control_validation.py core/emotion/security_control_validation.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.memory.tools.memory_drift_auditor

**Priority Score**: 52.0 | **Quality Score**: 70.0 | **Complexity**: medium (12h) | **Risk**: medium-high

**Current**: `labs/memory/tools/memory_drift_auditor.py`
**Target**: `core/memory/memory_drift_auditor.py`

**Why**: 2156 LOC

**Location Reasoning**: Default placement in core/memory/ - review manually

**Integration Steps**:

1. **REVIEW**: Read labs/memory/tools/memory_drift_auditor.py and understand architecture (2156 LOC, 1 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_memory_drift_auditor.py
4. **MOVE**: git mv labs/memory/tools/memory_drift_auditor.py core/memory/memory_drift_auditor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. labs.core.observability.alerting_system

**Priority Score**: 50.0 | **Quality Score**: 75.0 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/core/observability/alerting_system.py`
**Target**: `core/observability/alerting_system.py`

**Why**: 1128 LOC, 11 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/observability/alerting_system.py and understand architecture (1128 LOC, 11 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_alerting_system.py
4. **MOVE**: git mv labs/core/observability/alerting_system.py core/observability/alerting_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.core.compliance.democratic_oversight

**Priority Score**: 50.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/core/compliance/democratic_oversight.py`
**Target**: `core/compliance/democratic_oversight.py`

**Why**: 1177 LOC, 9 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/compliance/democratic_oversight.py and understand architecture (1177 LOC, 9 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_democratic_oversight.py
4. **MOVE**: git mv labs/core/compliance/democratic_oversight.py core/compliance/democratic_oversight.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.core.compliance.global_compliance_manager

**Priority Score**: 50.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/core/compliance/global_compliance_manager.py`
**Target**: `core/compliance/global_compliance_manager.py`

**Why**: 1018 LOC, 8 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/compliance/global_compliance_manager.py and understand architecture (1018 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_global_compliance_manager.py
4. **MOVE**: git mv labs/core/compliance/global_compliance_manager.py core/compliance/global_compliance_manager.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.core.symbolic.symbolic_validator

**Priority Score**: 50.0 | **Quality Score**: 75.0 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/core/symbolic/symbolic_validator.py`
**Target**: `core/symbolic/symbolic_validator.py`

**Why**: 1114 LOC, 11 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/symbolic/symbolic_validator.py and understand architecture (1114 LOC, 11 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_symbolic_validator.py
4. **MOVE**: git mv labs/core/symbolic/symbolic_validator.py core/symbolic/symbolic_validator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 21. bridge.api.validation

**Priority Score**: 49.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `bridge/api/validation.py`
**Target**: `core/bridge/validation.py`

**Why**: 1097 LOC, 9 classes

**Location Reasoning**: Default placement in core/bridge/ - review manually

**Integration Steps**:

1. **REVIEW**: Read bridge/api/validation.py and understand architecture (1097 LOC, 9 classes, 10 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_validation.py
4. **MOVE**: git mv bridge/api/validation.py core/bridge/validation.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 22. labs.core.ethics.logic.dsl_lite

**Priority Score**: 48.0 | **Quality Score**: 70.0 | **Complexity**: medium (8h) | **Risk**: medium-high

**Current**: `labs/core/ethics/logic/dsl_lite.py`
**Target**: `core/ethics/logic/dsl_lite.py`

**Why**: standard module

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/ethics/logic/dsl_lite.py and understand architecture (522 LOC, 1 classes, 33 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_dsl_lite.py
4. **MOVE**: git mv labs/core/ethics/logic/dsl_lite.py core/ethics/logic/dsl_lite.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 23. labs.core.agi_preparedness.capability_evaluation_framework

**Priority Score**: 48.0 | **Quality Score**: 70.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/core/agi_preparedness/capability_evaluation_framework.py`
**Target**: `core/agi_preparedness/capability_evaluation_framework.py`

**Why**: 1093 LOC, 8 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/agi_preparedness/capability_evaluation_framework.py and understand architecture (1093 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_capability_evaluation_framework.py
4. **MOVE**: git mv labs/core/agi_preparedness/capability_evaluation_framework.py core/agi_preparedness/capability_evaluation_framework.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 8 Completion Checklist

- [ ] All 23 modules moved to target locations
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

**Estimated Effort**: ~282 hours (~35 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_09.md (if batch 8 < 8)
**Previous Batch**: INTEGRATION_GUIDE_07.md (if batch 8 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
