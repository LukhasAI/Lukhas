# ADR-GLYPH-001: GLYPH Pipeline Architecture and Security Design

**Status:** Accepted  
**Date:** 2025-11-15  
**Context:** Issue #1244 - GLYPH Pipeline Component Implementation  
**Deciders:** LUKHAS Identity Team

## Context and Problem Statement

The GLYPH (QRGlyph) pipeline generates identity-integrated visual tokens combining QR codes with consciousness-aware features, steganographic embedding, and post-quantum cryptography. The initial implementation referenced components that needed proper interface definitions and security review.

**Key Requirements:**
1. Identity-integrated GLYPH generation with multiple security levels
2. Post-quantum cryptographic security for quantum-resistant authentication
3. Steganographic identity embedding (1024 bytes capacity)
4. Visual ORB integration for consciousness-aware rendering
5. Performance target: p95 < 10ms for GLYPH generation
6. Security: No XSS vectors, timing attacks, or information leakage

## Decision Drivers

- **Security First:** PQC implementation must follow NIST standards
- **Modularity:** Components must have clear, testable interfaces
- **Performance:** Sub-10ms generation time for user experience
- **Extensibility:** Support for future GLYPH types and features
- **Safety:** Safe stub implementations until production PQC libraries integrated

## Considered Options

### Option 1: Full PQC Integration (liboqs)
**Pros:**
- Cryptographically secure from day one
- Production-ready quantum resistance
- NIST-standardized algorithms

**Cons:**
- Heavy dependency (C library bindings)
- Complex build process
- Performance overhead
- Not needed until GLYPH_PIPELINE_ENABLED=true

### Option 2: Safe Stub Interfaces (Selected)
**Pros:**
- Clean interface definitions
- Testable without crypto dependencies
- Fast iteration on architecture
- Easy to swap for real implementation
- Matches current deployment (GLYPH_PIPELINE_ENABLED=false)

**Cons:**
- Not cryptographically secure yet
- Requires future migration to real PQC

### Option 3: Hybrid Approach
**Pros:**
- Optional PQC for advanced users
- Graceful degradation

**Cons:**
- Complex configuration
- Security confusion for users

## Decision Outcome

**Chosen option:** Option 2 - Safe Stub Interfaces

Implement safe, well-defined interfaces for all GLYPH components with clear documentation that current implementations are stubs. This allows:
1. Complete pipeline architecture validation
2. Interface and integration testing
3. Performance benchmarking
4. Security review of design patterns
5. Future migration path to production PQC

## Architecture Components

### 1. LUKHASQRGManager Adapter
**Location:** `labs/governance/identity/auth/qrg_generators.py`  
**Purpose:** Adapter to bridge import paths between core and labs implementations  
**Interface:** Exports `LUKHASQRGManager`, `QRGType` from core module

**Design Decision:** Use adapter pattern rather than code duplication to maintain single source of truth for QRG generation logic.

### 2. PQCCryptoEngine
**Location:** `labs/governance/identity/auth_backend/pqc_crypto_engine.py`  
**Purpose:** Post-quantum cryptographic operations interface  
**Algorithms:** CRYSTALS-Dilithium (signatures), CRYSTALS-Kyber (KEM)

**Security Design:**
```python
# Signature sizes (NIST standards)
Dilithium2: 2420 bytes (Level 2)
Dilithium3: 3293 bytes (Level 3) - Recommended
Dilithium5: 4595 bytes (Level 5)

# Key encapsulation
Kyber512: Level 1
Kyber768: Level 3 - Recommended
Kyber1024: Level 5
```

**Stub Implementation:**
- Uses SHAKE-256 for pseudo-key generation (deterministic for testing)
- Matches real algorithm key/signature sizes
- Documents that cryptographic security is NOT provided
- Interface matches expected production API

**Migration Path:** Replace with `liboqs` Python bindings when GLYPH_PIPELINE_ENABLED=true

### 3. LUKHASOrb Adapter
**Location:** `labs/governance/identity/core/visualization/lukhas_orb.py`  
**Purpose:** Adapter to export ORB visualization components  
**Interface:** Exports `LUKHASOrb`, `OrbState`, `OrbPattern`, `OrbVisualization`

**Design Decision:** Simple re-export adapter to fix import paths without duplicating visualization logic.

### 4. SteganographicIdentityEmbedder
**Location:** `labs/governance/identity/core/glyph/steganographic_id.py`  
**Purpose:** Embed identity data steganographically in images  
**Capacity:** 1024 bytes (supports up to 25% of image capacity)

**Existing Implementation:** Already complete with multiple embedding methods:
- LSB (Least Significant Bit)
- DCT (Discrete Cosine Transform)
- Quantum-enhanced LSB
- Multi-layer embedding

**Security Considerations:**
- Fernet encryption for embedded data
- Quantum-enhanced randomness for embedding patterns
- Detection resistance scoring
- Timing attack mitigation: Constant-time operations where possible

## Security Review

### 1. Post-Quantum Cryptography

**Algorithm Selection: CRYSTALS-Dilithium3**
- **Rationale:** NIST Level 3 security, balanced performance
- **Quantum Resistance:** 128-bit quantum security
- **Signature Size:** 3293 bytes (acceptable for GLYPH use case)
- **Status:** NIST standardized (FIPS 204)

**Algorithm Selection: CRYSTALS-Kyber768**
- **Rationale:** NIST Level 3 security, matching Dilithium
- **Quantum Resistance:** 128-bit quantum security
- **Ciphertext Size:** 1088 bytes
- **Status:** NIST standardized (FIPS 203)

**Current Implementation Risk:**
⚠️ **CRITICAL:** Stub implementation is NOT cryptographically secure. Production deployment MUST integrate real PQC library.

**Mitigation:**
- Clear documentation of stub status
- Deployment flag: `GLYPH_PIPELINE_ENABLED=false` (default)
- ADR requirement for security review before enabling

### 2. Steganographic Security

**Information Leakage Risks:**
- **Timing Attacks:** Embedding time varies with data size
  - **Mitigation:** Document as known limitation, future constant-time implementation
- **Visual Analysis:** Statistical detection of LSB embedding
  - **Mitigation:** Quantum-enhanced randomness, multi-layer embedding
- **Side Channels:** Image size metadata reveals capacity
  - **Mitigation:** Fixed image sizes recommended, padding

**Detection Resistance:**
- PSNR-based scoring (higher is better)
- Method bonuses: Multi-layer +0.3, Quantum LSB +0.2
- Target: >0.8 detection resistance score

### 3. Visual Rendering Security

**XSS Vector Prevention:**
- GLYPH images are generated programmatically (PIL)
- No user-controlled HTML/SVG rendering
- Base64 encoding for data transmission
- **Risk:** LOW - No DOM manipulation

**Content Security:**
- QR data is JSON-serialized (controlled format)
- Constitutional Gatekeeper validation (when available)
- Cultural safety checking (when available)

### 4. Identity Privacy

**PII Handling:**
- Lambda ID: Hashed (SHA-256, 16-char truncated)
- Biometric data: Hash only, never raw data
- Consciousness state: Anonymized (no user_lambda_id in ORB visualization)

**Data Retention:**
- GLYPHs stored in memory only (ephemeral)
- Expiry enforced via `expires_at` timestamp
- No persistent storage in current design

## Performance Considerations

**Target:** p95 < 10ms for GLYPH generation

**Component Timing Estimates:**
- QRG generation: 2-5ms
- Steganographic embedding: 3-8ms (depends on image size)
- PQC signature: 1-3ms (stub), 5-10ms (real Dilithium3)
- ORB visualization: 1-2ms
- **Total:** 7-18ms (stub), 12-28ms (production PQC)

**Performance Concerns:**
⚠️ Production PQC may exceed 10ms target for complex GLYPHs

**Optimizations:**
1. Async PQC signature generation (separate from main flow)
2. ORB visualization caching
3. Lazy steganographic embedding (only when requested)
4. QR complexity reduction for simple GLYPH types

**Revised Target:** p95 < 10ms for basic GLYPHs, p95 < 25ms for transcendent GLYPHs

## Testing Strategy

### Unit Tests
- [x] Component interface contracts
- [x] PQC key generation and signature verification (interface level)
- [ ] Steganographic embedding/extraction roundtrip
- [ ] ORB state transitions
- [ ] GLYPH type-specific data preparation

### Integration Tests
- [ ] Full pipeline: Request → GLYPH → Verification
- [ ] Each GLYPH type (8 types)
- [ ] Error handling and fallback mechanisms
- [ ] Performance benchmarks

### Security Tests
- [ ] PQC signature verification (when available)
- [ ] Steganographic integrity checks
- [ ] XSS vector scanning (static analysis)
- [ ] Timing attack detection (profiling)

### Symbolic Invariants
- Identity uniqueness: Each lambda_id → unique GLYPH_ID
- Expiry enforcement: GLYPHs expire after configured time
- Tier consistency: Security features match tier_level
- Signature integrity: qi_signature validates glyph_data

## Documentation

### Developer Guide
**Location:** `labs/governance/identity/docs/GLYPH_DEVELOPER_GUIDE.md`

**Contents:**
1. GLYPH pipeline overview
2. Component architecture diagram
3. GLYPH type selection guide
4. Security level configuration
5. Example code for each GLYPH type
6. Performance tuning tips
7. Troubleshooting common issues

### Security Documentation
**Location:** This ADR + inline code comments

**Contents:**
1. PQC algorithm choices and rationale
2. Known limitations of stub implementations
3. Security checklist before production deployment
4. Threat model and mitigations

## Deployment Strategy

### Phase 1: Development (Current)
- Stub implementations active
- `GLYPH_PIPELINE_ENABLED=false`
- Testing and interface validation
- Documentation complete

### Phase 2: Production Preparation
- Integrate `liboqs` or `pqcrypto` Python bindings
- Security audit of PQC integration
- Performance optimization
- Load testing

### Phase 3: Production Deployment
- `GLYPH_PIPELINE_ENABLED=true`
- Monitoring and alerting
- Gradual rollout by tier level
- Incident response plan

## Compliance and Standards

**NIST PQC Standards:**
- FIPS 203: Kyber (Key Encapsulation)
- FIPS 204: Dilithium (Digital Signatures)
- FIPS 205: SPHINCS+ (Stateless Hash-Based Signatures) - Future consideration

**Privacy Standards:**
- GDPR: Right to erasure (ephemeral GLYPHs)
- CCPA: Data minimization (hashed identifiers)
- Biometric data: Hash-only storage

## Consequences

### Positive
✅ Clear interface contracts for all components  
✅ Testable architecture without crypto dependencies  
✅ Performance benchmarking possible  
✅ Security review completed before implementation  
✅ Migration path to production PQC defined  
✅ Modular design enables independent component evolution

### Negative
⚠️ Stub implementations not cryptographically secure  
⚠️ Two-phase deployment (stubs → production PQC)  
⚠️ Performance target may require revision for complex GLYPHs  
⚠️ Multiple adapter layers add indirection

### Neutral
- Adapter pattern requires maintenance
- Documentation burden for stub limitations
- Testing strategy requires both stub and production coverage

## Links

- Issue: LukhasAI/Lukhas#1244
- Related: QRG Spec ADR (`docs/ADR/000-qrg-spec-adr.md`)
- NIST PQC: https://csrc.nist.gov/projects/post-quantum-cryptography
- Dilithium Spec: https://pq-crystals.org/dilithium/
- Kyber Spec: https://pq-crystals.org/kyber/

## Notes

**Review Checklist:**
- [x] Security review completed
- [x] PQC algorithm choices documented
- [x] Performance targets defined
- [x] Migration path specified
- [ ] Integration tests implemented
- [ ] Developer guide written
- [ ] Production deployment plan approved

**Future Enhancements:**
- SPHINCS+ integration for stateless signatures
- Falcon signatures (faster verification)
- Hardware-accelerated PQC (Intel AVX-512)
- Distributed GLYPH generation
- GLYPH revocation mechanism
