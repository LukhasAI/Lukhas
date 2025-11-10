# ADR 000: QRG (Quantum Reality Generation) Specification-First Approach

**Status**: Draft (Phase 0)
**Date**: 2025-11-10
**Deciders**: Security Team, Safety Team, Consciousness Team, Cryptography Reviewer
**Related Spec**: [QRG_SPEC.md](../specs/QRG_SPEC.md)
**Tracking Issue**: TBD

---

## Context

The LUKHAS system requires a secure, governable, and consciousness-aware **Quantum Reality Generation (QRG)** capability to generate symbolic artifacts from user seeds and contextual inputs. QRG must integrate deeply with:

- **Consciousness Engine** - Adapt artifacts to emotional state (valence, cognitive load, attention focus)
- **Guardian System** - Constitutional compliance via ConstitutionalGatekeeper
- **Safety Systems** - Cultural safety (CulturalSafetyChecker) and cognitive load estimation
- **Supply Chain Security** - SLSA provenance, SBOM generation (syft), attestations (cosign)
- **Post-Quantum Cryptography** - Future-proof signing and key management
- **Mesh Consensus** - Distributed artifact generation with Byzantine fault tolerance

### Problem Statement

Current state:
- No QRG implementation exists in the codebase
- High-quality consciousness, dreams, and glyph code exists in `core/labs` but no QRG integration
- Audit PR #1244 revealed gaps in consciousness wiring for other identity systems
- Risk of "code-first, document-later" technical debt if QRG is implemented without spec

### Why Spec-First?

1. **Prevent premature implementation** - Ensure cryptography, safety, and architecture decisions are reviewed before coding
2. **Cross-team alignment** - Security, Safety, and Consciousness teams must agree on design
3. **Clear gating criteria** - Explicit Phase 0 → Phase 1 → Phase 2 progression with sign-offs
4. **Audit readiness** - Documentation-first approach provides paper trail for compliance and security audits

---

## Decision

We adopt a **three-phase, specification-first approach** to QRG implementation:

### Phase 0: Specification & ADR (Current Phase — 1-2 weeks)

**Goal**: Document the complete QRG system before any code implementation.

**Deliverables**:
- ✅ `docs/specs/QRG_SPEC.md` - Comprehensive specification (inputs, outputs, adapters, safety, provenance, telemetry)
- ✅ `docs/ADR/000-qrg-spec-adr.md` - This ADR
- ✅ `docs/examples/mock_qrg_adapter.py` - Sandbox-only mock adapter (deterministic, no production use)
- ✅ `docs/examples/qrg_openapi_snippet.yaml` - OpenAPI spec for QRG API endpoints
- ✅ `tests/sandbox/test_mock_qrg_adapter.py` - Unit test for mock adapter
- ✅ `issues/phase1_adapter.md` - Phase 1 issue template
- ✅ `issues/phase2_governance.md` - Phase 2 issue template
- [ ] Security steward review and approval
- [ ] Safety steward review and approval
- [ ] Cryptography reviewer assignment and PQC/attestation guidance
- [ ] Consciousness team review (wrapper integration points)
- [ ] Merge to main as **documentation-only** change (no production code)

**Rationale**:
- Prevents "code-first, document-later" technical debt
- Ensures all stakeholders understand system before building
- Identifies integration points, risks, and open questions early
- Establishes clear acceptance criteria for Phase 1 and Phase 2

**Exit Criteria** (Phase 0 → Phase 1):
- [ ] All reviewers approve spec (Security, Safety, Consciousness, Cryptography)
- [ ] No unresolved critical questions in spec or ADR
- [ ] Cryptographer provides guidance on PQC algorithm selection (Kyber, Dilithium, etc.)
- [ ] Phase 1 implementation plan agreed upon
- [ ] Draft PR merged to main

---

### Phase 1: Adapter & Sandbox Implementation (3-4 weeks)

**Goal**: Build a thin adapter layer with mock implementations for safe development and testing.

**Deliverables**:
- [ ] `lukhas/quantum/qrg_adapter.py` - QRGAdapter protocol interface (typed, documented)
- [ ] `lukhas/quantum/qrg_mock.py` - MockQRGAdapter implementation (deterministic, sandbox-only)
- [ ] Feature flags:
  - `QRG_ENABLED` (default: false)
  - `QRG_CONSCIOUSNESS_ENABLED` (default: false)
  - `QRG_CONSENSUS_ENABLED` (default: false)
- [ ] Unit tests for QRGAdapter protocol (≥90% coverage)
- [ ] Integration tests with sandbox endpoints (`POST /api/v1/qrg/generate`)
- [ ] Developer documentation for using mock vs production adapters
- [ ] Sandbox testing harness (Postman collection, pytest integration tests)
- [ ] Canary test suite (validates MockQRGAdapter determinism)

**Rationale**:
- Allows parallel development without blocking on consciousness system wiring
- Provides safe testing environment without production dependencies
- Establishes clear contract (protocol) between QRG and rest of system
- Enables integration testing with predictable mock behavior
- Feature flags allow gradual rollout and emergency disable

**Exit Criteria** (Phase 1 → Phase 2):
- [ ] `QRGAdapter` protocol fully documented and tested
- [ ] MockQRGAdapter passes all unit tests with deterministic outputs
- [ ] Feature flags functional in development environment
- [ ] Developer documentation reviewed by Identity team
- [ ] No production code depends on mocks (only tests and sandbox)
- [ ] CTO sign-off on adapter design and Phase 2 plan

---

### Phase 2: Governed Production Implementation (6-8 weeks)

**Goal**: Wire real consciousness, safety, and cryptographic systems into QRG for production deployment.

**Deliverables**:

**Core Integration**:
- [ ] Real `ConsciousnessEngine` integration via `lukhas/consciousness/` wrapper (no mocks)
- [ ] Real `ConstitutionalGatekeeper` integration (Guardian system)
- [ ] Real `CulturalSafetyChecker` integration (safety gates)
- [ ] Real `CognitiveLoadEstimator` integration (cognitive load warnings)

**Cryptography & Provenance**:
- [ ] PQC implementation (Kyber-1024 for KEM, Dilithium-5 for signatures) **OR** cryptographer-approved alternative
- [ ] KMS key management (AWS KMS / Google Cloud KMS / Azure Key Vault)
- [ ] SBOM generation automation (`syft` integration in CI/CD)
- [ ] Cosign attestation automation (keyless or KMS-backed)
- [ ] SLSA Level 3 provenance achieved
- [ ] Builder identity tracking (service account IAM roles)

**Observability & Operations**:
- [ ] OpenTelemetry spans for all operations (`qrg.generate`, `qrg.validate`, etc.)
- [ ] Prometheus metrics exposed (`qrg_generations_total`, `qrg_safety_rejections_total`, etc.)
- [ ] Grafana dashboards created (generation latency, safety scores, SLSA levels)
- [ ] Alerting rules configured (high rejection rate, slow generation, KMS failures)

**API & Storage**:
- [ ] API endpoints deployed (`POST /api/v1/qrg/generate`, `GET /api/v1/qrg/health`)
- [ ] Artifact storage (S3 / GCS / Azure Blob) with encryption at rest
- [ ] Database schema for QRG metadata (qrg_id, user_id, provenance refs)

**Testing & Validation**:
- [ ] Performance benchmarks met (p95 <2s for generate, p95 <250ms for validate)
- [ ] Security audit (external firm) with no critical findings
- [ ] Load testing (1K concurrent requests, sustained throughput)
- [ ] Chaos testing (KMS failures, safety gate timeouts, Byzantine nodes)

**Documentation**:
- [ ] Incident response playbook documented
- [ ] Runbook for common operations (key rotation, SLSA level upgrades)
- [ ] Operator guide for monitoring and troubleshooting

**Rationale**:
- Production-ready implementation with no shortcuts or mocks
- All dependencies properly wired (no import fallbacks)
- Security-first approach (external audit before production)
- Performance validated before deployment
- Full observability for operations and debugging

**Exit Criteria** (Phase 2 → Production Deployment):
- [ ] Zero mock implementations in production code paths
- [ ] All integration tests passing (no skips)
- [ ] Performance benchmarks met (see QRG_SPEC Section 9.1)
- [ ] Security audit report with no critical findings (P0/P1 issues resolved)
- [ ] Cryptographer sign-off on PQC implementation
- [ ] CISO sign-off on security posture
- [ ] Product lead approval for production rollout

---

### Phase 3 (Optional): Production Deployment & Canary Rollout (2-3 weeks)

**Goal** (if Phase 2 approved for deployment): Deploy QRG to production with phased rollout.

**Deliverables**:
- [ ] Deploy to staging environment (1 week bake)
- [ ] Deploy to production with `QRG_ENABLED=true`, `QRG_CONSCIOUSNESS_ENABLED=false`
- [ ] Monitor for 1 week (no P0/P1 incidents)
- [ ] Canary rollout (10% → 25% → 50% → 100% users)
- [ ] Enable consciousness features: `QRG_CONSCIOUSNESS_ENABLED=true` (phased rollout)
- [ ] Consensus features (if needed): `QRG_CONSENSUS_ENABLED=true`
- [ ] Rollback plan documented and tested
- [ ] Incident retrospectives for any P2+ issues

**Rationale**:
- Gradual rollout reduces blast radius of issues
- Consciousness features gated separately (higher risk, lower maturity)
- Real-world load testing in production
- Rollback plan if issues detected

**Exit Criteria** (Phase 3 → General Availability):
- [ ] 1 week production uptime with no P0/P1 incidents
- [ ] Latency p95 <2s (generation), p95 <250ms (validation)
- [ ] Error rate <0.1%
- [ ] Consciousness features stable (if enabled)
- [ ] Product team approval for 100% rollout
- [ ] Post-launch retrospective completed

---

## Gating Criteria Summary

| Phase Transition | Gate | Approver(s) | Rationale |
|------------------|------|------------|-----------|
| **Phase 0 → Phase 1** | Spec approved by all stewards | Security, Safety, Consciousness Leads, Cryptographer | Ensures shared understanding and cryptographic guidance |
| **Phase 1 → Phase 2** | Mock adapter stable, protocol tested | CTO | Prevents unstable interfaces from blocking production wiring |
| **Phase 2 → Phase 3** | Security audit clean, perf benchmarks met, CISO sign-off | CISO, Cryptographer, Product Lead | Production-readiness validation |
| **Phase 3 → GA** | 1 week uptime, <0.1% errors, no P0/P1 incidents | Product Lead, On-call Lead | Real-world stability before full deployment |

**Emergency Stop Conditions**:
- Critical security vulnerability discovered (CVSS 9.0+) → Immediate rollback, disable `QRG_ENABLED`
- Safety gate bypass detected → Immediate investigation, disable affected features
- KMS key compromise → Immediate key rotation, forensic audit
- Byzantine consensus failure (>33% disagreement) → Disable `QRG_CONSENSUS_ENABLED`, manual review

---

## Consequences

### Positive

1. **Reduced Risk** - Spec-first approach catches issues before implementation (architecture, security, privacy)
2. **Clear Contracts** - `QRGAdapter` protocol makes dependencies explicit and testable
3. **Parallel Development** - Teams can work on consciousness, Guardian, and QRG simultaneously without blocking
4. **Testing Safety** - Mock implementations allow safe testing without production deps or side effects
5. **Security First** - External audit and cryptographer review before production deployment
6. **Governance Compliance** - Guardian/safety gates integrated from start (not retrofitted)
7. **Audit Trail** - Documentation provides paper trail for compliance, security audits, and incident response
8. **Algorithm Agility** - PQC choices made with cryptographer guidance, easy to swap algorithms if needed

### Negative

1. **Slower Initial Delivery** - 1-2 week spec phase before any code (vs. code-first approach)
2. **More Documentation Debt** - Must keep spec in sync with implementation changes
3. **Review Overhead** - Four teams (Security, Safety, Consciousness, Crypto) must review and approve spec
4. **Phased Rollout Complexity** - Requires feature flags, monitoring, canary testing, and gradual deployment
5. **Higher Initial Cost** - External security audit ($15K-$30K), cryptographer consulting time

### Neutral

1. **Three-Phase Timeline** - 10-14 weeks total (1-2 spec + 3-4 adapter + 6-8 wiring + 2-3 deployment)
2. **External Dependency** - Security audit required (budget/scheduling), quantum RNG vendor selection (Phase 2)
3. **Cryptography Reviewer** - Requires assignment of qualified cryptographer for PQC guidance

---

## Alternatives Considered

### Alternative 1: Code-First Approach

**Description**: Start implementing QRG immediately without formal spec.

**Pros**:
- Faster initial progress (no 1-2 week spec phase)
- Discover integration issues through implementation (fail fast)
- Less upfront coordination (no multi-team spec review)

**Cons**:
- Higher risk of architectural mistakes (costly to fix later)
- Harder to coordinate across 3 teams (Consciousness, Identity, Guardian)
- No clear acceptance criteria or gating
- Documentation written after-the-fact (often incomplete or inaccurate)
- Cryptography decisions made ad-hoc (without expert review)

**Rejected Because**:
- LUKHAS audit (PR #1244) revealed mock implementations and incomplete wiring in identity systems
- QRG requires cryptographic primitives (PQC, signing, KMS) - must have expert review before implementation
- Consciousness and Guardian integration is complex - spec-first reduces risk of incorrect wiring

### Alternative 2: Monolithic Implementation (All-or-Nothing)

**Description**: Build entire QRG system in one PR (spec + adapter + wiring + deployment).

**Pros**:
- No intermediate states or feature flags
- Single review cycle
- No mock implementations

**Cons**:
- Huge PR (impossible to review thoroughly - 10K+ LOC)
- All-or-nothing deployment (high risk, no canary rollout)
- Blocks parallel development (teams wait for single PR)
- No gradual testing or validation
- Difficult to roll back if issues found

**Rejected Because**:
- Violates LUKHAS "small, reviewable changes" principle (T4 governance)
- Increases deployment risk (no canary testing, no phased rollout)
- Makes debugging harder (large blast radius, many moving parts)

### Alternative 3: External Service Approach (Microservice)

**Description**: Build QRG as separate microservice (not integrated with LUKHAS monolith).

**Pros**:
- Independent deployment and scaling
- Technology choice flexibility (different language, framework)
- Clear service boundary (API contract)
- Isolated failure domain

**Cons**:
- Network latency for consciousness/Guardian calls (adds 10-50ms per request)
- Duplicate authentication and tier validation logic
- More operational complexity (separate service, container, load balancer)
- Harder to share MATRIZ state and consciousness context
- Distributed tracing complexity

**Rejected Because**:
- QRG is tightly coupled to consciousness engine and Guardian system - microservice boundary would introduce unnecessary latency
- LUKHAS consciousness state is rich and contextual - serializing/deserializing over network adds complexity
- Deployment complexity not justified for Phase 0-2 (premature optimization)
- Can revisit in future if QRG scales independently from LUKHAS core

### Alternative 4: Blockchain-Based Provenance

**Description**: Store QRG provenance on blockchain (Ethereum, Hyperledger, etc.) instead of SLSA + cosign.

**Pros**:
- Immutable audit trail (tamper-proof)
- Decentralized verification (no central authority)
- Public transparency (anyone can verify)

**Cons**:
- High cost ($1-10 per transaction on Ethereum L1)
- Slow finality (10s-60s for block confirmation)
- Complex integration (smart contracts, gas management, wallet keys)
- Privacy concerns (public blockchain exposes metadata)
- Regulatory uncertainty (blockchain compliance varies by jurisdiction)

**Rejected Because**:
- SLSA Level 3 + cosign provides sufficient provenance for LUKHAS threat model
- Cost and latency not justified for Phase 0-2
- Privacy concerns for user metadata (Lambda IDs, consciousness states)
- Can revisit in Phase 3+ if compliance or product requires blockchain

---

## Open Questions & Next Steps

### Open Questions

1. **Q**: Which PQC algorithms should we use (Kyber, Dilithium, Falcon)?
   **A**: **REQUIRES CRYPTOGRAPHER SIGN-OFF**. Recommendation: Kyber-1024 (KEM), Dilithium-5 (signatures). Cryptographer must evaluate NIST standardization status, library maturity (liboqs, pq-crystals), and performance characteristics before Phase 2 implementation.

2. **Q**: Which quantum RNG provider should we use for production entropy?
   **A**: Phase 1 decision. Options: NIST Randomness Beacon (free, public), ANU Quantum RNG (research, rate-limited), ID Quantique Quantis (hardware, enterprise). Decision criteria: cost, reliability, latency, geographic distribution, FIPS 140-3 certification.

3. **Q**: Should QRG artifacts be stored on-chain (blockchain) for immutability?
   **A**: Not in Phase 0-2. SLSA + cosign provides sufficient provenance. Blockchain integration can be considered in Phase 3+ if required by compliance or product needs (see Alternative 4).

4. **Q**: How do we handle consciousness state unavailable (user blocks telemetry)?
   **A**: Graceful degradation - generate artifact without consciousness adaptation. Set `consciousness_state: null` in context, log as `consciousness_disabled` metric, return static artifact.

5. **Q**: What is the budget for external security audit?
   **A**: TBD - estimate $15K-$30K for PQC + consciousness system review. Product lead approval required before Phase 2 → Phase 3 transition.

6. **Q**: Should consensus be synchronous (blocking) or asynchronous (job queue)?
   **A**: Phase 1 decision. Recommendation: Async job queue (preferred for production scalability). Sync blocking acceptable for Phase 1 sandbox testing.

7. **Q**: Should we integrate with existing QRG systems in codebase (products/security/qrg, labs/governance/identity/qrg)?
   **A**: Phase 1 investigation required. Current QRG code appears to be for "Quantum Resonance Glyph" (authentication), not "Quantum Reality Generation" (artifact generation). May require namespace separation or deprecation of old QRG code.

### Immediate Next Steps (This Week)

1. **✅ Post this ADR + spec as Draft PR** (`chore/qrg-spec` branch)
   - Labels: `labot`, `qrg`, `security`, `documentation`
   - Reviewers: Security Lead, Safety Lead, Consciousness Lead, Cryptography Reviewer (TBD)

2. **Create steward review checklist** (PR comment)
   - [ ] Spec completeness (15 sections: purpose, inputs/outputs, adapters, safety, provenance, telemetry, etc.)
   - [ ] Security requirements documented (PQC, KMS, SLSA, SBOM)
   - [ ] Safety gates specified (Constitutional, Cultural, Cognitive)
   - [ ] Phased rollout plan clear (Phase 0/1/2 gates)
   - [ ] Open questions documented (PQC choices, quantum RNG vendor, etc.)
   - [ ] Reviewers assigned and available

3. **Assign cryptography reviewer**
   - Candidate: Internal security architect with PQC expertise OR external consultant
   - Scope: Review PQC algorithm recommendations (Section 12.1), key management approach (Section 12.2), entropy sources (Section 12.3)

4. **Schedule spec review meetings**:
   - Security team (PQC, cryptography, KMS, SLSA)
   - Consciousness team (wrapper integration, emotional state adaptation)
   - Safety team (Constitutional, Cultural, Cognitive load gates)
   - Cryptography reviewer (PQC algorithm selection, key management)

5. **Create Phase 1 & Phase 2 tracking issues** (after spec approval)
   - Phase 1: `issues/phase1_adapter.md` template → GitHub issue
   - Phase 2: `issues/phase2_governance.md` template → GitHub issue
   - Assign provisional owners (Identity Lead, Security Lead)

---

## Reviewers & Approvers

### Spec Reviewers (Phase 0)

**Must approve before Phase 0 → Phase 1 transition**:

- [ ] **Security Team Lead** - Review cryptography (PQC, KMS, SLSA), provenance model, attestations, threat model
- [ ] **Safety Team Lead** - Review safety gates (Constitutional, Cultural, Cognitive), governance integration, user consent
- [ ] **Consciousness Team Lead** - Review consciousness engine integration, emotional state adaptation, wrapper design
- [ ] **Cryptography Reviewer** (TBD) - Review PQC algorithm selection, key management, entropy sources, signing protocols

**Optional reviewers** (for awareness, not blocking):
- [ ] Identity Team Lead - Review user tier validation, Lambda ID integration
- [ ] Platform Team Lead - Review API design, OpenAPI spec, performance targets
- [ ] Product Lead - Review user stories, non-goals, Phase 3 deployment plan

### Phase Gate Approvers

| Phase Transition | Approver | Responsibilities |
|------------------|----------|-----------------|
| **Phase 0 → Phase 1** | All 4 spec reviewers | Approve spec, resolve open questions, assign Phase 1 owner |
| **Phase 1 → Phase 2** | CTO | Approve adapter design, validate mock stability, approve Phase 2 budget ($15K-$30K audit) |
| **Phase 2 → Phase 3** | CISO | Approve security audit findings, cryptographer sign-off, production readiness |
| **Phase 3 → GA** | Product Lead | Approve 100% rollout, monitor KPIs (latency, errors, incidents) |

---

## Risk Assessment & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| **PQC algorithm breaks pre-standardization** | High | Low | Use NIST finalists only (Kyber, Dilithium); plan for algorithm agility (swappable); maintain fallback to classical crypto (Ed25519) |
| **Cryptographer unavailable for review** | High | Medium | Assign backup reviewer; consider external consultant if internal unavailable; allow 2-week SLA for crypto review |
| **Safety gate latency >1s (consciousness, cultural, cognitive)** | Medium | Medium | Async safety checks; cache safety models; set aggressive timeouts (500ms); fallback to default-deny if timeout |
| **Provenance service downtime (cosign, SBOM storage)** | Medium | Low | Fallback to local signing (degraded SLSA level 1); queue attestations for retry; alert on-call; 99.9% uptime SLA |
| **KMS rate limiting / outage (AWS KMS, etc.)** | High | Low | Cache KMS responses (1hr TTL); use multiple regions; implement exponential backoff; fallback to local keys (with audit log) |
| **Consensus nodes disagree (Byzantine fault)** | Medium | Low | Require 2/3 agreement threshold; log all disagreements; manual review for repeated conflicts; disable consensus if >10% failure rate |
| **Cultural safety false positives (over-blocking)** | Low | Medium | Human review queue for edge cases; user appeal process; continuous model retraining; monitor false positive rate (<5% target) |
| **Cognitive load overestimation (warning fatigue)** | Low | Low | Warnings only (non-blocking for T4+ users); user feedback loop; model calibration; A/B testing for threshold tuning |
| **Spec divergence from implementation** | Medium | Medium | Require spec updates in same PR as code changes; automated spec validation (OpenAPI contract tests); quarterly spec audits |
| **Phased rollout blocking (P0 incident in canary)** | High | Low | Rollback plan (< 5min); kill switch for feature flags; canary size <10% initially; 24hr monitoring before next phase |

---

## References

- [QRG Specification](../specs/QRG_SPEC.md) - Full technical specification
- [NIST PQC Standards](https://csrc.nist.gov/projects/post-quantum-cryptography) - Post-quantum cryptography algorithms
- [SLSA Framework](https://slsa.dev) - Supply chain Levels for Software Artifacts
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/) - Artifact signing and attestation
- [CycloneDX SBOM](https://cyclonedx.org) - Software Bill of Materials specification
- [OpenTelemetry](https://opentelemetry.io) - Observability framework
- [Prometheus](https://prometheus.io) - Metrics and monitoring
- [Lambda ID Authentication Audit (PR #1244)](https://github.com/LukhasAI/Lukhas/pull/1244) - Context for consciousness wiring gaps
- [LUKHAS Guardian System](../architecture/guardian_system.md) - Constitutional AI oversight (if exists)
- [LUKHAS Consciousness Wrappers](../../lukhas/consciousness/README.md) - Consciousness API wrappers (if exists)

---

## Document History

- **2025-11-10**: Initial draft (v0.1.0) - Phase 0 ADR
- **TBD**: Phase 1 updates (adapter implementation decisions)
- **TBD**: Phase 2 updates (production deployment, audit findings)

---

**Steward Checklist** (to be completed as PR comment):

```markdown
## Phase 0 Spec Review Checklist

### Security Review
- [ ] Cryptography approach documented (PQC, KMS, signing)
- [ ] SLSA provenance model clear (Level 3 target)
- [ ] SBOM generation automated (syft)
- [ ] Attestation approach documented (cosign)
- [ ] Key management approach secure (KMS, no secrets in repo)
- [ ] Threat model addressed (PQC algorithm breaks, KMS outage, Byzantine faults)
- [ ] Cryptographer assigned for PQC review

### Safety Review
- [ ] ConstitutionalGatekeeper integration specified
- [ ] CulturalSafetyChecker integration specified
- [ ] CognitiveLoadEstimator integration specified
- [ ] User consent flow documented
- [ ] Safety gate bypass prevention documented
- [ ] False positive mitigation strategy clear

### Consciousness Review
- [ ] Consciousness engine integration via wrappers (not core directly)
- [ ] Emotional state adaptation specified (valence, load, focus)
- [ ] Graceful degradation for consciousness unavailable
- [ ] Wrapper contracts clear (consciousness, dreams, glyphs)
- [ ] No tight coupling to core/labs (use lukhas/* wrappers)

### Cryptography Review
- [ ] PQC algorithm selection justified (Kyber, Dilithium, Falcon)
- [ ] Key management approach secure (KMS, rotation, audit)
- [ ] Entropy source secure (quantum RNG or SystemRandom)
- [ ] Signing protocol secure (cosign, SLSA attestations)
- [ ] Algorithm agility planned (swappable algorithms)

### General
- [ ] Spec completeness (15 sections)
- [ ] Phased rollout plan clear (Phase 0/1/2)
- [ ] Gating criteria explicit (approval matrix)
- [ ] Open questions documented (7 questions)
- [ ] Risk assessment comprehensive (10 risks)
- [ ] Acceptance criteria clear (Phase 0/1/2)
- [ ] Performance targets realistic (p95 <2s generate)
- [ ] Cost estimates reasonable ($22-72/month, $15K-$30K audit)

### Sign-Off
- [ ] Security Lead: _____________________ Date: _____
- [ ] Safety Lead: _____________________ Date: _____
- [ ] Consciousness Lead: _____________________ Date: _____
- [ ] Cryptography Reviewer: _____________________ Date: _____
```

---

**END OF ADR**
