# Phase 2: QRG Governed Production Implementation

**Status**: Ready for assignment (after Phase 1 completion)
**Depends on**: Phase 1 completion (adapter protocol + mock implementation)
**Related Spec**: [QRG_SPEC.md](../docs/specs/QRG_SPEC.md)
**Related ADR**: [000-qrg-spec-adr.md](../docs/ADR/000-qrg-spec-adr.md)
**Estimated Duration**: 6-8 weeks
**Owner**: TBD (Security Lead + Identity Lead)

---

## Overview

Implement production-ready QRG system with real consciousness engine integration, safety gates, cryptographic provenance (SLSA, SBOM, cosign), and PQC signing. This phase transitions from sandbox mocks to governed production implementation with full observability, security audit, and performance validation.

**⚠️ CRITICAL**: Phase 2 requires cryptographer sign-off before implementation begins. PQC algorithm choices and key management approach must be reviewed and approved.

---

## Goals

1. **Wire Real Dependencies** - Consciousness, Guardian, Safety systems (no mocks)
2. **Implement Cryptographic Provenance** - SLSA Level 3, SBOM, cosign attestations
3. **Deploy PQC Signing** - Kyber-1024 + Dilithium-5 (or cryptographer-approved alternatives)
4. **Full Observability** - OTEL spans, Prometheus metrics, Grafana dashboards
5. **Security Audit** - External firm review with zero critical findings
6. **Performance Validation** - p95 <2s generate, p95 <250ms validate

---

## Deliverables

### 1. Core System Integration

#### 1.1 Consciousness Engine Integration

**File**: `lukhas/quantum/qrg_consciousness.py`

**Integration Points**:
- `lukhas/consciousness/` wrapper (NOT core directly)
- Adapt artifact generation to emotional state (valence, load, focus)
- Graceful degradation if consciousness unavailable (`QRG_CONSCIOUSNESS_ENABLED=false`)

**Acceptance Criteria**:
- [ ] Uses `lukhas/consciousness/` wrapper (no direct core imports)
- [ ] Adapts symbolic tokens based on emotional valence
- [ ] Adapts affect vector based on cognitive load and attention focus
- [ ] Graceful degradation if consciousness service unavailable
- [ ] Logs consciousness state usage for telemetry
- [ ] Respects `QRG_CONSCIOUSNESS_ENABLED` feature flag

---

#### 1.2 Guardian System Integration

**File**: `lukhas/quantum/qrg_guardian.py`

**Integration Points**:
- `core.interfaces.as_agent.core.gatekeeper.ConstitutionalGatekeeper`
- Block artifact generation if constitutional violation detected
- Enforce user consent and tier validation

**Acceptance Criteria**:
- [ ] Calls ConstitutionalGatekeeper before artifact generation
- [ ] Raises QRGSafetyRejection if approval denied
- [ ] Logs rejection reasons for audit trail
- [ ] Enforces user consent (checks consent flags)
- [ ] Enforces tier validation (T4+ for advanced features)
- [ ] Timeout protection (500ms max, fallback to deny)

---

#### 1.3 Cultural Safety Integration

**File**: `lukhas/quantum/qrg_safety.py`

**Integration Points**:
- `utils.cultural_safety_checker.CulturalSafetyChecker`
- Validate symbolic tokens and affect vectors
- Check cultural context (languages, regions, accessibility)

**Acceptance Criteria**:
- [ ] Calls CulturalSafetyChecker after artifact generation
- [ ] Rejects if safety score <0.85
- [ ] Logs safety scores for monitoring
- [ ] Supports cultural context (languages, regions)
- [ ] Timeout protection (500ms max, fallback to deny)

---

#### 1.4 Cognitive Load Integration

**File**: `lukhas/quantum/qrg_cognitive.py`

**Integration Points**:
- `utils.cognitive_load_estimator.CognitiveLoadEstimator`
- Estimate artifact complexity vs user state
- Warn (but don't block) if load >0.8

**Acceptance Criteria**:
- [ ] Calls CognitiveLoadEstimator after artifact generation
- [ ] Estimates load based on token count + affect dimensionality
- [ ] Warns if load >0.8 (non-blocking for T4+ users)
- [ ] Logs load estimates for telemetry
- [ ] Timeout protection (500ms max, fallback to no warning)

---

### 2. Cryptography & Provenance

#### 2.1 Post-Quantum Cryptography Implementation

**⚠️ REQUIRES CRYPTOGRAPHER APPROVAL BEFORE IMPLEMENTATION**

**Files**:
- `lukhas/quantum/crypto/pqc_signing.py`
- `lukhas/quantum/crypto/key_management.py`

**Algorithms** (pending cryptographer approval):
- **Signatures**: Dilithium-5 (ML-DSA) or Falcon-1024
- **Key Encapsulation**: Kyber-1024 (ML-KEM)
- **Hashing**: SHA3-256 or BLAKE3
- **Fallback**: Ed25519 (if PQC not yet deployed)

**Libraries** (pending cryptographer approval):
- liboqs (Open Quantum Safe)
- pq-crystals (NIST PQC finalists)
- cryptography (Python standard library)

**Acceptance Criteria**:
- [ ] **Cryptographer sign-off** on algorithm selection
- [ ] **Cryptographer sign-off** on library selection (audit status, maturity)
- [ ] Signing keys stored in KMS (AWS KMS / GCP KMS / Azure Key Vault)
- [ ] No private keys in repository or environment variables
- [ ] Key rotation plan documented (quarterly rotation)
- [ ] Algorithm agility: easy to swap algorithms if NIST standards change
- [ ] Fallback to Ed25519 if PQC unavailable (with degraded SLSA level)

---

#### 2.2 SBOM Generation

**Tool**: `syft` (Anchore)

**Integration Point**: CI/CD pipeline (GitHub Actions / GitLab CI)

**Workflow**:
```bash
# Generate SBOM during build
syft packages dir:/path/to/qrg-service -o cyclonedx-json > qrg-service.sbom.json

# Upload SBOM to artifact storage
aws s3 cp qrg-service.sbom.json s3://lukhas-qrg-sboms/$(git rev-parse HEAD).cdx.json

# Reference SBOM in QRGResponse provenance.sbom_ref
```

**Acceptance Criteria**:
- [ ] SBOM generation automated in CI/CD
- [ ] SBOM format: CycloneDX JSON (preferred) or SPDX
- [ ] SBOM includes all Python dependencies (requirements.txt / pyproject.toml)
- [ ] SBOM includes system libraries (if containerized)
- [ ] SBOM uploaded to artifact storage (S3 / GCS / Azure Blob)
- [ ] SBOM ref included in QRGResponse provenance block
- [ ] SBOM retention policy: 90 days (configurable)

---

#### 2.3 Cosign Attestation

**Tool**: `cosign` (Sigstore)

**Integration Point**: CI/CD pipeline (GitHub Actions / GitLab CI)

**Workflow**:
```bash
# Sign artifact metadata using cosign (KMS-backed)
cosign sign-blob --key kms://aws-kms/key-id artifact-metadata.json > artifact.sig

# Generate attestation bundle
cosign attest --key kms://aws-kms/key-id --predicate artifact-metadata.json

# Upload attestation
aws s3 cp attestation.att s3://lukhas-qrg-attestations/$(qrg_id).att
```

**Acceptance Criteria**:
- [ ] Cosign attestation automated in CI/CD
- [ ] Signing keys stored in KMS (no keyless signing for production)
- [ ] Attestation format: in-toto predicate
- [ ] Attestation uploaded to artifact storage
- [ ] Attestation ref included in QRGResponse provenance block
- [ ] Verification script documented (`cosign verify-blob`)

---

#### 2.4 SLSA Level 3 Provenance

**Goal**: Achieve SLSA Level 3 provenance for QRG artifacts

**Requirements**:
- **Build service**: Use ephemeral environment (GitHub Actions hosted runners)
- **Provenance generation**: slsa-github-generator action
- **Verification**: slsa-verifier CLI

**Acceptance Criteria**:
- [ ] SLSA Level 3 provenance achieved (verified with slsa-verifier)
- [ ] Provenance includes builder identity (GitHub Actions OIDC)
- [ ] Provenance includes build parameters (commit SHA, branch, workflow ID)
- [ ] Provenance signed with Sigstore keyless signing
- [ ] Provenance uploaded to rekor transparency log (optional)
- [ ] SLSA level recorded in QRGResponse provenance block

---

### 3. Observability & Monitoring

#### 3.1 OpenTelemetry Spans

**File**: `lukhas/quantum/qrg_telemetry.py`

**Span Names**:
- `qrg.generate` - Full artifact generation
- `qrg.generate.artifact` - Artifact generation only
- `qrg.generate.safety_checks` - Safety gate checks
- `qrg.generate.provenance` - Provenance creation
- `qrg.validate` - Artifact validation

**Attributes**:
- `qrg.user_id`, `qrg.seed` (truncated), `qrg.tier_level`, `qrg.entropy_source`, `qrg.qrg_id`, `qrg.total_time_ms`, `qrg.safety.status`

**Acceptance Criteria**:
- [ ] All operations emit OTEL spans
- [ ] Spans include timing metrics
- [ ] Spans linked to parent traces (distributed tracing)
- [ ] Span attributes follow semantic conventions
- [ ] Traces visible in OTEL collector (Jaeger / Zipkin / Datadog)

---

#### 3.2 Prometheus Metrics

**File**: `lukhas/quantum/qrg_metrics.py`

**Metrics**:
```python
qrg_generations_total = Counter("qrg_generations_total", ["tier_level", "entropy_source", "status"])
qrg_generation_duration_seconds = Histogram("qrg_generation_duration_seconds", ["tier_level"])
qrg_safety_rejections_total = Counter("qrg_safety_rejections_total", ["gate_type", "reason"])
qrg_safety_score = Histogram("qrg_safety_score", ["gate_type"])
qrg_provenance_slsa_level = Gauge("qrg_provenance_slsa_level", ["qrg_id"])
qrg_signature_verifications_total = Counter("qrg_signature_verifications_total", ["status"])
qrg_cognitive_load = Histogram("qrg_cognitive_load", ["tier_level"])
```

**Acceptance Criteria**:
- [ ] All operations emit Prometheus metrics
- [ ] Metrics exposed on `/metrics` endpoint
- [ ] Metrics scraped by Prometheus server
- [ ] Metric labels follow naming conventions
- [ ] Histograms use appropriate buckets (see QRG_SPEC Section 8.2)

---

#### 3.3 Grafana Dashboards

**File**: `monitoring/grafana/qrg_dashboard.json`

**Panels**:
- Generation rate (req/min)
- Generation latency (p50, p95, p99)
- Safety rejection rate (by gate type)
- Safety scores (by gate type)
- SLSA levels (distribution)
- Error rate (4xx, 5xx)
- Cognitive load (distribution)

**Acceptance Criteria**:
- [ ] Dashboard JSON committed to repo
- [ ] Dashboard imported to Grafana
- [ ] All metrics visible and updating
- [ ] Alerts configured (see Section 3.4)

---

#### 3.4 Alerting Rules

**File**: `monitoring/prometheus/qrg_alerts.yml`

**Alerts**:
- QRGHighRejectionRate (>10% rejection rate for 10min)
- QRGSlowGeneration (p95 >5s for 5min)
- QRGKMSFailure (KMS errors >5 in 1min)
- QRGSafetyGateDown (safety gate unavailable for 2min)

**Acceptance Criteria**:
- [ ] Alert rules loaded in Prometheus
- [ ] Alerts trigger correctly (test in staging)
- [ ] Alerts routed to PagerDuty / Slack / email
- [ ] Runbook links included in alert annotations

---

### 4. API & Storage

#### 4.1 Production Endpoints

**File**: `serve/routes/qrg.py` (replace sandbox with production adapter)

**Endpoints**:
- `POST /api/v1/qrg/generate` → ProductionQRGAdapter.generate()
- `GET /api/v1/qrg/health` → ProductionQRGAdapter.health()

**Behavior**:
- Feature flag gated (`QRG_ENABLED`, `QRG_CONSCIOUSNESS_ENABLED`, `QRG_CONSENSUS_ENABLED`)
- Authentication required (Lambda ID JWT)
- Rate limiting enforced (10 req/min for T4 users)
- CORS enabled for web clients
- Request/response logging (audit trail)

**Acceptance Criteria**:
- [ ] Endpoints use ProductionQRGAdapter (not MockQRGAdapter)
- [ ] Feature flags respected (404 when disabled)
- [ ] Authentication enforced (401 if missing/invalid)
- [ ] Rate limiting enforced (429 after limit exceeded)
- [ ] Audit logs written to secure storage
- [ ] Contract tests pass (OpenAPI spec matches implementation)

---

#### 4.2 Artifact Storage

**Service**: AWS S3 / Google Cloud Storage / Azure Blob Storage

**Bucket Structure**:
```
lukhas-qrg-artifacts/
├── artifacts/
│   └── {qrg_id}.json
├── sboms/
│   └── {build_id}.cdx.json
└── attestations/
    └── {qrg_id}.att
```

**Acceptance Criteria**:
- [ ] Bucket created with encryption at rest (AES-256 or KMS)
- [ ] Lifecycle policy: delete after 90 days (configurable)
- [ ] Access control: service account only (no public access)
- [ ] Versioning enabled (for audit trail)
- [ ] CloudWatch / Cloud Logging enabled

---

### 5. Testing & Validation

#### 5.1 Performance Benchmarks

**File**: `tests/performance/quantum/test_qrg_performance.py`

**Targets** (from QRG_SPEC Section 9.1):
- Generate p50 <500ms, p95 <2s, p99 <5s
- Validate p50 <100ms, p95 <250ms, p99 <500ms
- Health check p50 <50ms, p95 <100ms, p99 <200ms

**Tool**: locust or pytest-benchmark

**Acceptance Criteria**:
- [ ] All latency targets met (p95 thresholds)
- [ ] Load testing: 1K concurrent requests, sustained throughput
- [ ] Performance report generated (HTML or PDF)
- [ ] Baseline established for regression detection

---

#### 5.2 Security Audit

**External Firm**: TBD (budget: $15K-$30K)

**Scope**:
- PQC implementation review (Kyber, Dilithium, key management)
- Provenance model (SLSA, SBOM, cosign)
- Safety gate integration (ConstitutionalGatekeeper, CulturalSafetyChecker)
- Consciousness engine integration (data privacy, consent)
- API security (authentication, authorization, rate limiting)

**Acceptance Criteria**:
- [ ] Audit firm selected and contracted
- [ ] Audit scope agreed upon
- [ ] Audit report delivered with no P0/P1 findings
- [ ] P2+ findings addressed or accepted as risk
- [ ] CISO sign-off on audit results

---

#### 5.3 Chaos Testing

**File**: `tests/chaos/quantum/test_qrg_chaos.py`

**Scenarios**:
- KMS unavailable (test fallback to local keys with audit)
- Safety gate timeout (test fallback to deny)
- Consciousness engine unavailable (test graceful degradation)
- Storage service unavailable (test queued retries)
- Byzantine consensus failure (test 2/3 agreement threshold)

**Tool**: chaos-mesh or pytest with mock failures

**Acceptance Criteria**:
- [ ] All chaos scenarios tested
- [ ] Graceful degradation verified (no crashes)
- [ ] Alerts triggered correctly
- [ ] Runbook tested for each scenario

---

### 6. Documentation

#### 6.1 Incident Response Playbook

**File**: `docs/operations/qrg_incident_playbook.md`

**Contents**:
- Critical incident scenarios (KMS compromise, safety gate bypass, PQC break)
- Escalation paths (on-call → security team → CISO)
- Rollback procedures (disable feature flags, revert deploy)
- Forensic investigation steps
- Communication templates (status page, incident reports)

**Acceptance Criteria**:
- [ ] Playbook covers ≥5 critical scenarios
- [ ] Escalation paths clear (names, Slack channels, PagerDuty)
- [ ] Rollback tested in staging
- [ ] Reviewed by Security Lead and On-call Lead

---

#### 6.2 Operations Runbook

**File**: `docs/operations/qrg_runbook.md`

**Contents**:
- Common operations (key rotation, SLSA level upgrade, feature flag toggle)
- Troubleshooting guides (high rejection rate, slow generation, KMS errors)
- Monitoring dashboard links
- Log query examples (CloudWatch Insights, Datadog APM)

**Acceptance Criteria**:
- [ ] Runbook covers ≥10 common operations
- [ ] Troubleshooting guides tested (reproduce issue, follow guide, verify fix)
- [ ] Dashboard links validated
- [ ] Reviewed by Platform Team Lead

---

## Acceptance Criteria (Phase 2 → Phase 3 Gate)

**Must complete before Phase 3 (production deployment) starts:**

- [ ] **Zero mock implementations** in production code paths
- [ ] **All integration tests passing** (no skips)
- [ ] **Performance benchmarks met** (p95 <2s generate, p95 <250ms validate)
- [ ] **Security audit clean** (no P0/P1 findings)
- [ ] **Cryptographer sign-off** on PQC implementation
- [ ] **CISO sign-off** on security posture
- [ ] **SLSA Level 3** provenance achieved
- [ ] **All safety gates operational** (Constitutional, Cultural, Cognitive)
- [ ] **OTEL spans** emitted for all operations
- [ ] **Prometheus metrics** exposed and dashboards created
- [ ] **Incident response playbook** documented and tested
- [ ] **Product lead approval** for production rollout

---

## Non-Goals (Phase 2)

**DO NOT implement in Phase 2:**

- ❌ Production deployment (happens in Phase 3)
- ❌ Canary rollout (happens in Phase 3)
- ❌ User-facing UI/UX
- ❌ Blockchain-based provenance (use SLSA + cosign)
- ❌ Real-time quantum RNG (use pseudo-RNG with quantum fallback)
- ❌ Multi-region deployment (single region for Phase 2)

---

## Dependencies

**Before Phase 2 starts:**
- [ ] Phase 1 completion (adapter protocol + mock implementation)
- [ ] CTO sign-off on Phase 1 → Phase 2 transition
- [ ] **Cryptographer assigned** and available for PQC review
- [ ] Budget approved for security audit ($15K-$30K)

**During Phase 2:**
- Access to staging environment
- KMS service (AWS KMS / GCP KMS / Azure Key Vault)
- Artifact storage (S3 / GCS / Azure Blob)
- OTEL collector (Jaeger / Zipkin / Datadog)
- Prometheus + Grafana
- External security audit firm

---

## Timeline

**Estimated Duration**: 6-8 weeks

**Week 1-2: Core Integration**
- [ ] Consciousness engine integration
- [ ] Guardian system integration
- [ ] Cultural safety integration
- [ ] Cognitive load integration

**Week 3-4: Cryptography & Provenance**
- [ ] PQC implementation (with cryptographer review)
- [ ] SBOM generation automation
- [ ] Cosign attestation automation
- [ ] SLSA Level 3 provenance

**Week 5: Observability**
- [ ] OTEL spans implementation
- [ ] Prometheus metrics implementation
- [ ] Grafana dashboards
- [ ] Alerting rules

**Week 6: Testing**
- [ ] Performance benchmarks
- [ ] Chaos testing
- [ ] Security audit kickoff

**Week 7-8: Documentation & Audit**
- [ ] Incident response playbook
- [ ] Operations runbook
- [ ] Security audit completion
- [ ] CISO sign-off

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **PQC library immature** | High | Cryptographer evaluates library audit status; fallback to Ed25519 if PQC not ready |
| **Security audit finds P0 issue** | High | Allocate 2-week buffer for audit remediation; delay Phase 3 if needed |
| **KMS rate limiting** | Medium | Cache KMS responses; use multiple regions; exponential backoff |
| **Safety gate latency >1s** | Medium | Async safety checks; aggressive timeouts; fallback to deny |
| **Performance benchmarks not met** | Medium | Profile slow operations; optimize or adjust targets (requires ADR update) |
| **Consciousness engine unavailable** | Low | Graceful degradation; disable `QRG_CONSCIOUSNESS_ENABLED` flag |

---

## Exit Criteria Summary

**Phase 2 is complete when:**

1. All deliverables merged to main branch
2. All tests passing (unit + integration + performance + chaos)
3. Security audit completed with no P0/P1 findings
4. Cryptographer sign-off obtained
5. CISO sign-off obtained
6. Product lead approval for Phase 3 deployment

**After Phase 2 completion:**

→ Proceed to Phase 3: Production Deployment & Canary Rollout

---

## Related Issues

- [ ] Phase 1 Adapter Implementation (prerequisite)
- [ ] Phase 3 Production Deployment (successor)

---

**Owner**: TBD (Security Lead + Identity Lead)
**Reviewers**: Security Lead, Cryptographer, Safety Lead, Consciousness Lead
**Approvers**: CISO (for Phase 2 → Phase 3 transition), Cryptographer (for PQC sign-off)

---

**Created**: 2025-11-10
**Last Updated**: 2025-11-10
