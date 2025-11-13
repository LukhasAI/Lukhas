# Claude Code Web - Test Fix Package

## 🎯 Mission: Fix 200 Test Collection Errors

**Date:** November 7, 2025
**Repo:** /Users/agi_dev/LOCAL-REPOS/Lukhas
**Python:** 3.9.6
**Total Errors:** 200 test files

## 📊 Error Categories

### 1. TypeError: dataclass() (19 errors)
**Pattern:** `TypeError: dataclass() got an unexpected keyword argument`

```
tests/api/test_routing_admin_auth.py
tests/core/identity/test_advanced_identity_manager.py
tests/core/identity/test_identity_manager.py
tests/core/orchestration/brain/spine/test_healix_integration.py
tests/dashboard/test_widget_integration.py
tests/identity/test_enhanced_identity_service.py
tests/unit/bridge/api_gateway/test_unified_api_gateway.py
tests/unit/security/test_bio_oscillator_session_validation.py
tests/unit/security/test_security_monitor.py
```

**Fix:** Likely Pydantic/dataclass mixing. Check for:
- `@dataclass` with Pydantic `BaseModel`
- Python 3.9 incompatible dataclass syntax
- Missing imports

---

### 2. RecursionError (14 errors)
**Pattern:** `RecursionError: maximum recursion depth exceeded`

```
tests/cognitive/property_based/test_reasoning_edge_cases.py
tests/cognitive/stress/test_cognitive_load_infrastructure.py
tests/cognitive/test_comprehensive_coverage.py
tests/consciousness/test_advanced_cognitive_features.py
tests/drift/test_drift_autorepair.py
tests/e2e/rl/test_consciousness_rl.py
tests/integration/bio/test_bio_architecture.py
tests/ledger/test_event_sourcing_properties.py
tests/memory/test_memory_backends.py
tests/memory/test_memory_lifecycle.py
tests/observability/test_integration.py
tests/orchestration/test_externalized_routing.py
tests/unit/consciousness/test_registry_activation_order.py
```

**Fix:** Circular imports or infinite recursion in fixtures. Check for:
- Circular imports between modules
- Fixture recursion (fixture calling itself)
- Import loops at module level

---

### 3. ModuleNotFoundError (12 errors)
**Pattern:** `ModuleNotFoundError: No module named 'X'`

```
tests/contract/candidate/aka_qualia
tests/e2e/candidate/aka_qualia
tests/integration/candidate/aka_qualia
tests/smoke
tests/unit/candidate/aka_qualia
```

**Common missing modules:**
- `aka_qualia` (appears multiple times)
- `opentelemetry.exporter` (in smoke tests)

**Fix:**
- Add missing dependencies to requirements.txt
- Fix import paths
- Remove tests for deprecated modules

---

### 4. ValueError: not enough values to unpack (8 errors)
**Pattern:** `ValueError: not enough values to unpack`

```
tests/unit/bridge/test_audio_engine.py
tests/unit/bridge/test_direct_ai_router.py
tests/unit/core/orchestration/test_integration_hub_quantum.py
tests/unit/core/test_time_tz.py
tests/unit/memory/test_fold_engine.py
tests/unit/memory/test_memory_manager.py
tests/unit/orchestration/test_kernel_bus_smoke.py
tests/unit/products/experience/test_experience_modules.py
```

**Fix:** Tuple unpacking issues. Check for:
- Function returning wrong number of values
- Incorrect tuple destructuring
- API changes

---

### 5. FileNotFoundError (2 errors)
**Pattern:** `FileNotFoundError: [Errno 2] No such file or directory`

```
tests/rules/test_star_rules.py
tests/unit/tools/test_todo_tooling.py
```

**Fix:** Missing fixture files, data files, or incorrect paths

---

### 6. AttributeError (3 errors)
**Pattern:** `AttributeError: module has no attribute X`

```
tests/integration/bridge/adapters/test_gmail_adapter.py
tests/unit/bridge/adapters/test_gmail_adapter.py
tests/unit/orchestration/test_openai_modulated_service.py
```

**Fix:** Check for:
- Incorrect imports
- Deprecated API usage
- Missing attributes after refactoring

---

### 7. NameError (1 error)
**Pattern:** `NameError: name 'Dict' is not defined`

```
tests/performance/test_router_fast_path.py
```

**Fix:** Replace `Dict` with `dict` (PEP 585)

---

### 8. pytest.Failed (3 errors)
**Pattern:** Test configuration failures

```
tests/security/test_pqc_redteam.py - Failed: 'pqc' not found in markers
tests/unit/bridge/adapters/test_oauth_manager_advanced.py - Failed: 'medium'
tests/unit/memory/test_memory_event_optimization.py - Failed: 'property'
```

**Fix:** Add missing pytest markers to pytest.ini

---

### 9. Generic/Other Errors (138 errors)
Tests without specific error messages in collection output

---

## 🎯 Priority Order

### Priority 1: Quick Wins (30 tests - ~30 min)
**Impact:** Highest ROI

1. **NameError fixes** (1 test): `Dict` → `dict`
2. **Pytest markers** (3 tests): Add to pytest.ini
3. **FileNotFoundError** (2 tests): Create/fix paths
4. **dataclass fixes** (19 tests): Fix Pydantic mixing
5. **ValueError unpacking** (5 tests): Fix return values

**Estimated time:** 30 minutes
**Tests fixed:** 30
**Impact:** 15% reduction

### Priority 2: Critical Systems (50 tests - ~1 hour)
**Focus:** Security, governance, identity

1. **tests/unit/security/** (3 tests)
2. **tests/integration/security/** (1 test)
3. **tests/unit/governance/** (20+ tests)
4. **tests/unit/identity/** (10+ tests)
5. **tests/e2e/security/** (1 test)
6. **tests/guardian/** (5 tests)

**Estimated time:** 1 hour
**Tests fixed:** 50
**Impact:** Critical systems unblocked

### Priority 3: Recursion Errors (14 tests - ~45 min)
**Complexity:** Medium - requires import analysis

1. Identify circular import chains
2. Break import loops
3. Refactor fixture dependencies
4. Test each fix

**Estimated time:** 45 minutes
**Tests fixed:** 14
**Impact:** 7% reduction

### Priority 4: Missing Modules (12 tests - ~30 min)
**Options:** Fix imports OR deprecate tests

1. Identify required vs deprecated modules
2. Add missing dependencies
3. Fix import paths
4. OR mark as deprecated/skip

**Estimated time:** 30 minutes
**Tests fixed:** 12
**Impact:** 6% reduction

### Priority 5: Remaining Tests (94 tests - ~2 hours)
**Approach:** Batch processing

1. Group by directory
2. Fix common patterns
3. Test batch by batch

**Estimated time:** 2 hours
**Tests fixed:** 94
**Impact:** 47% of total

---

## 📋 Complete Error List (200 tests)

```
ERROR tests/api/test_routing_admin_auth.py - TypeError
ERROR tests/candidate/qi/test_qi_entanglement.py
ERROR tests/capabilities/test_governance_suite.py
ERROR tests/cognitive/property_based/test_reasoning_edge_cases.py - RecursionError
ERROR tests/cognitive/stress/test_cognitive_load_infrastructure.py - RecursionError
ERROR tests/cognitive/test_comprehensive_coverage.py - RecursionError
ERROR tests/consciousness/test_advanced_cognitive_features.py - RecursionError
ERROR tests/consciousness/test_c1_consciousness_components.py
ERROR tests/consciousness/test_creativity_engine.py
ERROR tests/consciousness/test_guardian_integration.py
ERROR tests/consciousness/test_lukhas_reflection_engine.py
ERROR tests/consciousness/test_reflection_engine.py
ERROR tests/constraints/test_plan_verifier.py
ERROR tests/contract/candidate/aka_qualia - ModuleNotFoundError
ERROR tests/core/api/test_api_system.py
ERROR tests/core/identity/test_advanced_identity_manager.py - TypeError
ERROR tests/core/identity/test_identity_manager.py - TypeError
ERROR tests/core/modules/test_voice_narration.py
ERROR tests/core/orchestration/brain/spine/test_healix_integration.py - TypeError
ERROR tests/core/orchestration/test_dream_adapter.py
ERROR tests/core/symbolic/test_dast_engine.py
ERROR tests/core/symbolic/test_neuro_symbolic_fusion_layer.py
ERROR tests/core/test_consciousness_signal_router.py
ERROR tests/dashboard/test_widget_integration.py - TypeError
ERROR tests/deployment/test_blue_green_deployment.py
ERROR tests/drift/test_drift_acceptance.py
ERROR tests/drift/test_drift_autorepair.py - RecursionError
ERROR tests/drift/test_drift_manager.py
ERROR tests/drift/test_drift_task15_acceptance.py
ERROR tests/e2e/candidate/aka_qualia - ModuleNotFoundError
ERROR tests/e2e/core/test_exceptions_additional.py
ERROR tests/e2e/governance/test_guardian.py
ERROR tests/e2e/lukhas/test_consciousness.py
ERROR tests/e2e/rl/test_consciousness_rl.py - RecursionError
ERROR tests/e2e/security/test_authentication.py
ERROR tests/e2e/test_async_reliability_integration.py
ERROR tests/e2e/test_guardian_integrated_platform.py
ERROR tests/e2e/test_matriz_orchestration.py
ERROR tests/ethics/test_dsl_eval.py
ERROR tests/ethics/test_tags_preprocess.py
ERROR tests/examples/test_governance_example.py
ERROR tests/governance/test_governance.py
ERROR tests/governance/test_guardian_defaults.py
ERROR tests/governance/test_lane_consistency.py
ERROR tests/guardian/test_pdp.py
ERROR tests/guardian/test_policy_format_compat.py
ERROR tests/identity/test_enhanced_identity_service.py - TypeError
ERROR tests/integration/api/test_api_endpoints.py
ERROR tests/integration/api/test_main.py
ERROR tests/integration/api/test_observability.py
ERROR tests/integration/bio/test_bio_architecture.py - RecursionError
ERROR tests/integration/bio/test_spirulina_atp_system.py
ERROR tests/integration/bridge/adapters/test_gmail_adapter.py - AttributeError
ERROR tests/integration/bridge/api_gateway/test_unified_api_gateway_integration.py
ERROR tests/integration/candidate/aka_qualia - ModuleNotFoundError
ERROR tests/integration/candidate/core/collective/test_collective_intelligence.py
ERROR tests/integration/candidate/core/test_nias_transcendence.py
ERROR tests/integration/contract/test_healthz_voice_required.py
ERROR tests/integration/end_to_end/test_authentication_flow.py
ERROR tests/integration/end_to_end/test_consciousness_memory.py
ERROR tests/integration/end_to_end/test_decision_pipeline.py
ERROR tests/integration/end_to_end/test_governance_orchestration.py
ERROR tests/integration/end_to_end/test_multi_component_workflows.py
ERROR tests/integration/identity/test_authentication_server.py
ERROR tests/integration/products/communication/test_abas_engine.py
ERROR tests/integration/qi/test_jurisdiction_compliance.py
ERROR tests/integration/security/test_security_monitor_integration.py - TypeError
ERROR tests/integration/test_aka_qualia.py
ERROR tests/integration/test_async_manager.py
ERROR tests/integration/test_cross_component.py
ERROR tests/integration/test_full_system_integration.py
ERROR tests/integration/test_matriz_complete_thought_loop.py
ERROR tests/integration/test_openai_facade_integration.py
ERROR tests/integration/test_orchestration_webauthn_integration.py
ERROR tests/integration/test_orchestrator_matriz_roundtrip.py
ERROR tests/integration/test_parallel_orchestration.py
ERROR tests/integration/test_production_main.py
ERROR tests/integration/tools/test_dependency_hasher.py
ERROR tests/labs/core/governance/test_guardian_integration_middleware.py
ERROR tests/ledger/test_event_sourcing_properties.py - RecursionError
ERROR tests/memory/test_indexes_api.py
ERROR tests/memory/test_lifecycle.py
ERROR tests/memory/test_memory_backends.py - RecursionError
ERROR tests/memory/test_memory_lifecycle.py - RecursionError
ERROR tests/obs/test_metrics_smoke.py
ERROR tests/observability/test_integration.py - RecursionError
ERROR tests/observability/test_label_contracts.py
ERROR tests/observability/test_matriz_cognitive_instrumentation.py
ERROR tests/observability/test_matriz_metrics_contract.py
ERROR tests/observability/test_opentelemetry_tracing.py
ERROR tests/observability/test_performance_validation.py
ERROR tests/orchestration/test_async_orchestrator_metrics.py
ERROR tests/orchestration/test_externalized_routing.py - RecursionError
ERROR tests/orchestration/test_guardian_enforcement.py
ERROR tests/orchestration/test_killswitch.py
ERROR tests/orchestration/test_multi_ai_router.py
ERROR tests/orchestration/test_plan_verifier.py
ERROR tests/perf/test_async_orchestrator_perf.py
ERROR tests/performance/test_performance_budgets.py
ERROR tests/performance/test_router_fast_path.py - NameError
ERROR tests/reliability/test_0_01_percent_features.py
ERROR tests/resilience/test_circuit_breaker.py
ERROR tests/rules/test_star_rules.py - FileNotFoundError
ERROR tests/scripts/test_agi_module_analyzer.py
ERROR tests/scripts/test_generate_todo_inventory.py
ERROR tests/security/test_pqc_redteam.py - pytest.Failed
ERROR tests/security/test_security_monitor.py - TypeError
ERROR tests/smoke - ModuleNotFoundError
ERROR tests/soak/test_guardian_matriz_throughput.py
ERROR tests/system/integration/test_failover.py
ERROR tests/system/integration/test_system_lifecycle.py
ERROR tests/test_backpressure_ring.py
ERROR tests/test_chatgpt_mcp.py
ERROR tests/test_clock.py
ERROR tests/test_consciousness_stream.py
ERROR tests/test_consciousness_tick.py
ERROR tests/test_drift.py
ERROR tests/test_guardian_quick.py
ERROR tests/test_guardian_serializers.py
ERROR tests/test_hidden_gems_summary.py
ERROR tests/test_mcp_enhanced_tools.py
ERROR tests/test_mcp_fetch.py
ERROR tests/test_mcp_minimal.py
ERROR tests/test_memory_sync.py
ERROR tests/test_policy_guard.py
ERROR tests/test_security_caching_storage.py
ERROR tests/tools/test_wavec_snapshot.py
ERROR tests/unit/behavior/test_behavioral_utils.py
ERROR tests/unit/bridge/adapters/test_drive_adapter.py
ERROR tests/unit/bridge/adapters/test_gmail_adapter.py - AttributeError
ERROR tests/unit/bridge/adapters/test_oauth_manager_advanced.py - pytest.Failed
ERROR tests/unit/bridge/api_gateway/test_unified_api_gateway.py - TypeError
ERROR tests/unit/bridge/external_adapters/test_gmail_adapter.py
ERROR tests/unit/bridge/test_audio_engine.py - ValueError
ERROR tests/unit/bridge/test_direct_ai_router.py - ValueError
ERROR tests/unit/candidate/aka_qualia - ModuleNotFoundError
ERROR tests/unit/candidate/consciousness/dream/test_dream_feedback_controller.py
ERROR tests/unit/candidate/consciousness/test_decision_engine.py
ERROR tests/unit/candidate/core/identity/test_constitutional_ai_compliance.py
ERROR tests/unit/candidate/qi/bio/test_bio_optimizer.py
ERROR tests/unit/candidate/qi/engines/identity/test_consolidate_identity_qi_secure.py
ERROR tests/unit/candidate/qi/test_qi_financial_consciousness_engine.py - AttributeError
ERROR tests/unit/consciousness/test_awareness_engine_setup.py
ERROR tests/unit/consciousness/test_awareness_log_synchronizer.py
ERROR tests/unit/consciousness/test_circuit_breakers.py
ERROR tests/unit/consciousness/test_core_integrator_access_tier.py
ERROR tests/unit/consciousness/test_ethical_drift_sentinel.py
ERROR tests/unit/consciousness/test_registry_activation_order.py - RecursionError
ERROR tests/unit/core/orchestration/test_integration_hub_quantum.py - ValueError
ERROR tests/unit/core/test_time_tz.py - ValueError
ERROR tests/unit/governance/ethics/test_candidate_constitutional_ai.py
ERROR tests/unit/governance/ethics/test_constitutional_ai.py
ERROR tests/unit/governance/ethics/test_enhanced_ethical_guardian.py
ERROR tests/unit/governance/ethics/test_enhanced_ethical_guardian_audit.py
ERROR tests/unit/governance/ethics/test_guardian_kill_switch.py
ERROR tests/unit/governance/ethics/test_guardian_reflector_imports.py
ERROR tests/unit/governance/ethics/test_moral_agent_template.py
ERROR tests/unit/governance/test_consent_history_manager.py
ERROR tests/unit/governance/test_consolidate_guardian_governance.py
ERROR tests/unit/governance/test_constitutional_ai_safety.py
ERROR tests/unit/governance/test_guardian_integration_middleware.py
ERROR tests/unit/governance/test_guardian_schema_standardization.py
ERROR tests/unit/governance/test_jules03_identity.py
ERROR tests/unit/governance/test_qrg_generator.py
ERROR tests/unit/governance/test_symbolic_scopes.py
ERROR tests/unit/identity/test_matriz_consciousness_identity_signals.py
ERROR tests/unit/identity/test_token_types.py
ERROR tests/unit/identity/test_token_types_aud_list.py
ERROR tests/unit/identity/test_token_types_expiry_guard.py
ERROR tests/unit/identity/test_token_types_helpers.py
ERROR tests/unit/identity/test_token_types_iat.py
ERROR tests/unit/identity/test_webauthn_credential.py
ERROR tests/unit/identity/test_webauthn_verify.py
ERROR tests/unit/lukhas/memory/test_index.py
ERROR tests/unit/memory/test_fold_engine.py - ValueError
ERROR tests/unit/memory/test_memory_event_optimization.py - pytest.Failed
ERROR tests/unit/memory/test_memory_manager.py - ValueError
ERROR tests/unit/memory/test_unified_memory_orchestrator.py
ERROR tests/unit/monitoring/test_monitoring_basic.py
ERROR tests/unit/orchestration/test_kernel_bus_smoke.py - ValueError
ERROR tests/unit/orchestration/test_openai_modulated_service.py - AttributeError
ERROR tests/unit/products/experience/test_experience_modules.py - ValueError
ERROR tests/unit/qi/test_bio_coordinator_smoke.py
ERROR tests/unit/qi/test_budgeter.py
ERROR tests/unit/qi/test_compliance_report.py
ERROR tests/unit/qi/test_multi_jurisdiction_engine.py
ERROR tests/unit/qi/test_privacy_statement.py
ERROR tests/unit/qi/test_system_orchestrator.py
ERROR tests/unit/security/test_bio_oscillator_session_validation.py - TypeError
ERROR tests/unit/security/test_secure_random.py
ERROR tests/unit/security/test_security_monitor.py - TypeError
ERROR tests/unit/test_additional_coverage.py
ERROR tests/unit/test_awareness_protocol.py
ERROR tests/unit/test_guardian_kill_switch.py
ERROR tests/unit/test_idempotency_redis.py
ERROR tests/unit/test_quota_hierarchy.py
ERROR tests/unit/test_ratelimit_headers.py
ERROR tests/unit/test_ratelimit_metrics.py
ERROR tests/unit/tools/test_categorize_todos.py
ERROR tests/unit/tools/test_todo_tooling.py - FileNotFoundError
```

---

## ✅ Success Criteria

After Claude Web fixes:
- ✅ Collection errors: 200 → 0
- ✅ Tests running: ~640 → ~840
- ✅ All security/governance tests pass
- ✅ No lane isolation violations
- ✅ All tests collect successfully

**Combined with 660 Jules tests = ~1,500 total tests running!**

## 💰 Value Proposition

| Metric | Value |
|--------|-------|
| Tests blocked | 200 |
| Time (manual) | 2-3 weeks |
| Time (Claude Web) | 3-5 hours |
| Cost (manual) | $20K-30K |
| Cost (Claude Web) | $1000 credit |
| **Savings** | **$19K-29K + 2-3 weeks** |

---

## 🚀 Ready to Upload to Claude Code Web

1. Open Claude Code Web (claude.ai)
2. Start new conversation
3. Upload this file
4. Say: "Please fix these 200 test collection errors following the priority order"
5. Monitor progress
6. Review and merge fixes

**This is industrial-scale bug fixing with AI. Let's go! 🚀**
