# LUKHAS Audit TODO Tasks

## Executive Summary
This document contains **62 precise tasks** derived from the Executive Summary audit to address all identified issues in the LUKHAS AI system. Tasks are organized by category, prioritized, and include specific fix instructions suitable for delegation to agents unfamiliar with the codebase.

## Priority Levels
- **P0**: Critical - Production blockers (must fix immediately)
- **P1**: High - Safety/Performance issues (fix within 1 week)
- **P2**: Medium - Feature completion (fix within 2 weeks)
- **P3**: Low - Documentation/cleanup (fix within month)

## Effort Estimates
- **S**: Small - <2 hours
- **M**: Medium - 2-8 hours
- **L**: Large - >8 hours

## Agent Routing Matrix (T4 / 0.01%)

**Legend**
- **CODEX** = deep repo refactors, Python infra, registries, orchestrator, performance
- **Jules** = observability, CI/CD, PromQL/Grafana, security & supply chain
- **Claude Code** = test authoring, DSL/spec logic, docs/runbooks, tricky edge-case reasoning
- **Copilot** = small refactors, repetitive unit tests, docstrings, mechanical edits

**Default assignment per task (backup in parentheses):**

- **Safety & Governance**
  - SG001: CODEX (Jules)
  - SG002: CODEX (Claude Code)
  - SG003: CODEX (Claude Code)
  - SG004: Claude Code (CODEX)
  - SG005: CODEX (Claude Code)
  - SG006: Jules (CODEX)
  - SG007: Jules (Claude Code)
  - SG008: Claude Code (CODEX)
  - SG009: CODEX (Jules)
  - SG010: Jules (Claude Code)

- **Memory System**
  - MS001: CODEX (Claude Code)
  - MS002: Claude Code (CODEX)
  - MS003: Claude Code (CODEX)
  - MS004: CODEX (Jules)
  - MS005: CODEX (Claude Code)
  - MS006: CODEX (Claude Code)
  - MS007: CODEX (Jules)
  - MS008: Claude Code (CODEX)

- **MATRIZ Pipeline & Orchestration**
  - MP001: CODEX (Claude Code)
  - MP002: CODEX (Claude Code)
  - MP003: Claude Code (Jules)
  - MP004: CODEX (Claude Code)
  - MP005: CODEX (Jules)
  - MP006: Jules (CODEX)
  - MP007: CODEX (Claude Code)
  - MP008: CODEX (Claude Code)
  - MP009: CODEX (Jules)
  - MP010: CODEX (Claude Code)
  - MP011: CODEX (Claude Code)
  - MP012: Claude Code (CODEX)

- **Observability & Metrics**
  - OB001: Jules (CODEX)
  - OB002: Jules (CODEX)
  - OB003: CODEX (Jules)
  - OB004: Jules (Claude Code)
  - OB005: Jules (Claude Code)
  - OB006: Jules (Claude Code)
  - OB007: Jules (CODEX)
  - OB008: Jules (Claude Code)

- **Security & Supply Chain**
  - SC001: Jules (CODEX)
  - SC002: Jules (Claude Code)
  - SC003: Jules (CODEX)
  - SC004: Jules (CODEX)
  - SC005: Jules (CODEX)
  - SC006: Claude Code (Jules)

- **Lane Management**
  - LM001: CODEX (Jules)
  - LM002: Jules (CODEX)
  - LM003: Claude Code (CODEX)
  - LM004: CODEX (Jules)
  - LM005: Claude Code (CODEX)

- **Documentation & Cleanup**
  - DC001: CODEX (Claude Code)
  - DC002: CODEX (Claude Code)
  - DC003: Claude Code (Jules)
  - DC004: Claude Code (CODEX)
  - DC005: CODEX (Claude Code)

- **Testing & Performance**
  - TP001: Claude Code (CODEX)
  - TP002: CODEX (Claude Code)
  - TP003: Jules (Claude Code)
  - TP004: CODEX (Claude Code)
  - TP005: Claude Code (Copilot)
  - TP006: Claude Code (CODEX)
  - TP007: Jules (CODEX)
  - TP008: Jules (CODEX)

---

## 1. Safety & Governance Critical Fixes (10 tasks)

#### T4/0.01% Augmentations (apply to SG001–SG010)
- Shadow-mode **counterfactual logging**: emit `would_action` vs `actual_action`; diff per route.
- **Fail-closed defaults**: flags/env missing → safe deny or noop-with-tag.
- **Property-based DSL tests** (Hypothesis) for zero-width/homoglyph/obfuscation; idempotence of tag pipeline.
- **Emergency drill in CI**: create/remove `/tmp/guardian_emergency_disable`; validate immediate effect.
- **Dual-approval invariants**: enforce `approver_a != approver_b`, reason, TTL; ledger schema migration test.
- **Perf budget gates**: p95 and overhead ratio alerts; CI perf test with `LUKHAS_PERF=1`.

### SG001: Enable Guardian DSL enforcement in canary mode [P0, S]
- **Problem**: Guardian safety enforcement is OFF by default
- **Location**: `docs/ethics/tags.md:L128-135`, `guardian/emit.py:L72-75`
- **Fix**: Set ENFORCE_ETHICS_DSL=1 for 10% canary traffic
- **Verify**: Check guardian_pipeline_ms p99 <5ms overhead

### SG002: Implement Guardian emergency kill-switch [P0, S]
- **Problem**: Kill-switch documented but not implemented in code
- **Location**: Add to `lukhas/governance/ethics/ethics_engine.py`
- **Fix**: Add `if Path('/tmp/guardian_emergency_disable').exists(): return ALLOW`
- **Verify**: Test file creation immediately disables enforcement

### SG003: Enable LLM Guardrail schema validation [P1, M]
- **Problem**: LLM guardrail is dark-launched, not validating outputs
- **Location**: `lukhas/core/bridge/llm_guardrail.py:L72-75,L94-102`
- **Fix**: Set ENABLE_LLM_GUARDRAIL=1 in staging
- **Verify**: Schema violations correctly rejected

### SG004: Document dual-approval override process [P1, S]
- **Problem**: Dual approval exists but process undocumented
- **Location**: `guardian/emit.py:L74-83`, `identity/consent/exemption_ledger.sql:L16-21`
- **Fix**: Create `docs/runbooks/guardian_override_playbook.md`
- **Verify**: Team can execute override in <10 minutes

### SG005: Fix consent ledger schema [P2, M]
- **Problem**: No user consent tracking for high-impact operations
- **Location**: `identity/consent/exemption_ledger.sql:L12-20`
- **Fix**: Add user_consent_timestamp and consent_method fields
- **Verify**: Consent required for FINANCIAL/PII operations

### SG006: Gradual Guardian enforcement rollout [P0, M]
- **Problem**: Need phased rollout plan
- **Location**: `docs/runbooks/safety_tags_go_live_drill.md:L74-82`
- **Fix**: Week 1: 10%, Week 2: 50%, Week 3: 100%
- **Verify**: Each phase completes without SLO violations

### SG007: Create Guardian metrics dashboard [P1, S]
- **Problem**: Dashboard defined but not deployed
- **Location**: `guardian/tags_dashboard.json`
- **Fix**: Import to Grafana, configure alerts
- **Verify**: All metrics visible, alerts fire on thresholds

### SG008: Implement safety tag DSL tests [P1, M]
- **Problem**: No end-to-end tests for DSL rules
- **Location**: Create `tests/integration/test_guardian_dsl.py`
- **Fix**: Test all 6 safety categories with ENFORCE_ETHICS_DSL=1
- **Verify**: All drift bands and edge cases tested

### SG009: Replace TelemetryCounter stubs [P1, S]
- **Problem**: Metrics are stubs, not real Prometheus counters
- **Location**: `lukhas/core/bridge/llm_guardrail.py:L24-32`
- **Fix**: Replace with prometheus_client Counter objects
- **Verify**: Metrics visible at /metrics endpoint

### SG010: Audit guardian_exemptions ledger [P2, S]
- **Problem**: Need regular audit of overrides
- **Location**: `identity/consent/exemption_ledger.sql:L7-21`
- **Fix**: Create `scripts/audit/guardian_overrides.py`
- **Verify**: Monthly audit report generated

---

## 2. Memory System Performance (8 tasks)

#### T4/0.01% Augmentations (apply to MS001–MS008)
- **Golden recall set** in `tests/data/memory_golden.json`; lock expected Top-K ids.
- **Wilson CI** for cascade-prevention KPIs; explicit ≥ target thresholds in tests.
- **Invariants**: consolidation is lossless for metadata and idempotent; property-based fuzzing (sizes/scores).
- **Quarantine audit**: metrics + monthly report of quarantined items by reason; manual release path.
- **Chaos hooks**: random delays/failures in store adapters behind `MATRIZ_CHAOS=1` (tests only).

### MS001: Implement missing MATRIZ cognitive nodes [P0, L]
- **Problem**: Nodes are stubs/placeholders
- **Location**: `candidate/core/matrix/nodes/__init__.py:L26-34`
- **Fix**: Create real MemoryNode, ThoughtNode, DecisionNode classes
- **Verify**: No LookupError in orchestrator

### MS002: Test memory cascade prevention at scale [P1, M]
- **Problem**: Not tested under heavy load
- **Location**: `lukhas/memory/fold_system.py:L120-129,L144-152`
- **Fix**: Test with 10,000+ items, verify 99.7% prevention
- **Verify**: recall_top_k() <100ms at scale

### MS003: Test fold consolidation edge cases [P1, M]
- **Problem**: Consolidation might lose data
- **Location**: `lukhas/memory/adaptive_memory.py:L108-115,L427-436`
- **Fix**: Force consolidation, verify summary quality
- **Verify**: Consolidated items remain searchable

### MS004: Optimize memory embeddings performance [P2, M]
- **Problem**: Embeddings might degrade performance
- **Location**: `lukhas/memory/adaptive_memory.py:L310-328`
- **Fix**: Implement vector indexing (FAISS/Annoy)
- **Verify**: Embeddings add <20ms to recall

### MS005: Add memory quarantine for anomalies [P3, S]
- **Problem**: No protection against poisoned entries
- **Location**: Add to `lukhas/memory/fold_system.py`
- **Fix**: Detect and quarantine extreme importance scores
- **Verify**: Anomalous entries quarantined

### MS006: Implement soft-delete for memory [P2, S]
- **Problem**: Pruned memories permanently lost
- **Location**: `lukhas/memory/fold_system.py:L134-143`
- **Fix**: Add deleted_at timestamp, 7-day retention
- **Verify**: Deleted items recoverable

### MS007: Add memory metrics to Prometheus [P2, S]
- **Problem**: Memory operations not instrumented
- **Location**: Throughout memory modules
- **Fix**: Add fold_count, cascade_events, recall_latency metrics
- **Verify**: Metrics visible in Grafana

### MS008: Create memory integration tests [P1, M]
- **Problem**: No end-to-end tests
- **Location**: Create `tests/integration/test_memory_system.py`
- **Fix**: Test all memory components together
- **Verify**: Race conditions identified and fixed

---

## 3. MATRIZ Pipeline & Orchestration (12 tasks)

#### T4/0.01% Augmentations (apply to MP001–MP012)
- **Backpressure**: bounded semaphore on parallel stages; export `queue_depth` & `rejections_total`.
- **Cancellation hygiene**: proper task cancellation + cleanup; record `cancel_reason`.
- **Retry policy**: transient vs permanent errors; capped retries with jitter; metric `retry_attempts_total`.
- **Health model**: per-node EWMA latency + success rate; configurable decay; export health score.
- **SLO guard**: CI perf test fails if end-to-end p95 exceeds budget; attach flamegraph on failure.

### MP001: Complete async orchestrator timeouts [P0, M]
- **Problem**: Incomplete timeout handling
- **Location**: `matriz/core/async_orchestrator.py:L34-42,L96-105`
- **Fix**: Wrap stages in asyncio.wait_for() with budgets
- **Verify**: Pipeline completes within 250ms total

### MP002: Implement adaptive node routing [P1, M]
- **Problem**: No fallback for unhealthy nodes
- **Location**: `matriz/core/async_orchestrator.py:L341-350`
- **Fix**: Track health, route to backup if unhealthy
- **Verify**: Automatic failover works

### MP003: Add orchestrator stress testing [P1, M]
- **Problem**: Not tested under concurrent load
- **Location**: Create `tests/stress/test_orchestrator.py`
- **Fix**: Test 100 concurrent requests
- **Verify**: P95 latency within SLO

### MP004: Create pipeline stage interfaces [P2, S]
- **Problem**: No formal interface
- **Location**: `lukhas/core/interfaces.py`
- **Fix**: Define ICognitiveNode protocol
- **Verify**: Type checking passes

### MP005: Implement pipeline stage metrics [P2, S]
- **Problem**: Stage performance not tracked
- **Location**: `matriz/core/async_orchestrator.py:L36-44`
- **Fix**: Add histogram per stage
- **Verify**: Stage breakdowns in dashboard

### MP006: Add orchestrator distributed tracing [P1, M]
- **Problem**: No tracing for debugging
- **Location**: Throughout orchestrator
- **Fix**: Add OpenTelemetry spans
- **Verify**: Full traces in Jaeger

### MP007: Implement orchestrator cancellation [P2, M]
- **Problem**: Can't cancel in-flight requests
- **Location**: Add to orchestrator
- **Fix**: Add cancellation token support
- **Verify**: Clean cancellation <100ms

### MP008: Add orchestrator request queuing [P3, M]
- **Problem**: No queuing under load
- **Location**: Add to orchestrator
- **Fix**: Implement priority queue
- **Verify**: Graceful overflow handling

### MP009: Create orchestrator health checks [P2, S]
- **Problem**: No health endpoint
- **Location**: Add /health endpoint
- **Fix**: Check node availability
- **Verify**: K8s integration ready

### MP010: Optimize orchestrator memory [P3, M]
- **Problem**: Memory not optimized
- **Location**: Throughout orchestrator
- **Fix**: Implement object pooling
- **Verify**: Stable under load

### MP011: Add orchestrator error recovery [P1, M]
- **Problem**: Limited error recovery
- **Location**: `matriz/core/async_orchestrator.py:L274-283`
- **Fix**: Add retry with exponential backoff
- **Verify**: Transient errors recovered

### MP012: Document orchestrator architecture [P3, S]
- **Problem**: Design undocumented
- **Location**: Create `docs/architecture/matriz_orchestrator.md`
- **Fix**: Document flows and strategies
- **Verify**: Complete with diagrams

---

## 4. Observability & Metrics (8 tasks)

#### T4/0.01% Augmentations (apply to OB001–OB008)
- **Metric cardinality budget**: bounded label sets; lint to block unbounded user/input labels.
- **Trace sampling**: head+tail; oversample errors/slow spans.
- **Dashboards as code**: Grafana JSONs treated as golden; prevent UID churn.
- **Runbook links**: every alert links to a runbook + owner.
- **RED/Golden signals**: RED panels per route; stage-level golden signals for memory/orchestrator.

### OB001: Enable Prometheus metrics export [P0, S]
- **Problem**: Not enabled by default
- **Location**: `lukhas/core/metrics_exporters.py:L26-34`
- **Fix**: Set LUKHAS_PROM_PORT=9090
- **Verify**: /metrics endpoint returns data

### OB002: Initialize OpenTelemetry tracing [P1, M]
- **Problem**: Only metrics, no tracing
- **Location**: `lukhas/core/metrics_exporters.py:L48-56`
- **Fix**: Add TracerProvider initialization
- **Verify**: Traces exported successfully

### OB003: Replace metric stubs [P1, M]
- **Problem**: TelemetryCounter stubs not real
- **Location**: Throughout codebase
- **Fix**: Replace with prometheus_client objects
- **Verify**: All metrics in Prometheus

### OB004: Create Grafana dashboards [P2, M]
- **Problem**: Dashboards not deployed
- **Location**: `guardian/tags_dashboard.json`
- **Fix**: Import all dashboards, configure alerts
- **Verify**: All dashboards working

### OB005: Implement SLO monitoring [P1, S]
- **Problem**: SLOs not monitored
- **Location**: Create `docs/slos/`
- **Fix**: Define targets, create SLI queries
- **Verify**: Error budgets tracked

### OB006: Add custom application metrics [P2, M]
- **Problem**: Business metrics not tracked
- **Location**: Throughout application
- **Fix**: Add business KPI metrics
- **Verify**: Dashboard shows KPIs

### OB007: Implement log aggregation [P2, M]
- **Problem**: Logs not centralized
- **Location**: Configuration files
- **Fix**: Set up ELK/Loki stack
- **Verify**: Logs searchable

### OB008: Run observability drill [P2, S]
- **Problem**: Not tested in practice
- **Location**: Create runbook
- **Fix**: Simulate failures, verify alerts
- **Verify**: Team can diagnose quickly

---

## 5. Security & Supply Chain (6 tasks)

#### T4/0.01% Augmentations (apply to SC001–SC006)
- **Actions pinned to SHAs**; enable OSSF Scorecard; fail CI under threshold.
- **SBOM** (e.g., `syft`) attached to releases.
- **pip-compile** with hash checking; constraints for hermetic installs.
- **Secret scanning**: gitleaks + GH Advanced Security; pre-commit secret hook.
- **Provenance**: SLSA-style build provenance notes in release flow (docs acceptable initially).

### SC001: Integrate SBOM generation [P1, S]
- **Problem**: Not automated
- **Location**: `.github/workflows/security-audit.yml`
- **Fix**: Add 'make sbom' to CI
- **Verify**: SBOM generated every build

### SC002: Implement license policy [P1, S]
- **Problem**: No compliance checking
- **Location**: Add to CI workflow
- **Fix**: Add pip-licenses check
- **Verify**: Disallowed licenses block

### SC003: Add secret scanning [P0, S]
- **Problem**: No automated detection
- **Location**: Add TruffleHog to CI
- **Fix**: Scan all branches
- **Verify**: Secrets detected before merge

### SC004: Harden GitHub Actions [P2, S]
- **Problem**: Use tags not SHAs
- **Location**: `.github/workflows/`
- **Fix**: Replace with commit SHAs
- **Verify**: All actions pinned

### SC005: Implement dependency freshness [P2, S]
- **Problem**: Might become stale
- **Location**: `.github/workflows/dependency-pinning.yml`
- **Fix**: Enhance weekly check
- **Verify**: Updates proposed weekly

### SC006: Create incident response plan [P2, M]
- **Problem**: Not documented
- **Location**: Create `docs/security/incident_response.md`
- **Fix**: Define procedures
- **Verify**: Drill completed

---

## 6. Lane Management (5 tasks)

#### T4/0.01% Augmentations (apply to LM001–LM005)
- **Import Linter contracts** per lane; CI artifact lists violations with mini graph.
- **Lane labels** mandatory on metrics/spans/logs; default injected from env if missing.
- **Promotion gate** GitHub Action verifies tests/SLO/observability prior to merge to production lane.
- **Brownout drills**: scheduled experiment toggling enforcement for 10 minutes with auto-report.

### LM001: Enforce lane import restrictions [P0, S]
- **Problem**: Might be violated
- **Location**: `config/tools/.importlinter`
- **Fix**: Run in CI, fail on violations
- **Verify**: Zero cross-lane imports

### LM002: Implement canary deployment [P1, M]
- **Problem**: No systematic canary
- **Location**: `guardian/flag_snapshot.sh`
- **Fix**: Add traffic splitting
- **Verify**: Automatic rollback works

### LM003: Create lane promotion checklist [P2, S]
- **Problem**: No formal process
- **Location**: Create `docs/lanes/promotion_checklist.md`
- **Fix**: Define criteria and automation
- **Verify**: Checklist complete

### LM004: Add lane labels to metrics [P2, S]
- **Problem**: Not segregated by lane
- **Location**: Throughout metrics
- **Fix**: Add 'lane' label
- **Verify**: Dashboards filter by lane

### LM005: Document lane architecture [P3, S]
- **Problem**: Not documented
- **Location**: Create `docs/architecture/lanes.md`
- **Fix**: Document purposes and flows
- **Verify**: Complete with diagrams

---

## 7. Documentation & Cleanup (5 tasks)

#### T4/0.01% Augmentations (apply to DC001–DC005)
- **Vocabulary lint** (Constellation vs legacy terms) with allowlist for archives.
- **Docs CI**: link checker + schema version checker; fail on stale schema refs.
- **Context auto-refresh**: script stamps dates & component counts; CI `--check` required.

### DC001: Complete Trinity→Constellation migration [P2, S]
- **Problem**: Some references remain
- **Location**: Run `scripts/codemods/trinity_to_constellation_focused.py`
- **Fix**: Update all references
- **Verify**: Zero 'Trinity' in active code

### DC002: Automate context header updates [P3, S]
- **Problem**: Component count stale
- **Location**: `context_headers.md`
- **Fix**: Create auto-update script
- **Verify**: CI validates accuracy

### DC003: Create operational runbooks [P2, M]
- **Problem**: Missing documentation
- **Location**: `docs/runbooks/`
- **Fix**: Create all critical runbooks
- **Verify**: Tested in drills

### DC004: Update architecture documentation [P3, M]
- **Problem**: Might be outdated
- **Location**: `ARCHITECTURE.md`
- **Fix**: Review and update
- **Verify**: Matches implementation

### DC005: Create API documentation [P3, M]
- **Problem**: No API docs
- **Location**: Create `docs/api/`
- **Fix**: Generate OpenAPI schemas
- **Verify**: Interactive docs available

---

## 8. Testing & Performance (8 tasks)

#### T4/0.01% Augmentations (apply to TP001–TP008)
- **Flake finder**: re-run failures N times; auto-quarantine tag + weekly report.
- **Matrix CI**: Python 3.9 & 3.11; docs note deltas.
- **Golden traces**: validate span topology & critical attributes.
- **Perf budgets in git**: thresholds + rationale versioned; PRs update rationale when changed.

### TP001: Create comprehensive test suite [P1, L]
- **Problem**: Coverage incomplete
- **Location**: `tests/`
- **Fix**: Add unit/integration/e2e tests
- **Verify**: 90% coverage achieved

### TP002: Implement performance benchmarks [P1, M]
- **Problem**: Not benchmarked
- **Location**: Create `benchmarks/`
- **Fix**: Test all critical paths
- **Verify**: Regressions detected

### TP003: Add load testing [P1, M]
- **Problem**: Not load tested
- **Location**: Create `tests/load/`
- **Fix**: Test sustained and spike load
- **Verify**: Breaking points documented

### TP004: Implement chaos testing [P2, L]
- **Problem**: Resilience not tested
- **Location**: Create `tests/chaos/`
- **Fix**: Test failure scenarios
- **Verify**: Graceful degradation

### TP005: Create test data generators [P2, M]
- **Problem**: No systematic test data
- **Location**: Create `tests/fixtures/`
- **Fix**: Generate edge cases
- **Verify**: Comprehensive data available

### TP006: Add contract testing [P2, M]
- **Problem**: No API validation
- **Location**: Create `tests/contracts/`
- **Fix**: Define and test contracts
- **Verify**: Breaking changes detected

### TP007: Implement security testing [P1, M]
- **Problem**: Not systematically tested
- **Location**: Create `tests/security/`
- **Fix**: Add SAST/DAST/pentesting
- **Verify**: Vulnerabilities detected

### TP008: Create test environment management [P3, M]
- **Problem**: Environments not managed
- **Location**: Create `tests/environments/`
- **Fix**: Automate provisioning
- **Verify**: Easy reset available

---

## Cross-Cutting Automation & CI Hooks

- **Make targets**
  - `make ci-shadow` → run counterfactual logging diff tests
  - `make ci-plugin-smoke` → boot with `LUKHAS_PLUGIN_DISCOVERY=auto` and assert minimal plugin set
  - `make ci-import-lint` → run Import Linter lane contracts
  - `make sbom` → generate SBOM and attach as artifact
  - `make perf` → run perf suite with budgets; upload flamegraphs on failure

- **Evidence bundle (per-PR artifact)**
  - Include: perf JSON, PromQL snapshots, coverage diff, lane violations (if any), SBOM, alert eval results.

- **Global acceptance gates (must be green before promotion)**
  - E2E p95 ≤ 250ms (CI perf mode); lane violations = 0; coverage ≥ baseline; security audit = green; dashboards present with SLOs & runbooks linked.

## Execution Timeline

### Week 1 (Immediate - P0 tasks)
- SG001, SG002 (Guardian enforcement)
- MS001 (Cognitive nodes)
- MP001 (Orchestrator timeouts)
- OB001 (Prometheus metrics)
- SC003 (Secret scanning)
- LM001 (Lane restrictions)

### Week 2 (P1 safety/performance)
- SG003-SG009 (Guardian/LLM guardrail)
- MS002-MS003 (Memory testing)
- MP002-MP006 (Orchestrator improvements)
- OB002-OB005 (Observability)
- SC001-SC002 (Security)

### Week 3 (P2 feature completion)
- Remaining memory tasks
- Pipeline completion
- Dashboard deployment
- Documentation updates

### Week 4 (P3 cleanup/testing)
- Comprehensive testing
- Documentation completion
- Performance optimization
- Final cleanup

---

## Success Criteria
✅ Guardian enforcement at 100%
✅ Memory recall <100ms
✅ Pipeline latency <250ms p95
✅ 90% test coverage
✅ Zero cross-lane imports
✅ All metrics instrumented

## Risk Mitigation
- Rollback points defined after each critical change
- Canary deployments for all risky changes
- Kill-switches for Guardian and key features
- Comprehensive monitoring before enforcement

---

*This document provides precise, actionable tasks that can be executed by agents unfamiliar with the codebase. Each task includes specific file locations, step-by-step instructions, and clear acceptance criteria.*