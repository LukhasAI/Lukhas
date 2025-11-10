# QRG (Quantum Resonance Glyph) Specification

**Status**: Draft
**Version**: 0.1.0
**Authors**: LUKHAS Identity Team
**Date**: 2025-11-10
**Related ADR**: [000-qrg-spec-adr.md](../adr/000-qrg-spec-adr.md)
**Tracking Issue**: #1253

---

## 1. Purpose & Motivation

Quantum Resonance Glyphs (QRG) are consciousness-aware, quantum-resistant authentication tokens designed to:

1. **Adapt to user emotional state** - Modify visual appearance based on consciousness signals
2. **Resist quantum attacks** - Use post-quantum cryptography (PQC) primitives
3. **Embed identity steganographically** - Hide user identity data within glyph imagery
4. **Validate cultural safety** - Ensure glyphs are appropriate across cultures and contexts
5. **Integrate with Guardian system** - Constitutional AI oversight for ethical usage

QRG extends traditional authentication tokens by making them **consciousness-native** - they respond to user state, adapt over time, and serve as both authentication credential and user-facing artifact.

---

## 2. User Stories

**US-1**: As a **T4 user**, I want to **register a QRG** so that I can authenticate with a consciousness-aware glyph instead of passwords.

**US-2**: As a **system administrator**, I want to **validate QRG cultural safety** so that no offensive or culturally inappropriate glyphs are generated.

**US-3**: As a **consciousness researcher**, I want to **track QRG adaptation over time** so that I can study how glyphs respond to emotional state changes.

**US-4**: As a **security auditor**, I want to **verify QRG quantum resistance** so that I can certify the system is PQC-compliant.

**US-5**: As a **Guardian system**, I want to **gate QRG generation** so that constitutional compliance is enforced before credential issuance.

---

## 3. Inputs & Outputs

### 3.1 Generate QRG (Registration)

**Input**:
```python
{
    "user_id": "lid:abc123...",
    "consciousness_state": {
        "emotional_valence": 0.7,      # [-1.0, 1.0] negative to positive
        "cognitive_load": 0.3,          # [0.0, 1.0] low to high
        "attention_focus": 0.8          # [0.0, 1.0] distracted to focused
    },
    "cultural_context": {
        "languages": ["en", "es"],
        "regions": ["US", "MX"],
        "accessibility_needs": ["high_contrast"]
    },
    "tier_level": 4,
    "entropy_source": "quantum_rng"  # or "pseudo_rng" for dev
}
```

**Output**:
```python
{
    "qrg_id": "qrg:xyz789...",
    "image_url": "https://lukhas.ai/qrg/xyz789.png",
    "image_b64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "public_key": "pqc:kyber1024:...",
    "metadata": {
        "generated_at": "2025-11-10T12:34:56Z",
        "consciousness_snapshot": {...},
        "cultural_safety_score": 0.95,
        "guardian_approved": true
    },
    "embedded_data_hash": "sha3-256:...",  # Hash of steganographic payload
    "expiry": "2026-11-10T12:34:56Z"
}
```

### 3.2 Authenticate with QRG

**Input**:
```python
{
    "qrg_id": "qrg:xyz789...",
    "challenge": "base64_challenge_from_server",
    "signature": "pqc:dilithium:base64_sig",
    "consciousness_state": {
        "emotional_valence": 0.6,
        "cognitive_load": 0.4,
        "attention_focus": 0.7
    }
}
```

**Output**:
```python
{
    "authenticated": true,
    "user_id": "lid:abc123...",
    "tier_level": 4,
    "consciousness_match_score": 0.87,  # How well current state matches registration
    "session_token": "jwt_token_here",
    "warnings": []  # e.g., ["consciousness_drift_detected"]
}
```

---

## 4. API Adapter Interface

QRG system must expose a **thin adapter interface** to isolate core implementation from production lanes:

```python
# lukhas/identity/qrg_adapter.py

from typing import Any, Protocol

class QRGAdapter(Protocol):
    """Protocol for QRG system integration."""

    async def generate_qrg(
        self,
        user_id: str,
        consciousness_state: dict[str, float],
        cultural_context: dict[str, Any],
        tier_level: int,
        entropy_source: str = "quantum_rng"
    ) -> dict[str, Any]:
        """Generate a new QRG for user registration."""
        ...

    async def authenticate_qrg(
        self,
        qrg_id: str,
        challenge: str,
        signature: str,
        consciousness_state: dict[str, float]
    ) -> dict[str, Any]:
        """Authenticate user with QRG credential."""
        ...

    async def revoke_qrg(
        self,
        user_id: str,
        qrg_id: str,
        reason: str
    ) -> dict[str, bool]:
        """Revoke a QRG credential."""
        ...

    async def list_user_qrgs(
        self,
        user_id: str
    ) -> dict[str, Any]:
        """List all QRGs for a user."""
        ...
```

**Configuration**:
```python
# Environment-based feature flag
QRG_ENABLED = os.environ.get("QRG_ENABLED", "false").lower() == "true"
QRG_CONSCIOUSNESS_ENABLED = os.environ.get("QRG_CONSCIOUSNESS_ENABLED", "false").lower() == "true"

# Conditional import with graceful degradation
if QRG_ENABLED:
    try:
        from core.governance.identity.qrg_integration import LUKHASQRGManager
        _qrg_manager = LUKHASQRGManager()
    except ImportError:
        _qrg_manager = None  # Fall back to mock or disabled state
```

---

## 5. Governance & Safety Requirements

### 5.1 Constitutional Gatekeeper Integration

**Requirement**: All QRG generation MUST pass Guardian constitutional validation before credential issuance.

```python
from core.interfaces.as_agent.core.gatekeeper import ConstitutionalGatekeeper

gatekeeper = ConstitutionalGatekeeper()

# Before generating QRG
approval = await gatekeeper.validate_action(
    action="generate_qrg",
    context={
        "user_id": user_id,
        "tier_level": tier_level,
        "consciousness_state": consciousness_state
    }
)

if not approval.get("approved", False):
    raise ValueError(f"Guardian rejected QRG generation: {approval.get('reason')}")
```

### 5.2 Cultural Safety Validation

**Requirement**: All QRG imagery MUST pass cultural safety checks before presentation to users.

```python
from utils.cultural_safety_checker import CulturalSafetyChecker

safety_checker = CulturalSafetyChecker()

# After generating glyph image
safety_result = await safety_checker.validate_image(
    image_data=glyph_image,
    cultural_context=cultural_context
)

if safety_result.get("safety_score", 0) < 0.85:
    # Reject and regenerate with different parameters
    raise ValueError(f"Cultural safety score too low: {safety_result}")
```

### 5.3 Consciousness Engine Integration

**Requirement**: Consciousness adaptation MUST be optional and feature-flagged.

```python
from consciousness.core_consciousness.consciousness_engine import ConsciousnessEngine

# Only use if consciousness features enabled
if QRG_CONSCIOUSNESS_ENABLED:
    consciousness_engine = ConsciousnessEngine()
    adapted_params = await consciousness_engine.adapt_glyph_parameters(
        base_params=default_params,
        emotional_state=consciousness_state
    )
else:
    adapted_params = default_params  # No consciousness adaptation
```

---

## 6. Cryptography & PQC Requirements

### 6.1 Post-Quantum Algorithms

**Requirement**: QRG MUST use NIST-approved PQC algorithms:

- **Key Encapsulation**: Kyber-1024 (ML-KEM)
- **Digital Signatures**: Dilithium-5 (ML-DSA)
- **Entropy Source**: Quantum RNG or cryptographically secure PRNG

**Implementation**:
```python
from cryptography.hazmat.primitives.asymmetric import kyber, dilithium

# Generate PQC key pair for QRG
private_key = kyber.Kyber1024PrivateKey.generate()
public_key = private_key.public_key()

# Sign QRG metadata
signature_key = dilithium.Dilithium5PrivateKey.generate()
signature = signature_key.sign(qrg_metadata_bytes)
```

### 6.2 Quantum Entropy

**Requirement**: Production QRG MUST use quantum entropy source for key generation.

**Options**:
1. **NIST Randomness Beacon** (free, public)
2. **ANU Quantum RNG API** (research, rate-limited)
3. **ID Quantique Quantis** (hardware, enterprise)

**Fallback**: For development/testing, use `secrets.SystemRandom()` with clear logging.

### 6.3 SLSA Provenance

**Requirement**: All PQC dependencies MUST have SLSA Level 2+ provenance.

```bash
# Example: Verify cryptography package provenance
pip install --require-hashes cryptography==41.0.5
```

---

## 7. Performance & Cost Estimates

### 7.1 Latency Budget

| Operation | Target | Stretch | Notes |
|-----------|--------|---------|-------|
| Generate QRG | <2s | <1s | Includes PQC keygen, image generation, consciousness adaptation |
| Authenticate QRG | <500ms | <250ms | PQC signature verification, consciousness matching |
| Revoke QRG | <200ms | <100ms | Database update, cache invalidation |
| List User QRGs | <300ms | <150ms | Database query, pagination |

### 7.2 Resource Usage

| Resource | Estimate | Notes |
|----------|----------|-------|
| QRG Image Size | 50-100 KB | PNG with steganographic data |
| Database Storage per QRG | 2 KB | Metadata, keys, hashes |
| Memory per Generation | 50 MB | PQC operations, image processing |
| CPU per Generation | 0.5-1.0 core-seconds | Kyber keygen + image rendering |

### 7.3 Cost Estimate (AWS)

Assuming 10,000 QRG generations/month:
- **Compute (Lambda)**: ~$5/month (1s x 1GB per invocation)
- **Storage (S3)**: ~$2/month (1GB images + metadata)
- **Database (RDS)**: ~$15/month (shared with other identity features)
- **Quantum RNG API**: $0-50/month (depends on provider)

**Total**: ~$22-72/month for 10K generations

---

## 8. Integration Points

### 8.1 Existing Systems

| System | Integration Point | Notes |
|--------|-------------------|-------|
| Lambda ID | `lukhas/identity/lambda_id.py` | Add `qrg_credential` option |
| Tiered Auth | `lukhas/identity/tiers.py` | Add QRG as T4 authentication method |
| WebAuthn | `lukhas/identity/webauthn_production.py` | QRG can coexist with FIDO2 |
| OIDC | `lukhas/api/oidc.py` | Add QRG scope to OAuth2 flows |
| Guardian | `lukhas/governance/guardian_system.py` | Constitutional checks |
| MATRIZ | `matriz/` | Consciousness state tracking |

### 8.2 New API Endpoints

```python
# POST /api/v1/identity/qrg/generate
# POST /api/v1/identity/qrg/authenticate
# DELETE /api/v1/identity/qrg/{qrg_id}
# GET /api/v1/identity/qrg/list/{user_id}
```

### 8.3 Database Schema

```sql
CREATE TABLE qrg_credentials (
    qrg_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(lid),
    public_key TEXT NOT NULL,
    image_url VARCHAR(512),
    consciousness_snapshot JSONB,
    cultural_context JSONB,
    tier_level INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    revoked_at TIMESTAMP,
    last_used_at TIMESTAMP,
    use_count INT DEFAULT 0
);

CREATE INDEX idx_qrg_user ON qrg_credentials(user_id);
CREATE INDEX idx_qrg_expiry ON qrg_credentials(expires_at) WHERE revoked_at IS NULL;
```

---

## 9. Testing Requirements

### 9.1 Unit Tests

- [ ] QRG format validation (ID structure, base64 encoding)
- [ ] PQC key generation (Kyber-1024, Dilithium-5)
- [ ] Consciousness parameter adaptation
- [ ] Cultural safety scoring
- [ ] Guardian gatekeeper approval/rejection
- [ ] Steganographic data embedding/extraction

### 9.2 Integration Tests

- [ ] Full QRG registration flow (generate + store + retrieve)
- [ ] Authentication flow (challenge + signature verification)
- [ ] Revocation flow (revoke + verify cannot authenticate)
- [ ] Consciousness drift detection
- [ ] Multi-user QRG listing

### 9.3 Contract Tests

- [ ] QRG adapter interface compliance
- [ ] API endpoint contracts (OpenAPI spec)
- [ ] Database schema migration tests

### 9.4 Security Tests

- [ ] PQC algorithm correctness (NIST test vectors)
- [ ] Quantum entropy quality (NIST SP 800-90B)
- [ ] Signature forgery resistance
- [ ] Steganographic payload integrity
- [ ] Guardian bypass attempts
- [ ] Cultural safety edge cases (offensive symbols, religious imagery)

### 9.5 Performance Tests

- [ ] Latency under load (1K concurrent generations)
- [ ] Memory usage profiling
- [ ] Database query performance (10K+ QRGs per user)
- [ ] Image generation throughput

---

## 10. Observability & Monitoring

### 10.1 Metrics (Prometheus)

```python
qrg_generations_total = Counter("qrg_generations_total", ["tier_level", "entropy_source"])
qrg_authentications_total = Counter("qrg_authentications_total", ["success", "consciousness_match"])
qrg_generation_duration_seconds = Histogram("qrg_generation_duration_seconds")
qrg_cultural_safety_score = Histogram("qrg_cultural_safety_score")
qrg_guardian_rejections_total = Counter("qrg_guardian_rejections_total", ["reason"])
```

### 10.2 Tracing (OpenTelemetry)

- Trace QRG generation from request to image storage
- Trace consciousness engine calls
- Trace Guardian approval decisions
- Trace PQC operations (keygen, sign, verify)

### 10.3 Logging

- **INFO**: QRG generation/authentication success
- **WARN**: Cultural safety score <0.90, consciousness drift >0.3
- **ERROR**: Guardian rejection, PQC failure, entropy exhaustion

---

## 11. Acceptance Criteria

**Phase 0 (This Spec)**:
- [x] Specification approved by security team
- [x] ADR created with phased rollout plan
- [x] Reviewers assigned (see ADR)

**Phase 1 (Adapter + Mocks)**:
- [ ] `QRGAdapter` protocol implemented in `lukhas/identity/qrg_adapter.py`
- [ ] Mock implementation for testing without consciousness dependencies
- [ ] Feature flags (`QRG_ENABLED`, `QRG_CONSCIOUSNESS_ENABLED`) working
- [ ] Unit tests for adapter interface (100% coverage)
- [ ] Documentation for developers on using mock vs production

**Phase 2 (Production Wiring)**:
- [ ] Real consciousness engine integration (no mocks)
- [ ] Real cultural safety checker integration
- [ ] Real Guardian gatekeeper integration
- [ ] PQC cryptography with quantum entropy
- [ ] All security tests passing
- [ ] Performance benchmarks met (see Section 7.1)
- [ ] API endpoints deployed to staging
- [ ] SLSA provenance for all PQC dependencies
- [ ] Security audit report (external firm)

**Phase 3 (Production Deployment)**:
- [ ] Deployed to production with `QRG_ENABLED=true`
- [ ] Consciousness features gated by `QRG_CONSCIOUSNESS_ENABLED=false` initially
- [ ] Monitoring dashboards live (Grafana)
- [ ] Incident response playbook documented
- [ ] 1-week bake time with no P0/P1 incidents
- [ ] Consciousness features enabled with `QRG_CONSCIOUSNESS_ENABLED=true`

---

## 12. Open Questions & Risks

### 12.1 Open Questions

1. **Q**: Should QRG replace or complement WebAuthn/FIDO2?
   **A**: Complement initially, evaluate replacement after 6 months of production data.

2. **Q**: What is the revocation strategy if consciousness engine is compromised?
   **A**: Guardian circuit breaker can disable consciousness features instantly via `QRG_CONSCIOUSNESS_ENABLED=false`.

3. **Q**: How do we handle consciousness state unavailable (e.g., user blocks telemetry)?
   **A**: Gracefully degrade to non-conscious QRG (static glyph, no adaptation).

4. **Q**: Should QRG imagery be user-customizable?
   **A**: Phase 3 feature - allow users to select base style (geometric, organic, abstract).

### 12.2 Risks

| Risk | Impact | Mitigation |
|------|--------|----------|
| PQC algorithm breaks pre-standardization | High | Use NIST finalists only, plan for algorithm agility |
| Consciousness engine latency >2s | Medium | Async generation, fallback to static QRG |
| Cultural safety false positives | Medium | Human review queue for edge cases |
| Guardian approval delays | Low | Implement approval timeout with safe defaults |
| Quantum RNG API downtime | Low | Fallback to PRNG with audit logging |

---

## 13. Phased Roadmap

**Phase 0: Specification (2 weeks)** ← **WE ARE HERE**
- Write spec (this document)
- Write ADR (see `000-qrg-spec-adr.md`)
- Security/architecture review
- Approve and merge to main

**Phase 1: Adapter + Mocks (3 weeks)**
- Implement `QRGAdapter` protocol
- Build mock implementations
- Feature flags and config
- Unit tests (100% coverage)
- Documentation

**Phase 2: Production Wiring (4-6 weeks)**
- Integrate consciousness engine
- Integrate cultural safety checker
- Integrate Guardian gatekeeper
- PQC cryptography implementation
- Security audit (external)
- Performance testing

**Phase 3: Deployment (2 weeks + monitoring)**
- Deploy to staging (1 week)
- Deploy to production (1 week)
- Monitor with consciousness disabled (1 week)
- Enable consciousness features (phased rollout)

---

## 14. Reviewers & Approvers

**Spec Reviewers**:
- [ ] Security Team Lead (PQC, cryptography)
- [ ] Consciousness Team Lead (consciousness engine integration)
- [ ] Identity Team Lead (authentication flows)
- [ ] Guardian Team Lead (constitutional compliance)

**Phase Gate Approvers**:
- [ ] CTO (Phase 1 → Phase 2)
- [ ] CISO (Phase 2 → Phase 3)
- [ ] Product Lead (Phase 3 production rollout)

---

## 15. References

- [NIST PQC Standards](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Kyber Specification](https://pq-crystals.org/kyber/)
- [Dilithium Specification](https://pq-crystals.org/dilithium/)
- [LUKHAS Guardian System](../architecture/guardian_system.md)
- [Consciousness Engine](../../consciousness/core_consciousness/README.md)
- [Cultural Safety Checker](../../utils/cultural_safety_checker.py)
- [Issue #1253: QRG Consciousness Wiring](https://github.com/LukhasAI/Lukhas/issues/1253)

---

**Document History**:
- 2025-11-10: Initial draft (v0.1.0)
