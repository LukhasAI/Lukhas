# AGENTS — MATRIZ Constellation Ops

## Roles at a glance
- **Codex (Lead Implementer):** code changes, tests, CI wiring, promotion evidence.
- **Claude/Sonnet (Spec & Safety):** design docs, schemas, guardian DSL, red-team tests.
- **ChatGPT-5 / GPT-4.0 (Refactor & Perf):** large refactors, micro-bench, bootstrap CI95% stats.
- **Gemini (Observability):** prom rules, label contracts, otel spans validation.
- **Grok (Chaos/Resilience):** fault injection plans, brownout/circuit drills.
- **Copilot (Edit Assist):** incremental diffs, boilerplate, typing adherence.

## Guardrails (T4 / 0.01%)
- **Fail-closed by default.** Feature flags default OFF except canary.
- **Evidence or it didn't happen.** Each PR must produce `artifacts/*_validation_*.json`.
- **No cross-lane imports.** Import-linter must pass before review.
- **Performance budgets are hard gates.** p95 targets enforced in CI.
- **Telemetry contracts.** No dynamic IDs in labels (e.g., `correlation_id`); use span attributes.

## PR Template (every agent)
- Problem / Solution / Impact
- Lanes touched + flags
- Tests: unit, integration, property, chaos
- Perf evidence (p50/p95/p99, CI95% bootstrap)
- promtool results (rules + tests)
- Guardian: DSL on/off proof, kill-switch drill output
- Import-linter: ✅
- Artifacts: list of files + SHA256

## Agent-Ready Prompts (Copy/Paste to Execute)

### Codex — Lane assignment & wiring

```
Implement lane manifests for {MODULES}. For each:
- create module.lane.yaml (lane=candidate unless already at integration)
- wire CI job names to lane in tests (marker: lane:{lane})
- ensure import-linter section blocks upward imports
- emit artifacts/*_validation_*.json
Do not change runtime behavior; only add wiring + CI + manifests.
```

### Claude/Sonnet — Guardian & schema hardening

```
Add guardian DSL enforcement tests + kill-switch drills for {MODULE}.
- tests: ON-by-default; simulate failure → assert fail-closed
- add governance/{module}_response_schema.json + contract tests
- update prom rules with burn-rate alert tests (promtool)
Output: artifacts/{module}_guardian_validation.json
```

### GPT-5 / GPT-4 — Performance + bootstrap evidence

```
Create perf runners for {MODULE}:
- unit N=10k, E2E N=2k, bootstrap resamples=1k
- emit p50/p95/p99 + CI95% intervals
- fail if p95 exceeds budgets
Output: artifacts/{module}_perf_e2e_bootstrap.json
```

### Gemini — Telemetry contracts

```
Validate metrics + traces for {MODULE}:
- forbid {correlation_id} in labels; require {lane,component,operation}
- add/verify promtool tests, otel span attributes
Output: artifacts/{module}_telemetry_contracts.json
```

### Grok — Chaos/resilience

```
Run chaos matrix for {MODULE} with net jitter, IO slowdown, clock skew:
- assert guardian fail-closed <1s
- assert perf regression <10%
Output: artifacts/{module}_resilience_validation.json
```

### Copilot — Glue & refactors

```
Refactor {MODULE} internal helpers for typing, smaller files, and docstrings.
Keep public API unchanged. Add missing unit tests for edge branches.
```

## Coordination Protocol

### Daily Standup (Async)
- **Status**: Current lane assignments and blockers
- **Evidence**: New artifacts generated in last 24h
- **Gates**: Which promotion gates are green/red/amber
- **Escalations**: T4/0.01% violations or security issues

### Weekly Lane Review
- **Promotion candidates**: Modules ready for lane advancement
- **Performance trends**: SLO compliance across lanes
- **Technical debt**: Modules requiring refactoring or deprecation
- **Capacity planning**: Resource allocation for upcoming quarters

### Emergency Response
- **Guardian activation**: Immediate fail-closed protocol
- **Rollback procedures**: Automatic rollback triggers and manual overrides
- **Incident management**: Agent roles during production incidents
- **Post-incident review**: Evidence collection and process improvements

## Quality Standards (Non-Negotiable)

### Code Quality
- **Type coverage**: >95% type annotation coverage
- **Test coverage**: >90% line coverage, >95% branch coverage
- **Documentation**: All public APIs documented with examples
- **Performance**: All functions <100ms p95, critical paths <10ms

### Security & Compliance
- **Security scanning**: bandit, semgrep, pip-audit all pass
- **Dependency management**: All dependencies pinned with SHA validation
- **GDPR compliance**: Data processing documented and auditable
- **Audit trails**: All state changes logged with correlation IDs

### Operational Excellence
- **Monitoring**: All components have comprehensive dashboards
- **Alerting**: SLO-based alerting with defined runbooks
- **Chaos engineering**: Monthly fault injection exercises
- **Disaster recovery**: Quarterly DR drills with documented procedures