---
status: wip
type: documentation
owner: unknown
module: reference
redirect: false
moved_to: null
---

# LUKHAS AI GLYPH Cryptographic Seal System

Portable, quantum-resistant cryptographic attestations for AI artifacts with verifiable offline and online validation.

## Overview

GLYPHs (Generative Linkage for AI artifacts with Provenance and Hashing) are cryptographically sealed attestations that bind AI-generated content to its creation context. They provide immutable provenance tracking without weakening the cryptographic guarantees through policy or UX complexity.

### What GLYPHs Are

- **Portable**: QR-embeddable seals that travel with content across platforms
- **Cryptographically Sealed**: Ed25519 (dev) or Dilithium3 (production) signatures
- **Verifiable Offline**: No network required for basic authenticity checks
- **Revocation-Aware**: Online checking for key revocation and policy updates
- **Quantum-Resistant**: Post-quantum cryptography ready for production

### What GLYPHs Aren't

- **Policy Engines**: GLYPHs reference policy fingerprints but don't execute policies
- **UX Layers**: The seal contains only essential cryptographic claims
- **Mutable**: Once signed, seals cannot be modified without invalidating signatures

## Architecture

### Core Components

1. **GLYPH Seal** (`qi/glyphs/seal.py`)
   - Minimal cryptographic payload (v0.1)
   - SHA3-512 content binding
   - Policy fingerprint references
   - Temporal validity controls

2. **Verification Engine** (`qi/glyphs/verify.py`)
   - Offline signature validation
   - Content hash verification
   - Online revocation checking
   - JWKS-based public key resolution

3. **Signer Service** (`qi/glyphs/signer_service.py`)
   - Production FastAPI microservice
   - HSM/KMS integration ready
   - Batch signing support
   - JWKS endpoint for public keys

4. **File Embedding** (`qi/glyphs/embed.py`)
   - PNG tEXt chunk embedding
   - JPEG EXIF UserComment
   - Text HTML comment insertion
   - Auto-detection and extraction

5. **CLI Interface** (`qi/glyphs/cli.py`)
   - Complete seal lifecycle management
   - QR code generation
   - Verification workflows
   - File embedding/extraction

## GLYPH Seal Structure (v0.1)

### Minimal Payload

```json
{
  "v": "0.1",
  "content_hash": "sha3-512:<hex>",
  "media_type": "text/plain",
  "created_at": "2025-08-16T12:00:00Z",
  "issuer": "lukhas://org/<tenant-id>",
  "model_id": "lukhas-qiv2.0",
  "policy_fingerprint": "sha3-256:<hex>",
  "calib_ref": {"temp": 1.08, "ece": 0.041},
  "jurisdiction": "eu",
  "proof_bundle": "https://verify.lukhas.ai/p/<id>",
  "expiry": "2026-08-16T00:00:00Z",
  "nonce": "base64",
  "prev": "<prior seal id or null>"
}
```

### Signature Structure

```json
{
  "algorithm": "ed25519",
  "signature": "base64_signature",
  "key_id": "signer_key_identifier",
  "chain": []
}
```

### Compact Representation

For QR codes and embedded storage, seals are encoded as:
```
Base64URL(JSON({seal: payload, sig: signature}))
```

## Quick Start

### Installation

```bash
# Install core dependencies
pip install pynacl qrcode[pil] pillow

# Optional for schema validation
pip install jsonschema

# Optional for JPEG embedding
pip install piexif
```

### Creating Your First Seal

```bash
# Create a test file
echo "Hello, LUKHAS AI!" > test.txt

# Create and embed seal
python3 -m qi.glyphs.cli create test.txt \
  --issuer "lukhas://org/my-tenant" \
  --model-id "lukhas-demo-v1.0" \
  --proof-bundle "https://verify.lukhas.ai/demo/123" \
  --policy-root "qi/safety/policy_packs/global" \
  --embed \
  --qr test.png

# Verify the seal
python3 -m qi.glyphs.cli verify test.txt test.txt.seal.json

# Extract from embedded file
python3 -m qi.glyphs.cli extract test.sealed.txt --verify
```

### Programmatic Usage

```python
from qi.glyphs.seal import GlyphSigner, policy_fingerprint_from_files
from qi.glyphs.verify import GlyphVerifier

# Create signer
signer = GlyphSigner(key_id="my-key-001")

# Seal content
with open("document.txt", "rb") as f:
    content_bytes = f.read()

# Generate policy fingerprint
policy_fp = policy_fingerprint_from_files(
    "qi/safety/policy_packs/global",
    "qi/risk"
)

# Create seal
result = signer.create_seal(
    content_bytes=content_bytes,
    media_type="text/plain",
    issuer="lukhas://org/my-org",
    model_id="lukhas-prod-v2.0",
    policy_fingerprint=policy_fp,
    jurisdiction="global",
    proof_bundle="https://verify.lukhas.ai/abc123",
    calib_ref={"temp": 1.05, "ece": 0.041}
)

# Verify seal
jwks = {"my-key-001": signer.get_public_key()}
verifier = GlyphVerifier(jwks)

verification = verifier.verify_seal(
    content_bytes,
    result["seal"],
    result["signature"]
)

if verification.valid:
    print(f"✅ Valid seal from {verification.issuer}")
else:
    print("❌ Invalid seal:", verification.errors)
```

## Production Deployment

### Signer Service

Deploy the FastAPI signer service behind HSM/KMS:

```bash
# Development
export GLYPH_AUTH_TOKEN="your-secure-token"
uvicorn qi.glyphs.signer_service:app --port 8080

# Production with HSM
export GLYPH_HSM_ENABLED="true"
export GLYPH_HSM_KEY_ID="prod-hsm-001"
export GLYPH_HSM_PROVIDER="aws-kms"
export GLYPH_REQUIRE_AUTH="true"
export GLYPH_AUTH_TOKEN="production-token"

uvicorn qi.glyphs.signer_service:app --host 0.0.0.0 --port 8080
```

### API Usage

```bash
# Create seal via API
curl -X POST "http://localhost:8080/seal" \
  -H "X-Auth-Token: your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content_hash": "sha3-512:abc123...",
    "media_type": "text/plain",
    "issuer": "lukhas://org/my-tenant",
    "model_id": "lukhas-prod-v2.0",
    "proof_bundle": "https://verify.lukhas.ai/xyz789",
    "jurisdiction": "eu"
  }'

# Get public keys
curl "http://localhost:8080/.well-known/jwks.json"

# Health check
curl "http://localhost:8080/health"
```

## File Format Support

### PNG Images

Seals embedded in PNG tEXt chunks:

```python
from qi.glyphs.embed import embed_seal_png, extract_seal_png

# Embed
embed_seal_png("input.png", seal_data, "output.png")

# Extract
seal_data = extract_seal_png("sealed.png")
```

### JPEG Images

Seals embedded in EXIF UserComment:

```python
from qi.glyphs.embed import embed_seal_jpeg, extract_seal_jpeg

# Embed
embed_seal_jpeg("input.jpg", seal_data, "output.jpg")

# Extract
seal_data = extract_seal_jpeg("sealed.jpg")
```

### Text Files

Seals embedded as HTML comments:

```python
from qi.glyphs.embed import embed_seal_text, extract_seal_text

# Embed
sealed_content = embed_seal_text(original_text, seal_data)

# Extract
seal_data, clean_text = extract_seal_text(sealed_content)
```

### Auto-Detection

```python
from qi.glyphs.embed import auto_embed_seal, auto_extract_seal

# Auto-embed based on file extension
output_file = auto_embed_seal("document.pdf", seal_data)

# Auto-extract
seal_data, clean_file = auto_extract_seal("sealed_document.pdf")
```

## Verification Modes

### Offline Verification

Verify using cached JWKS:

```python
from qi.glyphs.verify import verify_compact_seal

# Load JWKS from file
with open("public_keys.json") as f:
    jwks = json.load(f)

# Verify compact seal (from QR code)
result = verify_compact_seal(qr_data, content_bytes, jwks)
```

### Online Verification

Include revocation and bundle checking:

```python
verifier = GlyphVerifier(jwks)
result = verifier.verify_seal(
    content_bytes,
    seal_data,
    signature_data,
    online_check=True  # Check revocation status
)

if result.online_checked:
    print(f"Revocation status: {result.revocation_status}")
```

## Security Features

### Cryptographic Algorithms

- **Ed25519**: Development and testing (fast, widely supported)
- **Dilithium3**: Production quantum-resistant signatures (future)
- **SHA3-512**: Content hash integrity
- **SHA3-256**: Policy fingerprint computation

### Key Management

- **Development**: Ephemeral keys generated per session
- **Production**: HSM/KMS managed keys with quarterly rotation
- **JWKS**: Standard JSON Web Key Set distribution
- **Key IDs**: Unique identifiers for key rotation

### Temporal Controls

- **Expiry**: All seals have configurable TTL (default 365 days)
- **Nonce**: Cryptographically secure replay protection
- **Created**: Immutable creation timestamp
- **Revocation**: Online checking for compromised keys

### Policy Binding

- **Fingerprints**: SHA3-256 hash of policy pack state
- **Immutable**: Policies referenced by fingerprint cannot change post-signing
- **Jurisdictional**: Support for region-specific policy variants
- **Proof Bundles**: Expanded evidence available online

## Integration Examples

### With Receipt System

```python
from qi.safety.teq_coupler import emit_calibrated_receipt
from qi.glyphs.seal import GlyphSigner

# Create seal
signer = GlyphSigner()
seal_result = signer.create_seal(...)

# Emit receipt with GLYPH metadata
receipt = emit_calibrated_receipt(
    artifact_sha="abc123",
    run_id="run_001",
    task="generate_content",
    calibration_result=gate_result,
    metrics={
        "glyph_seal_compact": seal_result["compact"],
        "glyph_issuer": seal_result["seal"]["issuer"],
        "glyph_model": seal_result["seal"]["model_id"]
    }
)
```

### With C-EVAL System

```python
from qi.eval.ceval_runner import run_suite
from qi.glyphs.seal import GlyphSigner

# Run evaluation
results = run_suite("qi/eval/core_tasks.json")

# Create seal for evaluation results
signer = GlyphSigner()
seal = signer.create_seal(
    content_bytes=json.dumps(results).encode(),
    media_type="application/json",
    model_id="lukhas-eval-v1.0",
    issuer="lukhas://org/lukhas-ai",
    # ... other params
)
```

## Schema Validation

GLYPH seals conform to JSON Schema located at `qi/glyphs/GLYPH_SEAL.schema.json`:

```bash
# Validate seal against schema
python3 -c "
import json, jsonschema
with open('qi/glyphs/GLYPH_SEAL.schema.json') as f:
    schema = json.load(f)
with open('my_seal.json') as f:
    seal = json.load(f)
jsonschema.validate(seal['seal'], schema)
print('✅ Valid seal')
"
```

## CLI Reference

### Commands

- `create` - Create cryptographic seals
- `verify` - Verify seal authenticity
- `extract` - Extract seals from embedded files
- `info` - Show system information

### Create Options

```bash
python3 -m qi.glyphs.cli create <file> [options]

Required:
  --issuer ISSUER           Issuer ID (lukhas://org/<tenant>)
  --model-id MODEL_ID       Model identifier
  --proof-bundle URL        Proof bundle URL

Optional:
  --policy-root DIR         Policy pack root directory
  --policy-fingerprint FP   Pre-computed fingerprint
  --overlays DIR           Policy overlay directory
  --jurisdiction JURIS     Jurisdiction (default: global)
  --ttl-days DAYS          Validity days (default: 365)
  --calib-ref JSON         Calibration reference
  --prev SEAL_ID           Previous seal for chaining
  --key-id KEY_ID          Signing key identifier
  --output FILE            Output JSON file
  --embed                  Embed in original file
  --embed-output FILE      Embedded output file
  --qr FILE                Generate QR code PNG
```

### Verify Options

```bash
python3 -m qi.glyphs.cli verify <file> <seal> [options]

Optional:
  --jwks FILE              JWKS file for verification
  --online                 Perform online checks
  --compact                Seal is compact format
```

### Extract Options

```bash
python3 -m qi.glyphs.cli extract <file> [options]

Optional:
  --output FILE            Output seal JSON
  --verify                 Verify extracted seal
```

## Trust Boundaries

### Immutable Claims

GLYPHs maintain strict trust boundaries:

1. **Content Hash**: Cryptographically bound to artifact
2. **Policy Fingerprint**: References immutable policy snapshot
3. **Issuer Identity**: Bound to cryptographic key
4. **Temporal Validity**: Cannot be extended post-signing

### Mutable References

1. **Policy Content**: Fingerprinted but content stored separately
2. **Proof Bundles**: Expanded evidence available online
3. **Revocation Status**: Keys can be revoked post-signing
4. **Calibration Data**: Informational only, not security-critical

## Roadmap

### Phase 1: Production Ready ✅

- [x] Core seal creation and verification
- [x] File embedding for major formats
- [x] CLI tooling and APIs
- [x] JSON Schema validation
- [x] QR code generation
- [x] Receipt system integration

### Phase 2: Production Hardening 🚧

- [ ] Transparency log implementation
- [ ] CRL (Certificate Revocation List) support
- [ ] HSM/KMS integration testing
- [ ] Batch processing optimization
- [ ] Performance benchmarking

### Phase 3: Ecosystem Integration 📋

- [ ] Browser extension for verification
- [ ] Mobile app QR scanning
- [ ] Content management system plugins
- [ ] Enterprise SSO integration
- [ ] Audit trail analytics

### Phase 4: Quantum Readiness 🔮

- [ ] Dilithium3 production deployment
- [ ] Key migration utilities
- [ ] Hybrid classical-quantum signatures
- [ ] Performance optimization
- [ ] Compliance certification

## Troubleshooting

### Common Issues

**"Content hash mismatch"**
- Ensure file hasn't been modified after sealing
- Check for encoding issues (text files)
- Verify extraction preserved original content

**"Signature verification failed"**
- Ensure correct JWKS public key
- Check key_id matches in JWKS
- Verify signature wasn't corrupted

**"Seal expired"**
- Check current time vs expiry timestamp
- Renewal requires creating new seal
- Consider longer TTL for archival content

**"Missing policy fingerprint"**
- Ensure policy-root directory exists
- Check file permissions on policy files
- Verify policy files are valid YAML

### Debug Mode

```bash
# Verbose CLI output
python3 -m qi.glyphs.cli create test.txt --issuer ... --debug

# Verification details
python3 -m qi.glyphs.cli verify test.txt seal.json --verbose

# Test suite
python3 test_glyph_system.py
```

### Performance

- **Seal Creation**: ~5ms (Ed25519) to ~50ms (Dilithium3)
- **Verification**: ~2ms offline, ~200ms online
- **QR Generation**: ~10ms for standard seals
- **File Embedding**: <1ms for text, ~50ms for images

## Contributing

GLYPHs are part of the LUKHAS AI ecosystem. Contributions welcome:

1. Test additional file formats
2. Improve embedding efficiency
3. Add cryptographic algorithm support
4. Enhance verification UX
5. Build ecosystem integrations

See `CLAUDE.md` for development guidelines.

---

**"Immutable truth in a mutable world"** - LUKHAS AI GLYPH System v0.1
