---
status: wip
type: documentation
owner: unknown
module: matriz
redirect: false
moved_to: null
---

# AGENTS — MATRIZ Constellation Ops (T4 / 0.01%)

## Roles
- **Codex (Lead Implementer):** code changes, tests, CI wiring, promotion evidence.
- **Claude/Sonnet (Spec & Safety):** schemas, guardian DSL, red-team tests.
- **ChatGPT-5 / GPT-4:** refactors, micro-bench, CI95% stats.
- **Gemini (Observability):** Prometheus rules, label contracts, OTEL spans.
- **Grok (Chaos/Resilience):** fault injection, brownouts, rollback drills.
- **Copilot (Edit Assist):** diffs, typing, docstrings.

## Guardrails
- Fail-closed defaults; canary is the only default-ON.
- "Evidence or it didn't happen" → `artifacts/*_validation_*.json`.
- No cross-lane imports (import-linter must pass).
- Perf budgets are **hard gates** (p95; CI95% bootstrap).
- Telemetry contracts: **no dynamic IDs in labels**; IDs only in span attributes.

## PR Template
**Problem / Solution / Impact**
**Lanes touched + flags**
**Tests:** unit + integration + property + chaos
**Perf:** p50/p95/p99 + CI95% (unit vs E2E separated)
**Observability:** prom rules + tests; OTEL spans `{lane,component,operation}`; `correlation_id` **attribute only**
**Guardian:** DSL on/off proof + kill-switch drill output
**Import-linter:** ✅
**Artifacts:** list + SHA256 / merkle
