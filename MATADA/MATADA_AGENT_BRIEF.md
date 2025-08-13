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