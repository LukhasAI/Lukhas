# MATADA Implementation Plan (v1.1) — Safety Substrate, Modular Routing, Governance by Design

> **North Star:** “No node → no go.” Every advisory artifact must project to a valid **MATADA node**. Safety, scale, governance, and innovation flow from this substrate.

## 0) What is MATADA?

**MATADA (Modular Adaptive Temporal Attention Dynamic Architecture)** is LUKHAS AI’s canonical cognition substrate. A **MATADA node** is a first-class, provenance-rich record of thought: state (confidence, salience, risk, utility), relationships (links), evolution (triggers/reflections), and governance (tenant, consent scopes, policy version, colony role).

- **Why keep the name?** It’s memorable, on-brand with the “digital mycelium,” and precisely names the core: modularity, adaptivity, temporal structure, attention, dynamic evolution, architecture.

## 1) Non‑Negotiables (Altman/Amodei/Hassabis Standards)

- **Safety by construction:** Simulation (“Dreams”) emits only `HYPOTHESIS`/`REPLAY`. Privileged types require **GTΨ** step‑up.
- **Uniform contracts:** Skill Capsules emit `node_out` that validates against `matada_node_v1.json` (schema v1.1).
- **Governance‑ready:** Nodes carry `tenant`, `consent_scopes`, `policy_version`, and `trace_id` for replay and DSAR.
- **Future‑proof:** Symbolic‑temporal nodes are canonical; embeddings are optional attachments.

## 2) Scope (Phase 0 → Phase 3)

### Phase 0 — Baseline (Today)
- Schema v1.1 shipped (`labels`, `provenance.colony`).
- Validator utility in place.
- Docs 1–7 aligned with MATADA.

### Phase 1 — Emit & Persist (Week 1)
- All skills return `node_out`.
- Simulation projects shards → `HYPOTHESIS` nodes.
- Dream Inbox writer persists `matada_nodes` atomically with shards.

### Phase 2 — Route & Govern (Week 2)
- Orchestrator routes by `capabilities` + `labels`.
- Λ‑Trace 2.0: span attributes include `node_id`, `tenant`, `policy_version`, `consent_scopes`.
- Admin export: filter by `labels`, `colony`, `tenant`, `consent_scopes`.

### Phase 3 — Optimize & Prove (Week 3–4)
- Bandit uses `state.utility/risk`.
- Canary tests: consent‑missing → no nodes; schema drift → CI fail.
- KPIs: node validity ≥ 99.9%, p95 schedule/handoff SLOs, audit export < 1s/10k nodes.

## 3) Deliverables & Owners

- **A1 (Coordinator):** Enforce docs/contracts; unblock agents; publish weekly release notes.
- **A4 (Orchestrator Brain):** Bus contracts, routing by labels/capabilities; import‑linter rules.
- **A3 (Integration Master):** Skill Capsule adapters emit `node_out`; resilience patterns.
- **A6 (Testing/DevOps):** CI schema validation, consent canary, span↔node join test (≥99.9%).
- **A2 (Compliance Guardian):** Policy guards (FORBID types), GTΨ, DSAR export flows.
- **A7 (Security Ops):** PII lints, KMS/Vault policies, policy_version stamping.
- **A5 (UX Artist):** UNL explanations (“why” cards) sourced from node links/evidence.
- **Colony leads:** Add `provenance.colony` + `labels` to nodes; cap nodes/links per job.

## 4) Contracts

- **Schema:** `matada_node_v1.json` (v1.1) is the only canonical format.
- **Routing:** `labels` use `namespace:key=value@v` (e.g., `colony:role=planner@1`).
- **Safety:** `FORBID_NODE_TYPES = {"DECISION","AWARENESS"}` in Simulation lane.
- **Persistence:** Writer fails hard if `DREAM_INBOX_VALIDATE=1` and nodes invalid; otherwise logs & drops invalid nodes.

## 5) Success Metrics

- ✅ 100% of advisory artifacts have ≥1 valid node.
- ✅ Consent missing ⇒ 0 nodes (with rationale) — enforced by tests.
- ✅ Span↔node join rate ≥ 99.9%.
- ✅ Admin export under consent filters returns in < 1s for 10k nodes.
- ✅ Zero `DECISION/AWARENESS` nodes from Simulation lane.

## 6) Risks & Mitigations

- **Tag sprawl →** registry + linter; limit `labels` ≤ 12.
- **Graph bloat →** per‑job budgets; summarizer compaction.
- **Consent drift →** consent‑required canary + policy_version stamping.
- **Schema drift →** CI schema validation across all `node_out`.

## 7) Timeline (aggressive, achievable)

- **Week 1:** Emit & persist; consent canary; basic exports.
- **Week 2:** Routing by labels/capabilities; Λ‑Trace 2.0.
- **Weeks 3–4:** KPIs, dashboards, bandit optimization, DSAR polish.

---
*Owner: A1 (Coordinator). Updated: 2025‑08‑13.*
