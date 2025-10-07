---
status: wip
type: documentation
owner: unknown
module: testing
redirect: false
moved_to: null
---

# JULES Agent Test Creation Allocation
**LUKHAS AI Test Suite Development Plan**

Generated: 2025-09-12  
Framework: T4 Testing Infrastructure  
Total Agents: 10 (Jules-01 through Jules-10)

---

## 📋 EXECUTIVE SUMMARY

After T4 framework implementation and test consolidation, we have identified **~150+ missing test modules** across 6 core architectural domains. This document allocates test creation tasks to 10 Jules agents for systematic test development.

**Current Status:**
- ✅ Working Tests: ~450 (consolidated from 800+ duplicates)  
- ⚠️ Missing Tests: ~150+ critical modules
- 🎯 Target: 95%+ test coverage with T4 quality gates

---

## 🧭 GLOBAL RULES (T4 / 0.01%)

**Determinism:** `TZ=UTC PYTHONHASHSEED=0 NUMBA_DISABLE_JIT=1` for every test run (local & CI).

**Lane isolation:**  
- ✅ Test **lukhas/** and **MATRIZ/** as production.  
- ⚠️ Any test that touches **candidate/** must be `@pytest.mark.quarantine` or `@pytest.mark.tier4` and **MUST NOT** import into `lukhas/**`. Use bridges or feature flags.

**Contract-first:** No new tests without a tiny `CONTRACT.md` (inputs/outputs/invariants) per module. Tests must assert invariants, not implementation details.

**Golden discipline:** MATRIZ/Identity routes require at least one golden JSON per route in `tests/golden/tier1/`. Router tests must pass with `MATRIZ_TRACES_DIR` override and with golden fallback.

**Ownership:** Every test file must declare:  
```yaml
# at file top (comment ok)
owner: Jules-XX
tier: tier1|tier2|tier3|tier4
module_uid: <path.to.module>
criticality: P0|P1|P2
```

**Mock policy:** Only mock external I/O. Never mock core domain logic (consciousness, memory, identity). Prefer contract tests with real components.

**Quality gates (per-PR):**
- Coverage per touched module ≥ its ratchet (cannot go down).  
- No `assert True/False`, no blanket `except: pass`, no prints as checks.  
- File-level **perf budget**: default 500 ms/test p95 (opt-out via `@pytest.mark.slow`).  
- **Flake control:** `@pytest.mark.quarantine` allowed; if a quarantined test fails twice in CI, PR fails.

**Evidence artifacts (auto):**
- `reports/tests/infra/collection.json` (discovery)  
- `reports/tests/cov.xml` + `reports/tests/priority_matrix.csv`  
- `reports/tests/perf/timings.json` (durations)  
- `reports/tests/golden/validation.json` (shape checks)

---

## 🎯 AGENT ALLOCATION STRATEGY

### ✅ Definition of Done (applies to every Jules agent)

- Tests created under `tests/{unit|integration|system}/...` following repo layout.
- Each test file has `owner`, `tier`, `module_uid`, `criticality` header (see GLOBAL RULES).
- Coverage (line) ≥ 80% and branch ≥ 60% **for the assigned module(s)** OR an explicit waiver with mitigation.
- Golden artifacts present where applicable; validator passes.
- All tests pass with **lane isolation** (no `lukhas → candidate` imports).
- Perf: p95 ≤ 500 ms/test (unless marked `slow` with rationale).
- CI artifacts written (collection, coverage, timings, golden validation).
- PR includes `SPEC_TEMPLATE.yaml`-based spec for the module and links to `CONTRACT.md`.

---

### **Jules-01: TIER 1 IDENTITY & AUTHENTICATION**
**Priority: CRITICAL** | **Estimated Tests: 25**

**Modules to Test:**
- `lukhas/governance/identity/core/auth/`
- `candidate/governance/identity/auth_backend/`
- `lukhas/governance/security/access_control.py`
- `candidate/governance/identity/core/qrg/qrg_manager.py`

**Key Test Requirements:**
```yaml
authentication:
  - test_user_login_success
  - test_password_validation 
  - test_session_management
  - test_multi_factor_auth
authorization:
  - test_permission_checking
  - test_role_based_access
  - test_resource_authorization
security:
  - test_token_generation
  - test_encryption_validation
  - test_security_headers
```

**Test Markers:** `@pytest.mark.tier1`, `@pytest.mark.security`, `@pytest.mark.critical`

**Lane policy:** Test only `lukhas/governance/...` in tier1. Any `candidate/...` path must be marked `quarantine` and cannot be imported by `lukhas` modules.

**Golden artifacts to produce:**
- `tests/golden/tier1/identity_login_success.json`
- `tests/golden/tier1/permission_matrix.json`

**Perf budget:** p95 < 300 ms for auth unit tests; < 800 ms for integration login→authorize flow.

**Minimal CONTRACT.md invariants (examples):**
- Token lifetime ≥ configured min; refresh invalidates prior session.
- Role→permission matrix is monotonic (no privilege escalation on downgrade).

---

### **Jules-02: TIER 1 CONSCIOUSNESS & AWARENESS**
**Priority: CRITICAL** | **Estimated Tests: 30**

**Modules to Test:**
- `candidate/consciousness/awareness/system_awareness.py`
- `candidate/consciousness/states/`
- `lukhas/core/orchestration/brain/consciousness/`
- `candidate/consciousness/dream/`

**Key Test Requirements:**
```yaml
awareness_processing:
  - test_consciousness_state_transitions
  - test_awareness_level_detection
  - test_context_processing
decision_making:
  - test_decision_tree_execution
  - test_reasoning_validation
  - test_consciousness_driven_choices
dream_states:
  - test_dream_engine_processing
  - test_oneiric_integration
  - test_dream_memory_links
```

**Test Markers:** `@pytest.mark.tier1`, `@pytest.mark.consciousness`, `@pytest.mark.critical`

**Golden artifacts:** `consciousness_state_cycle.json`, `awareness_context_window.json`

**Invariants:** 
- State transitions are total & valid; no illegal transitions.
- Awareness context window obeys size & eviction policy (MRU).
- Dream writes are tagged and retrievable without corrupting waking state.

---

### **Jules-03: TIER 1 MEMORY SYSTEMS**
**Priority: CRITICAL** | **Estimated Tests: 20**

**Modules to Test:**
- `candidate/memory/core/unified_memory_orchestrator.py`
- `candidate/memory/systems/memory_manager.py`
- `candidate/memory/folds/fold_engine.py`
- `memory/` (core module)

**Key Test Requirements:**
```yaml
memory_storage:
  - test_hierarchical_storage
  - test_memory_fold_operations
  - test_data_persistence
memory_retrieval:
  - test_key_based_retrieval
  - test_semantic_search
  - test_memory_lineage_tracking
performance:
  - test_memory_optimization
  - test_compression_algorithms
  - test_memory_leak_prevention
```

**Test Markers:** `@pytest.mark.tier1`, `@pytest.mark.memory`, `@pytest.mark.critical`

**DB/Test data policy:** Use tmp SQLite per test; `PRAGMA foreign_keys=ON`.

**Invariants:** 
- Fold open→append→close preserves lineage hash. 
- Retrieval by key and semantic vectors returns consistent top‑k across seeds.

---

### **Jules-04: TIER 2 GOVERNANCE & ETHICS**
**Priority: HIGH** | **Estimated Tests: 18**

**Modules to Test:**
- `candidate/governance/ethics/enhanced_ethical_guardian.py`
- `lukhas/governance/ethics/constitutional_ai.py`
- `candidate/governance/consent/consent_manager.py`
- `candidate/governance/guardian_system_integration.py`

**Key Test Requirements:**
```yaml
ethics_validation:
  - test_ethical_decision_making
  - test_constitutional_ai_compliance
  - test_guardian_system_integration
compliance:
  - test_gdpr_compliance
  - test_consent_management
  - test_regulatory_validation
monitoring:
  - test_ethics_violation_detection
  - test_compliance_reporting
  - test_audit_trail_generation
```

**Test Markers:** `@pytest.mark.tier2`, `@pytest.mark.ethics`, `@pytest.mark.governance`

**Guardian invariants:** 
- Constitutional checks run before orchestration approval.
- Ethics violations emit structured audit events with nonce & timestamp.

---

### **Jules-05: TIER 2 ORCHESTRATION & WORKFLOWS**
**Priority: HIGH** | **Estimated Tests: 22**

**Modules to Test:**
- `candidate/orchestration/multi_model_orchestration.py`
- `candidate/bridge/orchestration/`
- `lukhas/core/orchestration/`
- `candidate/bridge/workflow/workflow_orchestrator.py`

**Key Test Requirements:**
```yaml
workflow_management:
  - test_workflow_execution_engine
  - test_task_dependency_resolution
  - test_workflow_state_management
task_scheduling:
  - test_scheduler_algorithms
  - test_task_prioritization
  - test_resource_allocation
multi_ai_orchestration:
  - test_ai_model_coordination
  - test_consensus_mechanisms
  - test_model_fallback_strategies
```

**Test Markers:** `@pytest.mark.tier2`, `@pytest.mark.orchestration`, `@pytest.mark.integration`

**Workflow invariants:** 
- DAG topological order respected; cycle detection trips fast.
- Fallback path taken on model error; idempotent retries.

---

### **Jules-06: TIER 3 API GATEWAY & EXTERNAL SERVICES**
**Priority: MEDIUM** | **Estimated Tests: 15**

**Modules to Test:**
- `candidate/bridge/api_gateway/unified_api_gateway.py`
- `candidate/bridge/api/`
- `candidate/bridge/external_adapters/`
- `candidate/bridge/adapters/`

**Key Test Requirements:**
```yaml
api_gateway:
  - test_request_routing
  - test_rate_limiting
  - test_api_versioning
external_adapters:
  - test_gmail_adapter
  - test_dropbox_adapter
  - test_oauth_integration
service_integration:
  - test_service_discovery
  - test_circuit_breaker_patterns
  - test_retry_mechanisms
```

**Test Markers:** `@pytest.mark.tier3`, `@pytest.mark.api`, `@pytest.mark.integration`

**Security:** No real credentials. Use recorded fixtures; OAuth flow mocked only at boundary.

**Invariants:** 
- Rate limits enforced; 429 on exceed with retry-after.

---

### **Jules-07: BIO-QUANTUM SYSTEMS**
**Priority: MEDIUM** | **Estimated Tests: 12**

**Modules to Test:**
- `candidate/bio/` (all bio modules)
- `candidate/qi/` (quantum inspired modules)
- `lukhas/bio/core/bio_symbolic.py`
- `candidate/bio/quantum_inspired_layer/`

**Key Test Requirements:**
```yaml
bio_systems:
  - test_bio_symbolic_processing
  - test_mitochondrial_models
  - test_endocrine_integration
quantum_inspired:
  - test_qi_processing_core
  - test_quantum_state_simulation
  - test_bio_quantum_bridges
symbolic_integration:
  - test_symbolic_reasoning
  - test_bio_symbolic_adaptation
  - test_proteome_processing
```

**Test Markers:** `@pytest.mark.tier3`, `@pytest.mark.bio`, `@pytest.mark.quantum`

**Scientific humility:** Mark speculative models as `tier4` and document assumptions.

**Invariants:** 
- Bio-symbolic adapter preserves symbol IDs; no drift across runs (determinism env).

---

### **Jules-08: PERFORMANCE & MONITORING**
**Priority: MEDIUM** | **Estimated Tests: 10**

**Modules to Test:**
- `candidate/aka_qualia/metrics.py`
- `lukhas/core/distributed_tracing.py`
- `candidate/tools/performance_monitor.py`
- Monitoring and observability systems

**Key Test Requirements:**
```yaml
performance_monitoring:
  - test_metrics_collection
  - test_performance_benchmarks
  - test_resource_utilization
distributed_tracing:
  - test_trace_propagation
  - test_span_creation
  - test_distributed_debugging
observability:
  - test_prometheus_integration
  - test_dashboard_generation
  - test_alert_mechanisms
```

**Test Markers:** `@pytest.mark.tier3`, `@pytest.mark.performance`, `@pytest.mark.monitoring`

**Perf budgets:** 
- Metrics export ≤ 100 ms p95; tracing span creation ≤ 1 ms per span (unit).

---

### **Jules-09: INTEGRATION & E2E TESTING**
**Priority: HIGH** | **Estimated Tests: 16**

**Modules to Test:**
- Cross-module integration patterns
- End-to-end user journeys
- System-wide functionality

**Key Test Requirements:**
```yaml
integration_tests:
  - test_full_authentication_flow
  - test_consciousness_memory_integration
  - test_governance_orchestration_flow
e2e_tests:
  - test_user_onboarding_journey
  - test_ai_decision_making_pipeline
  - test_multi_component_workflows
system_tests:
  - test_system_startup_shutdown
  - test_failover_scenarios
  - test_data_consistency
```

**Test Markers:** `@pytest.mark.tier2`, `@pytest.mark.integration`, `@pytest.mark.e2e`

**E2E harness:** Use `docker-compose` profile `test`; external services mocked via adapters.

**Golden:** Capture `user_onboarding_success.json` after first green.

---

### **Jules-10: SPECIALIZED & LEGACY SYSTEMS**
**Priority: LOW-MEDIUM** | **Estimated Tests: 8**

**Modules to Test:**
- Legacy integration modules
- Specialized utilities
- Edge case handlers
- Tool integrations

**Key Test Requirements:**
```yaml
legacy_systems:
  - test_legacy_api_compatibility
  - test_data_migration_utilities
  - test_backwards_compatibility
tools_integration:
  - test_claude_integration
  - test_external_tool_orchestration
  - test_development_utilities
edge_cases:
  - test_error_handling
  - test_boundary_conditions
  - test_stress_scenarios
```

**Test Markers:** `@pytest.mark.tier4`, `@pytest.mark.legacy`, `@pytest.mark.tools`

**Legacy guard:** All legacy tests must assert deprecation warnings and compatibility mode behavior; never load legacy into production path by default.

**MCP:** Claude/MCP integration tests must run offline with local server stub.

---

## 📚 TECHNICAL SPECIFICATIONS

### **Test Framework Requirements**
All Jules agents must follow T4 framework standards:

```python
# Required imports and structure
import pytest
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# Test class structure
@pytest.mark.tier1  # or appropriate tier
@pytest.mark.critical  # or appropriate priority
class TestModuleName:
    """Test suite for ModuleName functionality"""
    
    def setup_method(self):
        """Setup before each test method"""
        pass
        
    def test_basic_functionality(self):
        """Test basic module functionality"""
        # Arrange
        # Act  
        # Assert
        pass
        
    def test_error_conditions(self):
        """Test error handling and edge cases"""
        pass
        
    def test_performance_requirements(self):
        """Test performance and resource constraints"""
        pass
```

### **Mandatory Test Categories**
Each agent must create tests for:
1. **Unit Tests**: Individual function/method testing
2. **Integration Tests**: Module interaction testing  
3. **Performance Tests**: Speed and resource usage
4. **Error Handling**: Edge cases and failure modes
5. **Security Tests**: Authentication, authorization, data protection

### **Quality Gates**
- **Minimum Coverage**: 80% line coverage per module
- **Performance**: All tests must complete within 30s
- **Reliability**: 99.5% test success rate required
- **Documentation**: Comprehensive docstrings and comments

---

## 🎯 SUCCESS CRITERIA

### **Per Agent Deliverables:**
- [ ] Complete test suite for assigned modules
- [ ] Minimum 80% code coverage
- [ ] All tests pass T4 framework validation
- [ ] Performance benchmarks within targets
- [ ] Documentation and test specifications

### **Overall Project Success:**
- [ ] **500+ total tests** (current ~450 + 150 new)
- [ ] **95% system coverage** across all tiers
- [ ] **Zero critical vulnerabilities** in test validation
- [ ] **Sub-100ms p95 latency** for tier1 tests
- [ ] **T4 framework compliance** for all new tests

---

## 📅 TIMELINE & COORDINATION

### **Phase 1 (Week 1): Critical Tier 1 Tests**
- Jules-01, Jules-02, Jules-03: Core system tests
- Target: 75 new tests, tier1 coverage complete

### **Phase 2 (Week 2): High Priority Tier 2 Tests**  
- Jules-04, Jules-05, Jules-09: Governance, orchestration, integration
- Target: 56 new tests, tier2 coverage substantial

### **Phase 3 (Week 3): Supporting Systems**
- Jules-06, Jules-07, Jules-08, Jules-10: API, bio-quantum, performance, legacy
- Target: 45 new tests, comprehensive coverage

### **Phase 4 (Week 4): Validation & Integration**
- All agents: Cross-validation, integration testing, performance optimization
- Target: System-wide validation, documentation complete

---

## 🔧 DEVELOPMENT TOOLS & RESOURCES

### **Required Tools:**
- **pytest**: Primary test framework
- **pytest-cov**: Coverage reporting
- **pytest-xdist**: Parallel test execution
- **hypothesis**: Property-based testing
- **factory_boy**: Test data generation

### **Available Resources:**
- **T4 Framework**: `/tools/tests/` validation tools
- **Architecture Specs**: `LUKHAS_ARCHITECTURE_MASTER.json`
- **Test Templates**: `tests/specs/SPEC_TEMPLATE.yaml`
- **Coverage Gates**: Automated quality validation
- **CI/CD Pipeline**: Automated test execution

### **Documentation:**
- **Test Standards**: Follow existing patterns in `tests/`
- **Code Style**: Black formatting, type hints required
- **Git Workflow**: Feature branches, PR-based integration
- **Review Process**: Peer review + automated validation

---

## 🧑‍💻 RUNBOOK (for every agent)

1) Create/claim a ticket from `reports/tests/queues/*.csv` and link it in your PR.
2) Generate/complete module spec from `tests/specs/SPEC_TEMPLATE.yaml`; attach as `tests/specs/<module>.yaml`.
3) Write/verify `CONTRACT.md` (tiny; invariants only) next to the module if missing.
4) Implement tests under `tests/{unit|integration|system}/...`.
5) Run:
   ```
   make test-fast
   make test-all
   pytest -q -m tier1 --durations=10 --maxfail=1
   ```
6) Ensure artifacts exist under `reports/tests/**`; fix if missing.
7) Open PR with labels: `tests`, `tierX`, and your agent label `Jules-YY`.
8) Green CI, reviewer sign‑off, merge via lane policy.

---

## ⚡ QUICK START GUIDE

### **For Each Jules Agent:**

1. **Setup Environment**
   ```bash
   git clone <lukhas-repo>
   cd Lukhas
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Understand Your Module**
   ```bash
   # Find your assigned modules
   find . -path "./candidate/your-module/*" -name "*.py"
   find . -path "./lukhas/your-module/*" -name "*.py" 
   ```

3. **Create Test Structure**
   ```bash
   mkdir -p tests/unit/your-module
   mkdir -p tests/integration/your-module
   cp tests/specs/SPEC_TEMPLATE.yaml tests/specs/your-module.yaml
   ```

4. **Run Existing Tests**
   ```bash
   pytest tests/ -m tier1 --tb=short
   ```

5. **Validate Your Tests**
   ```bash
   python tools/tests/spec_lint.py
   pytest your-tests/ --cov=your-module --cov-report=term-missing
   ```

---

**Ready for deployment to Jules agents. Each agent has clear ownership, specifications, and success criteria for systematic test development.**