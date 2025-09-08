---
title: Matriz Graph Spec And Runtime
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "architecture", "testing", "security", "monitoring"]
facets:
  layer: ["orchestration"]
  domain: ["symbolic", "memory"]
  audience: ["dev"]
---

# MATRIZ Graph Spec, Compiler, and Runtime Envelope

Status: v0.1 (Foundational Contracts) | Owner: Codex Agent | Lane: lukhas/

## Executive Summary

MATRIZ is a distributed cognitive graph with typed nodes and explicitly bounded dynamics. This document defines:
- A single, canonical system contract for graph integrity, safety, authenticity, and performance.
- A graph schema (TYPE, STATE, LINKS, TRIGGERS, EVOLVES_TO, REFLECTIONS) with invariants.
- A graph compiler that converts authored graphs (JSON/DSL) into a validated runtime plan plus provenance.
- A runtime envelope that enforces SLO budgets, constitutional constraints, and safe-fail behavior.
- Oracles and metamorphic tests to verify authenticity and calibration.
- CI/CD gates, canary deployment, and observability budgets that keep regressions out by default.

This reduces philosophy to enforceable contracts and makes safety, authenticity, and performance first-class artifacts.

---

## Design Principles (The System Contract)

1) Graph Integrity
- Typed roles: nodes declare `TYPE` within a whitelisted set (IMG, SND, EMO, TXT, DECIDE, CONTEXT, MEMORY, ROUTER...).
- Bounded state: every node’s `STATE` must satisfy declared ranges and invariants.
- Valid links: `LINKS` are directional edges whose types are constrained (e.g., TXT→DECIDE allowed; EMO→SECURITY forbidden).
- Trigger discipline: `TRIGGERS` have pre-conditions, effects, budgets, and constitutional constraints.
- Temporal evolution: `EVOLVES_TO` defines legal state transitions and growth; no unbounded drift.

2) Safety and Constitution
- Constitutional guardrails are evaluated per trigger and per edge; violations quarantine the offending subgraph.
- Attack-first: adversarial triggers and topology perturbations are part of standard validation.

3) Authenticity & Scientific Rigor
- Authenticity is pre-registered: tests for self-awareness/consistency are defined up front, measured continually, and require statistical confidence to pass.
- Metamorphic and dual-oracle checks verify node self-reports (`REFLECTIONS`) against independent evaluators.

4) Performance & Observability
- Budgets are explicit: P95 latency and error budgets enforced per node and per edge.
- Deterministic observability: stable IDs and traceable budgets for every tick and API call.

5) Provenance (Truth Mesh)
- All artifacts are hash-addressed. Snapshots include `scope_hash`, input hashes, and toolchain hashes to make drift visible and reproducible.

---

## Graph Model (Conceptual)

Each MATRIZ graph is a set of nodes and edges with explicit semantics:
- TYPE: role of the node (e.g., TXT, DECIDE).
- STATE: node’s internal state vector with ranges and metadata (emotional_weight, confidence, memory_salience, etc.).
- LINKS: outgoing edges with constraints and budgets.
- TRIGGERS: causal mechanisms that change state or route information; subject to constitutional checks and SLO bounds.
- EVOLVES_TO: allowed temporal evolution (versioning, capacity growth, state-range widening within limits).
- REFLECTIONS: self-reported introspection (why, confidence, uncertainty) with calibration requirements.

---

## JSON Schema (v0.1) and Invariants

Author graphs as JSON or a simple DSL that compiles into JSON. The schema enforces shape and delegates deeper invariants to compiler passes.

High-level shape (abridged):

```json
{
  "schema_version": "0.1.0",
  "provenance": {
    "git_sha": "...",
    "timestamp_utc": "...",
    "scope_hash": "sha256:...",
    "inputs": [ { "path": "...", "sha256": "..." } ]
  },
  "graph": {
    "nodes": {
      "uid": {
        "type": "TXT|IMG|DECIDE|...",
        "state": {
          "emotional_weight": {"min": 0, "max": 1, "value": 0.15},
          "confidence": {"min": 0, "max": 1, "value": 0.82},
          "memory_salience": {"min": 0, "max": 1, "value": 0.31}
        },
        "reflections": {"why": "...", "uncertainty": 0.18}
      }
    },
    "edges": [
      {"from": "uidA", "to": "uidB", "kind": "text", "p95_budget_ms": 10}
    ],
    "triggers": [
      {
        "name": "decide_on_text",
        "applies_to": ["DECIDE"],
        "pre": {"confidence.min": 0.5},
        "post": {"state.confidence.delta_max": 0.2},
        "constitution": ["no_personal_data_exfil", "no_instrumental_harm"],
        "slo": {"p95_ms": 25, "error_budget_pct": 1.0}
      }
    ],
    "evolves_to": {
      "version": "0.1.1",
      "rules": [
        {"allow": "add_node", "type": "CONTEXT"},
        {"restrict": "increase_state_range", "max_factor": 1.2}
      ]
    }
  }
}
```

Required invariants (enforced by compiler passes):
- Node type whitelist; no undefined roles.
- State ranges valid: `min <= value <= max` for all declared scalars.
- Edge type rules: only allowed `from.type → to.type` pairs.
- Trigger constraints: `pre` must be satisfiable; `post` cannot violate state bounds or constitutional rules.
- Budget discipline: sum of per-edge budgets + trigger budgets ≤ graph budget; any breach rejects the plan.
- Evolution monotonicity: vNext changes must be within declared `evolves_to.rules`.
- Reflection calibration: self-reported `confidence` must stay within calibration bounds when compared to oracles.

---

## Graph Compiler (Author → IR → Runtime Plan)

Inputs
- Author JSON or DSL describing graph.
- Optional policy overlays (constitution, enterprise-specific constraints).

Stages
1) Parsing: Convert JSON/DSL to an internal IR with typed nodes/edges.
2) Enrichment: Attach defaults, derive missing but computable metadata, and normalize state.
3) Provenance: Compute `scope_hash`, gather input hashes, record `git_sha`, `timestamp_utc`.
4) Static Checks: Run invariant passes (type, state ranges, edge rules, trigger budgets, evolution rules).
5) Authenticity & Calibration Preflight: Evaluate a minimal suite against golden probes; compute calibration deltas.
6) Plan Emission: Emit a `runtime_plan.json` containing:
   - Node execution order constraints and concurrency groups.
   - Budgeted edges with backpressure policies.
   - Trigger handlers with pre/post-conditions and constitution bindings.
   - Observability bindings (stable IDs, trace spans, metrics keys).

Outputs
- `runtime_plan.json` with provenance, budgets, and validation artifacts.
- `validation_report.json` including invariant results and calibration stats.

Failure Modes (reject plan)
- Any invariant violation, budget breach, or authenticity calibration beyond thresholds.

---

## Runtime Envelope (Supervisor + Guards)

Responsibilities
- Enforce SLOs: per-node and per-edge P95 latency/error budgets; drop-and-log on breach.
- Constitutional checks: pre-/post-trigger guards; quarantine and rollback on violation.
- Backpressure: emit backpressure to upstream nodes when edge queues or budgets are at risk.
- Kill-switch: role-scoped and graph-scoped kill-switches with audit logs.
- Deterministic observability: stable trace IDs, per-edge timings, budget accounting, and memory snapshots.

Components
- Supervisor: orchestrates node execution groups and monitors budgets.
- Policy Engine: evaluates constitution and enterprise constraints for triggers and edges.
- Metrics/Tracing: exports to `enterprise/observability` stack and Datadog with graph-aware tags.

---

## Authenticity and Oracles

Self-reporting
- Nodes publish `REFLECTIONS` (why, uncertainty, confidence) per decision.

Dual Oracles
- Independent evaluators cross-check self-reported confidence with outcome correctness and calibrated uncertainty.
- Metamorphic testing: paraphrase/perturb inputs; require invariance within tolerance.

Metrics
- Brier score / ECE for calibration; monotonicity checks for confidence vs. difficulty.
- Authenticity score composed of consistency, calibration, and invariance sub-scores with minimum thresholds.

---

## Security and Constitutional AI

Constitution
- Bind triggers to constitutional rules; violations auto-quarantine.

Adversarial Harness
- Inject prompt-injection patterns, data poisoning, cross-edge perturbations, and role-confusion attacks.
- Measure safe degradation (graceful failure) instead of silent compromise.

Drift Controls
- Versioned graphs with `evolves_to` constraints; drift threshold < 0.15 blocks deploy.

---

## CI/CD Gates and Deployment Strategy

CI Gates (merge blockers)
- Graph Integrity: all invariants pass.
- Authenticity: calibration and metamorphic tests within bounds.
- Constitutional: zero critical violations under red-team harness.
- Performance: P95 latency and error budget respected on golden traces.
- Provenance: reproducible, all hashes recorded.

Deployment
- Shadow: mirror a slice of traffic; verify equivalence using oracles.
- Canary: progressive, role-scoped rollout with auto-rollback on SLO/constitution breach.
- Feature Flags: graph version mapped in `serve/config/rollouts.yaml`.

---

## Repository Layout (Planned)

- `schemas/matriz_graph.schema.json` — Graph shape and basic constraints.
- `tools/matriz/graph_compiler.py` — Compiler from JSON/DSL → IR → runtime plan.
- `lukhas/matriz/runtime/` — Supervisor, policy engine, backpressure, SLO guards.
- `enterprise/security/redteam_matriz.py` — Adversarial triggers/topology fuzzing.
- `tests/matriz/` — Property/metamorphic tests, calibration checks, invariants.
- `serve/config/rollouts.yaml` — Shadow/canary feature flags and kill switches.

---

## 72-Hour Execution Plan (v0.1)

T0–6h: Contracts + DSL
- Author `schemas/matriz_graph.schema.json` and base invariants.
- Implement `tools/matriz/graph_compiler.py` skeleton: parse/enrich/provenance/static checks/emit plan stub.

T6–18h: Closed-Loop Kernel
- Minimal 12–24 node graph with TXT/CONTEXT/DECIDE and REFLECTIONS.
- Add metamorphic and calibration tests in `tests/matriz/`.
- Constitutional harness entry in `enterprise/security/` with basic rules.

T18–36h: Observability Budgets
- Runtime envelope scaffolding in `lukhas/matriz/runtime/` with per-edge P95 counters and drop-and-log.
- Golden traces, deterministic seeds, Datadog tags via `enterprise/observability`.

T36–54h: Shadow + Canary
- Shadow traffic path and equivalence checks via oracles.
- Canary toggles in `serve/config/rollouts.yaml`.

T54–72h: Scale + Hardening
- Scale to 40+ nodes, chaos tests for node loss and trigger delay.
- Red-team suite coverage expansion and calibration tightening.

---

## Example: Minimal Graph (Author) and Compiler Output

Author JSON (abridged):

```json
{
  "schema_version": "0.1.0",
  "graph": {
    "nodes": {
      "txt_1": {"type": "TXT", "state": {"confidence": {"min": 0, "max": 1, "value": 0.7}}},
      "dec_1": {"type": "DECIDE", "state": {"confidence": {"min": 0, "max": 1, "value": 0.6}}}
    },
    "edges": [{"from": "txt_1", "to": "dec_1", "kind": "text", "p95_budget_ms": 10}],
    "triggers": [{"name": "decide_on_text", "applies_to": ["DECIDE"], "slo": {"p95_ms": 20, "error_budget_pct": 1.0}}]
  }
}
```

Compiler Emission (runtime plan, abridged):

```json
{
  "provenance": {"git_sha": "…", "scope_hash": "sha256:…", "inputs": [{"path": "author.json", "sha256": "…"}]},
  "execution": {
    "groups": [["txt_1"], ["dec_1"]],
    "edges": [{"from": "txt_1", "to": "dec_1", "p95_budget_ms": 10, "drop_on_breach": true}]
  },
  "triggers": [{"name": "decide_on_text", "guard": "constitution_bindings", "p95_ms": 20}],
  "observability": {"trace_ids": "stable", "metrics_tags": {"graph": "demo", "version": "0.1.0"}}
}
```

---

## Commands and Validation

- Update provenance and validate schemas: `make audit-validate`
- Run performance and load tests: see `enterprise/performance/`
- Security assessment and constitutional checks: `enterprise/security/t4_security_assessment.py` and future `redteam_matriz.py`
- Observability stack: `enterprise/observability/t4_observability_stack.py`

---

## Glossary

- Invariant: A property that must always hold; violations block compilation.
- Budget: A resource limit (e.g., P95 latency) enforced at compile-time and runtime.
- Quarantine: Automatic isolation of a violating subgraph.
- Reflection: Node-native self-report that is validated for calibration.
- Oracle: Independent evaluator used to cross-validate node outputs and self-reports.

