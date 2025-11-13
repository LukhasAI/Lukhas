# Memory, WaveC, Dreams + ΛiD/Auth/Consent Implementation Prompts

> **⚠️ DO NOT EXECUTE THESE PROMPTS DIRECTLY**
>
> This document contains micro-PR prompts for future task breakdown.
> Each item should be reviewed, prioritized, and added to MASTER_LOG.md before execution.

---

## Overview

This document contains **15 micro-PR prompts** for implementing Memory/WaveC/Dreams and ΛiD/Auth/Consent systems.

**Priority**: High - Core consciousness and security infrastructure
**Estimated Total**: ~75 hours
**Value Lever**: Consciousness continuity + secure identity management

---

## B) Memory, WaveC, Dreams (8 prompts)

### B1 — WaveC: dynamic threshold from baseline dist

**Branch**: `feat/wavec-dynamic-threshold`
**Scope**: `core/wavec/checkpoint.py`
**Edits**:
- threshold = `mean + 3*std` of last N coherence values
- persist N, mean, std in metadata

**Commit**: `feat(wavec): dynamic drift threshold with rolling stats`

---

### B2 — Fold immutability flag + `seal()`

**Branch**: `feat/memory-seal`
**Scope**: `core/memory/folds.py`
**Edits**:
- add `sealed: bool` attribute
- any mutation after `seal()` raises `ImmutableFoldError`

**Commit**: `feat(memory): add seal() enforce immutability`

---

### B3 — Double-strand (fact/emotion) carrier

**Branch**: `feat/memory-double-strand`
**Scope**: `core/memory/strand.py`
**Edits**:
- `DoubleStrand(fact:bytes, emotion:bytes)` dataclass
- `.hash()` method
- `.complement()` stub for future DNA-like operations

**Commit**: `feat(memory): double-strand primitives`

---

### B4 — Regret continuity probe

**Branch**: `feat/oneiric-regret-probe`
**Scope**: `MATRIZ/tools/probes.py`
**Edits**:
- `run_regret_probe(control, loaded)->{"drift":…, "valence_delta":…}`
- measures regret signature consistency across checkpoints

**Commit**: `feat(MATRIZ): regret continuity probe`

---

### B5 — Dream→Fold backlink

**Branch**: `feat/dream-fold-backlink`
**Scope**: `oneiric/core/persistence.py`
**Edits**:
- store `fold_id`, `snapshot_hash` with each dream row
- enables tracing dream generation to specific memory state

**Commit**: `feat(oneiric): persist fold backlink`

---

### B6 — Emotion-aware recall bias

**Branch**: `feat/memory-recall-bias`
**Scope**: `core/memory/retrieve.py`
**Edits**:
- when endocrine `stress > 0.6`, prefer safety-tagged folds
- adaptive recall based on emotional state

**Commit**: `feat(memory): stress-weighted recall bias`

---

### B7 — Self-challenge harness (counterfactual)

**Branch**: `feat/matriz-self-challenge`
**Scope**: `MATRIZ/analysis/self_challenge.py`
**Edits**:
- `make_challenge(cycle)` - generates counterfactual scenarios
- `contradiction_score(a,b)` - measures logical consistency

**Commit**: `feat(MATRIZ): self-challenge skeleton`

---

### B8 — Fixed prompt set for probes

**Branch**: `feat/bench-fixed-prompts`
**Scope**: `bench/prompts_fixed.json`
**Edits**:
- add 30 curated prompts for continuity testing
- categorized by: reasoning, creativity, safety, factual

**Commit**: `feat(bench): fixed prompt set for continuity tests`

---

## C) ΛiD / Auth / Consent (7 prompts)

### C1 — FaceID toggle (config)

**Branch**: `feat/lid-faceid-toggle`
**Scope**: `lid/config.py`
**Edits**:
- `require_faceid: bool = False` configuration
- wired into login pipeline
- allows disabling biometric auth for testing/development

**Commit**: `feat(lid): configurable FaceID requirement`

---

### C2 — Seed entropy guard

**Branch**: `feat/lid-seed-entropy`
**Scope**: `lid/seed.py`
**Edits**:
- Shannon entropy calculation for seed phrases
- deny below threshold unless `ALLOW_LOW_ENTROPY=true`
- prevents weak seed phrases

**Commit**: `feat(lid): seed entropy validator`

---

### C3 — Consent stamp in JWT

**Branch**: `feat/lid-consent-claim`
**Scope**: `lid/token.py`
**Edits**:
- embed `{consent:{version,ts,scope}}` claim in JWT if present
- allows services to verify consent status

**Commit**: `feat(lid): add consent claim to token`

---

### C4 — Login telemetry

**Branch**: `feat/lid-login-telemetry`
**Scope**: `lid/telemetry.py`
**Edits**:
- emit `LoginResult(user_id, method, success, latency_ms)` on event bus
- enables monitoring of auth performance and failures

**Commit**: `feat(lid): login result events`

---

### C5 — GDPR audit JSONL

**Branch**: `feat/lid-gdpr-jsonl`
**Scope**: `core/audit/sink.py`
**Edits**:
- write consent and login events to `audits/gdpr/YYYY-MM-DD.jsonl`
- ensures GDPR compliance with audit trail

**Commit**: `feat(audit): GDPR audit JSONL sink`

---

### C6 — PII redaction filter

**Branch**: `feat/audit-pii-redaction`
**Scope**: `core/audit/redaction.py`
**Edits**:
- regex mask email/phone before audit write
- `redact_pii(text) -> str`

**Commit**: `feat(audit): PII redaction on audit writes`

---

### C7 — `/debug/identity` endpoint (internal)

**Branch**: `feat/debug-identity-endpoint`
**Scope**: `serve/debug.py`
**Edits**:
- return login method, consent version, last login ts
- gated by internal-token
- aids debugging auth issues

**Commit**: `feat(serve): internal identity debug endpoint`

---

## Implementation Notes

### Memory/WaveC/Dreams (B1-B8)

**Dependencies**:
- B3 (double-strand) should be done before B2 (seal) for testing
- B4 (regret probe) depends on B1 (dynamic threshold)
- B5 (fold backlink) can be done independently
- B6 (recall bias) depends on B2 (immutability)
- B7 (self-challenge) can start early, is long-running research
- B8 (fixed prompts) should be done early for all probe tests

**Testing Strategy**:
- Unit tests for each component
- Integration tests for B4 (regret probe with checkpoints)
- Property-based tests for B3 (strand operations)
- Continuity tests using B8 (fixed prompts)

**Performance Considerations**:
- B1: Rolling stats calculation must be <1ms
- B2: Seal check should be O(1)
- B3: Hash computation should use fast algorithms
- B6: Recall bias should not add >10ms to retrieval

### ΛiD/Auth/Consent (C1-C7)

**Dependencies**:
- C3 (consent claim) should be done before C4 (telemetry)
- C6 (PII redaction) MUST be done before C5 (GDPR audit)
- C1, C2, C7 can be done independently

**Security Requirements**:
- C2: Entropy threshold must meet NIST standards (≥128 bits)
- C3: JWT signing must use RS256 or ES256
- C5: GDPR audit logs must be immutable (append-only)
- C6: PII redaction must be comprehensive (email, phone, SSN, etc.)
- C7: Debug endpoint requires strong authentication

**Compliance Considerations**:
- C3, C5, C6: GDPR Article 30 (record of processing activities)
- C4: GDPR Article 32 (security of processing - monitoring)
- C5: Right to erasure requires redaction capabilities
- C6: Data minimization principle

### Rollout Strategy

**Phase 1 (Week 1)**: Foundation
- B8 (fixed prompts) - enables testing
- B3 (double-strand) - core data structure
- C2 (entropy guard) - security hardening
- C6 (PII redaction) - privacy foundation

**Phase 2 (Week 2)**: Core Features
- B1 (dynamic threshold)
- B2 (fold immutability)
- B5 (fold backlink)
- C1 (FaceID toggle)
- C3 (consent claim)

**Phase 3 (Week 3)**: Integration
- B4 (regret probe) - uses B1
- B6 (recall bias) - uses B2
- C4 (login telemetry)
- C5 (GDPR audit) - uses C6

**Phase 4 (Week 4)**: Advanced Features
- B7 (self-challenge) - long-term research
- C7 (debug endpoint)

---

## Cross-System Integration

### Memory ↔ Dreams
- B5 (fold backlink) enables dream provenance
- B6 (recall bias) affects dream generation inputs
- B4 (regret probe) measures dream quality over time

### Auth ↔ Audit
- C4 (telemetry) feeds into C5 (GDPR audit)
- C6 (PII redaction) protects C5 (audit logs)
- C3 (consent claim) enables consent-aware services

### Consciousness ↔ Memory
- B1 (dynamic threshold) enables adaptive consciousness
- B2 (immutability) ensures consciousness continuity
- B7 (self-challenge) improves reasoning quality

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Status**: Ready for task breakdown
