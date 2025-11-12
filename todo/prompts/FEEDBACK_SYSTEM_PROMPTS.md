# Feedback System Implementation Prompts

> **⚠️ DO NOT EXECUTE THESE PROMPTS DIRECTLY**
>
> This document contains micro-PR prompts for future task breakdown.
> Each item should be reviewed, prioritized, and added to MASTER_LOG.md before execution.

---

## Overview

This document contains **12 micro-PR prompts** for implementing the LUKHAS Feedback System.

**Priority**: High - "Ship value now" backlog
**Estimated Total**: ~50 hours
**Value Lever**: Direct user feedback loop for continuous improvement

---

## A) Feedback System — "ship value now" backlog (12 prompts)

### A1 — Feedback schema v1 + JSONL sink

**Branch**: `feat/feedback-schema-v1`
**Scope**: create `core/feedback/schema.py`, `core/feedback/sink_jsonl.py`
**Edits**:

* `FeedbackRecord` (dataclass): `user_id:str|None`, `session_id:str|None`, `source:str`, `type:str`, `payload:dict`, `severity:str='info'`, `ts:datetime`, `hash:str`
* `compute_hash(record)->str` (stable SHA256 of canonical json)
* JSONL sink: append one record per line to `$FEEDBACK_PATH` (env), auto-rotate daily

**Checks**: `python -m py_compile core/feedback/schema.py core/feedback/sink_jsonl.py`
**Commit**: `feat(feedback): schema v1 + JSONL sink with stable hashing`

---

### A2 — Feedback ingest API (internal)

**Branch**: `feat/feedback-ingest-api`
**Scope**: `serve/feedback.py` (FastAPI/Starlette or your server)
**Edits**:

* `POST /internal/feedback` accepts `FeedbackRecord` JSON; validates, redacts PII (email/phone) then writes via JSONL sink
* Require `X-Internal-Token` env-backed secret; 429 if rate limited (see A3)

**Checks**: `python -m py_compile serve/feedback.py`
**Commit**: `feat(feedback): internal ingest endpoint with PII redaction`

---

### A3 — Token-bucket rate limit for feedback

**Branch**: `feat/feedback-ratelimit`
**Scope**: `core/feedback/ratelimit.py`
**Edits**:

* Simple in-mem token bucket keyed by `(ip|user_id)`; default 60/min
* Integrate into `serve/feedback.py` returning `429` when exhausted

**Checks**: `python -m py_compile core/feedback/ratelimit.py`
**Commit**: `feat(feedback): token bucket rate limit for ingest`

---

### A4 — Source reputation tracker

**Branch**: `feat/feedback-reputation`
**Scope**: `core/feedback/reputation.py`
**Edits**:

* Maintain rolling score per `source` (e.g., `oracle`, `dream_ui`, `mesh`) with EWMA; discount noisy sources
* Helper `should_downweight(record)->bool`

**Commit**: `feat(feedback): EWMA reputation per source + downweight helper`

---

### A5 — Feedback→Directive bridge (DAST)

**Branch**: `feat/feedback-to-directive`
**Scope**: `dast/orchestrator.py`
**Edits**:

* Listen for `FeedbackRecord(type in {"bad_output","latency","safety"})`
* Update a `directive_bias` struct (e.g., `increase_grounding`, `reduce_novelty`, `boost_safety`) with decay

**Commit**: `feat(dast): route feedback into directive_bias with decay`

---

### A6 — Reward tap: `regret_signature` ↔ feedback

**Branch**: `feat/feedback-regret-tap`
**Scope**: `oneiric/core/generator.py`
**Edits**:

* After dream, if `regret_signature.valence < -0.3`, emit a `FeedbackRecord(source="oneiric", type="regret_signal")`

**Commit**: `feat(oneiric): emit regret-based feedback records`

---

### A7 — Guardian learning hints

**Branch**: `feat/feedback-guardian-hints`
**Scope**: `core/guardian/policies.py`
**Edits**:

* On veto, emit `FeedbackRecord(type="veto", payload={"reason_code":…})`; wire to sink

**Commit**: `feat(guardian): emit feedback on veto for post-hoc learning`

---

### A8 — Human-in-the-loop triage queue (local)

**Branch**: `feat/feedback-triage-queue`
**Scope**: `core/feedback/triage_queue.py`
**Edits**:

* FIFO backed by JSONL with `status: open|labeled|resolved`
* Helper functions `enqueue(record)`, `label(id,label:str)`

**Commit**: `feat(feedback): lightweight triage queue & labeling`

---

### A9 — Feedback metrics endpoint

**Branch**: `feat/feedback-metrics`
**Scope**: `serve/metrics.py`
**Edits**:

* Export counters: `feedback_total`, `feedback_veto_total`, `feedback_regret_total`, `feedback_rate_limited_total`

**Commit**: `feat(metrics): feedback counters for observability`

---

### A10 — Feedback sampling (privacy/safety)

**Branch**: `feat/feedback-sampler`
**Scope**: `core/feedback/sampler.py`
**Edits**:

* Bernoulli sampler per `type` with rates from env; never sample `payload.text` unless `ALLOW_TEXT=true`

**Commit**: `feat(feedback): per-type sampling with text guard`

---

### A11 — Feedback CLI

**Branch**: `feat/cli-feedback-tools`
**Scope**: `cli/feedback.py`
**Edits**:

* `list --type=… --since=…`, `stats`, `label <id> <tag>`

**Commit**: `feat(cli): feedback list/stats/label commands`

---

### A12 — Feedback doc (dev runbook)

**Branch**: `docs/feedback-runbook`
**Scope**: `docs/systems/FEEDBACK_SYSTEM.md`
**Edits**:

* Sequence diagram, env vars, curl examples, retention policy

**Commit**: `docs(feedback): system overview & ops runbook`

---

## Implementation Notes

### Dependencies
- A1 must be completed before A2 (schema required for API)
- A3 should be completed before A2 goes live (rate limiting)
- A4 can be done in parallel with A1-A3
- A5-A7 depend on A1 (schema) and A2 (ingest endpoint)
- A8-A12 can be done independently after A1

### Testing Strategy
- Unit tests for each component
- Integration tests for A2 (API endpoint)
- Load tests for A3 (rate limiting)
- E2E tests for feedback → directive flow (A5)

### Security Considerations
- PII redaction (A2) is CRITICAL
- Internal token authentication (A2)
- Privacy-preserving sampling (A10)
- GDPR compliance for feedback storage

### Rollout Strategy
1. **Week 1**: A1-A4 (foundation + rate limiting)
2. **Week 2**: A2 + A3 (API with protection)
3. **Week 3**: A5-A7 (integration with DAST/Guardian/Oneiric)
4. **Week 4**: A8-A12 (tooling + documentation)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Status**: Ready for task breakdown
