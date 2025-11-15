# GLYPH Developer Guide

## Introduction

This guide provides comprehensive documentation for developers working with the LUKHAS GLYPH (QRGlyph) generation pipeline. GLYPHs are identity-integrated visual tokens that combine QR codes with consciousness-aware features, steganographic embedding, and post-quantum cryptography.

## Table of Contents

1. [Quick Start](#quick-start)
2. [GLYPH Types](#glyph-types)
3. [Security Levels](#security-levels)
4. [Architecture Overview](#architecture-overview)
5. [Component Reference](#component-reference)
6. [Usage Examples](#usage-examples)
7. [Performance Tuning](#performance-tuning)
8. [Security Best Practices](#security-best-practices)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic GLYPH Generation

```python
from labs.governance.identity.core.glyph.glyph_pipeline import (
    GLYPHPipeline,
    GLYPHGenerationRequest,
    GLYPHType,
    GLYPHSecurityLevel,
)

# Initialize pipeline
pipeline = GLYPHPipeline()

# Create a basic identity GLYPH
request = GLYPHGenerationRequest(
    lambda_id="user_001",
    glyph_type=GLYPHType.IDENTITY_BASIC,
    security_level=GLYPHSecurityLevel.BASIC,
    tier_level=1,
    expiry_hours=24,
)

# Generate GLYPH
result = pipeline.generate_glyph(request)

if result.success:
    print(f"GLYPH ID: {result.glyph_id}")
    print(f"Processing time: {result.generation_metadata['processing_time']:.3f}s")
    
    # Access the GLYPH image
    glyph_image = result.glyph_image
    glyph_image.save("my_glyph.png")
else:
    print(f"Error: {result.error_message}")
```

### Verification

```python
# Verify a generated GLYPH
verification_result = pipeline.verify_glyph(
    glyph_id=result.glyph_id,
    verification_data={
        "lambda_id": "user_001",
        "tier_level": 1,
    }
)

if verification_result["verified"]:
    print("GLYPH verified successfully!")
else:
    print("Verification failed")
```

## GLYPH Types

The pipeline supports 8 different GLYPH types, each optimized for specific use cases:

### 1. IDENTITY_BASIC

**Use Case:** Standard identity verification  
**Features:** Lambda ID, tier level, timestamp  
**Security:** Basic QR encoding  
**Performance:** Fastest (2-5ms)  
**Recommended For:** Tier 1 users, simple authentication

```python
request = GLYPHGenerationRequest(
    lambda_id="user_001",
    glyph_type=GLYPHType.IDENTITY_BASIC,
    security_level=GLYPHSecurityLevel.BASIC,
    tier_level=1,
)
```

### 2. IDENTITY_BIOMETRIC

**Use Case:** Biometric-linked identity  
**Features:** Biometric hash, enhanced encryption  
**Security:** Enhanced with crypto  
**Performance:** Moderate (5-10ms)  
**Recommended For:** Tier 2-3 users, high-security applications

```python
request = GLYPHGenerationRequest(
    lambda_id="user_002",
    glyph_type=GLYPHType.IDENTITY_BIOMETRIC,
    security_level=GLYPHSecurityLevel.ENHANCED,
    tier_level=2,
    biometric_data={
        "fingerprint": "hash_value",
        "face_embedding": "vector_hash",
    },
)
```

### 3. IDENTITY_CONSCIOUSNESS

**Use Case:** Consciousness-aware authentication  
**Features:** Real-time consciousness state, ORB visualization  
**Security:** Enhanced  
**Performance:** Moderate (8-15ms)  
**Recommended For:** Tier 3+ users, meditation/focus apps

```python
from labs.governance.identity.core.visualization.consciousness_mapper import (
    ConsciousnessState,
    EmotionalState,
)

consciousness_state = ConsciousnessState(
    consciousness_level=0.75,
    emotional_state=EmotionalState.FOCUS,
    emotional_intensity=0.7,
    neural_synchrony=0.8,
    attention_focus=["authentication", "security"],
    stress_level=0.2,
    relaxation_level=0.8,
    authenticity_score=0.9,
    timestamp=time.time(),
)

request = GLYPHGenerationRequest(
    lambda_id="user_003",
    glyph_type=GLYPHType.IDENTITY_CONSCIOUSNESS,
    security_level=GLYPHSecurityLevel.ENHANCED,
    tier_level=3,
    consciousness_state=consciousness_state,
)
```

### 4. IDENTITY_CULTURAL

**Use Case:** Culturally-adapted authentication  
**Features:** Cultural symbols, color palettes, respect levels  
**Security:** Enhanced  
**Performance:** Moderate (7-12ms)  
**Recommended For:** Global applications, inclusive design

```python
request = GLYPHGenerationRequest(
    lambda_id="user_004",
    glyph_type=GLYPHType.IDENTITY_CULTURAL,
    security_level=GLYPHSecurityLevel.ENHANCED,
    tier_level=2,
    cultural_context="eastern",  # 'western', 'eastern', 'arabic', 'african', 'universal'
)
```

### 5. IDENTITY_QUANTUM

**Use Case:** Quantum-resistant authentication  
**Features:** Post-quantum signatures (Dilithium3)  
**Security:** Quantum-resistant  
**Performance:** Higher (15-25ms)  
**Recommended For:** Tier 4+ users, long-term security

```python
request = GLYPHGenerationRequest(
    lambda_id="user_005",
    glyph_type=GLYPHType.IDENTITY_QUANTUM,
    security_level=GLYPHSecurityLevel.QUANTUM,
    tier_level=4,
)
```

### 6. IDENTITY_STEGANOGRAPHIC

**Use Case:** Hidden data embedding  
**Features:** Steganographic identity embedding (1024 bytes capacity)  
**Security:** Enhanced with steganography  
**Performance:** Higher (10-20ms)  
**Recommended For:** Covert authentication, sensitive data

```python
request = GLYPHGenerationRequest(
    lambda_id="user_006",
    glyph_type=GLYPHType.IDENTITY_STEGANOGRAPHIC,
    security_level=GLYPHSecurityLevel.ENHANCED,
    tier_level=3,
    steganographic_data={
        "data": "secret_payload",
        "key": "encryption_key_123",
        "method": "quantum_lsb",
    },
)
```

### 7. IDENTITY_DREAM

**Use Case:** Dream state authentication  
**Features:** Dream pattern integration  
**Security:** Enhanced  
**Performance:** Moderate (8-15ms)  
**Recommended For:** Sleep research, dream journaling

```python
request = GLYPHGenerationRequest(
    lambda_id="user_007",
    glyph_type=GLYPHType.IDENTITY_DREAM,
    security_level=GLYPHSecurityLevel.ENHANCED,
    tier_level=3,
    dream_pattern={
        "symbols": ["flying", "water", "light"],
        "lucidity": 0.6,
        "vividness": 0.8,
    },
)
```

### 8. IDENTITY_FUSION

**Use Case:** Maximum security, all modalities  
**Features:** All features combined (biometric, consciousness, quantum, etc.)  
**Security:** Transcendent (maximum)  
**Performance:** Highest (20-30ms)  
**Recommended For:** Tier 5 users, critical operations

```python
request = GLYPHGenerationRequest(
    lambda_id="user_008",
    glyph_type=GLYPHType.IDENTITY_FUSION,
    security_level=GLYPHSecurityLevel.TRANSCENDENT,
    tier_level=5,
    consciousness_state=consciousness_state,
    biometric_data=biometric_data,
    cultural_context="universal",
    dream_pattern=dream_pattern,
    steganographic_data=stego_data,
)
```

## Security Levels

### BASIC
- Standard QR encoding
- No additional encryption
- Fast generation (2-5ms)
- Suitable for tier 0-1

### ENHANCED
- Additional cryptographic protection
- Biometric linking support
- Cultural adaptation
- Moderate performance (5-15ms)
- Suitable for tier 2-3

### QUANTUM
- Post-quantum cryptographic signatures (CRYSTALS-Dilithium3)
- Quantum-resistant security (NIST Level 3)
- Higher performance cost (15-25ms)
- Suitable for tier 4+

### TRANSCENDENT
- Maximum security (all features enabled)
- Multi-factor authentication
- Consciousness fusion
- Highest performance cost (20-30ms)
- Suitable for tier 5 only

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GLYPH Pipeline                            │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ LUKHASQRGMgr  │  │ PQCCrypto    │  │ Steganographic  │  │
│  │               │  │ Engine       │  │ Embedder        │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐                        │
│  │ LUKHASOrb     │  │ Consciousness│                        │
│  │ Visualizer    │  │ Mapper       │                        │
│  └───────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Request Preparation**: Convert `GLYPHGenerationRequest` to internal format
2. **Identity Data**: Prepare identity data based on GLYPH type template
3. **QRG Generation**: Generate adaptive QR code using `LUKHASQRGManager`
4. **Identity Embedding**: Embed identity features into GLYPH
5. **Steganographic Layers**: Add hidden data (if requested)
6. **ORB Visualization**: Generate consciousness visualization (if required)
7. **Quantum Signature**: Create PQC signature (if high security)
8. **Final Assembly**: Combine all components into final GLYPH image

## Component Reference

### PQCCryptoEngine

**Location:** `labs/governance/identity/auth_backend/pqc_crypto_engine.py`

**Supported Algorithms:**

#### Signature Algorithms (CRYSTALS-Dilithium)
- **Dilithium2**: NIST Level 2, 2420-byte signatures
- **Dilithium3**: NIST Level 3, 3293-byte signatures (Recommended)
- **Dilithium5**: NIST Level 5, 4595-byte signatures

#### Key Encapsulation (CRYSTALS-Kyber)
- **Kyber512**: NIST Level 1
- **Kyber768**: NIST Level 3 (Recommended)
- **Kyber1024**: NIST Level 5

**Example:**

```python
from labs.governance.identity.auth_backend.pqc_crypto_engine import PQCCryptoEngine

engine = PQCCryptoEngine()

# Generate signature keypair
keypair = engine.generate_signature_keypair("Dilithium3")

# Sign message
message = b"Hello, quantum world!"
signature = engine.sign_message(message, keypair.private_key, "Dilithium3")

# Verify signature
is_valid = engine.verify_signature(message, signature, keypair.public_key)
```

**⚠️ Important:** Current implementation is a safe stub. Production deployment requires integration with `liboqs` or similar PQC library.

### SteganographicIdentityEmbedder

**Location:** `labs/governance/identity/core/glyph/steganographic_id.py`

**Embedding Methods:**
- LSB (Least Significant Bit)
- DCT (Discrete Cosine Transform)
- Quantum-enhanced LSB (Recommended)
- Multi-layer embedding (Maximum security)

**Capacity:** Up to 1024 bytes (25% of image capacity)

**Example:**

```python
from labs.governance.identity.core.glyph.steganographic_id import (
    SteganographicIdentityEmbedder,
    IdentityEmbedData,
    EmbeddingMethod,
    EmbeddingStrength,
)

embedder = SteganographicIdentityEmbedder()

identity_data = IdentityEmbedData(
    lambda_id="user_001",
    tier_level=3,
    timestamp=time.time(),
)

result = embedder.embed_identity_data(
    carrier_image=qr_image,
    identity_data=identity_data,
    method=EmbeddingMethod.QUANTUM_LSB,
    strength=EmbeddingStrength.MODERATE,
)

if result.success:
    print(f"Detection resistance: {result.detection_resistance_score}")
    print(f"Capacity used: {result.capacity_used * 100:.1f}%")
```

### LUKHASOrb

**Location:** `labs/governance/identity/core/visualization/orb.py`

**Purpose:** Dynamic visualization of consciousness state

**Example:**

```python
from labs.governance.identity.core.visualization.lukhas_orb import LUKHASOrb, OrbState

orb = LUKHASOrb()

orb_state = OrbState(
    consciousness_level=0.8,
    emotional_state="focus",
    neural_synchrony=0.9,
    tier_level=5,
    authentication_confidence=0.95,
    attention_focus=["security", "privacy"],
    timestamp=time.time(),
    user_lambda_id="anonymous",
)

visualization = orb.update_state(orb_state)
animation_frame = orb.get_animation_frame(0.016)  # 60 FPS
```

## Performance Tuning

### Target Performance

- **Basic GLYPHs:** p95 < 10ms
- **Enhanced GLYPHs:** p95 < 15ms
- **Quantum GLYPHs:** p95 < 25ms
- **Transcendent GLYPHs:** p95 < 30ms

### Optimization Strategies

#### 1. Async PQC Signatures

For GLYPHs that don't require immediate signature verification:

```python
import asyncio

async def generate_with_async_signature(pipeline, request):
    # Generate GLYPH without signature first
    result = pipeline.generate_glyph(request)
    
    # Add signature asynchronously
    if request.security_level in [GLYPHSecurityLevel.QUANTUM, GLYPHSecurityLevel.TRANSCENDENT]:
        signature = await asyncio.to_thread(
            pipeline._generate_quantum_signature,
            result.glyph_data,
            result.identity_embedding
        )
        result.qi_signature = signature
    
    return result
```

#### 2. ORB Visualization Caching

Cache ORB visualizations for similar consciousness states:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_orb_visualization(consciousness_level, emotional_state, tier_level):
    # Generate ORB visualization
    pass
```

#### 3. Lazy Steganographic Embedding

Only embed steganographic data when explicitly requested:

```python
request = GLYPHGenerationRequest(
    lambda_id="user_001",
    glyph_type=GLYPHType.IDENTITY_BASIC,  # No steganography by default
    security_level=GLYPHSecurityLevel.BASIC,
    tier_level=1,
)

# Later, if needed:
if needs_steganography:
    request.glyph_type = GLYPHType.IDENTITY_STEGANOGRAPHIC
    request.steganographic_data = {...}
```

#### 4. QR Complexity Reduction

For simple use cases, reduce QR complexity:

```python
pipeline_config = {
    "qr_complexity": "minimal",  # vs "balanced", "complex"
    "enable_particles": False,
    "enable_fractals": False,
}

pipeline = GLYPHPipeline(config=pipeline_config)
```

## Security Best Practices

### 1. PII Protection

**Never store raw biometric data:**

```python
# ❌ BAD
request.biometric_data = {
    "fingerprint_image": raw_image_data,
}

# ✅ GOOD
request.biometric_data = {
    "fingerprint": hashlib.sha256(raw_image_data).hexdigest(),
}
```

### 2. Expiry Enforcement

Always set appropriate expiry times:

```python
# Short-lived for authentication
request.expiry_hours = 1  # 1 hour

# Medium-lived for sessions
request.expiry_hours = 24  # 1 day

# Long-lived for access tokens
request.expiry_hours = 168  # 1 week
```

### 3. Tier-Appropriate Security

Match security level to tier:

```python
tier_to_security = {
    0: GLYPHSecurityLevel.BASIC,
    1: GLYPHSecurityLevel.BASIC,
    2: GLYPHSecurityLevel.ENHANCED,
    3: GLYPHSecurityLevel.ENHANCED,
    4: GLYPHSecurityLevel.QUANTUM,
    5: GLYPHSecurityLevel.TRANSCENDENT,
}

security_level = tier_to_security.get(user_tier, GLYPHSecurityLevel.BASIC)
```

### 4. Verification Required

Always verify GLYPHs before trusting them:

```python
def authenticate_with_glyph(pipeline, glyph_id, user_data):
    verification = pipeline.verify_glyph(glyph_id, user_data)
    
    if not verification["verified"]:
        raise AuthenticationError("GLYPH verification failed")
    
    if not verification["identity_verified"]:
        raise AuthenticationError("Identity mismatch")
    
    if not verification["qi_verified"]:
        logger.warning("Quantum signature verification failed")
    
    return verification
```

### 5. Production PQC Integration

Before enabling `GLYPH_PIPELINE_ENABLED=true`:

```python
# Check PQC library is available
try:
    import oqs
    PQC_AVAILABLE = True
except ImportError:
    PQC_AVAILABLE = False
    logger.error("Production PQC library not available!")

if not PQC_AVAILABLE and os.getenv("GLYPH_PIPELINE_ENABLED") == "true":
    raise RuntimeError("Cannot enable GLYPH pipeline without PQC library")
```

## Troubleshooting

### Issue: Import Errors

**Problem:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:** The GLYPH pipeline is designed to work without web dependencies. Ensure you're importing from the correct paths:

```python
# ✅ Correct
from labs.governance.identity.core.glyph.glyph_pipeline import GLYPHPipeline

# ❌ Incorrect (may trigger web deps)
from labs.governance.identity import GLYPHPipeline
```

### Issue: Slow GLYPH Generation

**Problem:** GLYPH generation takes >100ms

**Solutions:**

1. Check GLYPH type complexity:
```python
# Profile different types
import time

for glyph_type in GLYPHType:
    start = time.time()
    result = pipeline.generate_glyph(request)
    print(f"{glyph_type.value}: {(time.time() - start) * 1000:.1f}ms")
```

2. Reduce security level if appropriate
3. Use async generation for non-blocking operations
4. Check system load and available resources

### Issue: Steganographic Embedding Fails

**Problem:** `detection_resistance_score < 0.8`

**Solutions:**

1. Use higher-resolution carrier images
2. Switch to quantum-enhanced embedding:
```python
method=EmbeddingMethod.QUANTUM_LSB
```

3. Reduce embedded data size
4. Use multi-layer embedding for better resistance

### Issue: Verification Fails

**Problem:** `verified: False` for valid GLYPH

**Solutions:**

1. Check expiry:
```python
if datetime.now() > expires_at:
    # GLYPH expired
```

2. Ensure verification data matches generation:
```python
verification_data = {
    "lambda_id": original_lambda_id,  # Must match
    "tier_level": original_tier,      # Must match
}
```

3. Check GLYPH storage:
```python
if glyph_id not in pipeline.generated_glyphs:
    # GLYPH not found - may have been cleared from memory
```

## Additional Resources

- **ADR:** See `docs/ADR/ADR-GLYPH-001-pipeline-architecture.md` for architecture decisions
- **API Reference:** See inline code documentation in `glyph_pipeline.py`
- **Examples:** See `tests/unit/labs/governance/identity/glyph/` for usage examples
- **Security:** Contact security team for production PQC integration guidance

## Support

For questions or issues:
- GitHub Issues: LukhasAI/Lukhas#1244
- Documentation: This guide + ADR-GLYPH-001
- Code: `labs/governance/identity/core/glyph/`
