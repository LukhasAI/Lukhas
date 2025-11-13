# QRG Standard Proposal v0.1
**Quantum Resilient Glyph (QRG) Cryptographic Decision Signatures**

**Status**: Draft Proposal
**Date**: 2025-11-12
**Authors**: LUKHAS AI Governance Team
**Category**: Standards Track

## Abstract

This document proposes the Quantum Resilient Glyph (QRG) standard for cryptographic signatures on AI system decisions, policy changes, and operational events. QRG provides tamper-evident provenance for critical system operations, enabling verification that decisions originated from authorized entities and have not been modified in transit. The standard specifies ECDSA P-256 signatures with structured JSON payloads, designed for both human readability and machine verification.

QRG addresses the growing need for accountability and transparency in AI systems by creating an auditable chain of custody for decisions that affect system behavior, user data, and ethical constraints.

## 1. Introduction

### 1.1 Motivation

Modern AI systems make decisions with significant consequences: memory storage, policy enforcement, capability activation, and ethical evaluations. Without cryptographic signatures, these decisions are vulnerable to:

- **Tampering**: Unauthorized modification of decisions or policies
- **Repudiation**: Claims that decisions were not made by the stated authority
- **Loss of Context**: Inability to trace decision provenance over time
- **Compliance Failures**: Lack of audit trails for regulatory requirements

Traditional code signing addresses software integrity but fails to capture runtime decisions, configuration changes, and dynamic policy updates. AI systems require decision-level signatures that bind decisions to their context, timestamp, and authorization.

### 1.2 Design Goals

QRG achieves the following objectives:

1. **Tamper Evidence**: Detect any modification to signed decisions or payloads
2. **Non-Repudiation**: Cryptographically bind decisions to signing entities
3. **Human Readability**: JSON format accessible to humans and machines
4. **Quantum Resilience**: Signature algorithm compatible with post-quantum migration paths
5. **Consent Awareness**: Optional consent hash linking decisions to user authorization
6. **Temporal Traceability**: ISO 8601 timestamps for audit trails
7. **Minimal Overhead**: Efficient verification suitable for high-throughput systems

### 1.3 Scope

This specification covers:

- QRG signature data structure (Section 3)
- Cryptographic primitives (ECDSA P-256, SHA-256)
- Canonical payload serialization (Section 3.2)
- Signature generation and verification algorithms (Section 4)
- Use cases and integration patterns (Section 5)
- Key management considerations (Section 6)

This specification does NOT cover:

- Key distribution protocols (use TLS, PKI, or similar)
- Revocation mechanisms (future extension)
- Multi-signature schemes (future extension)
- Hardware security module (HSM) integration (implementation-specific)

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

- **QRG**: Quantum Resilient Glyph, a cryptographic signature structure
- **Payload**: The JSON object being signed (decision, policy, event)
- **Canonical Hash**: SHA-256 hash of canonical JSON serialization
- **Consent Hash**: Optional hash linking decision to user consent
- **Signature**: ECDSA signature over the canonical payload hash
- **Verification**: Cryptographic validation of signature against payload

## 3. QRG Signature Structure

### 3.1 Data Model

A QRG signature is a structured object containing the following fields:

```json
{
  "algo": "ecdsa-sha256",
  "pubkey_pem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
  "sig_b64": "MEUCIQDExampleSignatureBase64Encoded...",
  "ts": "2025-11-12T18:30:00.000Z",
  "payload_hash": "a3f5d8c2e1b7f4a9c3d6e8b1a2f5c8d9e0b3a6c9f2e5d8b1a4c7f0e3b6d9a2",
  "consent_hash": "b4e6c9d3f2a8e1b5c8d2a7f0e4b9c6d1a5f8e2b7c0d3a6f9e1b4c8d7a0f5e2"
}
```

**Field Definitions**:

- `algo` (string, REQUIRED): Signature algorithm identifier. MUST be `"ecdsa-sha256"` in version 0.1.
- `pubkey_pem` (string, REQUIRED): Public key in PEM format (PKCS#8 SubjectPublicKeyInfo). Used to verify signature.
- `sig_b64` (string, REQUIRED): ECDSA signature bytes encoded as base64. Signature is over the `payload_hash`.
- `ts` (string, REQUIRED): ISO 8601 timestamp with millisecond precision and `Z` timezone (UTC). Indicates when signature was generated.
- `payload_hash` (string, REQUIRED): SHA-256 hash (hex-encoded) of canonical JSON payload. This is what gets signed.
- `consent_hash` (string, OPTIONAL): SHA-256 hash (hex-encoded) linking decision to user consent. MAY be null.

### 3.2 Canonical Payload Serialization

To ensure deterministic hashing, payloads MUST be canonicalized before hashing. QRG uses the following canonicalization rules:

1. **JSON Serialization**: Use RFC 8785 rules (equivalent to JSON.stringify with sorted keys)
2. **Key Sorting**: Serialize all object keys in lexicographic order
3. **No Whitespace**: Remove all whitespace (no spaces, newlines, or tabs)
4. **Minimal Separators**: Use `,` for array/object separators and `:` for key-value separators
5. **UTF-8 Encoding**: Encode serialized JSON as UTF-8 bytes before hashing

**Example**:

Original payload:
```json
{
  "version": "1.0.0",
  "notes": "Fixed security vulnerability",
  "date": "2025-11-12"
}
```

Canonical form (what gets hashed):
```
{"date":"2025-11-12","notes":"Fixed security vulnerability","version":"1.0.0"}
```

**Reference Implementation** (Python):
```python
import json
from hashlib import sha256

def canonical_payload_hash(payload: dict) -> str:
    """Compute canonical hash of payload."""
    js = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(js.encode("utf-8")).hexdigest()
```

### 3.3 Signature Serialization

QRG signatures SHOULD be serialized as JSON for storage and transmission. The serialized form includes all fields from Section 3.1.

**JSON Serialization**:
```json
{
  "qrg_signature": {
    "algo": "ecdsa-sha256",
    "pubkey_pem": "...",
    "sig_b64": "...",
    "ts": "2025-11-12T18:30:00.000Z",
    "payload_hash": "...",
    "consent_hash": null
  },
  "payload": {
    "version": "1.0.0",
    "notes": "Release notes"
  }
}
```

Implementations MAY store signature and payload separately, but MUST preserve both for verification.

## 4. Cryptographic Algorithms

### 4.1 Signature Algorithm

QRG version 0.1 uses **ECDSA with P-256 curve and SHA-256 hashing**.

**Rationale**:
- **ECDSA P-256**: Widely supported, NIST-standardized, 128-bit security level
- **SHA-256**: Collision-resistant hash function, suitable for integrity verification
- **Deterministic ECDSA**: Implementations SHOULD use RFC 6979 deterministic signatures
- **Quantum Consideration**: While ECDSA is vulnerable to quantum attacks, P-256 provides a migration path to post-quantum algorithms (future QRG versions will support CRYSTALS-Dilithium)

### 4.2 Key Generation

**Private Key**:
- Generate using cryptographically secure random number generator (CSRNG)
- Curve: SECP256R1 (P-256)
- Format: PKCS#8 PEM-encoded private key
- Storage: MUST be stored securely (HSM, KMS, encrypted at rest)

**Public Key**:
- Derived from private key via elliptic curve point multiplication
- Format: PKCS#8 SubjectPublicKeyInfo PEM-encoded public key
- Distribution: MAY be embedded in signatures or distributed via PKI

**Reference Implementation** (Python):
```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

def generate_private_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1(), default_backend())

def private_key_to_pem(priv: ec.EllipticCurvePrivateKey) -> bytes:
    return priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def public_key_to_pem(pub: ec.EllipticCurvePublicKey) -> bytes:
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
```

### 4.3 Signature Generation

**Algorithm**:
1. Canonicalize payload using rules from Section 3.2
2. Compute SHA-256 hash of canonical payload
3. Sign the hash using ECDSA P-256 with private key
4. Encode signature bytes as base64
5. Extract public key from private key and encode as PEM
6. Generate ISO 8601 timestamp (UTC)
7. Construct QRG signature object with all fields

**Reference Implementation** (Python):
```python
import base64
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

def qrg_sign(payload: dict, priv_pem: bytes, consent_hash: str = None) -> dict:
    """Generate QRG signature for payload."""
    priv = load_private_key_pem(priv_pem)
    payload_hash = canonical_payload_hash(payload)
    data = payload_hash.encode("utf-8")

    # Sign using ECDSA-SHA256
    signature = priv.sign(data, ec.ECDSA(hashes.SHA256()))
    sig_b64 = base64.b64encode(signature).decode("ascii")

    # Extract public key
    pub_pem = public_key_to_pem(priv.public_key()).decode("utf-8")

    return {
        "algo": "ecdsa-sha256",
        "pubkey_pem": pub_pem,
        "sig_b64": sig_b64,
        "ts": datetime.utcnow().isoformat() + "Z",
        "payload_hash": payload_hash,
        "consent_hash": consent_hash
    }
```

### 4.4 Signature Verification

**Algorithm**:
1. Canonicalize payload using rules from Section 3.2
2. Compute SHA-256 hash of canonical payload
3. Compare computed hash to `payload_hash` field (MUST match)
4. Decode `sig_b64` from base64 to signature bytes
5. Load public key from `pubkey_pem` field
6. Verify ECDSA signature against payload hash using public key
7. Return verification result (true/false)

**Reference Implementation** (Python):
```python
import base64

def qrg_verify(payload: dict, qrg: dict) -> bool:
    """Verify QRG signature against payload."""
    pub = load_public_key_pem(qrg["pubkey_pem"].encode("utf-8"))

    # Verify payload hash
    expected_hash = canonical_payload_hash(payload)
    if expected_hash != qrg["payload_hash"]:
        return False

    # Verify signature
    signature = base64.b64decode(qrg["sig_b64"].encode("ascii"))
    data = qrg["payload_hash"].encode("utf-8")

    try:
        pub.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
```

## 5. Use Cases

### 5.1 Release Notes Signing

**Scenario**: Sign software release notes to prove authenticity.

**Payload**:
```json
{
  "version": "2.1.0",
  "date": "2025-11-12",
  "notes": "Security fixes for Guardian system",
  "author": "LUKHAS AI Team"
}
```

**Signature Generation**:
```python
from core.qrg.signing import qrg_sign

payload = {
    "version": "2.1.0",
    "date": "2025-11-12",
    "notes": "Security fixes for Guardian system",
    "author": "LUKHAS AI Team"
}

with open("release_key.pem", "rb") as f:
    priv_pem = f.read()

signature = qrg_sign(payload, priv_pem)
```

**Output**:
```json
{
  "payload": {...},
  "qrg_signature": {
    "algo": "ecdsa-sha256",
    "pubkey_pem": "...",
    "sig_b64": "...",
    "ts": "2025-11-12T18:30:00.000Z",
    "payload_hash": "...",
    "consent_hash": null
  }
}
```

### 5.2 Policy Change Signatures

**Scenario**: Sign Guardian policy updates to prevent unauthorized modifications.

**Payload**:
```json
{
  "policy_id": "guardian_drift_threshold",
  "old_value": 0.15,
  "new_value": 0.20,
  "reason": "Reduce false positive drift detections",
  "approved_by": "governance_committee"
}
```

**Benefits**:
- Audit trail of all policy changes
- Prevention of unauthorized threshold modifications
- Compliance with regulatory requirements

### 5.3 AI Decision Signatures

**Scenario**: Sign Guardian ethical decisions for non-repudiation.

**Payload**:
```json
{
  "decision_id": "eth_eval_20251112_001",
  "action_type": "data_deletion",
  "allowed": true,
  "reason": "GDPR Article 17 Right to Erasure",
  "confidence": 0.95,
  "timestamp": "2025-11-12T18:30:00.000Z"
}
```

**Benefits**:
- Proof that AI system made decision (not human tampering)
- Audit trail for compliance investigations
- Accountability for automated decisions

### 5.4 Consent Verification

**Scenario**: Link decision signatures to user consent.

**Workflow**:
1. User grants consent with cryptographic proof
2. System computes `consent_hash = SHA256(consent_document)`
3. Decision signature includes `consent_hash` field
4. Auditors can verify decision was authorized by consent

**Example**:
```python
consent_document = {
    "user_id": "user123",
    "action": "memory_storage",
    "granted_at": "2025-11-12T18:00:00.000Z"
}

consent_hash = canonical_payload_hash(consent_document)

decision = {
    "action": "store_memory",
    "user_id": "user123",
    "timestamp": "2025-11-12T18:30:00.000Z"
}

signature = qrg_sign(decision, priv_pem, consent_hash=consent_hash)
```

## 6. Security Considerations

### 6.1 Key Management

**Private Key Storage**:
- MUST be stored encrypted at rest
- SHOULD use Hardware Security Module (HSM) or Key Management Service (KMS) in production
- MUST NOT be committed to version control
- SHOULD implement key rotation policies (e.g., annual rotation)

**Public Key Distribution**:
- MAY be embedded in signatures for self-contained verification
- SHOULD be distributed via secure channel (TLS, PKI)
- MAY be published in trusted public key directories

**Key Compromise**:
- If private key is compromised, ALL signatures from that key are suspect
- Implement key revocation lists (future extension)
- Monitor for unauthorized signature generation

### 6.2 Replay Protection

QRG signatures alone do NOT prevent replay attacks. To prevent replay:

1. **Timestamp Validation**: Reject signatures older than acceptable window (e.g., 5 minutes)
2. **Nonce Inclusion**: Include unique nonce in payload to prevent duplicate signatures
3. **Sequence Numbers**: Use monotonically increasing sequence numbers in payloads
4. **State Tracking**: Track processed signature IDs to detect reuse

**Example** (timestamp validation):
```python
from datetime import datetime, timedelta

def is_signature_fresh(qrg: dict, max_age_seconds: int = 300) -> bool:
    """Check if signature timestamp is within acceptable window."""
    sig_time = datetime.fromisoformat(qrg["ts"].replace("Z", "+00:00"))
    age = (datetime.now(tz=sig_time.tzinfo) - sig_time).total_seconds()
    return age <= max_age_seconds
```

### 6.3 Canonicalization Attacks

Improper canonicalization can lead to signature bypasses. Implementations MUST:

- Use deterministic JSON serialization (Section 3.2)
- Reject non-canonical JSON during verification
- Validate UTF-8 encoding
- Reject payloads with unusual Unicode characters (e.g., zero-width spaces)

### 6.4 Quantum Resistance

ECDSA P-256 is vulnerable to quantum computers with sufficient qubits (Shor's algorithm). Mitigation strategies:

1. **Short-Lived Signatures**: Use signatures for near-term verification only
2. **Hybrid Signatures**: Combine ECDSA with post-quantum algorithm (future extension)
3. **Migration Path**: QRG v1.0 will support CRYSTALS-Dilithium3
4. **Algorithm Agility**: `algo` field enables algorithm upgrades

**Recommendation**: Treat QRG signatures as valid for operational timeframes (days to weeks), not long-term archival (years).

### 6.5 Side-Channel Attacks

ECDSA signature generation is vulnerable to timing attacks. Implementations SHOULD:

- Use constant-time cryptographic libraries
- Implement RFC 6979 deterministic ECDSA (eliminates nonce-related attacks)
- Avoid signing untrusted payloads that could leak key bits

## 7. Implementation Guidance

### 7.1 Minimal Implementation

A compliant QRG implementation MUST:

1. Support ECDSA P-256 with SHA-256
2. Implement canonical JSON serialization (Section 3.2)
3. Generate signatures matching Section 3.1 structure
4. Verify signatures per Section 4.4
5. Handle PEM-encoded keys (PKCS#8)
6. Support optional `consent_hash` field

### 7.2 Reference Implementation

**Language**: Python 3.9+
**Library**: `cryptography` (https://cryptography.io)
**Location**: `core/qrg/signing.py`, `core/qrg/model.py`

**Key Functions**:
- `qrg_sign(payload, priv_pem, consent_hash=None) -> QRGSignature`
- `qrg_verify(payload, qrg) -> bool`
- `canonical_payload_hash(payload) -> str`

**Installation**:
```bash
pip install cryptography
```

### 7.3 Integration Checklist

- [ ] Generate long-lived key pair for organization
- [ ] Store private key in KMS/HSM
- [ ] Publish public key in trusted directory
- [ ] Implement signature generation in CI/CD pipeline
- [ ] Add verification to deployment processes
- [ ] Implement timestamp validation for replay protection
- [ ] Monitor signature verification failures
- [ ] Document key rotation procedures
- [ ] Test signature verification with tampered payloads
- [ ] Train operators on QRG verification workflows

## 8. Future Extensions

### 8.1 Post-Quantum Algorithms

QRG v1.0 will support:
- **CRYSTALS-Dilithium3**: NIST-standardized post-quantum signature algorithm
- **Hybrid Signatures**: ECDSA + Dilithium for transition period
- **Algorithm Negotiation**: Support for multiple `algo` values

### 8.2 Multi-Signature Schemes

QRG v1.0 will support:
- **Threshold Signatures**: Require M-of-N signers for high-risk operations
- **Multi-Party Computation**: Distributed key generation and signing
- **Signature Aggregation**: Compact multi-signature representation

### 8.3 Revocation Mechanisms

QRG v1.0 will support:
- **Certificate Revocation Lists (CRLs)**: Published lists of revoked keys
- **Online Certificate Status Protocol (OCSP)**: Real-time revocation checking
- **Short-Lived Certificates**: Automatic expiration without revocation

### 8.4 Hardware Token Integration

QRG v1.0 will support:
- **FIDO2/WebAuthn**: Browser-based signing with hardware tokens
- **YubiKey**: USB hardware token integration
- **TPM**: Trusted Platform Module binding

## 9. References

### 9.1 Normative References

- **RFC 2119**: Key words for use in RFCs to Indicate Requirement Levels
- **RFC 6979**: Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA)
- **RFC 8785**: JSON Canonicalization Scheme (JCS)
- **FIPS 186-4**: Digital Signature Standard (DSS)
- **SEC 2**: Recommended Elliptic Curve Domain Parameters

### 9.2 Informative References

- LUKHAS AI Architecture: `docs/architecture/GUARDIAN_SYSTEM.md`
- LUKHAS AI Manifesto: `docs/MANIFESTO.md`
- QRG Operations Guide: `docs/operations/qrg_signing.md`
- Identity System: `core/identity/`
- Guardian System: `lukhas_website/lukhas/governance/guardian/`

## 10. Acknowledgments

This specification builds on prior work in code signing (PGP, X.509), blockchain signatures (Bitcoin, Ethereum), and AI governance research. Special thanks to the LUKHAS AI Governance Team for design feedback and the cryptography community for robust primitives.

---

**Version**: 0.1 (Draft)
**Status**: Proposal
**Next Steps**: Community review, implementation feedback, security audit
**Contact**: LUKHAS AI Governance Team
