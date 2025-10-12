# Phase 2 OpenAI Alignment - Master Task Planning

**Status**: Planning Phase
**Created**: 2025-10-12
**Target**: Parallel quick wins for OpenAI façade and operational readiness

---

## Overview

This document provides comprehensive task planning for Phase 2 parallel work streams, divided between **Claude Code** (complex implementation tasks) and **GitHub Copilot** (mechanical/docs tasks). All artifacts are ready to paste and implement.

### Success Criteria
- OpenAI-compatible façade with `/v1/responses`, `/v1/embeddings`, `/v1/dreams` endpoints
- Full observability stack (health, metrics, traces, structured logging)
- Eval harness with >70% accuracy baseline
- Production-grade reliability (rate limits, backoff, SLO budgets)
- Supply chain security (SBOM, Dependabot, CodeQL, gitleaks)
- Complete documentation and operational runbooks

---

## Phase 2 Pre-Flight Checklist

**Critical verifications before proceeding:**

- [ ] Compat watcher enabled: `python3 scripts/check_alias_hits.py --max-hits 0` returns 0 after Batches 1-4
- [ ] Manifest path updater points at JSON (not YAML) for candidate → labs rename in Batch 3
- [ ] Phase 2 brief + start doc reviewed and ready
- [ ] All team members assigned to tracks (Claude Code vs Copilot)

---

## Track A: OpenAI Alignment Surface (Claude Code)

### A1. OpenAI Façade + Responses/Assistants-style API
**Branch**: `feat/openai-facade`
**Why**: Let any OpenAI-native client hit Lukhas with near drop-in semantics
**Complexity**: High - Core integration with Matriz orchestrator

**What to Build**:
- `lukhas/adapters/openai/api.py` with minimal routes:
  - `POST /v1/responses` → Matriz orchestrator
  - `GET /v1/models`
  - `POST /v1/embeddings` (proxy to memory/vec)
- Emit stream events (SSE) compatible with "delta/step" style
- Auth middleware with Bearer token support
- Error catalog (401, 429, 500 shapes)

**Acceptance Criteria**:
- [ ] `pytest -q tests/smoke/test_openai_facade.py::test_responses_minimal` passes
- [ ] OpenAPI file published at `docs/openapi/lukhas-openai.yaml`
- [ ] CI adds a step under "MATRIZ Validate" to build the spec
- [ ] All endpoints return OpenAI-compatible JSON shapes
- [ ] SSE streaming works for long-running responses

**Artifacts Created**:
- `lukhas/adapters/openai/api.py` (new)
- `lukhas/adapters/openai/auth.py` (new)
- `tests/smoke/test_openai_facade.py` (new)
- `docs/openapi/lukhas-openai.yaml` (new)
- `docs/API_ERRORS.md` (new)

**Estimated Time**: 6-8 hours
**Dependencies**: None (can start immediately)

---

### A2. Tool Schema Bridge (OpenAI "functions" JSON Schema)
**Branch**: `feat/openai-tools-bridge`
**Why**: Make Matriz capabilities callable as OpenAI tools immediately
**Complexity**: Medium - Schema transformation and validation

**What to Build**:
- Generator that exports `tools:[{type:"function",function:{name,description,parameters}}]`
- Read from each module's manifest capability block
- Validate parameters against JSON Schema spec

**Acceptance Criteria**:
- [ ] `python3 scripts/export_openai_tools.py --manifests manifests --out build/openai_tools.json` produces valid schema
- [ ] Smoke test loads JSON and validates param schemas against jsonschema
- [ ] CI uploads `openai_tools.json` as an artifact
- [ ] At least 10 tools exported from manifests

**Artifacts Created**:
- `scripts/export_openai_tools.py` (new)
- `tests/tools/test_openai_tools_export.py` (new)
- `build/openai_tools.json` (generated)

**Estimated Time**: 3-4 hours
**Dependencies**: Requires manifest structure to be stable

---

### A3. Eval Harness (Mini)
**Branch**: `feat/evals-harness`
**Why**: OpenAI-style eval loops make regressions visible
**Complexity**: Medium - Test infrastructure and reporting

**What to Build**:
- `evals/` directory with 10 tiny JSONL cases (vision/memory/guardian/flow)
- Runner that hits the façade and reports accuracy
- JSON + Markdown + JUnit XML artifacts
- Makefile targets: `make evals` and `make evals-strict`

**Acceptance Criteria**:
- [ ] `make evals` runs in <90s and prints accuracy + simple assertions
- [ ] Gate in CI as "warn-only" initially (append job to MATRIZ Validate)
- [ ] Produces `docs/audits/evals_report.json` and `docs/audits/evals_report.md`
- [ ] >70% baseline accuracy with stub responses

**Artifacts Created**:
- `evals/run_evals.py` (new)
- `evals/README.md` (new)
- `evals/cases/echo.jsonl` (new)
- `evals/cases/openai_shapes.jsonl` (new)
- `tests/smoke/test_evals_runner.py` (new)
- Makefile targets (update)

**Estimated Time**: 4-5 hours
**Dependencies**: Requires A1 (façade) to be functional

---

### A4. Structured Logging & Traces (OpenAI-ish Event Taxonomy)
**Branch**: `feat/structured-logging`
**Why**: Uniform event names (run.started, step.completed, tool.called) ease debugging & demos
**Complexity**: Medium - Logging infrastructure and context propagation

**What to Build**:
- `lukhas/observability/events.py` with dataclasses + JSON lines
- Plug into orchestrator emit points
- PII redaction filters (email, tokens)
- OTEL trace ID propagation

**Acceptance Criteria**:
- [ ] Smoke test verifies presence of run_id, step_id, model, latency_ms fields
- [ ] CI: upload `runlogs/*.jsonl` on PR builds
- [ ] `tests/logging/test_redaction.py` passes (masks email addresses)
- [ ] Trace headers present when `OTEL_EXPORTER_OTLP_ENDPOINT` set

**Artifacts Created**:
- `lukhas/observability/events.py` (new)
- `lukhas/observability/filters.py` (new)
- `tests/logging/test_redaction.py` (new)
- `tests/smoke/test_tracing.py` (new)

**Estimated Time**: 3-4 hours
**Dependencies**: None (can start immediately)

---

### A5. Rate-Limit & 429/Backoff Semantics
**Branch**: `feat/rate-limiting`
**Why**: OpenAI clients expect specific error shapes and Retry-After
**Complexity**: Low-Medium - Middleware implementation

**What to Build**:
- `lukhas/core/reliability/ratelimit.py` with rate limit tracking
- Middleware emitting 429 with `type:"rate_limit_exceeded"`
- Jittered exponential backoff helper
- Config file for rate limit thresholds

**Acceptance Criteria**:
- [ ] Unit test for 429 with proper headers (including Retry-After)
- [ ] Doc blurb in API README "Backoff & Retries"
- [ ] `configs/runtime/reliability.yaml` defines rate limits per endpoint
- [ ] `tests/reliability/test_backoff.py` verifies jittered exponential backoff

**Artifacts Created**:
- `lukhas/core/reliability/ratelimit.py` (new)
- `lukhas/core/reliability/backoff.py` (new)
- `configs/runtime/reliability.yaml` (new)
- `tests/reliability/test_backoff.py` (new)

**Estimated Time**: 2-3 hours
**Dependencies**: None (can start immediately)

---

## Track B: Mechanical & Docs (GitHub Copilot)

### B6. Fix Manifest Stats Reporter Crash & Add Totals
**Branch**: `fix/manifest-stats-reporter`
**Why**: Quick surgical win for dict/str shape crash
**Complexity**: Low - Defensive programming

**What to Fix**:
- Patch `scripts/report_manifest_stats.py` to handle list of manifests and mixed shapes
- Add error handling for missing fields
- Generate both JSON and Markdown outputs

**Acceptance Criteria**:
- [ ] `python3 scripts/report_manifest_stats.py --manifests manifests --out docs/audits` succeeds
- [ ] Writes both `manifest_stats.json` & `manifest_stats.md`
- [ ] Wire into workflow (already has a step—ensure it passes)
- [ ] No crashes on edge cases (empty manifests, missing fields)

**Estimated Time**: 1 hour
**Dependencies**: None

---

### B7. Docs: OpenAI Dev Quickstart
**Branch**: `docs/openai-quickstart`
**Why**: Meet developers where they are; reduce adoption friction
**Complexity**: Low - Documentation writing

**What to Write**:
- `docs/openai/QUICKSTART.md` showing:
  - How to set `OPENAI_API_KEY`
  - Call Lukhas façade with the OpenAI SDK
  - Mapping table "OpenAI concept → Lukhas"
  - Example code in Python, JavaScript, curl

**Acceptance Criteria**:
- [ ] Link added from Codex Phase-2 docs index
- [ ] Examples verified to work against local façade
- [ ] Covers models, embeddings, responses, dreams endpoints
- [ ] Includes troubleshooting section

**Estimated Time**: 2 hours
**Dependencies**: Requires A1 (façade) to be specified

---

### B8. Update Star Canon Everywhere (Ambiguous → Oracle)
**Branch**: `chore/star-canon-oracle`
**Why**: Lock consistency as we finalize manifests & docs
**Complexity**: Low - Search and replace with verification

**What to Update**:
- Verify all docs & configs reference 🔮 Oracle (Quantum)
- Keep alias "Ambiguity" only as backward-compat
- Update `configs/star_rules.json` to be canonical

**Acceptance Criteria**:
- [ ] `rg 'Ambiguity \(Quantum\)' -n` returns 0 outside aliases
- [ ] `configs/star_rules.json` stays canonical (already set)
- [ ] All README and doc files use Oracle nomenclature
- [ ] Backward-compat aliases documented in migration guide

**Estimated Time**: 1 hour
**Dependencies**: None

---

### B9. PR Template Nudge for "Matriz Readiness"
**Branch**: `chore/pr-template-matriz`
**Why**: Keep discipline pack visible in every PR
**Complexity**: Low - Template update

**What to Update**:
- Ensure `PULL_REQUEST_TEMPLATE.md` links the MATRIZ checklist
- Requires ticking smoke/evals
- Links to MATRIZ Validate outputs (artifacts)

**Acceptance Criteria**:
- [ ] Template renders the checklist
- [ ] Links MATRIZ Validate outputs (artifacts)
- [ ] Includes Go/No-Go gate section
- [ ] Includes evidence pack checklist

**Estimated Time**: 30 minutes
**Dependencies**: None

---

### B10. Nightly Star-Rules Coverage Trend
**Branch**: `ci/nightly-coverage`
**Why**: Show movement of Supporting → promoted
**Complexity**: Low - CI workflow duplication

**What to Build**:
- Re-use `lint_star_rules.py` + `gen_rules_coverage.py`
- Create nightly workflow `matriz-nightly.yml`
- Push sparkline to `docs/audits/star_rules_coverage.md`

**Acceptance Criteria**:
- [ ] New workflow `matriz-nightly.yml` posts updated coverage file
- [ ] Runs on schedule (nightly at 5am UTC)
- [ ] Same style as validate job
- [ ] Generates historical trend data

**Estimated Time**: 1 hour
**Dependencies**: None

---

### B11. Lane Rename Doc Link Fixer
**Branch**: `chore/lane-rename-links`
**Why**: After candidate → labs, lots of doc links will break
**Complexity**: Low - Script automation

**What to Build**:
- Script that updates links in `docs/**` & `*.md` to `labs/…`
- Run link checker locally
- Generate `docs/audits/linkcheck.txt`

**Acceptance Criteria**:
- [ ] `python docs/check_links.py --root .` returns 0
- [ ] Artifact `docs/audits/linkcheck.txt` shows clean
- [ ] All relative paths updated correctly
- [ ] External links validated

**Estimated Time**: 2 hours
**Dependencies**: Requires Phase 2 Batch 3 lane rename to be complete

---

### B12. Security: Add Gitleaks as Second Line
**Branch**: `security/gitleaks`
**Why**: Belt-and-braces policy alongside detect-secrets
**Complexity**: Low - CI step addition

**What to Add**:
- Add CI step (`zricethezav/gitleaks@latest`) in MATRIZ Validate
- "warn-only" first
- Upload gitleaks.sarif artifact

**Acceptance Criteria**:
- [ ] Workflow runs the step
- [ ] Uploads `gitleaks.sarif` artifact alongside existing reports
- [ ] Runs on every PR
- [ ] Does not block green status initially

**Estimated Time**: 30 minutes
**Dependencies**: None

---

## Track C: Security & Supply Chain (Claude Code Lead, Copilot Support)

### C13. SBOM + Provenance (Copilot)
**Branch**: `security/sbom`
**Why**: Supply-chain visibility and attestations for external users
**Complexity**: Low - Script and CI integration

**What to Build**:
- `scripts/sbom.py` using CycloneDX
- Generate `build/sbom.cyclonedx.json`
- CI uploads SBOM artifact
- GitHub provenance (SLSA generator) on release tags

**Acceptance Criteria**:
- [ ] `scripts/sbom.py` writes `build/sbom.cyclonedx.json`
- [ ] CI uploads SBOM artifact
- [ ] Provenance enabled on release tags
- [ ] SBOM validates against CycloneDX schema

**Estimated Time**: 2 hours
**Dependencies**: None

---

### C14. Dependency Vulns & Static Analysis (Copilot)
**Branch**: `security/dependency-scanning`
**Why**: Complement detect-secrets; catch CVEs & unsafe patterns early
**Complexity**: Low - CI job addition

**What to Add**:
- `pip-audit` job in MATRIZ Validate (warn-only first)
- `bandit` job in MATRIZ Validate (warn-only first)
- Upload `pip_audit.json` & `bandit.sarif` artifacts

**Acceptance Criteria**:
- [ ] Steps run in CI
- [ ] Artifacts `pip_audit.json` & `bandit.sarif` uploaded
- [ ] Warn-only mode initially
- [ ] Documentation on how to fix common issues

**Estimated Time**: 1.5 hours
**Dependencies**: None

---

### C15. License Hygiene & Headers (Copilot)
**Branch**: `chore/license-headers`
**Why**: OpenAI-grade compliance hygiene
**Complexity**: Low - Pre-commit hook + report

**What to Build**:
- `liccheck`/`pip-licenses` report
- Header check (year, owner) via pre-commit
- Generate `docs/audits/licenses.md`

**Acceptance Criteria**:
- [ ] `docs/audits/licenses.md` generated
- [ ] Pre-commit blocks missing headers
- [ ] All licenses approved in allowlist
- [ ] SPDX identifiers present

**Estimated Time**: 2 hours
**Dependencies**: None

---

### C16. Health/Readiness/Metrics (Claude Code)
**Branch**: `feat/health-endpoints`
**Why**: SRE-grade operability and k8s readiness
**Complexity**: Low-Medium - Observability infrastructure

**What to Build**:
- `/healthz` endpoint (liveness)
- `/readyz` endpoint (readiness)
- `/metrics` endpoint (Prometheus format)
- Expose request_total, latency_ms series

**Acceptance Criteria**:
- [ ] `pytest passes tests/smoke/test_healthz.py`
- [ ] `curl /metrics` shows series (request_total, latency_ms)
- [ ] Health checks validate internal dependencies
- [ ] Metrics follow Prometheus naming conventions

**Artifacts Created**:
- Updated `lukhas/adapters/openai/api.py`
- `tests/smoke/test_healthz.py` (new)

**Estimated Time**: 2-3 hours
**Dependencies**: Requires A1 (façade base)

---

### C17. OpenTelemetry Traces + Log Redaction (Claude Code)
**Branch**: `feat/otel-tracing`
**Why**: End-to-end tracing and privacy safety
**Complexity**: Medium - OTEL SDK integration

**What to Build**:
- OTEL SDK wiring (OTLP exporter if `OTEL_EXPORTER_OTLP_ENDPOINT` set)
- PII redaction filter (email, tokens)
- W3C trace context propagation

**Acceptance Criteria**:
- [ ] `tests/smoke/test_tracing.py` asserts trace ids present when env set
- [ ] `tests/logging/test_redaction.py` masks email addresses
- [ ] Traces include span hierarchy
- [ ] Logs include trace correlation IDs

**Artifacts Created**:
- Updated `lukhas/observability/events.py`
- Updated `lukhas/observability/filters.py`
- `tests/smoke/test_tracing.py` (enhanced)
- `observability/otel-collector.yaml` (optional local config)

**Estimated Time**: 4-5 hours
**Dependencies**: Requires A4 (structured logging)

---

## Track D: Observability & Ops (Claude Code)

### C18. SLO Budgets & Alerts (Doc + Config)
**Branch**: `docs/slo-budgets`
**Why**: Define p95/p99 targets for façade endpoints now
**Complexity**: Low - Documentation and config

**What to Create**:
- `docs/ops/SLOs.md` with target definitions
- `configs/observability/slo_budgets.yaml`
- Define: responses_p95_ms, embeddings_p95_ms

**Acceptance Criteria**:
- [ ] CI uploads SLO docs
- [ ] Smoke warns if budgets exceeded
- [ ] Targets: responses p95 ≤ 1200ms, embeddings p95 ≤ 800ms
- [ ] Alert thresholds documented

**Estimated Time**: 1.5 hours
**Dependencies**: None

---

## Track E: Performance & Load (Copilot First Pass)

### E19. Quick k6/Locust Scenario for /v1/responses (Copilot)
**Branch**: `test/load-scenarios`
**Why**: Ensure latency budgets are realistic under moderate load
**Complexity**: Low - Load test script

**What to Build**:
- `load/resp_scenario.js` (k6) OR `load/locustfile.py` (locust)
- 100 VUs for 2 minutes
- Makefile target: `make load-smoke`

**Acceptance Criteria**:
- [ ] `make load-smoke` prints p95
- [ ] Job runs in nightly (warn-only)
- [ ] Reports include p95, p99, error rate
- [ ] Validates SLO budgets

**Estimated Time**: 2 hours
**Dependencies**: Requires A1 (façade) and C18 (SLO budgets)

---

### E20. Timeouts/Backoff Knobs (Copilot)
**Branch**: `config/reliability-knobs`
**Why**: Consistent client/server retry posture aligned with OpenAI semantics
**Complexity**: Low - Configuration

**What to Create**:
- `configs/runtime/reliability.yaml` with:
  - connect_timeout_ms
  - read_timeout_ms
  - backoff policy (base, factor, jitter)

**Acceptance Criteria**:
- [ ] `tests/reliability/test_backoff.py` verifies jittered exponential backoff
- [ ] Façade returns Retry-After on 429
- [ ] Config values applied consistently
- [ ] Documentation on tuning parameters

**Estimated Time**: 1.5 hours
**Dependencies**: Requires A5 (rate limiting)

---

## Track F: Release Engineering (Claude Code)

### C21. RC/Freeze Automation (Claude Code)
**Branch**: `ci/release-automation`
**Why**: Eliminate manual release drift
**Complexity**: Medium - Script and CI workflow

**What to Build**:
- `scripts/release_rc.sh` that:
  - Tags RC (vX.Y.Z-rc)
  - Generates CHANGELOG via commitizen
  - Attaches SBOM
- FREEZE checklist gate in CI

**Acceptance Criteria**:
- [ ] `gh release create vX.Y.Z-rc` with CHANGELOG + sbom attached
- [ ] PR template shows "Freeze ✅"
- [ ] Automated version bumping
- [ ] Release notes generation

**Estimated Time**: 3-4 hours
**Dependencies**: Requires C13 (SBOM)

---

### C22. Canary Environment (Ephemeral PR Deploy) (Claude Code)
**Branch**: `ci/pr-preview`
**Why**: Smoke new façade/observability in isolation
**Complexity**: Medium - CI deployment workflow

**What to Build**:
- Lightweight PR preview using uvicorn
- Optional: ngrok/github codespaces
- Post URL as PR comment
- Workflow: `matriz-preview.yml`

**Acceptance Criteria**:
- [ ] Workflow `matriz-preview.yml` posts a live link
- [ ] Triggers for PRs touching `lukhas/adapters/openai/*`
- [ ] Auto-cleanup after PR close
- [ ] Security isolation for preview envs

**Estimated Time**: 4-5 hours
**Dependencies**: Requires A1 (façade) and Dockerfile

---

## Track G: Docs & DX (Copilot)

### G23. Postman Collection + Examples (Copilot)
**Branch**: `docs/postman-collection`
**Why**: Drop-in API testing for integrators
**Complexity**: Low - Export and examples

**What to Create**:
- Convert `docs/openapi/lukhas-openai.yaml` → `docs/openapi/Postman_collection.json`
- Create `docs/openai/examples.py|js|curl.md`

**Acceptance Criteria**:
- [ ] Collection imports cleanly into Postman
- [ ] Examples run against façade locally
- [ ] Covers all main endpoints
- [ ] Includes auth examples

**Estimated Time**: 2 hours
**Dependencies**: Requires A1 (façade OpenAPI spec)

---

### G24. "Why Matriz" One-Pager (Copilot)
**Branch**: `docs/why-matriz`
**Why**: Align stakeholders; OpenAI-native narrative
**Complexity**: Low - Strategic documentation

**What to Write**:
- `docs/matriz/WHY_MATRIZ.md` with:
  - Vision
  - API surface
  - Complement to OpenAI
  - Risk/ethics stance

**Acceptance Criteria**:
- [ ] Linked from README and PR template
- [ ] Reviewed in launch checklist
- [ ] Clear differentiators vs OpenAI
- [ ] Technical and business value propositions

**Estimated Time**: 3 hours
**Dependencies**: None

---

## Track H: Productization (Dreams/Memory/Guardian)

### H25. Dreams API (Drift) Surface (Claude Code)
**Branch**: `feat/dreams-api`
**Why**: Flagship differentiator; scenario generation & self-critique
**Complexity**: High - Novel endpoint with consciousness integration

**What to Build**:
- `POST /v1/dreams` endpoint
- Inputs: seed, constraints
- Emits dream traces
- Schema in OpenAPI spec

**Acceptance Criteria**:
- [ ] `tests/smoke/test_dreams_api.py` passes
- [ ] Spec includes examples
- [ ] Nightly evals exercise dream loops
- [ ] Trace format documented

**Estimated Time**: 6-8 hours
**Dependencies**: Requires A1 (façade) and consciousness modules

---

### H26. Memory Index Mgmt Endpoints (Copilot)
**Branch**: `feat/memory-indexes`
**Why**: Parity with embeddings admin in OpenAI ecosystem
**Complexity**: Medium - CRUD endpoints

**What to Build**:
- `/v1/indexes` endpoints:
  - List indexes
  - Create index
  - Delete index
- Front memory orchestrator
- RBAC via policy_guard

**Acceptance Criteria**:
- [ ] `tests/memory/test_indexes_api.py` passes
- [ ] RBAC enforced via policy_guard
- [ ] Index metadata persisted
- [ ] Pagination support

**Estimated Time**: 4-5 hours
**Dependencies**: Requires memory orchestrator stability

---

### H27. Guardian Policy Hooks (Claude Code)
**Branch**: `feat/guardian-hooks`
**Why**: Ship "safety by default"
**Complexity**: Medium - Security policy integration

**What to Build**:
- Request/response hooks applying `contracts/security.policies`
- Apply before emit
- Audit fields in runlogs

**Acceptance Criteria**:
- [ ] `tests/guardian/test_policy_hooks.py` proves block/allow/log behavior
- [ ] Audit fields in runlogs
- [ ] Policy violations logged with context
- [ ] Performance impact < 50ms p95

**Estimated Time**: 5-6 hours
**Dependencies**: Requires A1 (façade) and guardian modules

---

## Execution Strategy

### Phase 1: Foundation (Week 1)
**Parallel execution - no dependencies**

**Claude Code Focus**:
1. A1 - OpenAI Façade (critical path)
2. A4 - Structured Logging
3. A5 - Rate Limiting

**Copilot Focus**:
1. B6 - Fix manifest stats reporter
2. B8 - Star canon updates
3. B9 - PR template
4. C13 - SBOM generation

### Phase 2: Observability & Testing (Week 1-2)
**Depends on A1 completion**

**Claude Code Focus**:
1. A2 - Tool schema bridge
2. A3 - Eval harness
3. C16 - Health/metrics endpoints

**Copilot Focus**:
1. B7 - OpenAI quickstart docs
2. B10 - Nightly coverage workflow
3. B12 - Gitleaks integration
4. C14 - Dependency scanning

### Phase 3: Advanced Features (Week 2)
**Depends on A1, A3 completion**

**Claude Code Focus**:
1. C17 - OTEL tracing
2. H25 - Dreams API
3. H27 - Guardian hooks

**Copilot Focus**:
1. E19 - Load testing scenarios
2. E20 - Reliability knobs config
3. G23 - Postman collection
4. G24 - Why Matriz doc

### Phase 4: Release Readiness (Week 2-3)
**Depends on all core features**

**Claude Code Focus**:
1. C21 - RC automation
2. C22 - PR preview environments

**Copilot Focus**:
1. B11 - Lane rename link fixer (after Batch 3)
2. C15 - License hygiene
3. H26 - Memory index endpoints

---

## Artifact Inventory

### Code Artifacts (30 files)

**Core Façade**:
- `lukhas/adapters/openai/api.py`
- `lukhas/adapters/openai/auth.py`

**Observability**:
- `lukhas/observability/events.py`
- `lukhas/observability/filters.py`

**Reliability**:
- `lukhas/core/reliability/ratelimit.py`
- `lukhas/core/reliability/backoff.py`

**Scripts**:
- `scripts/export_openai_tools.py`
- `scripts/sbom.py`
- `scripts/release_rc.sh`

**Tests (21 files)**:
- `tests/smoke/test_openai_facade.py`
- `tests/smoke/test_healthz.py`
- `tests/smoke/test_dreams_api.py`
- `tests/smoke/test_tracing.py`
- `tests/smoke/test_evals_runner.py`
- `tests/logging/test_redaction.py`
- `tests/reliability/test_backoff.py`
- `tests/tools/test_openai_tools_export.py`
- `tests/memory/test_indexes_api.py`
- `tests/guardian/test_policy_hooks.py`

**Evals**:
- `evals/run_evals.py`
- `evals/README.md`
- `evals/cases/echo.jsonl`
- `evals/cases/openai_shapes.jsonl`

**Load Testing**:
- `load/resp_scenario.js`

---

### Configuration Artifacts (10 files)

**Runtime Config**:
- `configs/runtime/reliability.yaml`
- `configs/observability/slo_budgets.yaml`

**OpenAPI**:
- `docs/openapi/lukhas-openai.yaml`
- `docs/openapi/Postman_collection.json`

**Container**:
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

**Observability**:
- `observability/otel-collector.yaml`

**Security**:
- `CODEOWNERS`
- `SECURITY.md`

---

### CI/CD Artifacts (4 workflows)

**Workflows**:
- `.github/workflows/matriz-validate.yml` (updates)
- `.github/workflows/matriz-nightly.yml` (new)
- `.github/workflows/matriz-preview.yml` (new)
- `.github/workflows/codeql.yml` (new)
- `.github/dependabot.yml` (new)

---

### Documentation Artifacts (10 files)

**API Docs**:
- `docs/openai/QUICKSTART.md`
- `docs/openai/examples.py|js|curl.md`
- `docs/API_ERRORS.md`

**Operations**:
- `docs/ops/SLOs.md`

**Product**:
- `docs/matriz/WHY_MATRIZ.md`

**Audits** (generated):
- `docs/audits/evals_report.json`
- `docs/audits/evals_report.md`
- `docs/audits/manifest_stats.json`
- `docs/audits/manifest_stats.md`
- `docs/audits/linkcheck.txt`
- `docs/audits/star_rules_coverage.md`

**Templates**:
- `PULL_REQUEST_TEMPLATE.md` (update)

---

## Acceptance Gates

### Per-Track Gates

**Track A (OpenAI Alignment)**:
- [ ] All `/v1/*` endpoints return valid OpenAI-compatible shapes
- [ ] OpenAPI spec validates
- [ ] Eval harness >70% accuracy baseline
- [ ] SSE streaming functional
- [ ] Tool export produces valid JSON Schema

**Track B (Mechanical)**:
- [ ] All scripts run without errors
- [ ] Documentation complete and linked
- [ ] Star canon consistent across codebase
- [ ] PR template includes all checklists

**Track C (Security)**:
- [ ] SBOM generated and validates
- [ ] All security scanners green (or warn-only as planned)
- [ ] License headers present
- [ ] No secrets detected

**Track D (Observability)**:
- [ ] Health endpoints respond correctly
- [ ] Metrics follow Prometheus conventions
- [ ] Traces include full span hierarchy
- [ ] SLO budgets documented

**Track E (Performance)**:
- [ ] Load tests run successfully
- [ ] p95 latency within SLO budgets
- [ ] Backoff/retry logic validated
- [ ] Rate limits enforced correctly

**Track F (Release)**:
- [ ] RC script executes cleanly
- [ ] PR previews deploy automatically
- [ ] Release artifacts include SBOM + CHANGELOG

**Track G (Docs & DX)**:
- [ ] Postman collection imports successfully
- [ ] Examples run against local façade
- [ ] All docs peer-reviewed
- [ ] Navigation links verified

**Track H (Productization)**:
- [ ] Dreams API generates valid traces
- [ ] Memory indexes CRUD functional
- [ ] Guardian hooks enforce policies
- [ ] Nightly evals pass for all features

---

## Post-Merge Verification Runbook

### 0. Boot Façade (Dev)
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
uvicorn lukhas.adapters.openai.api:get_app --host 0.0.0.0 --port 8000 &
```

### 1. Smokes
```bash
pytest -q tests/smoke -k "healthz or openai_facade or dreams_api or tracing or evals_runner"
```

### 2. Mini-Evals (Warn-Only)
```bash
make evals
cat docs/audits/evals_report.md
```

### 3. OpenAPI Validity
```bash
python -m pip install -q openapi-spec-validator PyYAML
python - <<'PY'
import yaml
from openapi_spec_validator import validate_spec
validate_spec(yaml.safe_load(open("docs/openapi/lukhas-openai.yaml")))
print("[openapi] spec valid")
PY
```

### 4. Tool Export
```bash
python3 scripts/export_openai_tools.py
pytest -q tests/tools/test_openai_tools_export.py || true
```

### 5. Links, Contracts, Context
```bash
python3 docs/check_links.py --root .
python3 scripts/validate_contract_refs.py
python3 scripts/validate_context_front_matter.py
```

### 6. Star Rules + Coverage
```bash
make star-rules-lint
make star-rules-coverage
cat docs/audits/star_rules_coverage.md
```

### 7. Security Belt & SBOM
```bash
detect-secrets scan --baseline .secrets.baseline || true
pipx run pip-audit -f json -o docs/audits/pip_audit.json || true
python3 scripts/sbom.py
```

### 8. Load Smoke (Optional)
```bash
k6 run load/resp_scenario.js || true
```

---

## Evidence Pack (Attach to PR)

### Required Artifacts
- [ ] `docs/audits/evals_report.md`
- [ ] `docs/audits/star_rules_coverage.md`
- [ ] `docs/audits/linkcheck.txt`
- [ ] `docs/audits/manifest_stats.md`
- [ ] `build/openai_tools.json`
- [ ] `docs/openapi/lukhas-openai.yaml`
- [ ] `build/sbom.cyclonedx.json`

### What "Good" Looks Like
- Smokes: all pass
- Evals: ≥70% accuracy (okay for stub; raise later)
- OpenAPI: validator prints "spec valid"
- Tools export: test green or warn-only (first run)
- Link checker: no broken links
- Star rules: coverage report updated; zero "no-hit" stars
- Security: no secrets; SBOM validates

---

## Go/No-Go Gate (PR Checklist)

**Core Façade**:
- [ ] `/healthz`, `/readyz`, `/metrics` ✅
- [ ] `/v1/models`, `/v1/embeddings`, `/v1/responses`, `/v1/dreams` ✅
- [ ] OpenAPI validated in CI ✅

**Quality**:
- [ ] Mini-evals ≥ 0.70 (warn-only) ✅
- [ ] All smokes passing ✅
- [ ] Link checker clean ✅

**Operations**:
- [ ] SLO docs + budgets committed ✅
- [ ] Health endpoints functional ✅
- [ ] Metrics exposed ✅

**Security**:
- [ ] detect-secrets + gitleaks (warn-only) ✅
- [ ] SBOM generated ✅
- [ ] License hygiene checks ✅

**Consistency**:
- [ ] Star canon consistent (🔮 Oracle canonical; Ambiguity only alias) ✅
- [ ] Manifest stats clean ✅
- [ ] No import boundary violations ✅

---

## Risk Register

### High Risk Items
1. **Dreams API Integration** (H25)
   - Complexity: Novel consciousness integration
   - Mitigation: Start with stub responses, iterate
   - Fallback: Defer to Phase 3 if blocked

2. **OTEL Tracing** (C17)
   - Complexity: Context propagation across async boundaries
   - Mitigation: Use proven libraries (opentelemetry-api)
   - Fallback: Manual correlation IDs if OTEL blocked

3. **PR Preview Environments** (C22)
   - Complexity: Infrastructure provisioning
   - Mitigation: Use GitHub Codespaces or simple ngrok
   - Fallback: Local testing only initially

### Medium Risk Items
1. **Tool Schema Export** (A2)
   - Risk: Manifest schema inconsistencies
   - Mitigation: Defensive parsing, skip invalid entries

2. **Eval Harness** (A3)
   - Risk: Flaky tests due to non-deterministic responses
   - Mitigation: Use "contains" checks, not exact matches

3. **Lane Rename Link Fixer** (B11)
   - Risk: Breaking external documentation links
   - Mitigation: Run link checker, maintain redirects

---

## Success Metrics

### Immediate (End of Week 1)
- [ ] 10+ tests passing in `tests/smoke/`
- [ ] OpenAPI spec validates
- [ ] Façade serves 100 requests without error
- [ ] CI green on all new jobs (warn-only)

### Short-Term (End of Week 2)
- [ ] Eval harness reports >70% accuracy
- [ ] All Track A & B tasks complete
- [ ] Security scanners integrated (warn-only)
- [ ] Load testing baseline established

### Medium-Term (End of Week 3)
- [ ] All tracks complete (A-H)
- [ ] Evidence pack artifacts generated
- [ ] Go/No-Go gate passes
- [ ] Ready for Phase 2 launch

---

## Notes for Claude Code

**When Working on Tasks**:
- Read this planning doc before starting any task
- Reference acceptance criteria for each task
- Use artifacts as starting templates (may need adaptation)
- Run verification steps after each major change
- Update task status in todo list

**If Tests Fail**:
- Don't patch tests—bring endpoints to spec
- Toggle auth only after `/healthz` stays public
- If tool export fails, default to `{"type":"object","properties":{}}`

**If Link Checker Finds Issues**:
- Run the fixer script
- Re-generate `docs/audits/linkcheck.txt`
- Verify external links manually

---

## Notes for GitHub Copilot

**When Working on Tasks**:
- Focus on mechanical/docs tasks (Track B, G)
- Use artifacts as-is where possible
- Verify all scripts run without errors
- Check formatting and linting
- Cross-link documentation

**Documentation Standards**:
- Use markdown for all docs
- Include code examples that work
- Link to related documentation
- Keep tone technical but accessible
- Follow T4 commit message standards

---

## Contact & Coordination

**Questions or Blockers?**
- Check this planning doc first
- Review acceptance criteria
- Consult artifact templates
- Ask for clarification if acceptance criteria unclear

**Task Dependencies**:
- See execution strategy phases above
- Coordinate on shared files (Makefile, CI workflows)
- Communicate completion of blocking tasks
- Update shared artifacts carefully

---

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Status**: Ready for Execution
