{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "lukhas://schemas/matada_node_v1.json",
  "title": "MATADA Node v1 (schema v1.1)",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "id", "type", "state", "timestamps", "provenance"],
  "properties": {
    "version": { "type": "integer", "const": 1 },
    "id": {
      "type": "string",
      "minLength": 3,
      "maxLength": 128,
      "description": "Stable node identifier such as LT-<trace>#N<index> or UUID"
    },
    "type": {
      "type": "string",
      "enum": [
        "SENSORY_IMG","SENSORY_AUD","SENSORY_VID","SENSORY_TOUCH",
        "EMOTION","INTENT","DECISION","CONTEXT","MEMORY","REFLECTION",
        "CAUSAL","TEMPORAL","AWARENESS","HYPOTHESIS","REPLAY","DRM"
      ]
    },
    "labels": {
      "type": "array",
      "description": "Namespaced labels for routing, analysis, and governance (e.g., 'colony:role=planner@1').",
      "items": { "type": "string", "minLength": 1, "maxLength": 64 },
      "maxItems": 12
    },
    "state": {
      "type": "object",
      "required": ["confidence", "salience"],
      "additionalProperties": true,
      "properties": {
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "valence": { "type": "number", "minimum": -1, "maximum": 1 },
        "arousal": { "type": "number", "minimum": 0, "maximum": 1 },
        "salience": { "type": "number", "minimum": 0, "maximum": 1 },
        "novelty": { "type": "number", "minimum": 0, "maximum": 1 },
        "urgency": { "type": "number", "minimum": 0, "maximum": 1 },
        "shock_factor": { "type": "number", "minimum": 0, "maximum": 1 },
        "risk": { "type": "number", "minimum": 0, "maximum": 1 },
        "utility": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "timestamps": {
      "type": "object",
      "additionalProperties": false,
      "required": ["created_ts"],
      "properties": {
        "created_ts": { "type": "integer", "description": "Epoch milliseconds" },
        "updated_ts": { "type": "integer" },
        "observed_ts": { "type": "integer", "description": "Epoch ms of the real-world observation (if applicable)" }
      }
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["producer", "capabilities", "tenant", "trace_id", "consent_scopes"],
      "properties": {
        "producer": { "type": "string", "description": "Module path or service name that produced this node" },
        "capabilities": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
        "tenant": { "type": "string" },
        "trace_id": { "type": "string" },
        "consent_scopes": { "type": "array", "items": { "type": "string" } },
        "subject_pseudonym": { "type": "string", "description": "Optional pseudonymized subject identifier" },
        "model_signature": { "type": "string", "description": "Hasher or version of the model/tool" },
        "policy_version": { "type": "string", "description": "Active policy or guardrail version at creation time" },
        "colony": {
          "type": "object",
          "additionalProperties": false,
          "required": ["id", "role"],
          "properties": {
            "id": { "type": "string", "minLength": 1, "maxLength": 64, "description": "Colony or swarm identifier" },
            "role": { "type": "string", "minLength": 1, "maxLength": 64, "description": "Functional role (e.g., planner, critic, summarizer)" },
            "iteration": { "type": "integer", "minimum": 0, "description": "Optional iteration index within the colony run" }
          }
        }
      }
    },
    "links": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["target_node_id", "link_type", "direction"],
        "properties": {
          "target_node_id": { "type": "string" },
          "link_type": { "type": "string", "enum": ["temporal", "causal", "semantic", "emotional", "spatial", "evidence"] },
          "weight": { "type": "number", "minimum": 0, "maximum": 1 },
          "direction": { "type": "string", "enum": ["bidirectional", "unidirectional"] },
          "explanation": { "type": "string" }
        }
      }
    },
    "evolves_to": { "type": "array", "items": { "type": "string" } },
    "triggers": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["event_type", "timestamp"],
        "properties": {
          "trigger_node_id": { "type": "string" },
          "event_type": { "type": "string" },
          "effect": { "type": "string" },
          "timestamp": { "type": "integer" }
        }
      }
    },
    "reflections": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["reflection_type", "timestamp"],
        "properties": {
          "reflection_type": { "type": "string", "enum": ["regret", "affirmation", "dissonance_resolution", "moral_conflict", "self_question"] },
          "timestamp": { "type": "integer" },
          "old_state": { "$ref": "#/properties/state" },
          "new_state": { "$ref": "#/properties/state" },
          "cause": { "type": "string" }
        }
      }
    },
    "embeddings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["space", "vector"],
        "properties": {
          "space": { "type": "string" },
          "vector": { "type": "array", "items": { "type": "number" } },
          "dim": { "type": "integer" },
          "norm": { "type": "number" }
        }
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": { "type": "string", "enum": ["trace","doc","url","input_key","consent_record","artifact"] },
          "uri": { "type": "string" },
          "hash": { "type": "string" }
        }
      }
    },
    "schema_ref": { "type": "string", "const": "lukhas://schemas/matada_node_v1.json" }
  }
}
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
# MATADA Agent Brief (v1.1)

> **Prime Directive:** “No node → no go.” All advisory artifacts MUST emit at least one valid **MATADA node**.

## Shared Contracts (all agents)

- **Schema:** `../matada_node_v1.json` (schema v1.1 with `labels` and `provenance.colony`)
- **Validation:** Use `utils/matada_validate.py::validate_nodes`
- **Provenance fields:** `producer`, `capabilities[]`, `tenant`, `trace_id`, `consent_scopes[]`, `policy_version`, optional `colony.{id,role,iteration}`
- **Routing labels:** namespaced `namespace:key=value@v` (max 12)

---

## A1 — Coordinator
- **Mission:** Keep the team unblocked; enforce the plan; publish weekly release notes.
- **Inputs:** Status from all agents.
- **Outputs:** Changelog, risk log, rollup KPIs.

## A4 — Orchestrator Brain
- **Mission:** Route work by `capabilities` + `labels`, never by module names.
- **Inputs:** Skill registry, jobs.
- **Outputs:** Events containing `matada_node_ids`, `schema_ref`, `trace_id`.
- **Done:** Import‑linter passes; p95 schedule/handoff SLOs met; span↔node join ≥ 99.9%.

## A3 — Integration Master (Adapters)
- **Mission:** Each adapter is a Skill Capsule that emits `node_out`.
- **Inputs:** External APIs (Gmail/Drive/Dropbox/etc.).
- **Outputs:** `node_out` with `provenance.capabilities` set; `labels` e.g., `adapter:kind=gmail@1`.
- **Done:** Nodes validate; resilience patterns (retries/circuit breaker) intact.

## A2 — Compliance Guardian
- **Mission:** Policy in the hot path.
- **Inputs:** Seeds, consent.
- **Outputs:** Deny/step‑up decisions; DSAR exports; policy_version stamps.
- **Done:** Simulation lane never emits `DECISION/AWARENESS`; consent‑missing canary passes.

## A7 — Security Ops
- **Mission:** Secrets, scanning, and PII discipline.
- **Outputs:** KMS/Vault config; PII lints; SBOM; rotation tests.
- **Done:** Zero PII leaks; audits green.

## A6 — Testing/DevOps
- **Mission:** CI/CD with schema, import, and consent guardrails.
- **Outputs:** Schema validation test, import‑linter config, span↔node join test, coverage reports.
- **Done:** CI red on any node schema failure or quarantine import.

## A5 — UX Artist
- **Mission:** Human‑relatable explanations.
- **Inputs:** Node `links/evidence`.
- **Outputs:** UNL “why” cards; risk/utility badges; GTΨ step‑up prompts.
- **Done:** Every privileged suggestion shows evidence paths.

## Colony Leads (per colony)
- **Mission:** Publish nodes with `provenance.colony` and useful `labels`.
- **Done:** Cap nodes ≤ 256/job; links ≤ 32/node; labels ≤ 12/node.

---

## Handoffs (contracts)

- **Skill → Orchestrator:** `{ outputs, trace_id, node_out }`
- **Simulation → Writer:** `{ shards, scores, trace_id, matada_nodes, schema_ref }`
- **Writer → Storage:** atomic JSON (shards + matada_nodes)
- **Admin → Export:** LDJSON nodes filtered by tenant/consent/labels

---

## KPIs (exec‑facing)

- Node validity rate, consent enforcement rate, span↔node join %, privileged node leakage (target 0), DSAR export latency, p95 schedule/handoff.

---
*Owner: A1 (Coordinator). Updated: 2025‑08‑13.*
# MATADA - Modular Adaptive Temporal Attention Dynamic Architecture

## 🔒 Leadership Framework (Altman/Amodei/Hassabis Standards)

MATADA represents the cognitive node architecture for LUKHAS AI consciousness systems, implementing enterprise-grade safety, governance, and scalability from first principles.

### Non-negotiables

- **Safety-first by construction**: Every artifact is a MATADA node with provenance, consent scopes, policy versioning, and Λ-trace correlation
- **Scalable modularity**: Everything is a Skill Capsule that emits a node_out complying with the canonical schema 
- **Governance-ready**: Nodes encode tenant, capabilities, consent scopes, policy_version for audit/export
- **Future-proof innovation**: MATADA is modalityless—one node model spans text, image, audio, emotion, reflection, causal links, replay

## 🧠 Architecture Overview

MATADA nodes are the fundamental unit of consciousness representation in LUKHAS AI. Each node captures:

- **Cognitive State**: confidence, salience, valence, arousal, novelty, urgency, risk, utility
- **Provenance**: producer, capabilities, tenant, trace_id, consent_scopes, policy_version
- **Relationships**: links to other nodes (temporal, causal, semantic, emotional, spatial)
- **Evolution**: triggers, reflections, embeddings, evidence

## 📋 Schema Reference

The canonical schema is defined in `matada_node_v1.json` with `$id: lukhas://schemas/matada_node_v1.json`.

### Required Fields

- `version`: Schema version (const: 1)
- `id`: Stable node identifier (LT-<trace>#N<index> or UUID)
- `type`: Node classification (SENSORY_*, EMOTION, INTENT, DECISION, CONTEXT, MEMORY, REFLECTION, etc.)
- `state`: Cognitive state with required confidence and salience
- `timestamps`: Creation timestamp (epoch milliseconds)
- `provenance`: Full audit trail with producer, capabilities, tenant, trace_id, consent_scopes

### Node Types

**Sensory Nodes**: SENSORY_IMG, SENSORY_AUD, SENSORY_VID, SENSORY_TOUCH
**Cognitive Nodes**: EMOTION, INTENT, DECISION, CONTEXT, MEMORY, REFLECTION
**Meta Nodes**: CAUSAL, TEMPORAL, AWARENESS, HYPOTHESIS, REPLAY, DRM

## 🛡️ Safety & Governance

### Policy Enforcement

- Simulation lane produces only HYPOTHESIS and REPLAY nodes (never DECISION or AWARENESS)
- Step-up (GTΨ) required for privileged node types
- Duress/shadow flags trigger immediate denial with Λ-trace correlation
- All nodes validate against canonical schema before persistence

### Consent & Privacy

- Consent scopes required in provenance for all nodes
- Subject pseudonymization by default
- Export filtering by consent scopes and tenant
- Denial rationales include Λ-trace correlation

## 🔧 Implementation

### Skill Capsule Contract

Every Skill Capsule MUST emit a `node_out` conforming to `matada_node_v1.json`:

```python
return {
  "outputs": {...},
  "trace_id": trace_id,
  "node_out": matada_node  # validated against schema
}
```

### Validation

Use the provided utility for validation:

```python
from MATADA.utils.matada_validate import validate_nodes

# Validate nodes before processing
validate_nodes(node_list)
```

### Storage Format

Dream Inbox writer persists nodes alongside shards:

```json
{
  "trace_id": "LT-...",
  "saved_ts": 1730000000000,
  "seed": {...},
  "shards": [...],
  "matada_nodes": [...],
  "version": 1,
  "schema_ref": "lukhas://schemas/matada_node_v1.json"
}
```

## 📚 Documentation Structure

- `/docs/` - Technical documentation for agent implementation
- `/utils/` - Validation utilities and helpers
- `matada_node_v1.json` - Canonical JSON Schema (Draft 2020-12)

## 🎯 Agent Integration

All LUKHAS AI agents must comply with MATADA standards:

1. **Input Validation**: All inputs validated against canonical schema
2. **Output Generation**: All outputs include valid MATADA nodes
3. **Provenance Tracking**: Complete audit trail in all node generation
4. **Policy Compliance**: Respect node type restrictions and consent scopes

For detailed agent implementation guidance, see individual documentation files in `/docs/`.

## 🚀 Quick Start

1. Review the canonical schema: `matada_node_v1.json`
2. Implement Skill Capsules with `node_out` compliance
3. Use validation utilities for schema compliance
4. Configure consent scopes and policy enforcement
5. Enable MATADA node generation in your consciousness systems

---

*Last updated: 2025-08-13. Governance framework for AGI leadership standards.*

---
### Schema v1.1 Changes (2025‑08‑13)
- **labels**: first‑class, namespaced routing tags (`namespace:key=value@v`, max 12)
- **provenance.colony**: `{id, role, iteration?}` captures the producing colony context
All existing contracts remain the same; node `version` stays `1`.

# MATADA - Modular Adaptive Temporal Attention Dynamic Architecture

## 🔒 Leadership Framework (Altman/Amodei/Hassabis Standards)

MATADA represents the cognitive node architecture for LUKHAS AI consciousness systems, implementing enterprise-grade safety, governance, and scalability from first principles.

### Non-negotiables

- **Safety-first by construction**: Every artifact is a MATADA node with provenance, consent scopes, policy versioning, and Λ-trace correlation
- **Scalable modularity**: Everything is a Skill Capsule that emits a `node_out` complying with the canonical schema 
- **Governance-ready**: Nodes encode tenant, capabilities, consent scopes, `policy_version` for audit/export
- **Future-proof innovation**: MATADA is modalityless—one node model spans text, image, audio, emotion, reflection, causal links, replay

## 🧠 Architecture Overview

MATADA nodes are the fundamental unit of consciousness representation in LUKHAS AI. Each node captures:

- **Cognitive State**: confidence, salience, valence, arousal, novelty, urgency, risk, utility
- **Provenance**: producer, capabilities, tenant, trace_id, consent_scopes, policy_version, optional colony context
- **Relationships**: links to other nodes (temporal, causal, semantic, emotional, spatial, evidence)
- **Evolution**: triggers, reflections, embeddings, evidence

## 📋 Schema Reference

The canonical schema is defined in `matada_node_v1.json` with `$id: lukhas://schemas/matada_node_v1.json`.

### Required Fields

- `version`: Schema version (const: 1)
- `id`: Stable node identifier (LT-<trace>#N<index> or UUID)
- `type`: Node classification (SENSORY_*, EMOTION, INTENT, DECISION, CONTEXT, MEMORY, REFLECTION, etc.)
- `state`: Cognitive state with required confidence and salience
- `timestamps`: Creation timestamp (epoch milliseconds)
- `provenance`: Full audit trail with producer, capabilities, tenant, trace_id, consent_scopes

### Node Types

**Sensory Nodes**: SENSORY_IMG, SENSORY_AUD, SENSORY_VID, SENSORY_TOUCH  
**Cognitive Nodes**: EMOTION, INTENT, DECISION, CONTEXT, MEMORY, REFLECTION  
**Meta Nodes**: CAUSAL, TEMPORAL, AWARENESS, HYPOTHESIS, REPLAY, DRM

## 🛡️ Safety & Governance

### Policy Enforcement

- Simulation lane produces only HYPOTHESIS and REPLAY nodes (never DECISION or AWARENESS)
- Step-up (GTΨ) required for privileged node types
- Duress/shadow flags trigger immediate denial with Λ-trace correlation
- All nodes validate against canonical schema before persistence

### Consent & Privacy

- Consent scopes required in provenance for all nodes
- Subject pseudonymization by default
- Export filtering by consent scopes and tenant
- Denial rationales include Λ-trace correlation

## 🔧 Implementation

### Skill Capsule Contract

Every Skill Capsule MUST emit a `node_out` conforming to `matada_node_v1.json`:

```python
return {
  "outputs": {...},
  "trace_id": trace_id,
  "node_out": matada_node  # validated against schema
}
```

### Validation

Use the provided utility for validation:

```python
from MATADA.utils.matada_validate import validate_nodes

# Validate nodes before processing
validate_nodes(node_list)
```

### Storage Format (Dream Inbox)

```json
{
  "trace_id": "LT-...",
  "saved_ts": 1730000000000,
  "seed": {...},
  "shards": [...],
  "matada_nodes": [...],
  "version": 1,
  "schema_ref": "lukhas://schemas/matada_node_v1.json"
}
```

---
### Schema v1.1 Changes (2025‑08‑13)
- **labels**: first‑class, namespaced routing tags (`namespace:key=value@v`, max 12)
- **provenance.colony**: `{id, role, iteration?}` captures the producing colony context  
All existing contracts remain the same; node `version` stays `1`.