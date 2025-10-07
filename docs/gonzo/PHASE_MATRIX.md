---
status: wip
type: documentation
owner: unknown
module: gonzo
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# PHASE\_MATRIX.md — MATRIZ Readiness Plan (T4 / 0.01%)

**Branch:** `main`
**Scope:** Identity → Orchestrator → Memory → Consciousness → Governance/Observability → Security
**Exit bar:** Latency p95 < 250ms, correctness proved, fail-closed defaults, full OTEL/Prom metrics, CI gates block regressions.

---

## Phase 0 — Preflight & Guardrails (P0, same-day)

**Goals**

* Lock the ground truth for perf/env; ensure CI blocks unsafe changes.

**Tasks**

* Add `scripts/preflight_check.py` (CPU governor, NTP, tool versions, container flags).
* Add `tests/auditor/test_burn_rate.py` (SLO burn-rate drill).
* Wire **import-linter** lane rules; fail on cross-lane imports.

**CI**

* `.github/workflows/t4-validation.yml`: job `preflight-and-lanes` (must pass before any suite).

**Acceptance**

* Preflight JSON written to `artifacts/preflight_*.json`.
* `import-linter` passes; any violation fails PR.

**Agent prompt**

```
Add scripts/preflight_check.py and wire to t4-validation.yml as a blocking job.
Add import-linter config for lane isolation (candidate → lukhas → products).
Create tests/auditor/test_burn_rate.py for SLO burn-rate checks (4/1h and 2/6h windows).
```

---

## Phase 1 — Identity Persistence & Rotation (I.1 + I.2) (P0)

**Goals**

* Durable sessions; ΛiD tokens (HMAC+CRC32) with rotation; tiered auth skeleton.

**Tasks**

* `lukhas/identity/session_store.py` (Redis/SQLite adapter + TTL + crash recovery).
* `lukhas/identity/token_generator.py` + `token_validator.py` (HMAC-SHA256, CRC32 trailer, `kid` rotation).
* `lukhas/identity/tiers.py` (T1–T3 initial flow; WebAuthn stub OK).

**CI**

* `identity-token-suite`, `identity-session-suite`.

**Acceptance**

* Round-trip, rotation overlap, replay-attack tests pass.
* Session survive restart; TTL enforced; audit log written.

**Agent prompts**

```
Implement SessionStore with Redis first, fallback SQLite; expose put/get/ttl/sweep; add property tests (concurrency).
Implement TokenGenerator/Validator per ΛiD spec (alias format + CRC32 + HMAC); add rotation & replay-protection tests.
Bootstrap T1–T3 in tiers.py with Argon2id and TOTP; expose /authenticate, /verify, /tier-check (stub handlers pass tests).
```

---

## Phase 2 — Memory Storage (M.1) (P0)

**Goals**

* Real vector memory; lifecycle; compression; metrics.

**Tasks**

* `lukhas/memory/backends/pgvector_store.py` (or `faiss_store.py`) with `add/bulk_add/search/delete/stats`.
* `lukhas/memory/indexer.py` (embedding plugins, SHA-256 dedupe).
* `lukhas/memory/lifecycle.py` (retention, archival, GDPR tombstones).
* `lukhas/memory/compression.py` (zstd level from env).
* Wire metrics → `observability/prometheus_metrics.py`.

**CI**

* `memory-storage-suite` (p95 upsert/search <100ms, n≥2000), promtool rules.

**Acceptance**

* GDPR delete emits audit; dedupe property test passes; histograms + counters exported.

**Agent prompt**

```
Implement pgvector_store.py with typed filters (identity, lane, fold, tags). Add indexer (embedding plugin, SHA-256 dedupe).
Add lifecycle (retention days, archival dir/S3, tombstones). Expose metrics: upsert/search histograms, docs_total, dedup_dropped_total.
Create tests: storage_e2e, lifecycle, compression, dedupe_property (Hypothesis).
```

---

## Phase 3 — Consciousness Engines (C.1) (P0→P1)

**Goals**

* Awareness/Reflection/Dream engines wired into stream; Guardian consulted on actions.

**Tasks**

* `lukhas/consciousness/{awareness_engine.py,reflection_engine.py,dream_engine.py,auto_consciousness.py,types.py}`.
* Per-tick calls in `consciousness_stream.py`.
* OTEL spans: `consciousness.awareness|reflection|dream|decide`.

**CI**

* `consciousness-core-suite` (perf unit p95 <10ms reflection; FSM tests; fail-closed on exceptions).

**Acceptance**

* Engines invoked per tick; decisions pass through Guardian; metrics live.

**Agent prompt**

```
Build AwarenessEngine.update (EMA drift, anomalies), ReflectionEngine.reflect (p95<10ms), DreamEngine FSM with consolidation hooks, AutoConsciousness decision loop calling guardian.validate_action_async.
Wire OTEL spans & Prom histograms. Add contract, perf, and FSM tests.
```

---

## Phase 4 — Orchestrator Routing (O.2) (P1)

**Goals**

* Externalized routing; A/B buckets; preview/validate without deploy.

**Tasks**

* `ai_orchestration/routing.py` + `config/routing.yml` (hot-reload).
* Admin preview API: `api/admin/routing.py`.
* Import-linter guard (no cross-lane).

**CI**

* `orchestrator-routing-suite`; promtool alerts for routing latency & error spikes.

**Acceptance**

* Preview sim == runtime; A/B split deterministic; edits audited.

**Agent prompt**

```
Move provider map to config/routing.yml; add runtime hot-reload and preview endpoint. Implement A/B buckets and rule validation tool scripts/route_lint.py. Add tests for determinism and parity.
```

---

## Phase 5 — Observability & Evidence (P1)

**Goals**

* Dark-mode→enforced telemetry; compressed evidence bundles.

**Tasks**

* Patch audit runner to emit `artifacts/summary/*.json` (p95, p99, CI95, env).
* Grafana dashboard JSON for MATRIZ nodes; Jaeger service map; burn-rate alerts.

**CI**

* `observability-enforcement` (fails if metrics missing or alerts invalid).

**Acceptance**

* promtool test green; traces show per-stage spans with `lane`, `component`, `correlation_id`.

**Agent prompt**

```
Add summary evidence writer; ensure Prom counters/histograms for memory, identity, consciousness, orchestrator. Commit grafana dashboard and prom rules + tests.
```

---

## Phase 6 — Security Hardening (I.6) (P1)

**Goals**

* Threat model, abuse tests, scanners block.

**Tasks**

* `security/THREAT_MODEL.md` (STRIDE), `security/tests/test_abuse_cases.py`.
* `scripts/pentest_smoke.py` (JWT tamper, replay, tier-downgrade).
* Tighten GH Actions to SHA pin; `pip-audit --strict`, SBOM.

**CI**

* `security-audit.yml` (Bandit, Semgrep, pip-audit strict, SBOM upload).

**Acceptance**

* No HIGH/CRIT; abuse tests pass; SBOM archived.

**Agent prompt**

```
Write STRIDE threat model, implement abuse tests for auth bypass/replay/downgrade; add pentest smoke script. Ensure GH actions are SHA-pinned; pip-audit strict blocks.
```

---

## Phase 7 — Governance Schema (G.3) (P1)

**Goals**

* Stable Guardian response schema + drift tests.

**Tasks**

* `governance/guardian_schema.json` (schema\_version, timestamp, correlation\_id, emergency\_active, enforcement\_enabled, decision, reasons\[], metrics{}).
* Serializer + contract tests across consumers.

**CI**

* `guardian-schema-drift` (snapshot test).

**Acceptance**

* All responses validate; schema drift fails CI.

**Agent prompt**

```
Define guardian_schema.json and serializer; update Memory/Consciousness/Identity consumers. Add schema contract & drift tests.
```

---

## Phase 8 — Lane Assignment & Canary (P1)

**Goals**

* Promote modules to lanes with guardrails.

**Initial lanes**

* **Registry**: Production (100%)
* **Guardian**: Production Canary (25%→50%→100%)
* **Orchestrator**: Production Canary (10%→25%→50%)
* **Identity**: Integration (promote after Phase 1)
* **Memory/Consciousness**: Integration (promote after Phases 2–3)

**CI**

* `lane-gates` job ensures canary % and flags match repo-encoded policy.

**Acceptance**

* Canary plan YAML checked-in; rollback tested; denial deltas within bands.

**Agent prompt**

```
Create deployment/canary/*.yml (k8s/compose) and a lane policy file (policy/lane_gates.yaml). Add CI check that fails if enforced flags or canary % drift from policy.
```

---

## Quick Commands

```bash
# Run preflight + lanes + security
pytest -q tests/auditor -k burn_rate && import-linter && bandit -q -r lukhas

# Memory suites
pytest -q tests/memory -q && promtool test rules ops/prometheus/slo_alerts_test.yml

# Identity suites
pytest -q tests/identity -q

# Consciousness suites
pytest -q tests/consciousness -q

# Orchestrator routing
pytest -q tests/orchestration -k routing
```

---

## Exit Checklist (must be ✅ before full Production)

* ✅ p95 < 250ms for all MATRIZ stages (CI95 reported; CV < 10%)
* ✅ Guardian fail-closed by default; kill-switch drill logged
* ✅ No cross-lane imports (import-linter)
* ✅ OTEL spans per stage; Prom histograms + promtool tests
* ✅ Identity: persistent sessions, token rotation, replay protection
* ✅ Memory: dedupe, lifecycle, GDPR audit, metrics
* ✅ Consciousness: engines wired; decisions validated by Guardian
* ✅ Security: STRIDE doc, abuse tests, scanners strict; SBOM archived
* ✅ Lane policy encoded; canary gates enforced in CI

---

### Notes

* Keep **feature flags default-safe**. All new surfaces behind `*_ENABLED=false` with canary percentage rollout.
* Store all evidence under `artifacts/` with SHA256 and run id.

---

If you want, I can also generate the skeleton files (empty modules + TODOs + test stubs) to accelerate Phase 1–3 in a single patch.
