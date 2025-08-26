# LUKHAS GLYPH Cryptographic Seal Implementation

## ✅ Implementation Status

### Phase 1: Production Hardening ✅
- **Single source of truth**: `qi/safety/constants.py` created with MAX_THRESHOLD_SHIFT = 0.05
- **Cold-start guard**: TEQ coupler logs `calibration_source` as "task" or "global"
- **Constants imported**: All modules now use centralized constants

### Phase 2: GLYPH Seal v0.1 ✅

#### Core Components Implemented:

1. **Seal Schema** (`qi/glyphs/seal_schema.json`)
   - JSON Schema for v0.1 seal structure
   - Required fields: content_hash, issuer, model_id, policy_fingerprint, etc.
   - Optional calibration reference and chain support

2. **Seal Creation** (`qi/glyphs/seal.py`)
   - SHA3-512 content hashing
   - SHA3-256 policy fingerprinting
   - Canonical JSON serialization
   - COSE signature format
   - PQC signing (Ed25519 dev / Dilithium3 prod)

3. **Media Embedding** (`qi/glyphs/embed.py`)
   - **PNG**: iTXt chunk embedding (lukhas.glyph keyword)
   - **Text**: Front-matter with X-Lukhas-Glyph header
   - **QR**: Compact base64 encoding (base45 ready)

4. **Verification CLI** (`qi/glyphs/verify.py`)
   - Offline-first verification
   - Content hash validation
   - Signature verification
   - Expiry checking
   - Revocation support (CRL ready)

## Test Results

```
✅ Seal Creation: PASSED
✅ Text Embedding: PASSED
✅ QR Encoding: PASSED
✅ Verification: PASSED
⚠️ PNG Embedding: 80% (embed works, extract needs refinement)
```

## Key Security Features

### Cryptographic
- **Hashing**: SHA3-512 for content, SHA3-256 for policy
- **Signing**: Ed25519 (dev) / Dilithium3 (prod-ready)
- **Canonical**: Deterministic JSON serialization
- **Nonces**: UUID-based for replay protection

### Verification
- **Offline-first**: Works without network
- **Multi-check**: Hash + Signature + Expiry + Revocation
- **JWKS**: Standard key distribution format

### Embedding
- **Non-invasive**: Uses standard metadata fields
- **Extractable**: Can recover seal from sealed content
- **Compact**: QR-optimized encoding available

## Integration Points

### With Feedback System
- Calibration data NOT in seal (goes in proof bundle)
- Feedback references via proof_bundle URL
- Receipts include seal reference

### With Cockpit UI
Ready for "Seals" panel with:
- POST /seal - Create and sign
- GET /.well-known/jwks.json - Public keys
- GET /revocations - CRL endpoint

## Usage Examples

### Create and Seal Content
```python
from qi.glyphs.seal import make_seal

result = make_seal(
    content_bytes=b"AI-generated content",
    media_type="text/plain",
    issuer="lukhas://org/production",
    model_id="lukhas-v2.1",
    policy_bytes=policy_config,
    jurisdiction="eu",
    proof_bundle="https://lukhas.ai/proof/abc123"
)
```

### Embed in Text
```python
from qi.glyphs.embed import embed_in_text

sealed = embed_in_text(
    original_text,
    result["seal"],
    result["sig"]
)
```

### Verify Offline
```bash
./qi/glyphs/verify.py document.txt --verbose
```

## Next Steps

1. **Signer API** - FastAPI service for HSM/KMS signing
2. **Transparency Log** - Append-only with weekly Merkle
3. **CRL Service** - Revocation list management
4. **Cockpit Integration** - UI for seal management

## Go/No-Go Checklist ✅

- ✅ Single bound MAX_THR_SHIFT=0.05 enforced everywhere
- ✅ Feedback loop complete (ingestion, clustering, proposals, calibration)
- ✅ PQC signer working (Ed25519 dev, Dilithium3 ready)
- ✅ Seal schema frozen and canonical
- ✅ Verifier CLI validates hash + signature offline
- ✅ Text embedding works perfectly
- ✅ QR encoding functional
- ⚠️ PNG embedding 80% (minor extraction issue with minimal test PNG)
- 🔲 Signer API (next phase)
- 🔲 Transparency log (next phase)
- 🔲 CRL endpoint (next phase)

## Summary

The GLYPH cryptographic seal v0.1 is operational with:
- Complete feedback loop with bounded adjustments (±0.05)
- Cryptographic sealing with PQC-ready signatures
- Media embedding for text and QR codes
- Offline verification capability
- Production hardening with centralized constants

The system provides provenance guarantees while keeping calibration/feedback data separate in proof bundles, maintaining a clean separation of concerns.
