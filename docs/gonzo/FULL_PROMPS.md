---
status: wip
type: documentation
---
# 🚀 LUKHAS T4/0.01% Execution Prompts

### T4/0.01% Guidance Add-ons

🔺 CRITICAL PRIORITY
 check for the scaffold and details at: /Users/agi_dev/LOCAL-REPOS/Lukhas/docs/gonzo/CRITICAL_SCAFFOLDS..md

M.1 — Implement Actual Memory Storage/Retrieval

Agent Prompt (drop-in):

Context: lukhas/memory/ has memory_orchestrator.py stub. We need a production memory layer.
Goal: Vector search + lifecycle + compression with audit/metrics.
Create/modify files:
	•	lukhas/memory/backends/pgvector_store.py (or faiss_store.py)
	•	lukhas/memory/indexer.py (embedding + upsert/search API)
	•	lukhas/memory/lifecycle.py (retention, archival, GDPR delete)
	•	lukhas/memory/compression.py (zstd or qpack, configurable)
	•	lukhas/memory/memory_orchestrator.py (implement routes; keep API stable)
	•	observability/prometheus_metrics.py (+ new counters/histograms registration)
Implement:

	1.	Backend
	•	Interface: add(doc) -> id, bulk_add(docs), search(query, k, filters=None), delete(id|filter), stats().
	•	Embeddings: pluggable (OPENAI_EMB, SENTENCE_TFM, LOCAL); cache in /.cache/emb/.
	2.	Indexer
	•	Upsert with dedupe fingerprint (sha256(normalized_text)) to avoid dupes.
	•	Metadata filters (identity, lane, fold, tags).
	3.	Lifecycle
	•	Retain N days (env: MEMORY_RETENTION_DAYS), archive to s3://… or ./archive/ gzip.
	•	GDPR: delete by lid with tombstone record + audit log.
	4.	Compression
	•	zstd lvl 6 default; toggle via MEMORY_COMPRESSION_LEVEL.
	5.	Observability
	•	Histograms: lukhas_memory_upsert_seconds, lukhas_memory_search_seconds.
	•	Counters: lukhas_memory_docs_total, lukhas_memory_dedup_dropped_total.
Tests (new):

	•	tests/memory/test_storage_e2e.py — upsert/search/delete, filter, perf p95<100ms.
	•	tests/memory/test_lifecycle.py — retention/archival/GDPR delete + audit entry.
	•	tests/memory/test_compression.py — roundtrip correctness; size < baseline.
	•	tests/memory/test_dedupe_property.py (Hypothesis) — idempotent upsert.
CI gates:
	•	Add job memory-storage-suite in t4-validation.yml (min samples 2000; p95<100ms).
	•	promtool tests for new metrics/alerts (search p95 and error rate).
Acceptance:
	•	p95 upsert/search <100ms (E2E); GDPR delete audited; dedupe correctness; metrics exposed; evidence JSON saved to artifacts/memory_validation_*.json.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/memory_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

C.1 — Implement Core Consciousness Components

Agent Prompt (drop-in):

Context: Stream exists; engines absent. Build core engines with clean interfaces for 🌊 Flow/⚡ Spark/🔮 Oracle.
Create/modify files:
	•	lukhas/consciousness/auto_consciousness.py
	•	lukhas/consciousness/awareness_engine.py
	•	lukhas/consciousness/reflection_engine.py
	•	lukhas/consciousness/dream_engine.py
	•	lukhas/consciousness/types.py (dataclasses: ConsciousnessState, ReflectionReport, DreamTrace, enums)
	•	Wire into consciousness_stream.py (init & per-tick calls)
Implement:

	1.	AwarenessEngine
	•	update(state, signals) -> AwarenessSnapshot with drift EMA, load, anomalies.
	2.	ReflectionEngine
	•	reflect(state) -> ReflectionReport (coherence score, deltas, anomalies). p95<10ms.
	3.	DreamEngine
	•	FSM: IDLE→ENTERING→DREAMING→EXITING, enter/step/exit, consolidation hooks.
	4.	AutoConsciousness
	•	Decision loop: read Awareness+Reflection, propose actions, call Guardian for validate_action_async.
	5.	Observability
	•	Spans: consciousness.awareness|reflection|dream|decide.
	•	Histograms: lukhas_reflection_latency_seconds, lukhas_dream_step_seconds.
Tests:

	•	tests/consciousness/test_engines_contract.py — API contracts + fail-closed on exceptions.
	•	tests/consciousness/test_reflection_perf.py — 10k iterations p95<10ms (unit+E2E).
	•	tests/consciousness/test_dream_fsm.py — legal transitions; Guardian kill-switch mid-dream exits safely.
CI gates: consciousness-core-suite (perf, promtool alerts, schema snapshot tests).
Acceptance: Engines functional & called per tick, perf budgets green, Guardian consulted on decisions, metrics live.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/consciousness_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

I.1 — Implement ΛiD Token Generation & Validation

Agent Prompt (drop-in):

Context: Only stubs; implement secure ΛiD alias/token system.
Create/modify files:
	•	lukhas/identity/token_generator.py
	•	lukhas/identity/token_validator.py
	•	lukhas/identity/alias_format.py (realm/zone/version format helpers)
	•	lukhas/identity/storage.py (KV or DB for issued tokens + rotation history)
	•	Wire into Identity API handlers.
Spec:
	•	Alias format: lid#<REALM>/<ZONE>/v<major>.<uuid>-<crc32>
	•	Token: base64url(HMAC_SHA256(secret, canonical_claims))
	•	CRC32: over alias body for quick integrity; full HMAC for auth.
	•	Rotation: ROTATE_AFTER_DAYS + overlap window; store old secrets (kid).
Implement:
	•	TokenGenerator.create(claims, kid) -> {alias, jwt, kid, exp}
	•	TokenValidator.verify(jwt|alias) -> ValidatedIdentity | error (checks: HMAC, crc32, exp, realm/zone allowlist).
	•	Storage with put_token, revoke, list_active(lid).
Security:
	•	Secrets via env/secret manager; no secrets in logs.
	•	Rate-limit verify endpoint; constant-time compares.
Tests:
	•	tests/identity/test_token_roundtrip.py — generate/validate/rotate.
	•	tests/identity/test_crc32_integrity.py — flip bit → detect.
	•	tests/identity/test_kid_rotation.py — old token valid until overlap end.
	•	Fuzz tests for parser (Hypothesis).
CI gates: identity-token-suite; bandit/semgrep rules for crypto misuse.
Acceptance: Tokens round-trip; rotation works; misuse blocked; docs in docs/identity/lid_tokens.md.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/identity_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

I.2 — Build Tiered Authentication System (T1–T5)

Agent Prompt (drop-in):

Context: Tiers not implemented; add end-to-end tier flows.
Create/modify files:
	•	lukhas/identity/tiers.py (policy + state machine)
	•	lukhas/identity/webauthn.py (T4 FIDO2 bridge; stub ok first)
	•	lukhas/identity/biometrics.py (T5 interface; mock in tests)
	•	API: handlers in lukhas/api/identity.py → /authenticate, /verify, /tier-check
Implement:
	•	T1: public; issue low-scope JWT.
	•	T2: user+pass (argon2id), lockout policy.
	•	T3: +TOTP (RFC 6238).
	•	T4: +WebAuthn challenge; store credential ids.
	•	T5: +biometric attestation (mock provider with test keys).
	•	Map token claim lukhas_tier and enforce per-route.
Security:
	•	All secrets from KMS; anti-replay; device binding for T4+.
Tests:
	•	tests/identity/test_tiers_end_to_end.py — each tier success/fail paths.
	•	Red-team tests: brute force throttled; replay blocked; downgrade prevented.
CI gates: identity-tiers-suite; OWASP cheat-sheet checks via semgrep.
Acceptance: Full tier progression; policy enforced in claims; Guardian check on tier elevation; metrics exported (lukhas_auth_latency_seconds, failures counter).

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/identity_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

I.3 — Implement OIDC Provider & JWT

Agent Prompt (drop-in):

Create/modify:
	•	lukhas/identity/oidc/provider.py — discovery, JWKS, auth, token, userinfo.
	•	lukhas/identity/jwt_utils.py — issue/verify with custom claims (lukhas_tier, lukhas_namespace, permissions[]).
	•	Routes in lukhas/api/oidc.py: /.well-known/openid-configuration, /jwks.json, /authorize, /token, /userinfo.
Implement: OAuth2 code flow (authz code + PKCE), refresh tokens, client registry, scopes.
Tests: conformance subset (OIDF), unit + integration (happy/sad), clock skew.
CI: oidc-provider-suite; publish OpenAPI; add prom histograms for /token latency.
Acceptance: Discovery/JWKS valid; tokens verify; custom claims present; refresh works.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/oidc_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

M.2 — Integrate Memory Metrics with Decision Systems

Agent Prompt (drop-in):

Implement:
	•	Hook affect_delta, driftScore into Guardian risk scoring (weight thresholds).
	•	AwarenessEngine adjusts tick rate based on drift volatility.
	•	Orchestrator decision weighting: penalize providers correlated with high negative drift outcomes.
Files:
	•	lukhas/guardian/risk_scoring.py
	•	lukhas/consciousness/awareness_engine.py (adaptive tick)
	•	ai_orchestration/features.py (add drift features)
Tests: ablation (no metrics → worse detection), property tests (higher drift → higher risk), perf unchanged.
CI: decision-metrics-suite.
Acceptance: Measurable lift in anomaly catch rate; no perf regression >10%.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/decision_metrics_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

C.2 — Integrate Memory & Emotion Bridges

Agent Prompt (drop-in):

Files: candidate/consciousness/bridges/memory/memory_consciousness_bridge.py, …/emotion/affect_bridge.py.
Implement: sync API with rolling window; emotion normalization; quarantine queue for cascades; counters & histograms.
Tests: cascade prevention ≥99.7%; perf <100ms; quarantine alerts.
CI: mem-emotion-bridge-validation.
Acceptance: KPIs met + metrics wired.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/bridge_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

I.6 — Security Hardening & Testing

Agent Prompt (drop-in):

Scope: Threat model + test harness + scanning.
Add:
	•	security/THREAT_MODEL.md (STRIDE), security/tests/test_abuse_cases.py
	•	scripts/pentest_smoke.py (auth bypass, JWT tamper, replay)
	•	CI: security-audit.yml → bandit, semgrep, pip-audit –strict, SBOM + (optional) cosign attest.
Acceptance: No HIGH/CRIT findings; abuse tests green; SBOM generated and archived.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/security_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

G.3 — Standardize Guardian Response Schema

Agent Prompt (drop-in):

Implement: JSON schema with schema_version, timestamp, correlation_id, emergency_active, enforcement_enabled, decision, reasons[], metrics{}.
Files: governance/guardian_schema.json, governance/guardian_system.py (serializer), tests/guardian/test_schema_contract.py.
CI: schema drift test; consumers (Memory/Consciousness/Identity) contract tests.
Acceptance: All responses validate; drift causes CI fail.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/guardian_schema_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

O.2 — Configurable Routing System

Agent Prompt (drop-in):

Implement: external routing in config/routing.yml (+ hot reload), admin API for rule preview, A/B buckets, validation tool scripts/route_lint.py.
Files: ai_orchestration/routing.py, config/routing.yml, api/admin/routing.py.
Tests: A/B split correct; preview sim equals runtime; no cross-lane imports.
CI: orchestrator-routing-suite.
Acceptance: Routing edits don’t require code deploy; audit log of changes.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/routing_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

C.4 — Enhance Consciousness API Endpoints

Agent Prompt (drop-in):

Wire:
	•	/query → AwarenessEngine.current_state()
	•	/dream → DreamEngine.enter/step/exit life cycle
	•	/status → gauges (drift, EMA, tick rate)
	•	/control → feature flags (canary %, pause)
Tests: auth required for control; rate-limited; metrics exposed.
Acceptance: Endpoints reflect live engines; Guardian checks on control ops.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/consciousness_api_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

### T4/0.01% Guidance Add-ons

I.5 — Build Identity API Endpoints

Agent Prompt (drop-in):

Implement:
	•	/authenticate (tiered flow)
	•	/verify (JWT/ΛiD validation)
	•	/tier-check (current + requirements)
	•	/resolve/:alias (ΛiD alias → profile)
Tests: end-to-end tier cases, rate-limit, abuse scenarios.
Acceptance: All routes enforce policy and emit audit logs.

- **Resilience:** Add property-based chaos tests (Hypothesis) with ≥10k ops to ensure stability under stress.
- **Evidence:** Save performance and schema validation artifacts into `artifacts/identity_api_validation_*.json` with SHA256 checksums and optional Merkle chain linking.
- **Governance:** Guardian must be consulted on all risky or state-altering operations, with fail-closed defaults and canary % gates.
- **Observability:** Ensure Prometheus histograms, counters, and OTEL spans are registered and validated with promtool.
- **Security:** Run Bandit/Semgrep/pip-audit with `--strict` and integrate SBOM into CI to block HIGH/CRIT findings.

📅 Execution Order & Dependencies
	1.	M.1 Memory Storage (foundation)
	2.	C.1 Engines (uses M.1 + Guardian)
	3.	I.1 Tokens → I.2 Tiers → I.3 OIDC (security base)
	4.	C.2 Bridges + M.2 Decision Metrics (cross-module signals)
	5.	I.6 Security Hardening (scans + abuse tests)
	6.	G.3 Schema, O.2 Routing, C.4 API, I.5 Identity API

✅ PR Checklists (attach to each PR description)
	•	Design & Interface
	•	Public APIs documented; breaking changes called out
	•	Feature flags default safe; canary % wired
	•	Testing
	•	Unit + integration + property tests
	•	E2E perf: p95 target met (report attached)
	•	Chaos scenario relevant to this change
	•	Observability
	•	Prometheus metrics (hist/counters) exported
	•	OTEL spans with attributes: lane, component, correlation_id
	•	promtool rules + tests added/updated
	•	Security & Governance
	•	Guardian invoked on risky ops
	•	No secrets logged; rate limits on sensitive endpoints
	•	Import-linter lane check green
	•	Evidence
	•	Artifacts in artifacts/<module>_validation_*.json
	•	SHA256 & merkle record updated
	•	AUDITOR_CHECKLIST.md phase updated if needed

# 📑 Auditor-Ready Enhancements
- Cross-environment reproducibility via Docker audit container (`docker/Dockerfile.audit`)
- Scripts: `scripts/replicate.sh` for independent reproduction, `scripts/pentest_smoke.py` for abuse-case validation
- Immutable audit trail: store evidence bundles under `/artifacts/immutable/` with GPG signatures
- Statistical rigor: bootstrap CI95%, Mann-Whitney U for significance, CV<10% thresholds
