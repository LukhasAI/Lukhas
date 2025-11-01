# Hidden Gems Integration Guide - All 193 Modules

**Generated**: 2025-10-23 00:29:15
**Total Modules**: 193
**Total Effort**: ~1748 hours

**Doctrine**: **Zero Guesswork.** Every action must be based on explicit reads, verified state, or a defined pattern. No assumptions.

### Context Integrity Check (run once per session)

```bash
pwd; git status --porcelain || true
test "$(pwd)" = "/Users/agi_dev/LOCAL-REPOS/Lukhas" || { echo "wrong repo root"; exit 1; }
test -f docs/audits/INTEGRATION_MANIFEST_SUMMARY.md && test -f docs/audits/integration_manifest.json || { echo "missing integration context"; exit 1; }
```

### Mission Trace (short-term objective memory)

When starting an integration run, create/update `.codex_trace.json`:

```json
{
  "session_id": "<auto>",
  "task": "Hidden Gems Integration",
  "phase": 0,
  "last_verified_state": "<timestamp>",
  "expected_artifacts": ["tests/integration/*","docs/architecture/*","moved modules with updated imports"]
}
```

### Acceptance Gates — Integration

1. Module relocated to target lane/path with history preserved
2. Imports updated; `make lane-guard` passes
3. New or adapted **integration tests** added and passing
4. Smoke suite unchanged or improved (≥ baseline)
5. Registry/exports wired; module discoverable by MATRIZ/core
6. Docs updated (architecture notes, registry references)
7. No circular imports or runtime import errors
+1. Commit message matches diagnostic self-report (artifacts listed)

### Operational Awareness

Before integrating each module, write a one-sentence intent to `.codex_trace.json` under that module's entry.

## Complexity Breakdown

- **Low**: 144 modules (~2-4 hours each)
- **Medium**: 49 modules (~6-12 hours each)
- **High**: 0 modules (~12-24 hours each)

## Quick Navigation

- [JSON Manifest](#json-manifest) - Codex-friendly structured data
- [Top 20 Priority](#top-20-priority) - Highest value, lowest risk
- [By Complexity](#by-complexity) - Grouped by integration effort
- [By Target Location](#by-target-location) - Grouped by destination
- [All 193 Modules](#all-193-modules) - Complete detailed list

---

## Top 20 Priority

Highest value, clear integration path, recommended for immediate work.

### 1. labs.core.colonies.ethics_swarm_colony (Score: 93.2)

**Current**: `labs/core/colonies/ethics_swarm_colony.py`
**Target**: `core/colonies/ethics_swarm_colony.py`
**Complexity**: medium (14h)
**Risk**: low

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
9. **COMMIT**: git commit -m "feat(core): integrate ethics_swarm_colony from labs"

---

### 2. labs.governance.guardian_system_integration (Score: 90.0)

**Current**: `labs/governance/guardian_system_integration.py`
**Target**: `core/governance//guardian_system_integration.py`
**Complexity**: low (12h)
**Risk**: low

**Why**: 1062 LOC, 7 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/guardian_system_integration.py and understand architecture (1062 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_guardian_system_integration.py
4. **MOVE**: git mv labs/governance/guardian_system_integration.py core/governance//guardian_system_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate guardian_system_integration from labs"

---

### 3. matriz.core.async_orchestrator (Score: 86.2)

**Current**: `matriz/core/async_orchestrator.py`
**Target**: `matriz/core/async_orchestrator.py`
**Complexity**: low (6h)
**Risk**: low

**Why**: 6 classes, already imports production code, high quality score

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read matriz/core/async_orchestrator.py and understand architecture (543 LOC, 6 classes, 10 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_async_orchestrator.py
4. **MOVE**: git mv matriz/core/async_orchestrator.py matriz/core/async_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate async_orchestrator from labs"

---

### 4. labs.consciousness.awareness.awareness_engine_elevated (Score: 85.0)

**Current**: `labs/consciousness/awareness/awareness_engine_elevated.py`
**Target**: `matriz/consciousness/awareness//awareness_engine_elevated.py`
**Complexity**: medium (16h)
**Risk**: low

**Why**: 1288 LOC, 21 classes, high quality score

**Location Reasoning**: Matches pattern 'consciousness.awareness' - move to matriz/consciousness/awareness/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/awareness/awareness_engine_elevated.py and understand architecture (1288 LOC, 21 classes, 5 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_awareness_engine_elevated.py
4. **MOVE**: git mv labs/consciousness/awareness/awareness_engine_elevated.py matriz/consciousness/awareness//awareness_engine_elevated.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate awareness_engine_elevated from labs"

---

### 5. labs.consciousness.reflection.id_reasoning_engine (Score: 85.0)

**Current**: `labs/consciousness/reflection/id_reasoning_engine.py`
**Target**: `matriz/consciousness/reflection//id_reasoning_engine.py`
**Complexity**: low (12h)
**Risk**: low

**Why**: 1183 LOC, 8 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/id_reasoning_engine.py and understand architecture (1183 LOC, 8 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_id_reasoning_engine.py
4. **MOVE**: git mv labs/consciousness/reflection/id_reasoning_engine.py matriz/consciousness/reflection//id_reasoning_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate id_reasoning_engine from labs"

---

### 6. labs.consciousness.reflection.swarm (Score: 85.0)

**Current**: `labs/consciousness/reflection/swarm.py`
**Target**: `matriz/consciousness/reflection//swarm.py`
**Complexity**: low (12h)
**Risk**: low

**Why**: 1032 LOC, 7 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/swarm.py and understand architecture (1032 LOC, 7 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_swarm.py
4. **MOVE**: git mv labs/consciousness/reflection/swarm.py matriz/consciousness/reflection//swarm.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate swarm from labs"

---

### 7. labs.consciousness.reflection.privacy_preserving_memory_vault (Score: 85.0)

**Current**: `labs/consciousness/reflection/privacy_preserving_memory_vault.py`
**Target**: `matriz/consciousness/reflection//privacy_preserving_memory_vault.py`
**Complexity**: medium (14h)
**Risk**: low

**Why**: 1233 LOC, 11 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/privacy_preserving_memory_vault.py and understand architecture (1233 LOC, 11 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_privacy_preserving_memory_vault.py
4. **MOVE**: git mv labs/consciousness/reflection/privacy_preserving_memory_vault.py matriz/consciousness/reflection//privacy_preserving_memory_vault.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate privacy_preserving_memory_vault from labs"

---

### 8. labs.governance.consent_ledger.ledger_v1 (Score: 85.0)

**Current**: `labs/governance/consent_ledger/ledger_v1.py`
**Target**: `core/governance/consent_ledger/ledger_v1.py`
**Complexity**: low (12h)
**Risk**: low

**Why**: 1140 LOC, 8 classes, already imports production code, high quality score

**Location Reasoning**: Matches pattern 'governance' - move to core/governance/

**Integration Steps**:

1. **REVIEW**: Read labs/governance/consent_ledger/ledger_v1.py and understand architecture (1140 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_ledger_v1.py
4. **MOVE**: git mv labs/governance/consent_ledger/ledger_v1.py core/governance/consent_ledger/ledger_v1.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate ledger_v1 from labs"

---

### 9. labs.core.glyph.glyph_memory_integration (Score: 84.0)

**Current**: `labs/core/glyph/glyph_memory_integration.py`
**Target**: `core/glyph/glyph_memory_integration.py`
**Complexity**: low (12h)
**Risk**: medium

**Why**: 8 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/glyph/glyph_memory_integration.py and understand architecture (911 LOC, 8 classes, 5 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_glyph_memory_integration.py
4. **MOVE**: git mv labs/core/glyph/glyph_memory_integration.py core/glyph/glyph_memory_integration.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate glyph_memory_integration from labs"

---

### 10. labs.consciousness.reflection.lambda_dependa_bot (Score: 84.0)

**Current**: `labs/consciousness/reflection/lambda_dependa_bot.py`
**Target**: `matriz/consciousness/reflection//lambda_dependa_bot.py`
**Complexity**: medium (14h)
**Risk**: medium

**Why**: 1570 LOC, 15 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/lambda_dependa_bot.py and understand architecture (1570 LOC, 15 classes, 1 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_lambda_dependa_bot.py
4. **MOVE**: git mv labs/consciousness/reflection/lambda_dependa_bot.py matriz/consciousness/reflection//lambda_dependa_bot.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate lambda_dependa_bot from labs"

---

### 11. serve.reference_api.public_api_reference (Score: 83.8)

**Current**: `serve/reference_api/public_api_reference.py`
**Target**: `serve/reference_api/public_api_reference.py`
**Complexity**: low (6h)
**Risk**: medium

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
9. **COMMIT**: git commit -m "feat(serve): integrate public_api_reference from labs"

---

### 12. labs.memory.core.unified_memory_orchestrator (Score: 83.3)

**Current**: `labs/memory/core/unified_memory_orchestrator.py`
**Target**: `matriz/memory/core//unified_memory_orchestrator.py`
**Complexity**: low (12h)
**Risk**: medium

**Why**: 1549 LOC, 6 classes, already imports production code

**Location Reasoning**: Matches pattern 'memory.core' - move to matriz/memory/core/

**Integration Steps**:

1. **REVIEW**: Read labs/memory/core/unified_memory_orchestrator.py and understand architecture (1549 LOC, 6 classes, 3 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_unified_memory_orchestrator.py
4. **MOVE**: git mv labs/memory/core/unified_memory_orchestrator.py matriz/memory/core//unified_memory_orchestrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate unified_memory_orchestrator from labs"

---

### 13. labs.consciousness.reflection.orchestration_service (Score: 82.1)

**Current**: `labs/consciousness/reflection/orchestration_service.py`
**Target**: `matriz/consciousness/reflection//orchestration_service.py`
**Complexity**: low (10h)
**Risk**: medium

**Why**: 2026 LOC, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/reflection/orchestration_service.py and understand architecture (2026 LOC, 2 classes, 13 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_orchestration_service.py
4. **MOVE**: git mv labs/consciousness/reflection/orchestration_service.py matriz/consciousness/reflection//orchestration_service.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate orchestration_service from labs"

---

### 14. labs.consciousness.cognitive.adapter (Score: 82.0)

**Current**: `labs/consciousness/cognitive/adapter.py`
**Target**: `matriz/consciousness/cognitive//adapter.py`
**Complexity**: low (12h)
**Risk**: medium

**Why**: 9 classes, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.cognitive' - move to matriz/consciousness/cognitive/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/cognitive/adapter.py and understand architecture (870 LOC, 9 classes, 5 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_adapter.py
4. **MOVE**: git mv labs/consciousness/cognitive/adapter.py matriz/consciousness/cognitive//adapter.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate adapter from labs"

---

### 15. labs.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi (Score: 81.9)

**Current**: `labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py`
**Target**: `matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py`
**Complexity**: medium (14h)
**Risk**: medium

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
9. **COMMIT**: git commit -m "feat(matriz): integrate dream_engine_fastapi from labs"

---

### 16. labs.memory.temporal.hyperspace_dream_simulator (Score: 80.9)

**Current**: `labs/memory/temporal/hyperspace_dream_simulator.py`
**Target**: `matriz/memory/temporal//hyperspace_dream_simulator.py`
**Complexity**: low (12h)
**Risk**: medium

**Why**: 1510 LOC, 9 classes, already imports production code

**Location Reasoning**: Matches pattern 'memory.temporal' - move to matriz/memory/temporal/

**Integration Steps**:

1. **REVIEW**: Read labs/memory/temporal/hyperspace_dream_simulator.py and understand architecture (1510 LOC, 9 classes, 5 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_hyperspace_dream_simulator.py
4. **MOVE**: git mv labs/memory/temporal/hyperspace_dream_simulator.py matriz/memory/temporal//hyperspace_dream_simulator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate hyperspace_dream_simulator from labs"

---

### 17. labs.core.integration.executive_decision_integrator (Score: 80.0)

**Current**: `labs/core/integration/executive_decision_integrator.py`
**Target**: `core/integration/executive_decision_integrator.py`
**Complexity**: low (12h)
**Risk**: medium

**Why**: 1623 LOC, 8 classes, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/integration/executive_decision_integrator.py and understand architecture (1623 LOC, 8 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_executive_decision_integrator.py
4. **MOVE**: git mv labs/core/integration/executive_decision_integrator.py core/integration/executive_decision_integrator.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate executive_decision_integrator from labs"

---

### 18. labs.core.symbolic.vocabulary_creativity_engine (Score: 80.0)

**Current**: `labs/core/symbolic/vocabulary_creativity_engine.py`
**Target**: `core/symbolic/vocabulary_creativity_engine.py`
**Complexity**: low (10h)
**Risk**: medium

**Why**: 1047 LOC, already imports production code

**Location Reasoning**: Already in production structure - verify placement

**Integration Steps**:

1. **REVIEW**: Read labs/core/symbolic/vocabulary_creativity_engine.py and understand architecture (1047 LOC, 2 classes, 0 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_vocabulary_creativity_engine.py
4. **MOVE**: git mv labs/core/symbolic/vocabulary_creativity_engine.py core/symbolic/vocabulary_creativity_engine.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(core): integrate vocabulary_creativity_engine from labs"

---

### 19. labs.memory.folds.memory_fold (Score: 80.0)

**Current**: `labs/memory/folds/memory_fold.py`
**Target**: `matriz/memory/folds//memory_fold.py`
**Complexity**: medium (12h)
**Risk**: medium

**Why**: 1256 LOC

**Location Reasoning**: Matches pattern 'memory.folds' - move to matriz/memory/folds/

**Integration Steps**:

1. **REVIEW**: Read labs/memory/folds/memory_fold.py and understand architecture (1256 LOC, 5 classes, 8 functions)
2. **CHECK_DEPS**: Identify and resolve external dependencies, add core imports if needed
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_memory_fold.py
4. **MOVE**: git mv labs/memory/folds/memory_fold.py matriz/memory/folds//memory_fold.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into appropriate system component (update __init__.py, add exports)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate memory_fold from labs"

---

### 20. labs.consciousness.core.engine_poetic (Score: 80.0)

**Current**: `labs/consciousness/core/engine_poetic.py`
**Target**: `matriz/consciousness/core//engine_poetic.py`
**Complexity**: low (10h)
**Risk**: medium

**Why**: 1441 LOC, already imports production code

**Location Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Integration Steps**:

1. **REVIEW**: Read labs/consciousness/core/engine_poetic.py and understand architecture (1441 LOC, 3 classes, 4 functions)
2. **CHECK_DEPS**: Verify all imports from core/matriz are valid and available
3. **CREATE_TESTS**: Write integration tests in tests/integration/test_engine_poetic.py
4. **MOVE**: git mv labs/consciousness/core/engine_poetic.py matriz/consciousness/core//engine_poetic.py
5. **UPDATE_IMPORTS**: Fix import paths in moved module and any dependent modules
6. **INTEGRATE**: Wire into MATRIZ engine or core system (add to registry, update config)
7. **TEST**: Run pytest tests/integration/ and tests/smoke/ to verify
8. **DOCUMENT**: Update docs/architecture/ with new component location and purpose
9. **COMMIT**: git commit -m "feat(matriz): integrate engine_poetic from labs"

---

## By Complexity

### Low Complexity (144 modules)

| Module | Score | Target | Effort | Risk |
|--------|-------|--------|--------|------|
| guardian_system_integration | 90.0 | /guardian_system_integration.py | 12h | low |
| async_orchestrator | 86.2 | core/async_orchestrator.py | 6h | low |
| id_reasoning_engine | 85.0 | /id_reasoning_engine.py | 12h | low |
| swarm | 85.0 | /swarm.py | 12h | low |
| ledger_v1 | 85.0 | consent_ledger/ledger_v1.py | 12h | low |
| glyph_memory_integration | 84.0 | glyph/glyph_memory_integration.py | 12h | medium |
| public_api_reference | 83.8 | reference_api/public_api_reference.py | 6h | medium |
| unified_memory_orchestrator | 83.3 | /unified_memory_orchestrator.py | 12h | medium |
| orchestration_service | 82.1 | /orchestration_service.py | 10h | medium |
| adapter | 82.0 | /adapter.py | 12h | medium |

*...and 134 more*

### Medium Complexity (49 modules)

| Module | Score | Target | Effort | Risk |
|--------|-------|--------|--------|------|
| ethics_swarm_colony | 93.2 | colonies/ethics_swarm_colony.py | 14h | low |
| awareness_engine_elevated | 85.0 | /awareness_engine_elevated.py | 16h | low |
| privacy_preserving_memory_vault | 85.0 | /privacy_preserving_memory_vault.py | 14h | low |
| lambda_dependa_bot | 84.0 | /lambda_dependa_bot.py | 14h | medium |
| dream_engine_fastapi | 81.9 | engine/dream_engine_fastapi.py | 14h | medium |
| memory_fold | 80.0 | /memory_fold.py | 12h | medium |
| access_control | 80.0 | security/access_control.py | 14h | medium |
| api | 79.7 | bridge/api.py | 14h | medium |
| GlobalInstitutionalCompliantEngine | 79.4 | brain/GlobalInstitutionalCompliantEngine.py | 14h | medium |
| constitutional_compliance_engine | 78.8 | governance/constitutional_compliance_engine.py | 16h | medium |

*...and 39 more*

## By Target Location

### core/ (136 modules)

- **ethics_swarm_colony** (score: 93.2, complexity: medium) → `core/colonies/ethics_swarm_colony.py`
- **guardian_system_integration** (score: 90.0, complexity: low) → `core/governance//guardian_system_integration.py`
- **ledger_v1** (score: 85.0, complexity: low) → `core/governance/consent_ledger/ledger_v1.py`
- **glyph_memory_integration** (score: 84.0, complexity: low) → `core/glyph/glyph_memory_integration.py`
- **executive_decision_integrator** (score: 80.0, complexity: low) → `core/integration/executive_decision_integrator.py`
- *...and 131 more*

### matriz/ (55 modules)

- **async_orchestrator** (score: 86.2, complexity: low) → `matriz/core/async_orchestrator.py`
- **awareness_engine_elevated** (score: 85.0, complexity: medium) → `matriz/consciousness/awareness//awareness_engine_elevated.py`
- **id_reasoning_engine** (score: 85.0, complexity: low) → `matriz/consciousness/reflection//id_reasoning_engine.py`
- **swarm** (score: 85.0, complexity: low) → `matriz/consciousness/reflection//swarm.py`
- **privacy_preserving_memory_vault** (score: 85.0, complexity: medium) → `matriz/consciousness/reflection//privacy_preserving_memory_vault.py`
- *...and 50 more*

### serve/ (2 modules)

- **public_api_reference** (score: 83.8, complexity: low) → `serve/reference_api/public_api_reference.py`
- **integrated_consciousness_api** (score: 77.2, complexity: low) → `serve/api//integrated_consciousness_api.py`

---

## All 193 Modules

Complete list with integration instructions.

### 1. labs.core.colonies.ethics_swarm_colony (Score: 93.2)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/colonies/ethics_swarm_colony.py` |
| Target Location | `core/colonies/ethics_swarm_colony.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | low |
| LOC | 1195 |
| Classes | 14 |
| Functions | 5 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1195 LOC, 14 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/core/colonies/ethics_swarm_colony.py and understand architecture (1195 LOC, 14 classes, 5 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_ethics_swarm_colony.py
4. MOVE: git mv labs/core/colonies/ethics_swarm_colony.py core/colonies/ethics_swarm_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate ethics_swarm_colony from labs"

---

### 2. labs.governance.guardian_system_integration (Score: 90.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/guardian_system_integration.py` |
| Target Location | `core/governance//guardian_system_integration.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | low |
| LOC | 1062 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1062 LOC, 7 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/governance/guardian_system_integration.py and understand architecture (1062 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_guardian_system_integration.py
4. MOVE: git mv labs/governance/guardian_system_integration.py core/governance//guardian_system_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate guardian_system_integration from labs"

---

### 3. matriz.core.async_orchestrator (Score: 86.2)

| Property | Value |
|----------|-------|
| Current Location | `matriz/core/async_orchestrator.py` |
| Target Location | `matriz/core/async_orchestrator.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | low |
| LOC | 543 |
| Classes | 6 |
| Functions | 10 |
| Imports Core | Yes |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 6 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read matriz/core/async_orchestrator.py and understand architecture (543 LOC, 6 classes, 10 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_async_orchestrator.py
4. MOVE: git mv matriz/core/async_orchestrator.py matriz/core/async_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate async_orchestrator from labs"

---

### 4. labs.consciousness.awareness.awareness_engine_elevated (Score: 85.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/awareness/awareness_engine_elevated.py` |
| Target Location | `matriz/consciousness/awareness/awareness_engine_elevated.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | low |
| LOC | 1288 |
| Classes | 21 |
| Functions | 5 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.awareness' - move to matriz/consciousness/awareness/

**Complexity Rationale**: 1288 LOC, 21 classes, high quality score

**Integration Steps**:

1. REVIEW: Read labs/consciousness/awareness/awareness_engine_elevated.py and understand architecture (1288 LOC, 21 classes, 5 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_awareness_engine_elevated.py
4. MOVE: git mv labs/consciousness/awareness/awareness_engine_elevated.py matriz/consciousness/awareness/awareness_engine_elevated.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate awareness_engine_elevated from labs"

---

### 5. labs.consciousness.reflection.id_reasoning_engine (Score: 85.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/id_reasoning_engine.py` |
| Target Location | `matriz/consciousness/reflection//id_reasoning_engine.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | low |
| LOC | 1183 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1183 LOC, 8 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/id_reasoning_engine.py and understand architecture (1183 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_id_reasoning_engine.py
4. MOVE: git mv labs/consciousness/reflection/id_reasoning_engine.py matriz/consciousness/reflection//id_reasoning_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate id_reasoning_engine from labs"

---

### 6. labs.consciousness.reflection.swarm (Score: 85.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/swarm.py` |
| Target Location | `matriz/consciousness/reflection//swarm.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | low |
| LOC | 1032 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1032 LOC, 7 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/swarm.py and understand architecture (1032 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_swarm.py
4. MOVE: git mv labs/consciousness/reflection/swarm.py matriz/consciousness/reflection//swarm.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate swarm from labs"

---

### 7. labs.consciousness.reflection.privacy_preserving_memory_vault (Score: 85.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/privacy_preserving_memory_vault.py` |
| Target Location | `matriz/consciousness/reflection//privacy_preserving_memory_vault.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | low |
| LOC | 1233 |
| Classes | 11 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1233 LOC, 11 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/privacy_preserving_memory_vault.py and understand architecture (1233 LOC, 11 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_privacy_preserving_memory_vault.py
4. MOVE: git mv labs/consciousness/reflection/privacy_preserving_memory_vault.py matriz/consciousness/reflection//privacy_preserving_memory_vault.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate privacy_preserving_memory_vault from labs"

---

### 8. labs.governance.consent_ledger.ledger_v1 (Score: 85.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/consent_ledger/ledger_v1.py` |
| Target Location | `core/governance/consent_ledger/ledger_v1.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | low |
| LOC | 1140 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1140 LOC, 8 classes, already imports production code, high quality score

**Integration Steps**:

1. REVIEW: Read labs/governance/consent_ledger/ledger_v1.py and understand architecture (1140 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_ledger_v1.py
4. MOVE: git mv labs/governance/consent_ledger/ledger_v1.py core/governance/consent_ledger/ledger_v1.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate ledger_v1 from labs"

---

### 9. labs.core.glyph.glyph_memory_integration (Score: 84.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/glyph/glyph_memory_integration.py` |
| Target Location | `core/glyph/glyph_memory_integration.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 911 |
| Classes | 8 |
| Functions | 5 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/glyph/glyph_memory_integration.py and understand architecture (911 LOC, 8 classes, 5 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_glyph_memory_integration.py
4. MOVE: git mv labs/core/glyph/glyph_memory_integration.py core/glyph/glyph_memory_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate glyph_memory_integration from labs"

---

### 10. labs.consciousness.reflection.lambda_dependa_bot (Score: 84.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/lambda_dependa_bot.py` |
| Target Location | `matriz/consciousness/reflection//lambda_dependa_bot.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1570 |
| Classes | 15 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1570 LOC, 15 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/lambda_dependa_bot.py and understand architecture (1570 LOC, 15 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_lambda_dependa_bot.py
4. MOVE: git mv labs/consciousness/reflection/lambda_dependa_bot.py matriz/consciousness/reflection//lambda_dependa_bot.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate lambda_dependa_bot from labs"

---

### 11. serve.reference_api.public_api_reference (Score: 83.8)

| Property | Value |
|----------|-------|
| Current Location | `serve/reference_api/public_api_reference.py` |
| Target Location | `serve/reference_api/public_api_reference.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 530 |
| Classes | 7 |
| Functions | 16 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read serve/reference_api/public_api_reference.py and understand architecture (530 LOC, 7 classes, 16 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_public_api_reference.py
4. MOVE: git mv serve/reference_api/public_api_reference.py serve/reference_api/public_api_reference.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(serve): integrate public_api_reference from labs"

---

### 12. labs.memory.core.unified_memory_orchestrator (Score: 83.3)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/core/unified_memory_orchestrator.py` |
| Target Location | `matriz/memory/core//unified_memory_orchestrator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1549 |
| Classes | 6 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'memory.core' - move to matriz/memory/core/

**Complexity Rationale**: 1549 LOC, 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/core/unified_memory_orchestrator.py and understand architecture (1549 LOC, 6 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_unified_memory_orchestrator.py
4. MOVE: git mv labs/memory/core/unified_memory_orchestrator.py matriz/memory/core//unified_memory_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate unified_memory_orchestrator from labs"

---

### 13. labs.consciousness.reflection.orchestration_service (Score: 82.1)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/orchestration_service.py` |
| Target Location | `matriz/consciousness/reflection//orchestration_service.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 2026 |
| Classes | 2 |
| Functions | 13 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 2026 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/orchestration_service.py and understand architecture (2026 LOC, 2 classes, 13 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_orchestration_service.py
4. MOVE: git mv labs/consciousness/reflection/orchestration_service.py matriz/consciousness/reflection//orchestration_service.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate orchestration_service from labs"

---

### 14. labs.consciousness.cognitive.adapter (Score: 82.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/cognitive/adapter.py` |
| Target Location | `matriz/consciousness/cognitive//adapter.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 870 |
| Classes | 9 |
| Functions | 5 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.cognitive' - move to matriz/consciousness/cognitive/

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/cognitive/adapter.py and understand architecture (870 LOC, 9 classes, 5 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_adapter.py
4. MOVE: git mv labs/consciousness/cognitive/adapter.py matriz/consciousness/cognitive//adapter.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate adapter from labs"

---

### 15. labs.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi (Score: 81.9)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py` |
| Target Location | `matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 804 |
| Classes | 13 |
| Functions | 10 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Complexity Rationale**: 13 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py and understand architecture (804 LOC, 13 classes, 10 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dream_engine_fastapi.py
4. MOVE: git mv labs/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py matriz/consciousness/dream/oneiric/oneiric_core/engine/dream_engine_fastapi.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate dream_engine_fastapi from labs"

---

### 16. labs.memory.temporal.hyperspace_dream_simulator (Score: 80.9)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/temporal/hyperspace_dream_simulator.py` |
| Target Location | `matriz/memory/temporal//hyperspace_dream_simulator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1510 |
| Classes | 9 |
| Functions | 5 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'memory.temporal' - move to matriz/memory/temporal/

**Complexity Rationale**: 1510 LOC, 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/temporal/hyperspace_dream_simulator.py and understand architecture (1510 LOC, 9 classes, 5 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_hyperspace_dream_simulator.py
4. MOVE: git mv labs/memory/temporal/hyperspace_dream_simulator.py matriz/memory/temporal//hyperspace_dream_simulator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate hyperspace_dream_simulator from labs"

---

### 17. labs.core.integration.executive_decision_integrator (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/integration/executive_decision_integrator.py` |
| Target Location | `core/integration/executive_decision_integrator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1623 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1623 LOC, 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/integration/executive_decision_integrator.py and understand architecture (1623 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_executive_decision_integrator.py
4. MOVE: git mv labs/core/integration/executive_decision_integrator.py core/integration/executive_decision_integrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate executive_decision_integrator from labs"

---

### 18. labs.core.symbolic.vocabulary_creativity_engine (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/symbolic/vocabulary_creativity_engine.py` |
| Target Location | `core/symbolic/vocabulary_creativity_engine.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 1047 |
| Classes | 2 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1047 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/symbolic/vocabulary_creativity_engine.py and understand architecture (1047 LOC, 2 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_vocabulary_creativity_engine.py
4. MOVE: git mv labs/core/symbolic/vocabulary_creativity_engine.py core/symbolic/vocabulary_creativity_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate vocabulary_creativity_engine from labs"

---

### 19. labs.memory.folds.memory_fold (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/folds/memory_fold.py` |
| Target Location | `matriz/memory/folds//memory_fold.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1256 |
| Classes | 5 |
| Functions | 8 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'memory.folds' - move to matriz/memory/folds/

**Complexity Rationale**: 1256 LOC

**Integration Steps**:

1. REVIEW: Read labs/memory/folds/memory_fold.py and understand architecture (1256 LOC, 5 classes, 8 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_memory_fold.py
4. MOVE: git mv labs/memory/folds/memory_fold.py matriz/memory/folds//memory_fold.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate memory_fold from labs"

---

### 20. labs.consciousness.core.engine_poetic (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/core/engine_poetic.py` |
| Target Location | `matriz/consciousness/core//engine_poetic.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 1441 |
| Classes | 3 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Complexity Rationale**: 1441 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/core/engine_poetic.py and understand architecture (1441 LOC, 3 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_engine_poetic.py
4. MOVE: git mv labs/consciousness/core/engine_poetic.py matriz/consciousness/core//engine_poetic.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate engine_poetic from labs"

---

### 21. labs.consciousness.reasoning.id_reasoning_engine (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reasoning/id_reasoning_engine.py` |
| Target Location | `core/consciousness/id_reasoning_engine.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 706 |
| Classes | 9 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reasoning/id_reasoning_engine.py and understand architecture (706 LOC, 9 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_id_reasoning_engine.py
4. MOVE: git mv labs/consciousness/reasoning/id_reasoning_engine.py core/consciousness/id_reasoning_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate id_reasoning_engine from labs"

---

### 22. labs.consciousness.reflection.memory_hub (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/memory_hub.py` |
| Target Location | `matriz/consciousness/reflection//memory_hub.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 1096 |
| Classes | 1 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1096 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/memory_hub.py and understand architecture (1096 LOC, 1 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_memory_hub.py
4. MOVE: git mv labs/consciousness/reflection/memory_hub.py matriz/consciousness/reflection//memory_hub.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate memory_hub from labs"

---

### 23. labs.consciousness.reflection.dreamseed_unified (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/dreamseed_unified.py` |
| Target Location | `matriz/consciousness/reflection//dreamseed_unified.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 694 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/dreamseed_unified.py and understand architecture (694 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dreamseed_unified.py
4. MOVE: git mv labs/consciousness/reflection/dreamseed_unified.py matriz/consciousness/reflection//dreamseed_unified.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate dreamseed_unified from labs"

---

### 24. labs.orchestration.gpt_colony_orchestrator (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/orchestration/gpt_colony_orchestrator.py` |
| Target Location | `core/orchestration/gpt_colony_orchestrator.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 548 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/orchestration/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/orchestration/gpt_colony_orchestrator.py and understand architecture (548 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_gpt_colony_orchestrator.py
4. MOVE: git mv labs/orchestration/gpt_colony_orchestrator.py core/orchestration/gpt_colony_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate gpt_colony_orchestrator from labs"

---

### 25. labs.governance.security.access_control (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/security/access_control.py` |
| Target Location | `core/governance/security/access_control.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1102 |
| Classes | 14 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1102 LOC, 14 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/security/access_control.py and understand architecture (1102 LOC, 14 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_access_control.py
4. MOVE: git mv labs/governance/security/access_control.py core/governance/security/access_control.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate access_control from labs"

---

### 26. core.oracle_nervous_system (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `core/oracle_nervous_system.py` |
| Target Location | `core/oracle_nervous_system.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 705 |
| Classes | 6 |
| Functions | 6 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/oracle_nervous_system.py and understand architecture (705 LOC, 6 classes, 6 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_oracle_nervous_system.py
4. MOVE: git mv core/oracle_nervous_system.py core/oracle_nervous_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate oracle_nervous_system from labs"

---

### 27. core.utils.orchestration_energy_aware_execution_planner (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `core/utils/orchestration_energy_aware_execution_planner.py` |
| Target Location | `core/utils/orchestration_energy_aware_execution_planner.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1254 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1254 LOC, 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/utils/orchestration_energy_aware_execution_planner.py and understand architecture (1254 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_orchestration_energy_aware_execution_planner.py
4. MOVE: git mv core/utils/orchestration_energy_aware_execution_planner.py core/utils/orchestration_energy_aware_execution_planner.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate orchestration_energy_aware_execution_planner from labs"

---

### 28. core.symbolic.symbolic_anomaly_explorer (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `core/symbolic/symbolic_anomaly_explorer.py` |
| Target Location | `core/symbolic/symbolic_anomaly_explorer.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1112 |
| Classes | 7 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1112 LOC, 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/symbolic/symbolic_anomaly_explorer.py and understand architecture (1112 LOC, 7 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_anomaly_explorer.py
4. MOVE: git mv core/symbolic/symbolic_anomaly_explorer.py core/symbolic/symbolic_anomaly_explorer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate symbolic_anomaly_explorer from labs"

---

### 29. matriz.core.memory_system (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `matriz/core/memory_system.py` |
| Target Location | `matriz/core/memory_system.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1034 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1034 LOC, 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read matriz/core/memory_system.py and understand architecture (1034 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_memory_system.py
4. MOVE: git mv matriz/core/memory_system.py matriz/core/memory_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate memory_system from labs"

---

### 30. matriz.interfaces.api_server (Score: 80.0)

| Property | Value |
|----------|-------|
| Current Location | `matriz/interfaces/api_server.py` |
| Target Location | `matriz/interfaces/api_server.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 622 |
| Classes | 6 |
| Functions | 20 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read matriz/interfaces/api_server.py and understand architecture (622 LOC, 6 classes, 20 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_api_server.py
4. MOVE: git mv matriz/interfaces/api_server.py matriz/interfaces/api_server.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate api_server from labs"

---

### 31. bridge.api.api (Score: 79.7)

| Property | Value |
|----------|-------|
| Current Location | `bridge/api/api.py` |
| Target Location | `core/bridge/api.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1270 |
| Classes | 13 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 1270 LOC, 13 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read bridge/api/api.py and understand architecture (1270 LOC, 13 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_api.py
4. MOVE: git mv bridge/api/api.py core/bridge/api.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate api from labs"

---

### 32. labs.core.orchestration.brain.GlobalInstitutionalCompliantEngine (Score: 79.4)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py` |
| Target Location | `core/orchestration/brain/GlobalInstitutionalCompliantEngine.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1180 |
| Classes | 9 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1180 LOC, 9 classes

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py and understand architecture (1180 LOC, 9 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_GlobalInstitutionalCompliantEngine.py
4. MOVE: git mv labs/core/orchestration/brain/GlobalInstitutionalCompliantEngine.py core/orchestration/brain/GlobalInstitutionalCompliantEngine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate GlobalInstitutionalCompliantEngine from labs"

---

### 33. labs.consciousness.reflection.reflection_layer (Score: 79.2)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/reflection_layer.py` |
| Target Location | `matriz/consciousness/reflection//reflection_layer.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1509 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1509 LOC, 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/reflection_layer.py and understand architecture (1509 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_reflection_layer.py
4. MOVE: git mv labs/consciousness/reflection/reflection_layer.py matriz/consciousness/reflection//reflection_layer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate reflection_layer from labs"

---

### 34. labs.core.governance.constitutional_compliance_engine (Score: 78.8)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/governance/constitutional_compliance_engine.py` |
| Target Location | `core/governance/constitutional_compliance_engine.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1310 |
| Classes | 12 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1310 LOC, 12 classes

**Integration Steps**:

1. REVIEW: Read labs/core/governance/constitutional_compliance_engine.py and understand architecture (1310 LOC, 12 classes, 4 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_constitutional_compliance_engine.py
4. MOVE: git mv labs/core/governance/constitutional_compliance_engine.py core/governance/constitutional_compliance_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate constitutional_compliance_engine from labs"

---

### 35. bridge.api_legacy.core.dream_commerce (Score: 78.8)

| Property | Value |
|----------|-------|
| Current Location | `bridge/api_legacy/core/dream_commerce.py` |
| Target Location | `core/bridge/dream_commerce.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 852 |
| Classes | 10 |
| Functions | 8 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read bridge/api_legacy/core/dream_commerce.py and understand architecture (852 LOC, 10 classes, 8 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dream_commerce.py
4. MOVE: git mv bridge/api_legacy/core/dream_commerce.py core/bridge/dream_commerce.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dream_commerce from labs"

---

### 36. labs.core.governance.guardian_system_2 (Score: 78.7)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/governance/guardian_system_2.py` |
| Target Location | `core/governance/guardian_system_2.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1127 |
| Classes | 15 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1127 LOC, 15 classes

**Integration Steps**:

1. REVIEW: Read labs/core/governance/guardian_system_2.py and understand architecture (1127 LOC, 15 classes, 4 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_guardian_system_2.py
4. MOVE: git mv labs/core/governance/guardian_system_2.py core/governance/guardian_system_2.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate guardian_system_2 from labs"

---

### 37. labs.core.api.service_stubs (Score: 78.6)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/api/service_stubs.py` |
| Target Location | `core/api/service_stubs.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 693 |
| Classes | 7 |
| Functions | 7 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/api/service_stubs.py and understand architecture (693 LOC, 7 classes, 7 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_service_stubs.py
4. MOVE: git mv labs/core/api/service_stubs.py core/api/service_stubs.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate service_stubs from labs"

---

### 38. labs.core.verifold.verifold_unified (Score: 78.3)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/verifold/verifold_unified.py` |
| Target Location | `core/verifold/verifold_unified.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 518 |
| Classes | 5 |
| Functions | 6 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/verifold/verifold_unified.py and understand architecture (518 LOC, 5 classes, 6 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_verifold_unified.py
4. MOVE: git mv labs/core/verifold/verifold_unified.py core/verifold/verifold_unified.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate verifold_unified from labs"

---

### 39. labs.consciousness.reflection.symbolic_drift_analyzer (Score: 77.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/symbolic_drift_analyzer.py` |
| Target Location | `matriz/consciousness/reflection//symbolic_drift_analyzer.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1032 |
| Classes | 6 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1032 LOC, 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/symbolic_drift_analyzer.py and understand architecture (1032 LOC, 6 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_drift_analyzer.py
4. MOVE: git mv labs/consciousness/reflection/symbolic_drift_analyzer.py matriz/consciousness/reflection//symbolic_drift_analyzer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate symbolic_drift_analyzer from labs"

---

### 40. api.integrated_consciousness_api (Score: 77.2)

| Property | Value |
|----------|-------|
| Current Location | `api/integrated_consciousness_api.py` |
| Target Location | `serve/api//integrated_consciousness_api.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 637 |
| Classes | 7 |
| Functions | 15 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'api' - move to serve/api/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read api/integrated_consciousness_api.py and understand architecture (637 LOC, 7 classes, 15 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_integrated_consciousness_api.py
4. MOVE: git mv api/integrated_consciousness_api.py serve/api//integrated_consciousness_api.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(serve): integrate integrated_consciousness_api from labs"

---

### 41. labs.consciousness.core.engine_complete (Score: 77.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/core/engine_complete.py` |
| Target Location | `matriz/consciousness/core//engine_complete.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1177 |
| Classes | 7 |
| Functions | 5 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Complexity Rationale**: 1177 LOC, 7 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/core/engine_complete.py and understand architecture (1177 LOC, 7 classes, 5 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_engine_complete.py
4. MOVE: git mv labs/consciousness/core/engine_complete.py matriz/consciousness/core//engine_complete.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate engine_complete from labs"

---

### 42. labs.consciousness.core.engine (Score: 77.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/core/engine.py` |
| Target Location | `matriz/consciousness/core//engine.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1014 |
| Classes | 5 |
| Functions | 5 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.core' - move to matriz/consciousness/core/

**Complexity Rationale**: 1014 LOC

**Integration Steps**:

1. REVIEW: Read labs/consciousness/core/engine.py and understand architecture (1014 LOC, 5 classes, 5 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_engine.py
4. MOVE: git mv labs/consciousness/core/engine.py matriz/consciousness/core//engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate engine from labs"

---

### 43. labs.consciousness.reflection.cognitive_architecture_controller (Score: 76.2)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/cognitive_architecture_controller.py` |
| Target Location | `matriz/consciousness/reflection//cognitive_architecture_controller.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1584 |
| Classes | 18 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1584 LOC, 18 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/cognitive_architecture_controller.py and understand architecture (1584 LOC, 18 classes, 4 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_cognitive_architecture_controller.py
4. MOVE: git mv labs/consciousness/reflection/cognitive_architecture_controller.py matriz/consciousness/reflection//cognitive_architecture_controller.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate cognitive_architecture_controller from labs"

---

### 44. labs.core.identity_aware_base_colony (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity_aware_base_colony.py` |
| Target Location | `core/identity_aware_base_colony.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 613 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/identity_aware_base_colony.py and understand architecture (613 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_identity_aware_base_colony.py
4. MOVE: git mv labs/core/identity_aware_base_colony.py core/identity_aware_base_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate identity_aware_base_colony from labs"

---

### 45. labs.core.colonies.oracle_colony (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/colonies/oracle_colony.py` |
| Target Location | `core/colonies/oracle_colony.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 507 |
| Classes | 4 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/colonies/oracle_colony.py and understand architecture (507 LOC, 4 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_oracle_colony.py
4. MOVE: git mv labs/core/colonies/oracle_colony.py core/colonies/oracle_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate oracle_colony from labs"

---

### 46. labs.core.identity.constitutional_ai_compliance (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/constitutional_ai_compliance.py` |
| Target Location | `core/identity/constitutional_ai_compliance.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1038 |
| Classes | 10 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1038 LOC, 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/identity/constitutional_ai_compliance.py and understand architecture (1038 LOC, 10 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_constitutional_ai_compliance.py
4. MOVE: git mv labs/core/identity/constitutional_ai_compliance.py core/identity/constitutional_ai_compliance.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate constitutional_ai_compliance from labs"

---

### 47. labs.core.observability.alerting_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/observability/alerting_system.py` |
| Target Location | `core/observability/alerting_system.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1128 |
| Classes | 11 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1128 LOC, 11 classes

**Integration Steps**:

1. REVIEW: Read labs/core/observability/alerting_system.py and understand architecture (1128 LOC, 11 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_alerting_system.py
4. MOVE: git mv labs/core/observability/alerting_system.py core/observability/alerting_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate alerting_system from labs"

---

### 48. labs.core.compliance.democratic_oversight (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/compliance/democratic_oversight.py` |
| Target Location | `core/compliance/democratic_oversight.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1177 |
| Classes | 9 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1177 LOC, 9 classes

**Integration Steps**:

1. REVIEW: Read labs/core/compliance/democratic_oversight.py and understand architecture (1177 LOC, 9 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_democratic_oversight.py
4. MOVE: git mv labs/core/compliance/democratic_oversight.py core/compliance/democratic_oversight.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate democratic_oversight from labs"

---

### 49. labs.core.compliance.global_compliance_manager (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/compliance/global_compliance_manager.py` |
| Target Location | `core/compliance/global_compliance_manager.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1018 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1018 LOC, 8 classes

**Integration Steps**:

1. REVIEW: Read labs/core/compliance/global_compliance_manager.py and understand architecture (1018 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_global_compliance_manager.py
4. MOVE: git mv labs/core/compliance/global_compliance_manager.py core/compliance/global_compliance_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate global_compliance_manager from labs"

---

### 50. labs.core.audit.audit_decision_embedding_engine (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/audit/audit_decision_embedding_engine.py` |
| Target Location | `core/audit/audit_decision_embedding_engine.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 619 |
| Classes | 10 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/audit/audit_decision_embedding_engine.py and understand architecture (619 LOC, 10 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_audit_decision_embedding_engine.py
4. MOVE: git mv labs/core/audit/audit_decision_embedding_engine.py core/audit/audit_decision_embedding_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate audit_decision_embedding_engine from labs"

---

### 51. labs.core.orchestration.golden_trio.trio_orchestrator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/golden_trio/trio_orchestrator.py` |
| Target Location | `core/orchestration/golden_trio/trio_orchestrator.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 552 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/golden_trio/trio_orchestrator.py and understand architecture (552 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_trio_orchestrator.py
4. MOVE: git mv labs/core/orchestration/golden_trio/trio_orchestrator.py core/orchestration/golden_trio/trio_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate trio_orchestrator from labs"

---

### 52. labs.core.orchestration.brain.autonomous_github_manager (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/autonomous_github_manager.py` |
| Target Location | `core/orchestration/brain/autonomous_github_manager.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 582 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/autonomous_github_manager.py and understand architecture (582 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_autonomous_github_manager.py
4. MOVE: git mv labs/core/orchestration/brain/autonomous_github_manager.py core/orchestration/brain/autonomous_github_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate autonomous_github_manager from labs"

---

### 53. labs.core.orchestration.brain.abstract_reasoning.interface (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/abstract_reasoning/interface.py` |
| Target Location | `core/orchestration/brain/abstract_reasoning/interface.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 571 |
| Classes | 1 |
| Functions | 6 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/abstract_reasoning/interface.py and understand architecture (571 LOC, 1 classes, 6 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_interface.py
4. MOVE: git mv labs/core/orchestration/brain/abstract_reasoning/interface.py core/orchestration/brain/abstract_reasoning/interface.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate interface from labs"

---

### 54. labs.core.symbolic.vision_vocabulary (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/symbolic/vision_vocabulary.py` |
| Target Location | `core/symbolic/vision_vocabulary.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 1047 |
| Classes | 2 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1047 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/symbolic/vision_vocabulary.py and understand architecture (1047 LOC, 2 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_vision_vocabulary.py
4. MOVE: git mv labs/core/symbolic/vision_vocabulary.py core/symbolic/vision_vocabulary.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate vision_vocabulary from labs"

---

### 55. labs.core.symbolic.symbolic_validator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/symbolic/symbolic_validator.py` |
| Target Location | `core/symbolic/symbolic_validator.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1114 |
| Classes | 11 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1114 LOC, 11 classes

**Integration Steps**:

1. REVIEW: Read labs/core/symbolic/symbolic_validator.py and understand architecture (1114 LOC, 11 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_validator.py
4. MOVE: git mv labs/core/symbolic/symbolic_validator.py core/symbolic/symbolic_validator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate symbolic_validator from labs"

---

### 56. labs.memory.systems.replay_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/systems/replay_system.py` |
| Target Location | `core/memory/replay_system.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 573 |
| Classes | 8 |
| Functions | 5 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/systems/replay_system.py and understand architecture (573 LOC, 8 classes, 5 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_replay_system.py
4. MOVE: git mv labs/memory/systems/replay_system.py core/memory/replay_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate replay_system from labs"

---

### 57. labs.consciousness.creativity.haiku_generator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/creativity/haiku_generator.py` |
| Target Location | `core/consciousness/haiku_generator.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 912 |
| Classes | 4 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/creativity/haiku_generator.py and understand architecture (912 LOC, 4 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_haiku_generator.py
4. MOVE: git mv labs/consciousness/creativity/haiku_generator.py core/consciousness/haiku_generator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate haiku_generator from labs"

---

### 58. labs.consciousness.unified.symbolic_bio_symbolic_orchestrator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py` |
| Target Location | `core/consciousness/symbolic_bio_symbolic_orchestrator.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 697 |
| Classes | 3 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py and understand architecture (697 LOC, 3 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_bio_symbolic_orchestrator.py
4. MOVE: git mv labs/consciousness/unified/symbolic_bio_symbolic_orchestrator.py core/consciousness/symbolic_bio_symbolic_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate symbolic_bio_symbolic_orchestrator from labs"

---

### 59. labs.consciousness.states.simulation_controller (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/states/simulation_controller.py` |
| Target Location | `core/consciousness/simulation_controller.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 515 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/states/simulation_controller.py and understand architecture (515 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_simulation_controller.py
4. MOVE: git mv labs/consciousness/states/simulation_controller.py core/consciousness/simulation_controller.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate simulation_controller from labs"

---

### 60. labs.consciousness.states.async_client (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/states/async_client.py` |
| Target Location | `core/consciousness/async_client.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium |
| LOC | 3365 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 3365 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/states/async_client.py and understand architecture (3365 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_async_client.py
4. MOVE: git mv labs/consciousness/states/async_client.py core/consciousness/async_client.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate async_client from labs"

---

### 61. labs.consciousness.systems.unified_consciousness_engine (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/systems/unified_consciousness_engine.py` |
| Target Location | `core/consciousness/unified_consciousness_engine.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 748 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/systems/unified_consciousness_engine.py and understand architecture (748 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_unified_consciousness_engine.py
4. MOVE: git mv labs/consciousness/systems/unified_consciousness_engine.py core/consciousness/unified_consciousness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate unified_consciousness_engine from labs"

---

### 62. labs.consciousness.interfaces.natural_language_interface (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/interfaces/natural_language_interface.py` |
| Target Location | `core/consciousness/natural_language_interface.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 897 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/interfaces/natural_language_interface.py and understand architecture (897 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_natural_language_interface.py
4. MOVE: git mv labs/consciousness/interfaces/natural_language_interface.py core/consciousness/natural_language_interface.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate natural_language_interface from labs"

---

### 63. labs.consciousness.reflection.integrated_safety_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/integrated_safety_system.py` |
| Target Location | `matriz/consciousness/reflection//integrated_safety_system.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 849 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/integrated_safety_system.py and understand architecture (849 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_integrated_safety_system.py
4. MOVE: git mv labs/consciousness/reflection/integrated_safety_system.py matriz/consciousness/reflection//integrated_safety_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate integrated_safety_system from labs"

---

### 64. labs.consciousness.reflection.EthicalReasoningSystem (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/EthicalReasoningSystem.py` |
| Target Location | `matriz/consciousness/reflection//EthicalReasoningSystem.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1682 |
| Classes | 11 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1682 LOC, 11 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/EthicalReasoningSystem.py and understand architecture (1682 LOC, 11 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_EthicalReasoningSystem.py
4. MOVE: git mv labs/consciousness/reflection/EthicalReasoningSystem.py matriz/consciousness/reflection//EthicalReasoningSystem.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate EthicalReasoningSystem from labs"

---

### 65. labs.consciousness.reflection.visionary_orchestrator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/visionary_orchestrator.py` |
| Target Location | `matriz/consciousness/reflection//visionary_orchestrator.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 783 |
| Classes | 5 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/visionary_orchestrator.py and understand architecture (783 LOC, 5 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_visionary_orchestrator.py
4. MOVE: git mv labs/consciousness/reflection/visionary_orchestrator.py matriz/consciousness/reflection//visionary_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate visionary_orchestrator from labs"

---

### 66. labs.consciousness.reflection.master_orchestrator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/master_orchestrator.py` |
| Target Location | `matriz/consciousness/reflection//master_orchestrator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 989 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/master_orchestrator.py and understand architecture (989 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_master_orchestrator.py
4. MOVE: git mv labs/consciousness/reflection/master_orchestrator.py matriz/consciousness/reflection//master_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate master_orchestrator from labs"

---

### 67. labs.consciousness.reflection.content_enterprise_orchestrator (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/content_enterprise_orchestrator.py` |
| Target Location | `matriz/consciousness/reflection//content_enterprise_orchestrator.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 868 |
| Classes | 13 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 13 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/content_enterprise_orchestrator.py and understand architecture (868 LOC, 13 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_content_enterprise_orchestrator.py
4. MOVE: git mv labs/consciousness/reflection/content_enterprise_orchestrator.py matriz/consciousness/reflection//content_enterprise_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate content_enterprise_orchestrator from labs"

---

### 68. labs.consciousness.reflection.meta_cognitive_orchestrator_alt (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py` |
| Target Location | `matriz/consciousness/reflection//meta_cognitive_orchestrator_alt.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1056 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1056 LOC, 8 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py and understand architecture (1056 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_meta_cognitive_orchestrator_alt.py
4. MOVE: git mv labs/consciousness/reflection/meta_cognitive_orchestrator_alt.py matriz/consciousness/reflection//meta_cognitive_orchestrator_alt.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate meta_cognitive_orchestrator_alt from labs"

---

### 69. labs.consciousness.reflection.ethical_reasoning_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/ethical_reasoning_system.py` |
| Target Location | `matriz/consciousness/reflection//ethical_reasoning_system.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 2120 |
| Classes | 11 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 2120 LOC, 11 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/ethical_reasoning_system.py and understand architecture (2120 LOC, 11 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_ethical_reasoning_system.py
4. MOVE: git mv labs/consciousness/reflection/ethical_reasoning_system.py matriz/consciousness/reflection//ethical_reasoning_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate ethical_reasoning_system from labs"

---

### 70. labs.consciousness.reflection.actor_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/actor_system.py` |
| Target Location | `matriz/consciousness/reflection//actor_system.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 628 |
| Classes | 7 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/actor_system.py and understand architecture (628 LOC, 7 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_actor_system.py
4. MOVE: git mv labs/consciousness/reflection/actor_system.py matriz/consciousness/reflection//actor_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate actor_system from labs"

---

### 71. labs.consciousness.reflection.symbolic_weaver (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/symbolic_weaver.py` |
| Target Location | `matriz/consciousness/reflection//symbolic_weaver.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium |
| LOC | 1832 |
| Classes | 11 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1832 LOC, 11 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/symbolic_weaver.py and understand architecture (1832 LOC, 11 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_weaver.py
4. MOVE: git mv labs/consciousness/reflection/symbolic_weaver.py matriz/consciousness/reflection//symbolic_weaver.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate symbolic_weaver from labs"

---

### 72. labs.governance.identity.unified_login_interface (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/unified_login_interface.py` |
| Target Location | `core/governance/identity/unified_login_interface.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 790 |
| Classes | 7 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/unified_login_interface.py and understand architecture (790 LOC, 7 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_unified_login_interface.py
4. MOVE: git mv labs/governance/identity/unified_login_interface.py core/governance/identity/unified_login_interface.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate unified_login_interface from labs"

---

### 73. labs.governance.identity.auth_backend.websocket_server (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/auth_backend/websocket_server.py` |
| Target Location | `core/governance/identity/auth_backend/websocket_server.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 628 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/auth_backend/websocket_server.py and understand architecture (628 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_websocket_server.py
4. MOVE: git mv labs/governance/identity/auth_backend/websocket_server.py core/governance/identity/auth_backend/websocket_server.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate websocket_server from labs"

---

### 74. labs.governance.identity.core.sent.policy_engine (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/sent/policy_engine.py` |
| Target Location | `core/governance/identity/core/sent/policy_engine.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1015 |
| Classes | 7 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1015 LOC, 7 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/sent/policy_engine.py and understand architecture (1015 LOC, 7 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_policy_engine.py
4. MOVE: git mv labs/governance/identity/core/sent/policy_engine.py core/governance/identity/core/sent/policy_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate policy_engine from labs"

---

### 75. labs.governance.identity.auth.qrg_generators (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/auth/qrg_generators.py` |
| Target Location | `core/governance/identity/auth/qrg_generators.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 770 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/auth/qrg_generators.py and understand architecture (770 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_qrg_generators.py
4. MOVE: git mv labs/governance/identity/auth/qrg_generators.py core/governance/identity/auth/qrg_generators.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate qrg_generators from labs"

---

### 76. labs.governance.identity.auth_web.websocket_server (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/auth_web/websocket_server.py` |
| Target Location | `core/governance/identity/auth_web/websocket_server.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 628 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/auth_web/websocket_server.py and understand architecture (628 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_websocket_server.py
4. MOVE: git mv labs/governance/identity/auth_web/websocket_server.py core/governance/identity/auth_web/websocket_server.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate websocket_server from labs"

---

### 77. labs.governance.security.privacy_guardian (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/security/privacy_guardian.py` |
| Target Location | `core/governance/security/privacy_guardian.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1142 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1142 LOC

**Integration Steps**:

1. REVIEW: Read labs/governance/security/privacy_guardian.py and understand architecture (1142 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_privacy_guardian.py
4. MOVE: git mv labs/governance/security/privacy_guardian.py core/governance/security/privacy_guardian.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate privacy_guardian from labs"

---

### 78. labs.governance.security.audit_system (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/security/audit_system.py` |
| Target Location | `core/governance/security/audit_system.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 973 |
| Classes | 10 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/security/audit_system.py and understand architecture (973 LOC, 10 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_audit_system.py
4. MOVE: git mv labs/governance/security/audit_system.py core/governance/security/audit_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate audit_system from labs"

---

### 79. labs.governance.ethics.guardian_reflector (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/ethics/guardian_reflector.py` |
| Target Location | `core/governance/ethics/guardian_reflector.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 590 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/ethics/guardian_reflector.py and understand architecture (590 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_guardian_reflector.py
4. MOVE: git mv labs/governance/ethics/guardian_reflector.py core/governance/ethics/guardian_reflector.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate guardian_reflector from labs"

---

### 80. labs.governance.ethics.ethical_decision_maker (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/ethics/ethical_decision_maker.py` |
| Target Location | `core/governance/ethics/ethical_decision_maker.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1042 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1042 LOC, 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/ethics/ethical_decision_maker.py and understand architecture (1042 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_ethical_decision_maker.py
4. MOVE: git mv labs/governance/ethics/ethical_decision_maker.py core/governance/ethics/ethical_decision_maker.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate ethical_decision_maker from labs"

---

### 81. core.matriz_signal_emitters (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `core/matriz_signal_emitters.py` |
| Target Location | `core/matriz_signal_emitters.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium |
| LOC | 576 |
| Classes | 9 |
| Functions | 6 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/matriz_signal_emitters.py and understand architecture (576 LOC, 9 classes, 6 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_matriz_signal_emitters.py
4. MOVE: git mv core/matriz_signal_emitters.py core/matriz_signal_emitters.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate matriz_signal_emitters from labs"

---

### 82. core.tier_aware_colony_proxy (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `core/tier_aware_colony_proxy.py` |
| Target Location | `core/tier_aware_colony_proxy.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium |
| LOC | 517 |
| Classes | 4 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/tier_aware_colony_proxy.py and understand architecture (517 LOC, 4 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_tier_aware_colony_proxy.py
4. MOVE: git mv core/tier_aware_colony_proxy.py core/tier_aware_colony_proxy.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate tier_aware_colony_proxy from labs"

---

### 83. memory.fold_lineage_tracker (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `memory/fold_lineage_tracker.py` |
| Target Location | `core/memory/fold_lineage_tracker.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium |
| LOC | 1066 |
| Classes | 5 |
| Functions | 5 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 1066 LOC

**Integration Steps**:

1. REVIEW: Read memory/fold_lineage_tracker.py and understand architecture (1066 LOC, 5 classes, 5 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_fold_lineage_tracker.py
4. MOVE: git mv memory/fold_lineage_tracker.py core/memory/fold_lineage_tracker.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate fold_lineage_tracker from labs"

---

### 84. bridge.api.validation (Score: 75.0)

| Property | Value |
|----------|-------|
| Current Location | `bridge/api/validation.py` |
| Target Location | `core/bridge/validation.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium |
| LOC | 1097 |
| Classes | 9 |
| Functions | 10 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 1097 LOC, 9 classes

**Integration Steps**:

1. REVIEW: Read bridge/api/validation.py and understand architecture (1097 LOC, 9 classes, 10 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_validation.py
4. MOVE: git mv bridge/api/validation.py core/bridge/validation.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate validation from labs"

---

### 85. labs.consciousness.systems.integrator (Score: 74.8)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/systems/integrator.py` |
| Target Location | `core/consciousness/integrator.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 565 |
| Classes | 11 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 11 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/systems/integrator.py and understand architecture (565 LOC, 11 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_integrator.py
4. MOVE: git mv labs/consciousness/systems/integrator.py core/consciousness/integrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate integrator from labs"

---

### 86. labs.consciousness.reflection.core (Score: 74.6)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/core.py` |
| Target Location | `matriz/consciousness/reflection//core.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium-high |
| LOC | 1583 |
| Classes | 14 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1583 LOC, 14 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/core.py and understand architecture (1583 LOC, 14 classes, 4 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_core.py
4. MOVE: git mv labs/consciousness/reflection/core.py matriz/consciousness/reflection//core.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate core from labs"

---

### 87. labs.consciousness.reflection.colony_orchestrator (Score: 74.4)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/colony_orchestrator.py` |
| Target Location | `matriz/consciousness/reflection//colony_orchestrator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 847 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/colony_orchestrator.py and understand architecture (847 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_colony_orchestrator.py
4. MOVE: git mv labs/consciousness/reflection/colony_orchestrator.py matriz/consciousness/reflection//colony_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate colony_orchestrator from labs"

---

### 88. labs.consciousness.reflection.event_replay_snapshot (Score: 74.4)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/event_replay_snapshot.py` |
| Target Location | `matriz/consciousness/reflection//event_replay_snapshot.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 673 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/event_replay_snapshot.py and understand architecture (673 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_event_replay_snapshot.py
4. MOVE: git mv labs/consciousness/reflection/event_replay_snapshot.py matriz/consciousness/reflection//event_replay_snapshot.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate event_replay_snapshot from labs"

---

### 89. labs.consciousness.states.shared_state (Score: 74.3)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/states/shared_state.py` |
| Target Location | `core/consciousness/shared_state.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 986 |
| Classes | 7 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/states/shared_state.py and understand architecture (986 LOC, 7 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_shared_state.py
4. MOVE: git mv labs/consciousness/states/shared_state.py core/consciousness/shared_state.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate shared_state from labs"

---

### 90. labs.consciousness.reflection.circuit_breaker (Score: 74.3)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/circuit_breaker.py` |
| Target Location | `matriz/consciousness/reflection//circuit_breaker.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 760 |
| Classes | 14 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 14 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/circuit_breaker.py and understand architecture (760 LOC, 14 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_circuit_breaker.py
4. MOVE: git mv labs/consciousness/reflection/circuit_breaker.py matriz/consciousness/reflection//circuit_breaker.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate circuit_breaker from labs"

---

### 91. labs.governance.identity.qrg_integration (Score: 74.2)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/qrg_integration.py` |
| Target Location | `core/governance/identity/qrg_integration.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 652 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/qrg_integration.py and understand architecture (652 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_qrg_integration.py
4. MOVE: git mv labs/governance/identity/qrg_integration.py core/governance/identity/qrg_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate qrg_integration from labs"

---

### 92. labs.bio.memory.symbolic_proteome (Score: 74.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/bio/memory/symbolic_proteome.py` |
| Target Location | `matriz/bio/memory/symbolic_proteome.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 835 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'bio' - move to matriz/bio/

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/bio/memory/symbolic_proteome.py and understand architecture (835 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_proteome.py
4. MOVE: git mv labs/bio/memory/symbolic_proteome.py matriz/bio/memory/symbolic_proteome.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate symbolic_proteome from labs"

---

### 93. labs.memory.repair.advanced_trauma_repair (Score: 74.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/repair/advanced_trauma_repair.py` |
| Target Location | `core/memory/advanced_trauma_repair.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 777 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/repair/advanced_trauma_repair.py and understand architecture (777 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_advanced_trauma_repair.py
4. MOVE: git mv labs/memory/repair/advanced_trauma_repair.py core/memory/advanced_trauma_repair.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate advanced_trauma_repair from labs"

---

### 94. labs.consciousness.reflection.openai_core_service (Score: 73.9)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/openai_core_service.py` |
| Target Location | `matriz/consciousness/reflection/openai_core_service.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 760 |
| Classes | 9 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/openai_core_service.py and understand architecture (760 LOC, 9 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_openai_core_service.py
4. MOVE: git mv labs/consciousness/reflection/openai_core_service.py matriz/consciousness/reflection/openai_core_service.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate openai_core_service from labs"

---

### 95. labs.memory.access.tier_system (Score: 73.8)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/access/tier_system.py` |
| Target Location | `core/memory/tier_system.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 596 |
| Classes | 7 |
| Functions | 8 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 7 classes

**Integration Steps**:

1. REVIEW: Read labs/memory/access/tier_system.py and understand architecture (596 LOC, 7 classes, 8 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_tier_system.py
4. MOVE: git mv labs/memory/access/tier_system.py core/memory/tier_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate tier_system from labs"

---

### 96. labs.consciousness.systems.advanced_consciousness_engine (Score: 73.3)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/systems/advanced_consciousness_engine.py` |
| Target Location | `core/consciousness/advanced_consciousness_engine.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 836 |
| Classes | 5 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/systems/advanced_consciousness_engine.py and understand architecture (836 LOC, 5 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_advanced_consciousness_engine.py
4. MOVE: git mv labs/consciousness/systems/advanced_consciousness_engine.py core/consciousness/advanced_consciousness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate advanced_consciousness_engine from labs"

---

### 97. labs.consciousness.dream.colony_dream_coordinator (Score: 73.1)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/dream/colony_dream_coordinator.py` |
| Target Location | `matriz/consciousness/dream/colony_dream_coordinator.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 899 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/dream/colony_dream_coordinator.py and understand architecture (899 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_colony_dream_coordinator.py
4. MOVE: git mv labs/consciousness/dream/colony_dream_coordinator.py matriz/consciousness/dream/colony_dream_coordinator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate colony_dream_coordinator from labs"

---

### 98. labs.core.resource_optimization_integration (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/resource_optimization_integration.py` |
| Target Location | `core/resource_optimization_integration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 516 |
| Classes | 5 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/resource_optimization_integration.py and understand architecture (516 LOC, 5 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_resource_optimization_integration.py
4. MOVE: git mv labs/core/resource_optimization_integration.py core/resource_optimization_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate resource_optimization_integration from labs"

---

### 99. labs.core.core_hub (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/core_hub.py` |
| Target Location | `core/core_hub.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 601 |
| Classes | 2 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/core_hub.py and understand architecture (601 LOC, 2 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_core_hub.py
4. MOVE: git mv labs/core/core_hub.py core/core_hub.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate core_hub from labs"

---

### 100. labs.core.orchestration.async_orchestrator (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/async_orchestrator.py` |
| Target Location | `core/orchestration/async_orchestrator.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 936 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/async_orchestrator.py and understand architecture (936 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_async_orchestrator.py
4. MOVE: git mv labs/core/orchestration/async_orchestrator.py core/orchestration/async_orchestrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate async_orchestrator from labs"

---

### 101. labs.core.api.api_system (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/api/api_system.py` |
| Target Location | `core/api/api_system.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 631 |
| Classes | 14 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 14 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/api/api_system.py and understand architecture (631 LOC, 14 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_api_system.py
4. MOVE: git mv labs/core/api/api_system.py core/api/api_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate api_system from labs"

---

### 102. labs.memory.protection.symbolic_quarantine_sanctum (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/protection/symbolic_quarantine_sanctum.py` |
| Target Location | `core/memory/symbolic_quarantine_sanctum.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1467 |
| Classes | 8 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 1467 LOC, 8 classes

**Integration Steps**:

1. REVIEW: Read labs/memory/protection/symbolic_quarantine_sanctum.py and understand architecture (1467 LOC, 8 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_symbolic_quarantine_sanctum.py
4. MOVE: git mv labs/memory/protection/symbolic_quarantine_sanctum.py core/memory/symbolic_quarantine_sanctum.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate symbolic_quarantine_sanctum from labs"

---

### 103. labs.consciousness.dream.reality_synthesis_engine (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/dream/reality_synthesis_engine.py` |
| Target Location | `matriz/consciousness/dream/reality_synthesis_engine.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 637 |
| Classes | 5 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/dream/reality_synthesis_engine.py and understand architecture (637 LOC, 5 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_reality_synthesis_engine.py
4. MOVE: git mv labs/consciousness/dream/reality_synthesis_engine.py matriz/consciousness/dream/reality_synthesis_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate reality_synthesis_engine from labs"

---

### 104. labs.consciousness.reflection.service (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/service.py` |
| Target Location | `matriz/consciousness/reflection/service.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 1211 |
| Classes | 2 |
| Functions | 8 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1211 LOC

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/service.py and understand architecture (1211 LOC, 2 classes, 8 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_service.py
4. MOVE: git mv labs/consciousness/reflection/service.py matriz/consciousness/reflection/service.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate service from labs"

---

### 105. labs.consciousness.reflection.metalearningenhancementsystem (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/metalearningenhancementsystem.py` |
| Target Location | `matriz/consciousness/reflection/metalearningenhancementsystem.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 983 |
| Classes | 3 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/metalearningenhancementsystem.py and understand architecture (983 LOC, 3 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_metalearningenhancementsystem.py
4. MOVE: git mv labs/consciousness/reflection/metalearningenhancementsystem.py matriz/consciousness/reflection/metalearningenhancementsystem.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate metalearningenhancementsystem from labs"

---

### 106. labs.consciousness.reflection.MetaLearningEnhancement (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/MetaLearningEnhancement.py` |
| Target Location | `matriz/consciousness/reflection/MetaLearningEnhancement.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 944 |
| Classes | 3 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/MetaLearningEnhancement.py and understand architecture (944 LOC, 3 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_MetaLearningEnhancement.py
4. MOVE: git mv labs/consciousness/reflection/MetaLearningEnhancement.py matriz/consciousness/reflection/MetaLearningEnhancement.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate MetaLearningEnhancement from labs"

---

### 107. core.integration.system_coordinator (Score: 72.5)

| Property | Value |
|----------|-------|
| Current Location | `core/integration/system_coordinator.py` |
| Target Location | `core/integration/system_coordinator.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 650 |
| Classes | 6 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/integration/system_coordinator.py and understand architecture (650 LOC, 6 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_system_coordinator.py
4. MOVE: git mv core/integration/system_coordinator.py core/integration/system_coordinator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate system_coordinator from labs"

---

### 108. labs.orchestration.openai_modulated_service (Score: 72.2)

| Property | Value |
|----------|-------|
| Current Location | `labs/orchestration/openai_modulated_service.py` |
| Target Location | `core/orchestration/openai_modulated_service.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 589 |
| Classes | 10 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/orchestration/ - review manually

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/orchestration/openai_modulated_service.py and understand architecture (589 LOC, 10 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_openai_modulated_service.py
4. MOVE: git mv labs/orchestration/openai_modulated_service.py core/orchestration/openai_modulated_service.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate openai_modulated_service from labs"

---

### 109. labs.consciousness.reflection.practical_optimizations (Score: 72.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/practical_optimizations.py` |
| Target Location | `matriz/consciousness/reflection/practical_optimizations.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 937 |
| Classes | 11 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 11 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/practical_optimizations.py and understand architecture (937 LOC, 11 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_practical_optimizations.py
4. MOVE: git mv labs/consciousness/reflection/practical_optimizations.py matriz/consciousness/reflection/practical_optimizations.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate practical_optimizations from labs"

---

### 110. labs.consciousness.reflection.client (Score: 71.9)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/client.py` |
| Target Location | `matriz/consciousness/reflection/client.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1724 |
| Classes | 7 |
| Functions | 3 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1724 LOC, 7 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/client.py and understand architecture (1724 LOC, 7 classes, 3 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_client.py
4. MOVE: git mv labs/consciousness/reflection/client.py matriz/consciousness/reflection/client.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate client from labs"

---

### 111. labs.core.symbolic.dream_delivery_manager (Score: 71.7)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/symbolic/dream_delivery_manager.py` |
| Target Location | `core/symbolic/dream_delivery_manager.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 693 |
| Classes | 3 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/symbolic/dream_delivery_manager.py and understand architecture (693 LOC, 3 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dream_delivery_manager.py
4. MOVE: git mv labs/core/symbolic/dream_delivery_manager.py core/symbolic/dream_delivery_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dream_delivery_manager from labs"

---

### 112. core.orchestration.brain.demo (Score: 71.2)

| Property | Value |
|----------|-------|
| Current Location | `core/orchestration/brain/demo.py` |
| Target Location | `core/orchestration/brain/demo.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 515 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/orchestration/brain/demo.py and understand architecture (515 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_demo.py
4. MOVE: git mv core/orchestration/brain/demo.py core/orchestration/brain/demo.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate demo from labs"

---

### 113. labs.governance.identity.core.brain_identity_integration (Score: 70.5)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/brain_identity_integration.py` |
| Target Location | `core/governance/identity/core/brain_identity_integration.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 528 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/brain_identity_integration.py and understand architecture (528 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_brain_identity_integration.py
4. MOVE: git mv labs/governance/identity/core/brain_identity_integration.py core/governance/identity/core/brain_identity_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate brain_identity_integration from labs"

---

### 114. labs.core.id (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/id.py` |
| Target Location | `core/id.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 699 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 8 classes

**Integration Steps**:

1. REVIEW: Read labs/core/id.py and understand architecture (699 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_id.py
4. MOVE: git mv labs/core/id.py core/id.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate id from labs"

---

### 115. labs.core.identity.matriz_consciousness_identity (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/matriz_consciousness_identity.py` |
| Target Location | `core/identity/matriz_consciousness_identity.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 948 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/identity/matriz_consciousness_identity.py and understand architecture (948 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_matriz_consciousness_identity.py
4. MOVE: git mv labs/core/identity/matriz_consciousness_identity.py core/identity/matriz_consciousness_identity.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate matriz_consciousness_identity from labs"

---

### 116. labs.core.identity.test_consciousness_identity_patterns (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/test_consciousness_identity_patterns.py` |
| Target Location | `core/identity/test_consciousness_identity_patterns.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 753 |
| Classes | 7 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/identity/test_consciousness_identity_patterns.py and understand architecture (753 LOC, 7 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_test_consciousness_identity_patterns.py
4. MOVE: git mv labs/core/identity/test_consciousness_identity_patterns.py core/identity/test_consciousness_identity_patterns.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate test_consciousness_identity_patterns from labs"

---

### 117. labs.core.identity.consciousness_namespace_isolation (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/consciousness_namespace_isolation.py` |
| Target Location | `core/identity/consciousness_namespace_isolation.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 749 |
| Classes | 7 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/identity/consciousness_namespace_isolation.py and understand architecture (749 LOC, 7 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_consciousness_namespace_isolation.py
4. MOVE: git mv labs/core/identity/consciousness_namespace_isolation.py core/identity/consciousness_namespace_isolation.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate consciousness_namespace_isolation from labs"

---

### 118. labs.core.identity.manager (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/manager.py` |
| Target Location | `core/identity/manager.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 716 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/core/identity/manager.py and understand architecture (716 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_manager.py
4. MOVE: git mv labs/core/identity/manager.py core/identity/manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate manager from labs"

---

### 119. labs.core.identity.lambda_id_core (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/identity/lambda_id_core.py` |
| Target Location | `core/identity/lambda_id_core.py` |
| Complexity | medium |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 717 |
| Classes | 11 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 11 classes

**Integration Steps**:

1. REVIEW: Read labs/core/identity/lambda_id_core.py and understand architecture (717 LOC, 11 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_lambda_id_core.py
4. MOVE: git mv labs/core/identity/lambda_id_core.py core/identity/lambda_id_core.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate lambda_id_core from labs"

---

### 120. labs.core.endocrine.hormone_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/endocrine/hormone_system.py` |
| Target Location | `core/endocrine/hormone_system.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 430 |
| Classes | 4 |
| Functions | 4 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/endocrine/hormone_system.py and understand architecture (430 LOC, 4 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_hormone_system.py
4. MOVE: git mv labs/core/endocrine/hormone_system.py core/endocrine/hormone_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate hormone_system from labs"

---

### 121. labs.core.ethics.logic.dsl_lite (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/ethics/logic/dsl_lite.py` |
| Target Location | `core/ethics/logic/dsl_lite.py` |
| Complexity | medium |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 522 |
| Classes | 1 |
| Functions | 33 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/core/ethics/logic/dsl_lite.py and understand architecture (522 LOC, 1 classes, 33 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_dsl_lite.py
4. MOVE: git mv labs/core/ethics/logic/dsl_lite.py core/ethics/logic/dsl_lite.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dsl_lite from labs"

---

### 122. labs.core.orchestration.brain.canadian_awareness_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/canadian_awareness_engine.py` |
| Target Location | `core/orchestration/brain/canadian_awareness_engine.py` |
| Complexity | medium |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 591 |
| Classes | 11 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 11 classes

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/canadian_awareness_engine.py and understand architecture (591 LOC, 11 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_canadian_awareness_engine.py
4. MOVE: git mv labs/core/orchestration/brain/canadian_awareness_engine.py core/orchestration/brain/canadian_awareness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate canadian_awareness_engine from labs"

---

### 123. labs.core.orchestration.brain.das_awareness_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/das_awareness_engine.py` |
| Target Location | `core/orchestration/brain/das_awareness_engine.py` |
| Complexity | medium |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 523 |
| Classes | 15 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 15 classes

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/das_awareness_engine.py and understand architecture (523 LOC, 15 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_das_awareness_engine.py
4. MOVE: git mv labs/core/orchestration/brain/das_awareness_engine.py core/orchestration/brain/das_awareness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate das_awareness_engine from labs"

---

### 124. labs.core.orchestration.brain.uk_awareness_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/uk_awareness_engine.py` |
| Target Location | `core/orchestration/brain/uk_awareness_engine.py` |
| Complexity | medium |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 564 |
| Classes | 11 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 11 classes

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/uk_awareness_engine.py and understand architecture (564 LOC, 11 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_uk_awareness_engine.py
4. MOVE: git mv labs/core/orchestration/brain/uk_awareness_engine.py core/orchestration/brain/uk_awareness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate uk_awareness_engine from labs"

---

### 125. labs.core.orchestration.brain.australian_awareness_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/orchestration/brain/australian_awareness_engine.py` |
| Target Location | `core/orchestration/brain/australian_awareness_engine.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 520 |
| Classes | 10 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 10 classes

**Integration Steps**:

1. REVIEW: Read labs/core/orchestration/brain/australian_awareness_engine.py and understand architecture (520 LOC, 10 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_australian_awareness_engine.py
4. MOVE: git mv labs/core/orchestration/brain/australian_awareness_engine.py core/orchestration/brain/australian_awareness_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate australian_awareness_engine from labs"

---

### 126. labs.core.governance.matriz_consciousness_governance (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/governance/matriz_consciousness_governance.py` |
| Target Location | `core/governance/matriz_consciousness_governance.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 690 |
| Classes | 5 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/core/governance/matriz_consciousness_governance.py and understand architecture (690 LOC, 5 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_matriz_consciousness_governance.py
4. MOVE: git mv labs/core/governance/matriz_consciousness_governance.py core/governance/matriz_consciousness_governance.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate matriz_consciousness_governance from labs"

---

### 127. labs.core.agi_preparedness.capability_evaluation_framework (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/core/agi_preparedness/capability_evaluation_framework.py` |
| Target Location | `core/agi_preparedness/capability_evaluation_framework.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1093 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1093 LOC, 8 classes

**Integration Steps**:

1. REVIEW: Read labs/core/agi_preparedness/capability_evaluation_framework.py and understand architecture (1093 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_capability_evaluation_framework.py
4. MOVE: git mv labs/core/agi_preparedness/capability_evaluation_framework.py core/agi_preparedness/capability_evaluation_framework.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate capability_evaluation_framework from labs"

---

### 128. labs.memory.tools.memory_drift_auditor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/tools/memory_drift_auditor.py` |
| Target Location | `core/memory/memory_drift_auditor.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 2156 |
| Classes | 1 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 2156 LOC

**Integration Steps**:

1. REVIEW: Read labs/memory/tools/memory_drift_auditor.py and understand architecture (2156 LOC, 1 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_memory_drift_auditor.py
4. MOVE: git mv labs/memory/tools/memory_drift_auditor.py core/memory/memory_drift_auditor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate memory_drift_auditor from labs"

---

### 129. labs.memory.learning.adaptive_meta_learning_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/learning/adaptive_meta_learning_system.py` |
| Target Location | `core/memory/adaptive_meta_learning_system.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 534 |
| Classes | 1 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/learning/adaptive_meta_learning_system.py and understand architecture (534 LOC, 1 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_adaptive_meta_learning_system.py
4. MOVE: git mv labs/memory/learning/adaptive_meta_learning_system.py core/memory/adaptive_meta_learning_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate adaptive_meta_learning_system from labs"

---

### 130. labs.memory.learning.meta_learning.federated_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/learning/meta_learning/federated_integration.py` |
| Target Location | `core/memory/federated_integration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 685 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/learning/meta_learning/federated_integration.py and understand architecture (685 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_federated_integration.py
4. MOVE: git mv labs/memory/learning/meta_learning/federated_integration.py core/memory/federated_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate federated_integration from labs"

---

### 131. labs.memory.learning.federated.FederatedIntegration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/learning/federated/FederatedIntegration.py` |
| Target Location | `core/memory/FederatedIntegration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 685 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/learning/federated/FederatedIntegration.py and understand architecture (685 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_FederatedIntegration.py
4. MOVE: git mv labs/memory/learning/federated/FederatedIntegration.py core/memory/FederatedIntegration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate FederatedIntegration from labs"

---

### 132. labs.memory.dna_helix.dna_healix (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/dna_helix/dna_healix.py` |
| Target Location | `core/memory/dna_healix.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 554 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/dna_helix/dna_healix.py and understand architecture (554 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dna_healix.py
4. MOVE: git mv labs/memory/dna_helix/dna_healix.py core/memory/dna_healix.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dna_healix from labs"

---

### 133. labs.memory.fold_system.distributed_memory_fold (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/fold_system/distributed_memory_fold.py` |
| Target Location | `core/memory/distributed_memory_fold.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 792 |
| Classes | 6 |
| Functions | 2 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/fold_system/distributed_memory_fold.py and understand architecture (792 LOC, 6 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_distributed_memory_fold.py
4. MOVE: git mv labs/memory/fold_system/distributed_memory_fold.py core/memory/distributed_memory_fold.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate distributed_memory_fold from labs"

---

### 134. labs.memory.systems.simple_store (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/systems/simple_store.py` |
| Target Location | `core/memory/simple_store.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 526 |
| Classes | 5 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/systems/simple_store.py and understand architecture (526 LOC, 5 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_simple_store.py
4. MOVE: git mv labs/memory/systems/simple_store.py core/memory/simple_store.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate simple_store from labs"

---

### 135. labs.memory.systems.neurosymbolic_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/systems/neurosymbolic_integration.py` |
| Target Location | `core/memory/neurosymbolic_integration.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1601 |
| Classes | 8 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: 1601 LOC, 8 classes

**Integration Steps**:

1. REVIEW: Read labs/memory/systems/neurosymbolic_integration.py and understand architecture (1601 LOC, 8 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_neurosymbolic_integration.py
4. MOVE: git mv labs/memory/systems/neurosymbolic_integration.py core/memory/neurosymbolic_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate neurosymbolic_integration from labs"

---

### 136. labs.memory.neocortical.neocortical_network (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/memory/neocortical/neocortical_network.py` |
| Target Location | `core/memory/neocortical_network.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 646 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/memory/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/memory/neocortical/neocortical_network.py and understand architecture (646 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_neocortical_network.py
4. MOVE: git mv labs/memory/neocortical/neocortical_network.py core/memory/neocortical_network.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate neocortical_network from labs"

---

### 137. labs.bridge.explainability_interface_layer (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/bridge/explainability_interface_layer.py` |
| Target Location | `core/bridge/explainability_interface_layer.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 697 |
| Classes | 9 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 9 classes

**Integration Steps**:

1. REVIEW: Read labs/bridge/explainability_interface_layer.py and understand architecture (697 LOC, 9 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_explainability_interface_layer.py
4. MOVE: git mv labs/bridge/explainability_interface_layer.py core/bridge/explainability_interface_layer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate explainability_interface_layer from labs"

---

### 138. labs.bridge.api.controllers (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/bridge/api/controllers.py` |
| Target Location | `core/bridge/controllers.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 542 |
| Classes | 6 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 6 classes

**Integration Steps**:

1. REVIEW: Read labs/bridge/api/controllers.py and understand architecture (542 LOC, 6 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_controllers.py
4. MOVE: git mv labs/bridge/api/controllers.py core/bridge/controllers.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate controllers from labs"

---

### 139. labs.bridge.api.api (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/bridge/api/api.py` |
| Target Location | `core/bridge/api.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 571 |
| Classes | 5 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/bridge/api/api.py and understand architecture (571 LOC, 5 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_api.py
4. MOVE: git mv labs/bridge/api/api.py core/bridge/api.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate api from labs"

---

### 140. labs.consciousness.constellation.framework_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/constellation/framework_integration.py` |
| Target Location | `core/consciousness/framework_integration.py` |
| Complexity | medium |
| Effort | 16 hours |
| Risk Level | medium-high |
| LOC | 812 |
| Classes | 14 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 14 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/constellation/framework_integration.py and understand architecture (812 LOC, 14 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_framework_integration.py
4. MOVE: git mv labs/consciousness/constellation/framework_integration.py core/consciousness/framework_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate framework_integration from labs"

---

### 141. labs.consciousness.reasoning.decision.bridge (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reasoning/decision/bridge.py` |
| Target Location | `core/consciousness/bridge.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 805 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 10 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reasoning/decision/bridge.py and understand architecture (805 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_bridge.py
4. MOVE: git mv labs/consciousness/reasoning/decision/bridge.py core/consciousness/bridge.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate bridge from labs"

---

### 142. labs.consciousness.testing.chaos_engineering_framework (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/testing/chaos_engineering_framework.py` |
| Target Location | `core/consciousness/chaos_engineering_framework.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 669 |
| Classes | 10 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 10 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/testing/chaos_engineering_framework.py and understand architecture (669 LOC, 10 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_chaos_engineering_framework.py
4. MOVE: git mv labs/consciousness/testing/chaos_engineering_framework.py core/consciousness/chaos_engineering_framework.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate chaos_engineering_framework from labs"

---

### 143. labs.consciousness.expansion.consciousness_expansion_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/expansion/consciousness_expansion_engine.py` |
| Target Location | `core/consciousness/consciousness_expansion_engine.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 641 |
| Classes | 3 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/expansion/consciousness_expansion_engine.py and understand architecture (641 LOC, 3 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_consciousness_expansion_engine.py
4. MOVE: git mv labs/consciousness/expansion/consciousness_expansion_engine.py core/consciousness/consciousness_expansion_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate consciousness_expansion_engine from labs"

---

### 144. labs.consciousness.states.world_models (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/states/world_models.py` |
| Target Location | `core/consciousness/world_models.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 543 |
| Classes | 7 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/states/world_models.py and understand architecture (543 LOC, 7 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_world_models.py
4. MOVE: git mv labs/consciousness/states/world_models.py core/consciousness/world_models.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate world_models from labs"

---

### 145. labs.consciousness.states.qi_mesh_integrator (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/states/qi_mesh_integrator.py` |
| Target Location | `core/consciousness/qi_mesh_integrator.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 624 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/states/qi_mesh_integrator.py and understand architecture (624 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_qi_mesh_integrator.py
4. MOVE: git mv labs/consciousness/states/qi_mesh_integrator.py core/consciousness/qi_mesh_integrator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate qi_mesh_integrator from labs"

---

### 146. labs.consciousness.systems.dream_engine.dream_reflection_loop (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/systems/dream_engine/dream_reflection_loop.py` |
| Target Location | `core/consciousness/dream_reflection_loop.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 885 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/systems/dream_engine/dream_reflection_loop.py and understand architecture (885 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dream_reflection_loop.py
4. MOVE: git mv labs/consciousness/systems/dream_engine/dream_reflection_loop.py core/consciousness/dream_reflection_loop.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dream_reflection_loop from labs"

---

### 147. labs.consciousness.dream.parallel_reality_simulator (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/dream/parallel_reality_simulator.py` |
| Target Location | `matriz/consciousness/dream/parallel_reality_simulator.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 849 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.dream' - move to matriz/consciousness/dream/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/dream/parallel_reality_simulator.py and understand architecture (849 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_parallel_reality_simulator.py
4. MOVE: git mv labs/consciousness/dream/parallel_reality_simulator.py matriz/consciousness/dream/parallel_reality_simulator.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate parallel_reality_simulator from labs"

---

### 148. labs.consciousness.quantum.collapse_governance_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/quantum/collapse_governance_system.py` |
| Target Location | `core/consciousness/collapse_governance_system.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 742 |
| Classes | 9 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 9 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/quantum/collapse_governance_system.py and understand architecture (742 LOC, 9 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_collapse_governance_system.py
4. MOVE: git mv labs/consciousness/quantum/collapse_governance_system.py core/consciousness/collapse_governance_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate collapse_governance_system from labs"

---

### 149. labs.consciousness.reflection.federated_meta_learning (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/federated_meta_learning.py` |
| Target Location | `matriz/consciousness/reflection/federated_meta_learning.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 927 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/federated_meta_learning.py and understand architecture (927 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_federated_meta_learning.py
4. MOVE: git mv labs/consciousness/reflection/federated_meta_learning.py matriz/consciousness/reflection/federated_meta_learning.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate federated_meta_learning from labs"

---

### 150. labs.consciousness.reflection.system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/system.py` |
| Target Location | `matriz/consciousness/reflection/system.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 936 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/system.py and understand architecture (936 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_system.py
4. MOVE: git mv labs/consciousness/reflection/system.py matriz/consciousness/reflection/system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate system from labs"

---

### 151. labs.consciousness.reflection.controller (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/controller.py` |
| Target Location | `matriz/consciousness/reflection/controller.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 905 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 8 classes

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/controller.py and understand architecture (905 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_controller.py
4. MOVE: git mv labs/consciousness/reflection/controller.py matriz/consciousness/reflection/controller.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate controller from labs"

---

### 152. labs.consciousness.reflection.awareness_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/awareness_system.py` |
| Target Location | `matriz/consciousness/reflection/awareness_system.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 995 |
| Classes | 3 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/awareness_system.py and understand architecture (995 LOC, 3 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_awareness_system.py
4. MOVE: git mv labs/consciousness/reflection/awareness_system.py matriz/consciousness/reflection/awareness_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate awareness_system from labs"

---

### 153. labs.consciousness.reflection.meta_learning (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/meta_learning.py` |
| Target Location | `matriz/consciousness/reflection/meta_learning.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 927 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/meta_learning.py and understand architecture (927 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_meta_learning.py
4. MOVE: git mv labs/consciousness/reflection/meta_learning.py matriz/consciousness/reflection/meta_learning.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate meta_learning from labs"

---

### 154. labs.consciousness.reflection.distributed_state_manager (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/distributed_state_manager.py` |
| Target Location | `matriz/consciousness/reflection/distributed_state_manager.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 577 |
| Classes | 5 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/distributed_state_manager.py and understand architecture (577 LOC, 5 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_distributed_state_manager.py
4. MOVE: git mv labs/consciousness/reflection/distributed_state_manager.py matriz/consciousness/reflection/distributed_state_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate distributed_state_manager from labs"

---

### 155. labs.consciousness.reflection.unified_memory_manager (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/unified_memory_manager.py` |
| Target Location | `matriz/consciousness/reflection/unified_memory_manager.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 1425 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 1425 LOC

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/unified_memory_manager.py and understand architecture (1425 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_unified_memory_manager.py
4. MOVE: git mv labs/consciousness/reflection/unified_memory_manager.py matriz/consciousness/reflection/unified_memory_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate unified_memory_manager from labs"

---

### 156. labs.consciousness.reflection.learning_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/learning_system.py` |
| Target Location | `matriz/consciousness/reflection/learning_system.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 848 |
| Classes | 9 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/learning_system.py and understand architecture (848 LOC, 9 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_learning_system.py
4. MOVE: git mv labs/consciousness/reflection/learning_system.py matriz/consciousness/reflection/learning_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate learning_system from labs"

---

### 157. labs.consciousness.reflection.agent_coordination (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/consciousness/reflection/agent_coordination.py` |
| Target Location | `matriz/consciousness/reflection/agent_coordination.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 690 |
| Classes | 13 |
| Functions | 3 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'consciousness.reflection' - move to matriz/consciousness/reflection/

**Complexity Rationale**: 13 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/consciousness/reflection/agent_coordination.py and understand architecture (690 LOC, 13 classes, 3 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_agent_coordination.py
4. MOVE: git mv labs/consciousness/reflection/agent_coordination.py matriz/consciousness/reflection/agent_coordination.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate agent_coordination from labs"

---

### 158. labs.orchestration.context_bus (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/orchestration/context_bus.py` |
| Target Location | `core/orchestration/context_bus.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 540 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/orchestration/ - review manually

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/orchestration/context_bus.py and understand architecture (540 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_context_bus.py
4. MOVE: git mv labs/orchestration/context_bus.py core/orchestration/context_bus.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate context_bus from labs"

---

### 159. labs.governance.auth_guardian_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/auth_guardian_integration.py` |
| Target Location | `core/governance//auth_guardian_integration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 555 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/auth_guardian_integration.py and understand architecture (555 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_auth_guardian_integration.py
4. MOVE: git mv labs/governance/auth_guardian_integration.py core/governance//auth_guardian_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate auth_guardian_integration from labs"

---

### 160. labs.governance.auth_glyph_registry (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/auth_glyph_registry.py` |
| Target Location | `core/governance//auth_glyph_registry.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 602 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/auth_glyph_registry.py and understand architecture (602 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_auth_glyph_registry.py
4. MOVE: git mv labs/governance/auth_glyph_registry.py core/governance//auth_glyph_registry.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate auth_glyph_registry from labs"

---

### 161. labs.governance.auth_cross_module_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/auth_cross_module_integration.py` |
| Target Location | `core/governance//auth_cross_module_integration.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 689 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/auth_cross_module_integration.py and understand architecture (689 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_auth_cross_module_integration.py
4. MOVE: git mv labs/governance/auth_cross_module_integration.py core/governance//auth_cross_module_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate auth_cross_module_integration from labs"

---

### 162. labs.governance.identity.deployment_package (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/deployment_package.py` |
| Target Location | `core/governance/identity/deployment_package.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 615 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 7 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/deployment_package.py and understand architecture (615 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_deployment_package.py
4. MOVE: git mv labs/governance/identity/deployment_package.py core/governance/identity/deployment_package.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate deployment_package from labs"

---

### 163. labs.governance.identity.lambda_id_auth (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/lambda_id_auth.py` |
| Target Location | `core/governance/identity/lambda_id_auth.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 506 |
| Classes | 8 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 8 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/lambda_id_auth.py and understand architecture (506 LOC, 8 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_lambda_id_auth.py
4. MOVE: git mv labs/governance/identity/lambda_id_auth.py core/governance/identity/lambda_id_auth.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate lambda_id_auth from labs"

---

### 164. labs.governance.identity.zkproof.multimodal_zk_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/zkproof/multimodal_zk_engine.py` |
| Target Location | `core/governance/identity/zkproof/multimodal_zk_engine.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 566 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/zkproof/multimodal_zk_engine.py and understand architecture (566 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_multimodal_zk_engine.py
4. MOVE: git mv labs/governance/identity/zkproof/multimodal_zk_engine.py core/governance/identity/zkproof/multimodal_zk_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate multimodal_zk_engine from labs"

---

### 165. labs.governance.identity.tools.onboarding_cli (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/tools/onboarding_cli.py` |
| Target Location | `core/governance/identity/tools/onboarding_cli.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 519 |
| Classes | 1 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/tools/onboarding_cli.py and understand architecture (519 LOC, 1 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_onboarding_cli.py
4. MOVE: git mv labs/governance/identity/tools/onboarding_cli.py core/governance/identity/tools/onboarding_cli.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate onboarding_cli from labs"

---

### 166. labs.governance.identity.core.unified_auth_manager (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/unified_auth_manager.py` |
| Target Location | `core/governance/identity/core/unified_auth_manager.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 799 |
| Classes | 8 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 8 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/unified_auth_manager.py and understand architecture (799 LOC, 8 classes, 2 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_unified_auth_manager.py
4. MOVE: git mv labs/governance/identity/core/unified_auth_manager.py core/governance/identity/core/unified_auth_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate unified_auth_manager from labs"

---

### 167. labs.governance.identity.core.colonies.biometric_verification_colony (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/colonies/biometric_verification_colony.py` |
| Target Location | `core/governance/identity/core/colonies/biometric_verification_colony.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 601 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/colonies/biometric_verification_colony.py and understand architecture (601 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_biometric_verification_colony.py
4. MOVE: git mv labs/governance/identity/core/colonies/biometric_verification_colony.py core/governance/identity/core/colonies/biometric_verification_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate biometric_verification_colony from labs"

---

### 168. labs.governance.identity.core.colonies.consciousness_verification_colony (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/colonies/consciousness_verification_colony.py` |
| Target Location | `core/governance/identity/core/colonies/consciousness_verification_colony.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 907 |
| Classes | 4 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/colonies/consciousness_verification_colony.py and understand architecture (907 LOC, 4 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_consciousness_verification_colony.py
4. MOVE: git mv labs/governance/identity/core/colonies/consciousness_verification_colony.py core/governance/identity/core/colonies/consciousness_verification_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate consciousness_verification_colony from labs"

---

### 169. labs.governance.identity.core.colonies.dream_verification_colony (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/colonies/dream_verification_colony.py` |
| Target Location | `core/governance/identity/core/colonies/dream_verification_colony.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 912 |
| Classes | 5 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/colonies/dream_verification_colony.py and understand architecture (912 LOC, 5 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_dream_verification_colony.py
4. MOVE: git mv labs/governance/identity/core/colonies/dream_verification_colony.py core/governance/identity/core/colonies/dream_verification_colony.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dream_verification_colony from labs"

---

### 170. labs.governance.identity.core.health.identity_health_monitor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/health/identity_health_monitor.py` |
| Target Location | `core/governance/identity/core/health/identity_health_monitor.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 713 |
| Classes | 5 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/health/identity_health_monitor.py and understand architecture (713 LOC, 5 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_identity_health_monitor.py
4. MOVE: git mv labs/governance/identity/core/health/identity_health_monitor.py core/governance/identity/core/health/identity_health_monitor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate identity_health_monitor from labs"

---

### 171. labs.governance.identity.core.tagging.identity_tag_resolver (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/tagging/identity_tag_resolver.py` |
| Target Location | `core/governance/identity/core/tagging/identity_tag_resolver.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 556 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 6 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/tagging/identity_tag_resolver.py and understand architecture (556 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_identity_tag_resolver.py
4. MOVE: git mv labs/governance/identity/core/tagging/identity_tag_resolver.py core/governance/identity/core/tagging/identity_tag_resolver.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate identity_tag_resolver from labs"

---

### 172. labs.governance.identity.core.glyph.distributed_glyph_generation (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/core/glyph/distributed_glyph_generation.py` |
| Target Location | `core/governance/identity/core/glyph/distributed_glyph_generation.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 753 |
| Classes | 7 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/core/glyph/distributed_glyph_generation.py and understand architecture (753 LOC, 7 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_distributed_glyph_generation.py
4. MOVE: git mv labs/governance/identity/core/glyph/distributed_glyph_generation.py core/governance/identity/core/glyph/distributed_glyph_generation.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate distributed_glyph_generation from labs"

---

### 173. labs.governance.identity.biometric.biometric_fusion_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/biometric/biometric_fusion_engine.py` |
| Target Location | `core/governance/identity/biometric/biometric_fusion_engine.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 712 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/biometric/biometric_fusion_engine.py and understand architecture (712 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_biometric_fusion_engine.py
4. MOVE: git mv labs/governance/identity/biometric/biometric_fusion_engine.py core/governance/identity/biometric/biometric_fusion_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate biometric_fusion_engine from labs"

---

### 174. labs.governance.identity.quantum.dynamic_qrglyph_engine (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/identity/quantum/dynamic_qrglyph_engine.py` |
| Target Location | `core/governance/identity/quantum/dynamic_qrglyph_engine.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 553 |
| Classes | 6 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 6 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/identity/quantum/dynamic_qrglyph_engine.py and understand architecture (553 LOC, 6 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_dynamic_qrglyph_engine.py
4. MOVE: git mv labs/governance/identity/quantum/dynamic_qrglyph_engine.py core/governance/identity/quantum/dynamic_qrglyph_engine.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate dynamic_qrglyph_engine from labs"

---

### 175. labs.governance.security.consent_manager (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/security/consent_manager.py` |
| Target Location | `core/governance/security/consent_manager.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 998 |
| Classes | 5 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: standard module

**Integration Steps**:

1. REVIEW: Read labs/governance/security/consent_manager.py and understand architecture (998 LOC, 5 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_consent_manager.py
4. MOVE: git mv labs/governance/security/consent_manager.py core/governance/security/consent_manager.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate consent_manager from labs"

---

### 176. labs.governance.ethics.compliance_monitor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/ethics/compliance_monitor.py` |
| Target Location | `core/governance/ethics/compliance_monitor.py` |
| Complexity | low |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 978 |
| Classes | 9 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/ethics/compliance_monitor.py and understand architecture (978 LOC, 9 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_compliance_monitor.py
4. MOVE: git mv labs/governance/ethics/compliance_monitor.py core/governance/ethics/compliance_monitor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate compliance_monitor from labs"

---

### 177. labs.governance.guardian.compliance_audit_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/guardian/compliance_audit_system.py` |
| Target Location | `core/governance/guardian/compliance_audit_system.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 819 |
| Classes | 11 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 11 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/guardian/compliance_audit_system.py and understand architecture (819 LOC, 11 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_compliance_audit_system.py
4. MOVE: git mv labs/governance/guardian/compliance_audit_system.py core/governance/guardian/compliance_audit_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate compliance_audit_system from labs"

---

### 178. labs.governance.guardian.drift_detector (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/guardian/drift_detector.py` |
| Target Location | `core/governance/guardian/drift_detector.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1062 |
| Classes | 9 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1062 LOC, 9 classes

**Integration Steps**:

1. REVIEW: Read labs/governance/guardian/drift_detector.py and understand architecture (1062 LOC, 9 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_drift_detector.py
4. MOVE: git mv labs/governance/guardian/drift_detector.py core/governance/guardian/drift_detector.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate drift_detector from labs"

---

### 179. labs.governance.guardian.system_health_monitor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/guardian/system_health_monitor.py` |
| Target Location | `core/governance/guardian/system_health_monitor.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 766 |
| Classes | 8 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 8 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/governance/guardian/system_health_monitor.py and understand architecture (766 LOC, 8 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_system_health_monitor.py
4. MOVE: git mv labs/governance/guardian/system_health_monitor.py core/governance/guardian/system_health_monitor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate system_health_monitor from labs"

---

### 180. labs.governance.monitoring.threat_monitor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/governance/monitoring/threat_monitor.py` |
| Target Location | `core/governance/monitoring/threat_monitor.py` |
| Complexity | medium |
| Effort | 12 hours |
| Risk Level | medium-high |
| LOC | 1268 |
| Classes | 3 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Matches pattern 'governance' - move to core/governance/

**Complexity Rationale**: 1268 LOC

**Integration Steps**:

1. REVIEW: Read labs/governance/monitoring/threat_monitor.py and understand architecture (1268 LOC, 3 classes, 1 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_threat_monitor.py
4. MOVE: git mv labs/governance/monitoring/threat_monitor.py core/governance/monitoring/threat_monitor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate threat_monitor from labs"

---

### 181. labs.emotion.tools.emotional_echo_detector (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/emotion/tools/emotional_echo_detector.py` |
| Target Location | `core/emotion/emotional_echo_detector.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 1405 |
| Classes | 7 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/emotion/ - review manually

**Complexity Rationale**: 1405 LOC, 7 classes

**Integration Steps**:

1. REVIEW: Read labs/emotion/tools/emotional_echo_detector.py and understand architecture (1405 LOC, 7 classes, 4 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_emotional_echo_detector.py
4. MOVE: git mv labs/emotion/tools/emotional_echo_detector.py core/emotion/emotional_echo_detector.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate emotional_echo_detector from labs"

---

### 182. labs.emotion.regulation.security_control_validation (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `labs/emotion/regulation/security_control_validation.py` |
| Target Location | `core/emotion/security_control_validation.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 660 |
| Classes | 9 |
| Functions | 0 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/emotion/ - review manually

**Complexity Rationale**: 9 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read labs/emotion/regulation/security_control_validation.py and understand architecture (660 LOC, 9 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_security_control_validation.py
4. MOVE: git mv labs/emotion/regulation/security_control_validation.py core/emotion/security_control_validation.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate security_control_validation from labs"

---

### 183. core.constellation_alignment_system (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/constellation_alignment_system.py` |
| Target Location | `core/constellation_alignment_system.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 701 |
| Classes | 7 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/constellation_alignment_system.py and understand architecture (701 LOC, 7 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_constellation_alignment_system.py
4. MOVE: git mv core/constellation_alignment_system.py core/constellation_alignment_system.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into MATRIZ engine or core system (add to registry, update config)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate constellation_alignment_system from labs"

---

### 184. core.matriz_consciousness_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/matriz_consciousness_integration.py` |
| Target Location | `core/matriz_consciousness_integration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 522 |
| Classes | 1 |
| Functions | 4 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/matriz_consciousness_integration.py and understand architecture (522 LOC, 1 classes, 4 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_matriz_consciousness_integration.py
4. MOVE: git mv core/matriz_consciousness_integration.py core/matriz_consciousness_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate matriz_consciousness_integration from labs"

---

### 185. core.bio_symbolic_processor (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/bio_symbolic_processor.py` |
| Target Location | `core/bio_symbolic_processor.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 532 |
| Classes | 5 |
| Functions | 2 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/bio_symbolic_processor.py and understand architecture (532 LOC, 5 classes, 2 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_bio_symbolic_processor.py
4. MOVE: git mv core/bio_symbolic_processor.py core/bio_symbolic_processor.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate bio_symbolic_processor from labs"

---

### 186. core.consciousness_signal_router (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/consciousness_signal_router.py` |
| Target Location | `core/consciousness_signal_router.py` |
| Complexity | low |
| Effort | 6 hours |
| Risk Level | medium-high |
| LOC | 733 |
| Classes | 7 |
| Functions | 1 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 7 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read core/consciousness_signal_router.py and understand architecture (733 LOC, 7 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_consciousness_signal_router.py
4. MOVE: git mv core/consciousness_signal_router.py core/consciousness_signal_router.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate consciousness_signal_router from labs"

---

### 187. core.integration.neuro_symbolic_fusion_layer (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/integration/neuro_symbolic_fusion_layer.py` |
| Target Location | `core/integration/neuro_symbolic_fusion_layer.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 605 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/integration/neuro_symbolic_fusion_layer.py and understand architecture (605 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_neuro_symbolic_fusion_layer.py
4. MOVE: git mv core/integration/neuro_symbolic_fusion_layer.py core/integration/neuro_symbolic_fusion_layer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate neuro_symbolic_fusion_layer from labs"

---

### 188. core.orchestration.brain.brain_integration (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/orchestration/brain/brain_integration.py` |
| Target Location | `core/orchestration/brain/brain_integration.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 633 |
| Classes | 3 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/orchestration/brain/brain_integration.py and understand architecture (633 LOC, 3 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_brain_integration.py
4. MOVE: git mv core/orchestration/brain/brain_integration.py core/orchestration/brain/brain_integration.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate brain_integration from labs"

---

### 189. core.symbolic.neuro_symbolic_fusion_layer (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/symbolic/neuro_symbolic_fusion_layer.py` |
| Target Location | `core/symbolic/neuro_symbolic_fusion_layer.py` |
| Complexity | low |
| Effort | 4 hours |
| Risk Level | medium-high |
| LOC | 508 |
| Classes | 4 |
| Functions | 1 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: already imports production code

**Integration Steps**:

1. REVIEW: Read core/symbolic/neuro_symbolic_fusion_layer.py and understand architecture (508 LOC, 4 classes, 1 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_neuro_symbolic_fusion_layer.py
4. MOVE: git mv core/symbolic/neuro_symbolic_fusion_layer.py core/symbolic/neuro_symbolic_fusion_layer.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate neuro_symbolic_fusion_layer from labs"

---

### 190. core.symbolic.lambda_sage (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `core/symbolic/lambda_sage.py` |
| Target Location | `core/symbolic/lambda_sage.py` |
| Complexity | medium |
| Effort | 14 hours |
| Risk Level | medium-high |
| LOC | 2151 |
| Classes | 6 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 2151 LOC, 6 classes

**Integration Steps**:

1. REVIEW: Read core/symbolic/lambda_sage.py and understand architecture (2151 LOC, 6 classes, 0 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_lambda_sage.py
4. MOVE: git mv core/symbolic/lambda_sage.py core/symbolic/lambda_sage.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate lambda_sage from labs"

---

### 191. bridge.api.orchestration_endpoints (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `bridge/api/orchestration_endpoints.py` |
| Target Location | `core/bridge/orchestration_endpoints.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 688 |
| Classes | 6 |
| Functions | 11 |
| Imports Core | No |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/bridge/ - review manually

**Complexity Rationale**: 6 classes

**Integration Steps**:

1. REVIEW: Read bridge/api/orchestration_endpoints.py and understand architecture (688 LOC, 6 classes, 11 functions)
2. CHECK_DEPS: Identify and resolve external dependencies, add core imports if needed
3. CREATE_TESTS: Write integration tests in tests/integration/test_orchestration_endpoints.py
4. MOVE: git mv bridge/api/orchestration_endpoints.py core/bridge/orchestration_endpoints.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate orchestration_endpoints from labs"

---

### 192. consciousness.__init__ (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `consciousness/__init__.py` |
| Target Location | `core/consciousness/__init__.py` |
| Complexity | low |
| Effort | 8 hours |
| Risk Level | medium-high |
| LOC | 400 |
| Classes | 17 |
| Functions | 6 |
| Imports Core | Yes |
| Imports MATRIZ | No |

**Reasoning**: Default placement in core/consciousness/ - review manually

**Complexity Rationale**: 17 classes, already imports production code

**Integration Steps**:

1. REVIEW: Read consciousness/__init__.py and understand architecture (400 LOC, 17 classes, 6 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test___init__.py
4. MOVE: git mv consciousness/__init__.py core/consciousness/__init__.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(core): integrate __init__ from labs"

---

### 193. matriz.nodes.validator_node (Score: 70.0)

| Property | Value |
|----------|-------|
| Current Location | `matriz/nodes/validator_node.py` |
| Target Location | `matriz/nodes/validator_node.py` |
| Complexity | low |
| Effort | 10 hours |
| Risk Level | medium-high |
| LOC | 1202 |
| Classes | 1 |
| Functions | 0 |
| Imports Core | No |
| Imports MATRIZ | Yes |

**Reasoning**: Already in production structure - verify placement

**Complexity Rationale**: 1202 LOC, already imports production code

**Integration Steps**:

1. REVIEW: Read matriz/nodes/validator_node.py and understand architecture (1202 LOC, 1 classes, 0 functions)
2. CHECK_DEPS: Verify all imports from core/matriz are valid and available
3. CREATE_TESTS: Write integration tests in tests/integration/test_validator_node.py
4. MOVE: git mv matriz/nodes/validator_node.py matriz/nodes/validator_node.py
5. UPDATE_IMPORTS: Fix import paths in moved module and any dependent modules
6. INTEGRATE: Wire into appropriate system component (update __init__.py, add exports)
7. TEST: Run pytest tests/integration/ and tests/smoke/ to verify
8. DOCUMENT: Update docs/architecture/ with new component location and purpose
9. COMMIT: git commit -m "feat(matriz): integrate validator_node from labs"

---

## 🧠 Reflection & Recovery

### Phase Reflection Protocol (per module)

After each of the 9 steps listed for a module:
1. **Summarize outcome** in one sentence
2. **Compare against** `expected_artifacts` in `.codex_trace.json`
3. **If deviation >10%** from expected state → revert and re-execute that step

### Controlled Recovery Mode (per module)

1. Log failure summary to `.codex_trace.json` under the module name
2. `git restore --staged . && git checkout -- .`
3. Re-read the last two modified files and the module's section in the guide
4. Retry with explicit `Edit` anchors (exact strings from Read output)
5. If failure repeats twice, escalate to manual audit

---

## Usage

### Codex Integration

```python
import json
with open('docs/audits/integration_manifest.json') as f:
    manifest = json.load(f)
    for module in manifest['modules']:
        if module['complexity'] == 'low':
            # Process low-complexity integrations first
            print(module['integration_steps'])
```

### Manual Integration

1. Pick a module from Top 20 Priority
2. Follow integration steps sequentially
3. Run tests after each major step
4. Update documentation
5. Commit with proper message format

### Bulk Integration Script

See `scripts/bulk_integrate_gems.py` for automated migration (coming soon).
