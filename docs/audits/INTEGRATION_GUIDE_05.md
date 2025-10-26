# Integration Guide - Batch 5/8

**Generated**: 2025-10-26 01:24:13
**Batch Size**: 20 modules
**Total Effort**: ~206 hours
**Average Priority**: 69.9
**Complexity**: 11 low, 9 medium
**Strategic Focus**: Multi-Modal Identity & Ethics

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
  "task": "Hidden Gems Integration - Batch 5",
  "batch": 5,
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

## Batch 5 Overview

### Complexity Distribution
- **Low Complexity**: 11 modules (2-4 hours each)
- **Medium Complexity**: 9 modules (6-12 hours each)

### Recommended Execution Strategy

**Mixed Complexity Batch** - Combination of low and medium. Recommended approach:
1. Start with low-complexity modules for momentum
2. Intersperse medium-complexity modules
3. Target: 2-3 modules per day
4. Expected completion: 8 work days (8h/day)

### Priority Range
- **Highest**: 71.0 (websocket_server)
- **Lowest**: 68.6 (lambda_dependa_bot)

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

### 1. labs.governance.identity.auth_web.websocket_server

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (4h) | **Risk**: medium

**Current**: `labs/governance/identity/auth_web/websocket_server.py`
**Target**: `core/governance/identity/auth_web/websocket_server.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/auth_web/websocket_server.py and understand architecture (628 LOC, 4 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_websocket_server.py
4. **MOVE**: git mv labs/governance/identity/auth_web/websocket_server.py core/governance/identity/auth_web/websocket_server.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 2. labs.governance.ethics.guardian_reflector

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (6h) | **Risk**: medium

**Current**: `labs/governance/ethics/guardian_reflector.py`
**Target**: `core/governance/ethics/guardian_reflector.py`

**Why**: 7 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/ethics/guardian_reflector.py and understand architecture (590 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_guardian_reflector.py
4. **MOVE**: git mv labs/governance/ethics/guardian_reflector.py core/governance/ethics/guardian_reflector.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 3. labs.governance.ethics.ethical_decision_maker

**Priority Score**: 71.0 | **Quality Score**: 75.0 | **Complexity**: low (12h) | **Risk**: medium

**Current**: `labs/governance/ethics/ethical_decision_maker.py`
**Target**: `core/governance/ethics/ethical_decision_maker.py`

**Why**: 1042 LOC, 8 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/ethics/ethical_decision_maker.py and understand architecture (1042 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_ethical_decision_maker.py
4. **MOVE**: git mv labs/governance/ethics/ethical_decision_maker.py core/governance/ethics/ethical_decision_maker.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 4. labs.core.orchestration.brain.australian_awareness_engine

**Priority Score**: 71.0 | **Quality Score**: 70.0 | **Complexity**: low (8h) | **Risk**: medium-high

**Current**: `labs/core/orchestration/brain/australian_awareness_engine.py`
**Target**: `core/orchestration/brain/australian_awareness_engine.py`

**Why**: 10 classes

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/orchestration/brain/australian_awareness_engine.py and understand architecture (520 LOC, 10 classes, 2 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_australian_awareness_engine.py
4. **MOVE**: git mv labs/core/orchestration/brain/australian_awareness_engine.py core/orchestration/brain/australian_awareness_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 5. matriz.nodes.validator_node

**Priority Score**: 71.0 | **Quality Score**: 70.0 | **Complexity**: low (10h) | **Risk**: medium-high

**Current**: `matriz/nodes/validator_node.py`
**Target**: `matriz/nodes/validator_node.py`

**Why**: 1202 LOC, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read matriz/nodes/validator_node.py and understand architecture (1202 LOC, 1 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_validator_node.py
4. **MOVE**: git mv matriz/nodes/validator_node.py matriz/nodes/validator_node.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 6. labs.consciousness.core.engine_complete

**Priority Score**: 70.8 | **Quality Score**: 77.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/consciousness/core/engine_complete.py`
**Target**: `matriz/consciousness/core//engine_complete.py`

**Why**: 1177 LOC, 7 classes

**Location Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/core/engine_complete.py and understand architecture (1177 LOC, 7 classes, 5 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_engine_complete.py
4. **MOVE**: git mv labs/consciousness/core/engine_complete.py matriz/consciousness/core//engine_complete.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 7. labs.consciousness.core.engine

**Priority Score**: 70.8 | **Quality Score**: 77.0 | **Complexity**: medium (12h) | **Risk**: medium

**Current**: `labs/consciousness/core/engine.py`
**Target**: `matriz/consciousness/core//engine.py`

**Why**: 1014 LOC

**Location Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/core/engine.py and understand architecture (1014 LOC, 5 classes, 5 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_engine.py
4. **MOVE**: git mv labs/consciousness/core/engine.py matriz/consciousness/core//engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 8. labs.governance.identity.qrg_integration

**Priority Score**: 70.7 | **Quality Score**: 74.2 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/identity/qrg_integration.py`
**Target**: `core/governance/identity/qrg_integration.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/qrg_integration.py and understand architecture (652 LOC, 6 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_qrg_integration.py
4. **MOVE**: git mv labs/governance/identity/qrg_integration.py core/governance/identity/qrg_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 9. labs.consciousness.reflection.EthicalReasoningSystem

**Priority Score**: 70.0 | **Quality Score**: 75.0 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/EthicalReasoningSystem.py`
**Target**: `matriz/consciousness/reflection/EthicalReasoningSystem.py`

**Why**: 1682 LOC, 11 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/EthicalReasoningSystem.py and understand architecture (1682 LOC, 11 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_EthicalReasoningSystem.py
4. **MOVE**: git mv labs/consciousness/reflection/EthicalReasoningSystem.py matriz/consciousness/reflection/EthicalReasoningSystem.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 10. labs.consciousness.reflection.meta_cognitive_orchestrator_alt

**Priority Score**: 70.0 | **Quality Score**: 75.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py`
**Target**: `matriz/consciousness/reflection/meta_cognitive_orchestrator_alt.py`

**Why**: 1056 LOC, 8 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py and understand architecture (1056 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_meta_cognitive_orchestrator_alt.py
4. **MOVE**: git mv labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py matriz/consciousness/reflection/meta_cognitive_orchestrator_alt.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 11. labs.consciousness.reflection.ethical_reasoning_system

**Priority Score**: 70.0 | **Quality Score**: 75.0 | **Complexity**: medium (16h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/ethical_reasoning_system.py`
**Target**: `matriz/consciousness/reflection/ethical_reasoning_system.py`

**Why**: 2120 LOC, 11 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/ethical_reasoning_system.py and understand architecture (2120 LOC, 11 classes, 1 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_ethical_reasoning_system.py
4. **MOVE**: git mv labs/consciousness/reflection/ethical_reasoning_system.py matriz/consciousness/reflection/ethical_reasoning_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 12. labs.consciousness.reflection.core

**Priority Score**: 69.8 | **Quality Score**: 74.6 | **Complexity**: medium (16h) | **Risk**: medium-high

**Current**: `labs/consciousness/reflection/core.py`
**Target**: `matriz/consciousness/reflection/core.py`

**Why**: 1583 LOC, 14 classes

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/core.py and understand architecture (1583 LOC, 14 classes, 4 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_core.py
4. **MOVE**: git mv labs/consciousness/reflection/core.py matriz/consciousness/reflection/core.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 13. labs.consciousness.reflection.privacy_preserving_memory_vault

**Priority Score**: 69.0 | **Quality Score**: 85.0 | **Complexity**: medium (14h) | **Risk**: low

**Current**: `labs/consciousness/reflection/privacy_preserving_memory_vault.py`
**Target**: `matriz/consciousness/reflection/privacy_preserving_memory_vault.py`

**Why**: 1233 LOC, 11 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/privacy_preserving_memory_vault.py and understand architecture (1233 LOC, 11 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_privacy_preserving_memory_vault.py
4. **MOVE**: git mv labs/consciousness/reflection/privacy_preserving_memory_vault.py matriz/consciousness/reflection/privacy_preserving_memory_vault.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 14. labs.governance.auth_guardian_integration

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/governance/auth_guardian_integration.py`
**Target**: `core/governance//auth_guardian_integration.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/auth_guardian_integration.py and understand architecture (555 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_auth_guardian_integration.py
4. **MOVE**: git mv labs/governance/auth_guardian_integration.py core/governance//auth_guardian_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 15. labs.governance.auth_glyph_registry

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/governance/auth_glyph_registry.py`
**Target**: `core/governance//auth_glyph_registry.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/auth_glyph_registry.py and understand architecture (602 LOC, 4 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_auth_glyph_registry.py
4. **MOVE**: git mv labs/governance/auth_glyph_registry.py core/governance//auth_glyph_registry.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 16. labs.governance.auth_cross_module_integration

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: low (6h) | **Risk**: medium-high

**Current**: `labs/governance/auth_cross_module_integration.py`
**Target**: `core/governance//auth_cross_module_integration.py`

**Why**: 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/auth_cross_module_integration.py and understand architecture (689 LOC, 6 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_auth_cross_module_integration.py
4. **MOVE**: git mv labs/governance/auth_cross_module_integration.py core/governance//auth_cross_module_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 17. labs.governance.identity.tools.onboarding_cli

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: low (4h) | **Risk**: medium-high

**Current**: `labs/governance/identity/tools/onboarding_cli.py`
**Target**: `core/governance/identity/tools/onboarding_cli.py`

**Why**: already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/identity/tools/onboarding_cli.py and understand architecture (519 LOC, 1 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_onboarding_cli.py
4. **MOVE**: git mv labs/governance/identity/tools/onboarding_cli.py core/governance/identity/tools/onboarding_cli.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 18. labs.governance.ethics.compliance_monitor

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: low (12h) | **Risk**: medium-high

**Current**: `labs/governance/ethics/compliance_monitor.py`
**Target**: `core/governance/ethics/compliance_monitor.py`

**Why**: 9 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/ethics/compliance_monitor.py and understand architecture (978 LOC, 9 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_compliance_monitor.py
4. **MOVE**: git mv labs/governance/ethics/compliance_monitor.py core/governance/ethics/compliance_monitor.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 19. labs.governance.guardian.compliance_audit_system

**Priority Score**: 69.0 | **Quality Score**: 70.0 | **Complexity**: medium (14h) | **Risk**: medium-high

**Current**: `labs/governance/guardian/compliance_audit_system.py`
**Target**: `core/governance/guardian/compliance_audit_system.py`

**Why**: 11 classes, already imports production code

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/guardian/compliance_audit_system.py and understand architecture (819 LOC, 11 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_compliance_audit_system.py
4. **MOVE**: git mv labs/governance/guardian/compliance_audit_system.py core/governance/guardian/compliance_audit_system.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

### 20. labs.consciousness.reflection.lambda_dependa_bot

**Priority Score**: 68.6 | **Quality Score**: 84.0 | **Complexity**: medium (14h) | **Risk**: medium

**Current**: `labs/consciousness/reflection/lambda_dependa_bot.py`
**Target**: `matriz/consciousness/reflection/lambda_dependa_bot.py`

**Why**: 1570 LOC, 15 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/lambda_dependa_bot.py and understand architecture (1570 LOC, 15 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_lambda_dependa_bot.py
4. **MOVE**: git mv labs/consciousness/reflection/lambda_dependa_bot.py matriz/consciousness/reflection/lambda_dependa_bot.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: T4 message with diagnostic body (baseline deltas, gates, registry updates)

---

## Batch 5 Completion Checklist

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

**Estimated Effort**: ~206 hours (~25 work days at 8h/day)

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

**Next Batch**: INTEGRATION_GUIDE_06.md (if batch 5 < 8)
**Previous Batch**: INTEGRATION_GUIDE_04.md (if batch 5 > 1)
**Master Guide**: INTEGRATION_GUIDE.md (all 193 modules)
