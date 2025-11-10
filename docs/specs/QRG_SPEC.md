# QRG (Quantum Reality Generation) Specification

**Status**: Draft (Phase 0)
**Version**: 0.1.0
**Authors**: LUKHAS Security & Consciousness Teams
**Date**: 2025-11-10
**Related ADR**: [000-qrg-spec-adr.md](../ADR/000-qrg-spec-adr.md)
**Tracking Issue**: TBD

---

## 1. Purpose & Motivation

Quantum Reality Generation (QRG) is a consciousness-aware artifact generation system designed to:

1. **Generate symbolic quantum reality artifacts** - Create rich, provenance-tracked artifacts from user consciousness states and contextual seeds
2. **Ensure safety & governance** - Integrate ConstitutionalGatekeeper, CulturalSafetyChecker, and CognitiveLoadEstimator checks
3. **Provide cryptographic provenance** - Track builder identity, SBOM, and attestations using cosign and SLSA
4. **Enable mesh consensus** - Support distributed quantum reality generation with consensus verification
5. **Maintain security & compliance** - Post-quantum cryptography, key management via KMS, and audit trails

QRG extends traditional artifact generation by making it **consciousness-native** and **governable** - artifacts adapt to user state, pass constitutional gates, and maintain full supply chain provenance.

---

## 2. User Stories

**US-1**: As a **T4 user**, I want to **generate a QRG artifact from a seed and context** so that I can receive a consciousness-aware symbolic payload.

**US-2**: As a **safety steward**, I want to **ensure all QRG artifacts pass cultural safety checks** so that no offensive or harmful content is generated.

**US-3**: As a **security auditor**, I want to **verify QRG provenance and attestations** so that I can certify artifact integrity and builder identity.

**US-4**: As a **Guardian system**, I want to **gate QRG generation via constitutional checks** so that ethical compliance is enforced before artifact creation.

**US-5**: As a **consciousness researcher**, I want to **track affect vectors and symbolic tokens** so that I can study how quantum reality adapts to emotional states.

**US-6**: As a **system architect**, I want to **integrate QRG with mesh consensus** so that distributed artifact generation can be validated and agreed upon.

---

## 3. Non-Goals

- **Real-time quantum hardware integration** - Phase 0 uses pseudo-random sources; quantum RNG is Phase 2+
- **User-facing UI/UX** - This spec covers backend API and adapters only; UI is separate
- **Direct blockchain integration** - Provenance uses SLSA/cosign, not blockchain (unless required by future ADR)
- **Replacement of existing authentication** - QRG is for artifact generation, not authentication (unlike QRG=Quantum Resonance Glyph)

---

## 4. Inputs & Outputs

### 4.1 QRGRequest Schema

Full typed schema for generation requests:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "QRGRequest",
  "required": ["user_id", "seed"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "Lambda ID or internal user identifier (e.g., lid:abc123...)",
      "pattern": "^lid:[a-zA-Z0-9_-]+$"
    },
    "seed": {
      "type": "string",
      "description": "Cryptographic seed for deterministic artifact generation",
      "minLength": 16,
      "maxLength": 256
    },
    "context": {
      "type": "object",
      "description": "Contextual metadata for artifact generation",
      "additionalProperties": true,
      "properties": {
        "consciousness_state": {
          "type": "object",
          "properties": {
            "emotional_valence": {
              "type": "number",
              "minimum": -1.0,
              "maximum": 1.0,
              "description": "Emotional state: -1.0 (negative) to 1.0 (positive)"
            },
            "cognitive_load": {
              "type": "number",
              "minimum": 0.0,
              "maximum": 1.0,
              "description": "Cognitive load: 0.0 (low) to 1.0 (high)"
            },
            "attention_focus": {
              "type": "number",
              "minimum": 0.0,
              "maximum": 1.0,
              "description": "Attention focus: 0.0 (distracted) to 1.0 (focused)"
            }
          }
        },
        "cultural_context": {
          "type": "object",
          "properties": {
            "languages": {
              "type": "array",
              "items": {"type": "string"},
              "description": "ISO 639-1 language codes (e.g., ['en', 'es'])"
            },
            "regions": {
              "type": "array",
              "items": {"type": "string"},
              "description": "ISO 3166-1 alpha-2 country codes (e.g., ['US', 'MX'])"
            },
            "accessibility_needs": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Accessibility requirements (e.g., ['high_contrast', 'screen_reader'])"
            }
          }
        },
        "tier_level": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5,
          "description": "User tier level (1-5, where 4+ enables advanced features)"
        }
      }
    },
    "options": {
      "type": "object",
      "description": "Optional generation parameters",
      "properties": {
        "entropy_source": {
          "type": "string",
          "enum": ["pseudo_rng", "quantum_rng"],
          "default": "pseudo_rng",
          "description": "Entropy source for artifact generation"
        },
        "consensus_required": {
          "type": "boolean",
          "default": false,
          "description": "Whether mesh consensus is required for this artifact"
        },
        "timeout_ms": {
          "type": "integer",
          "minimum": 100,
          "maximum": 30000,
          "default": 5000,
          "description": "Maximum time to wait for artifact generation (milliseconds)"
        }
      }
    }
  }
}
```

**Example QRGRequest**:
```json
{
  "user_id": "lid:abc123def456",
  "seed": "quantum-seed-2025-11-10-xyz",
  "context": {
    "consciousness_state": {
      "emotional_valence": 0.7,
      "cognitive_load": 0.3,
      "attention_focus": 0.8
    },
    "cultural_context": {
      "languages": ["en", "es"],
      "regions": ["US", "MX"],
      "accessibility_needs": ["high_contrast"]
    },
    "tier_level": 4
  },
  "options": {
    "entropy_source": "pseudo_rng",
    "consensus_required": false,
    "timeout_ms": 5000
  }
}
```

### 4.2 QRGResponse Schema

Full typed schema for generation responses:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "QRGResponse",
  "required": ["qrg_id", "seed", "artifact", "safety", "provenance"],
  "properties": {
    "qrg_id": {
      "type": "string",
      "description": "Unique identifier for this QRG artifact (e.g., qrg:uuid)",
      "pattern": "^qrg:[a-f0-9-]+$"
    },
    "seed": {
      "type": "string",
      "description": "Echo of the original seed for verification"
    },
    "artifact": {
      "type": "object",
      "description": "Generated artifact metadata and location",
      "required": ["type", "location", "hash"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["symbolic", "visual", "audio", "multimodal"],
          "description": "Type of generated artifact"
        },
        "location": {
          "type": "string",
          "format": "uri",
          "description": "URI to the artifact (e.g., s3://, https://, mock://)"
        },
        "hash": {
          "type": "string",
          "pattern": "^(sha256|sha3-256|blake3):[a-f0-9]+$",
          "description": "Cryptographic hash of artifact content"
        },
        "size_bytes": {
          "type": "integer",
          "minimum": 0,
          "description": "Size of artifact in bytes"
        },
        "content_type": {
          "type": "string",
          "description": "MIME type (e.g., application/json, image/png)"
        }
      }
    },
    "symbolic_payload": {
      "type": "object",
      "description": "Symbolic quantum reality payload",
      "properties": {
        "tokens": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Symbolic tokens representing quantum reality states"
        },
        "affect_vector": {
          "type": "array",
          "items": {"type": "number"},
          "description": "Multi-dimensional affect representation"
        },
        "metadata": {
          "type": "object",
          "additionalProperties": true,
          "description": "Additional symbolic metadata"
        }
      }
    },
    "safety": {
      "type": "object",
      "description": "Safety and governance check results",
      "required": ["status", "gate_checks"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["approved", "rejected", "flagged"],
          "description": "Overall safety status"
        },
        "gate_checks": {
          "type": "object",
          "properties": {
            "ConstitutionalGatekeeper": {
              "type": "object",
              "properties": {
                "status": {"type": "string", "enum": ["approved", "rejected"]},
                "reason": {"type": "string"},
                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
              }
            },
            "CulturalSafetyChecker": {
              "type": "object",
              "properties": {
                "status": {"type": "string", "enum": ["approved", "rejected"]},
                "reason": {"type": "string"},
                "score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
              }
            },
            "CognitiveLoadEstimator": {
              "type": "object",
              "properties": {
                "status": {"type": "string", "enum": ["approved", "flagged"]},
                "estimated_load": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "warnings": {"type": "array", "items": {"type": "string"}}
              }
            }
          }
        },
        "warnings": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Non-blocking warnings from safety checks"
        }
      }
    },
    "provenance": {
      "type": "object",
      "description": "Cryptographic provenance and attestation",
      "required": ["builder_id", "build_time"],
      "properties": {
        "builder_id": {
          "type": "string",
          "description": "Identity of the builder/service that generated this artifact"
        },
        "build_time": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of artifact generation"
        },
        "sbom_ref": {
          "type": "string",
          "format": "uri",
          "description": "Reference to Software Bill of Materials (SBOM) for this artifact"
        },
        "attestation_ref": {
          "type": "string",
          "format": "uri",
          "description": "Reference to cosign attestation bundle"
        },
        "slsa_level": {
          "type": "integer",
          "minimum": 0,
          "maximum": 4,
          "description": "SLSA provenance level (0-4)"
        },
        "signature": {
          "type": "object",
          "properties": {
            "algorithm": {
              "type": "string",
              "enum": ["ed25519", "dilithium5", "ecdsa-p256"],
              "description": "Signing algorithm used"
            },
            "public_key_ref": {
              "type": "string",
              "description": "Reference to public key for verification"
            },
            "signature_b64": {
              "type": "string",
              "description": "Base64-encoded signature"
            }
          }
        },
        "consensus": {
          "type": "object",
          "description": "Mesh consensus metadata (if applicable)",
          "properties": {
            "required": {"type": "boolean"},
            "participants": {"type": "integer", "minimum": 0},
            "agreement_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "job_id": {"type": "string"}
          }
        }
      }
    },
    "metrics": {
      "type": "object",
      "description": "Performance and telemetry metrics",
      "properties": {
        "generation_time_ms": {
          "type": "integer",
          "minimum": 0,
          "description": "Time taken to generate artifact (milliseconds)"
        },
        "safety_check_time_ms": {
          "type": "integer",
          "minimum": 0,
          "description": "Time taken for all safety checks (milliseconds)"
        },
        "total_time_ms": {
          "type": "integer",
          "minimum": 0,
          "description": "Total request processing time (milliseconds)"
        }
      }
    }
  }
}
```

**Example QRGResponse**:
```json
{
  "qrg_id": "qrg:550e8400-e29b-41d4-a716-446655440000",
  "seed": "quantum-seed-2025-11-10-xyz",
  "artifact": {
    "type": "symbolic",
    "location": "s3://lukhas-qrg/artifacts/550e8400-e29b-41d4-a716-446655440000.json",
    "hash": "sha256:a3b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "size_bytes": 2048,
    "content_type": "application/json"
  },
  "symbolic_payload": {
    "tokens": ["quantum", "consciousness", "resonance", "emergence"],
    "affect_vector": [0.7, 0.3, 0.8, 0.5],
    "metadata": {
      "dimensionality": 4,
      "entropy_bits": 256
    }
  },
  "safety": {
    "status": "approved",
    "gate_checks": {
      "ConstitutionalGatekeeper": {
        "status": "approved",
        "reason": "Passes all constitutional principles",
        "score": 0.95
      },
      "CulturalSafetyChecker": {
        "status": "approved",
        "reason": "No cultural violations detected",
        "score": 0.92
      },
      "CognitiveLoadEstimator": {
        "status": "approved",
        "estimated_load": 0.4,
        "warnings": []
      }
    },
    "warnings": []
  },
  "provenance": {
    "builder_id": "lukhas-qrg-service-prod-us-east-1",
    "build_time": "2025-11-10T15:30:00Z",
    "sbom_ref": "https://lukhas.ai/sbom/qrg/550e8400.cdx.json",
    "attestation_ref": "https://lukhas.ai/attestations/qrg/550e8400.att",
    "slsa_level": 3,
    "signature": {
      "algorithm": "ed25519",
      "public_key_ref": "https://lukhas.ai/keys/qrg-service.pub",
      "signature_b64": "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBzaWduYXR1cmU="
    },
    "consensus": {
      "required": false,
      "participants": 1,
      "agreement_score": 1.0,
      "job_id": "mesh-job-123"
    }
  },
  "metrics": {
    "generation_time_ms": 450,
    "safety_check_time_ms": 120,
    "total_time_ms": 580
  }
}
```

---

## 5. Adapter Interface Specification

QRG must expose a **thin adapter interface** to isolate implementation from integration points:

```python
# lukhas/quantum/qrg_adapter.py

from typing import Any, Dict, Protocol
from abc import ABC, abstractmethod

class QRGAdapter(Protocol):
    """
    Protocol for Quantum Reality Generation system integration.

    This adapter provides a stable contract between LUKHAS core and QRG implementations.
    All implementations must conform to this protocol for type safety and testability.
    """

    @abstractmethod
    async def generate(
        self,
        user_id: str,
        seed: str,
        context: Dict[str, Any],
        options: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Generate a QRG artifact from seed and context.

        Args:
            user_id: Lambda ID or internal user identifier (e.g., lid:abc123...)
            seed: Cryptographic seed for deterministic artifact generation
            context: Contextual metadata including consciousness_state, cultural_context, tier_level
            options: Optional parameters (entropy_source, consensus_required, timeout_ms)

        Returns:
            QRGResponse dict conforming to Section 4.2 schema

        Raises:
            QRGGenerationError: If generation fails due to internal error
            QRGSafetyRejection: If safety checks reject the artifact
            QRGTimeoutError: If generation exceeds timeout_ms
        """
        ...

    @abstractmethod
    async def validate(
        self,
        qrg_id: str,
        expected_hash: str
    ) -> Dict[str, bool]:
        """
        Validate a QRG artifact's integrity and provenance.

        Args:
            qrg_id: QRG artifact identifier (e.g., qrg:uuid)
            expected_hash: Expected cryptographic hash (e.g., sha256:...)

        Returns:
            {
                "valid": bool,
                "hash_match": bool,
                "signature_valid": bool,
                "provenance_verified": bool
            }
        """
        ...

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """
        Check adapter and service health.

        Returns:
            {
                "status": "healthy" | "degraded" | "unhealthy",
                "checks": {
                    "safety_gates": "ok" | "error",
                    "provenance_service": "ok" | "error",
                    "artifact_storage": "ok" | "error"
                },
                "version": str
            }
        """
        ...

# Example abstract base class implementation
class BaseQRGAdapter(ABC):
    """
    Base implementation of QRGAdapter with common functionality.

    Subclasses must implement _generate_artifact, _check_safety, and _create_provenance.
    """

    @abstractmethod
    async def _generate_artifact(
        self, seed: str, context: Dict[str, Any], options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate the raw artifact (subclass-specific logic)."""
        pass

    @abstractmethod
    async def _check_safety(
        self, artifact: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run safety gates (ConstitutionalGatekeeper, CulturalSafetyChecker, etc.)."""
        pass

    @abstractmethod
    async def _create_provenance(
        self, artifact: Dict[str, Any], metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create provenance block with SBOM, attestations, and signatures."""
        pass

    async def generate(
        self,
        user_id: str,
        seed: str,
        context: Dict[str, Any],
        options: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Orchestrate artifact generation, safety checks, and provenance."""
        import uuid
        import time

        start_time = time.time()
        options = options or {}

        # Generate artifact
        artifact = await self._generate_artifact(seed, context, options)
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Run safety checks
        safety_start = time.time()
        safety = await self._check_safety(artifact, context)
        safety_check_time_ms = int((time.time() - safety_start) * 1000)

        if safety["status"] == "rejected":
            raise QRGSafetyRejection(f"Safety rejected: {safety.get('gate_checks')}")

        # Create provenance
        provenance = await self._create_provenance(artifact, {
            "user_id": user_id,
            "seed": seed,
            "context": context,
            "options": options
        })

        qrg_id = f"qrg:{uuid.uuid4()}"
        total_time_ms = int((time.time() - start_time) * 1000)

        return {
            "qrg_id": qrg_id,
            "seed": seed,
            "artifact": artifact,
            "symbolic_payload": artifact.get("symbolic_payload", {}),
            "safety": safety,
            "provenance": provenance,
            "metrics": {
                "generation_time_ms": generation_time_ms,
                "safety_check_time_ms": safety_check_time_ms,
                "total_time_ms": total_time_ms
            }
        }

# Custom exceptions
class QRGGenerationError(Exception):
    """Raised when artifact generation fails."""
    pass

class QRGSafetyRejection(Exception):
    """Raised when safety checks reject the artifact."""
    pass

class QRGTimeoutError(Exception):
    """Raised when generation exceeds timeout."""
    pass
```

**Configuration & Feature Flags**:
```python
# Environment-based feature flags
QRG_ENABLED = os.environ.get("QRG_ENABLED", "false").lower() == "true"
QRG_CONSCIOUSNESS_ENABLED = os.environ.get("QRG_CONSCIOUSNESS_ENABLED", "false").lower() == "true"
QRG_CONSENSUS_ENABLED = os.environ.get("QRG_CONSENSUS_ENABLED", "false").lower() == "true"

# Conditional import with graceful degradation
if QRG_ENABLED:
    try:
        from lukhas.quantum.qrg_production import ProductionQRGAdapter
        _qrg_adapter = ProductionQRGAdapter()
    except ImportError:
        from lukhas.quantum.qrg_mock import MockQRGAdapter
        _qrg_adapter = MockQRGAdapter()
        logger.warning("QRG production implementation unavailable, using mock adapter")
else:
    _qrg_adapter = None
```

---

## 6. Safety & Governance Requirements

### 6.1 ConstitutionalGatekeeper Integration

**Requirement**: All QRG generation MUST pass Guardian constitutional validation before artifact creation.

```python
from core.interfaces.as_agent.core.gatekeeper import ConstitutionalGatekeeper

gatekeeper = ConstitutionalGatekeeper()

# Before generating QRG artifact
approval = await gatekeeper.validate_action(
    action="generate_qrg_artifact",
    context={
        "user_id": user_id,
        "seed": seed,
        "tier_level": context.get("tier_level", 1),
        "consciousness_state": context.get("consciousness_state", {})
    }
)

if not approval.get("approved", False):
    raise QRGSafetyRejection(f"Constitutional gatekeeper rejected: {approval.get('reason')}")
```

**Gate Checks**:
- **Ethical compliance**: Ensure artifact generation aligns with LUKHAS constitutional principles
- **User tier validation**: Verify user has appropriate tier level for requested features
- **Consent verification**: Check that user has consented to consciousness-aware processing
- **Rate limiting**: Enforce per-user generation quotas to prevent abuse

### 6.2 CulturalSafetyChecker Integration

**Requirement**: All QRG symbolic payloads MUST pass cultural safety validation before response.

```python
from utils.cultural_safety_checker import CulturalSafetyChecker

safety_checker = CulturalSafetyChecker()

# After generating symbolic payload
safety_result = await safety_checker.validate_symbolic_content(
    tokens=symbolic_payload["tokens"],
    affect_vector=symbolic_payload["affect_vector"],
    cultural_context=context.get("cultural_context", {})
)

if safety_result.get("safety_score", 0) < 0.85:
    # Reject and log for review
    raise QRGSafetyRejection(f"Cultural safety score too low: {safety_result}")
```

**Safety Checks**:
- **Symbolic token safety**: Ensure tokens don't contain offensive, harmful, or culturally inappropriate content
- **Cultural context matching**: Validate artifact is appropriate for user's languages and regions
- **Accessibility compliance**: Check that artifacts meet accessibility needs
- **Bias detection**: Scan for unintended biases in affect vectors and token distributions

### 6.3 CognitiveLoadEstimator Integration

**Requirement**: QRG MUST estimate cognitive load and warn if artifacts may overwhelm users.

```python
from utils.cognitive_load_estimator import CognitiveLoadEstimator

load_estimator = CognitiveLoadEstimator()

# After generating artifact
load_estimate = await load_estimator.estimate_load(
    symbolic_payload=symbolic_payload,
    consciousness_state=context.get("consciousness_state", {})
)

if load_estimate.get("estimated_load", 0) > 0.8:
    # Flag but don't reject (user may choose to proceed)
    warnings.append(f"High cognitive load estimated: {load_estimate['estimated_load']:.2f}")
```

**Load Estimation**:
- **Complexity scoring**: Measure symbolic payload complexity (token count, affect vector dimensionality)
- **State matching**: Compare artifact complexity to user's current cognitive load and attention focus
- **Adaptive warnings**: Provide warnings but allow T4+ users to override
- **Telemetry integration**: Track cognitive load patterns for continuous improvement

---

## 7. Provenance & Attestation Model

### 7.1 Required Provenance Fields

All QRG artifacts MUST include provenance blocks with:

1. **builder_id**: Identity of the service/container that generated the artifact (e.g., `lukhas-qrg-service-prod-us-east-1`)
2. **build_time**: ISO 8601 timestamp of generation (e.g., `2025-11-10T15:30:00Z`)
3. **sbom_ref**: URI to Software Bill of Materials in CycloneDX format
4. **attestation_ref**: URI to cosign attestation bundle
5. **slsa_level**: SLSA provenance level (target: Level 3 for production)
6. **signature**: Cryptographic signature of artifact metadata

### 7.2 SBOM Linking

**Requirement**: All QRG artifacts MUST have an associated SBOM tracking dependencies.

**Implementation**:
```bash
# Generate SBOM using syft
syft packages dir:/path/to/qrg-service -o cyclonedx-json > qrg-service.sbom.json

# Store SBOM in artifact storage (S3, etc.)
aws s3 cp qrg-service.sbom.json s3://lukhas-qrg-sboms/550e8400.cdx.json

# Reference in QRGResponse provenance.sbom_ref
"sbom_ref": "https://lukhas.ai/sbom/qrg/550e8400.cdx.json"
```

**SBOM Format**: CycloneDX JSON (preferred) or SPDX

**Contents**:
- All Python dependencies (from requirements.txt / pyproject.toml)
- System libraries (if containerized)
- Any ML models or data files used in generation

### 7.3 Cosign Usage

**Requirement**: All QRG artifacts MUST be signed using cosign for tamper-evidence.

**Implementation**:
```bash
# Sign artifact metadata using cosign (keyless or KMS-backed)
cosign sign-blob --key kms://aws-kms/key-id artifact-metadata.json > artifact.sig

# Generate attestation bundle
cosign attest --key kms://aws-kms/key-id --predicate artifact-metadata.json

# Store attestation
aws s3 cp attestation.att s3://lukhas-qrg-attestations/550e8400.att
```

**Key Management**:
- **DO NOT** store private keys in repository or environment variables
- **USE** AWS KMS, Google Cloud KMS, or Azure Key Vault for key storage
- **ROTATE** keys quarterly and maintain key audit logs
- **DOCUMENT** key ARNs/URIs in infrastructure docs (not in code)

**Verification**:
```bash
# Verify artifact signature
cosign verify-blob --key kms://aws-kms/key-id --signature artifact.sig artifact-metadata.json
```

### 7.4 Builder Identity

**Requirement**: Builder identity MUST be cryptographically verifiable and auditable.

**Implementation**:
- Use service account identities (e.g., AWS IAM roles, GCP service accounts)
- Include workload identity in attestation (e.g., OIDC token from GitHub Actions, EKS pod identity)
- Log builder identity to audit trails for incident response

**Example builder_id**:
```
lukhas-qrg-service-prod-us-east-1
├─ Service: lukhas-qrg-service
├─ Environment: prod
├─ Region: us-east-1
└─ IAM Role: arn:aws:iam::123456789012:role/lukhas-qrg-service-prod
```

---

## 8. Telemetry & Observability

### 8.1 OpenTelemetry Spans

**Requirement**: All QRG operations MUST emit OTEL spans for distributed tracing.

**Span Structure**:
```python
from opentelemetry import trace

tracer = trace.get_tracer("lukhas.qrg", version="0.1.0")

with tracer.start_as_current_span("qrg.generate") as span:
    span.set_attribute("qrg.user_id", user_id)
    span.set_attribute("qrg.seed", seed[:16])  # Truncate for PII safety
    span.set_attribute("qrg.tier_level", context.get("tier_level", 1))
    span.set_attribute("qrg.entropy_source", options.get("entropy_source", "pseudo_rng"))

    with tracer.start_as_current_span("qrg.generate.artifact"):
        artifact = await _generate_artifact(seed, context, options)

    with tracer.start_as_current_span("qrg.generate.safety_checks"):
        safety = await _check_safety(artifact, context)
        span.set_attribute("qrg.safety.status", safety["status"])

    with tracer.start_as_current_span("qrg.generate.provenance"):
        provenance = await _create_provenance(artifact, metadata)

    span.set_attribute("qrg.qrg_id", qrg_id)
    span.set_attribute("qrg.total_time_ms", total_time_ms)
```

**Span Names**:
- `qrg.generate` - Full artifact generation
- `qrg.generate.artifact` - Artifact generation only
- `qrg.generate.safety_checks` - Safety gate checks
- `qrg.generate.provenance` - Provenance creation
- `qrg.validate` - Artifact validation

### 8.2 Prometheus Metrics

**Requirement**: All QRG operations MUST emit Prometheus metrics for monitoring.

**Metric Definitions**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Generation counters
qrg_generations_total = Counter(
    "qrg_generations_total",
    "Total QRG artifacts generated",
    ["tier_level", "entropy_source", "status"]
)

qrg_generations_total.labels(tier_level=4, entropy_source="pseudo_rng", status="success").inc()

# Generation duration histogram
qrg_generation_duration_seconds = Histogram(
    "qrg_generation_duration_seconds",
    "Time to generate QRG artifact",
    ["tier_level"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

qrg_generation_duration_seconds.labels(tier_level=4).observe(0.58)

# Safety check metrics
qrg_safety_rejections_total = Counter(
    "qrg_safety_rejections_total",
    "Total QRG artifacts rejected by safety gates",
    ["gate_type", "reason"]
)

qrg_safety_score = Histogram(
    "qrg_safety_score",
    "Safety gate scores",
    ["gate_type"],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
)

# Provenance metrics
qrg_provenance_slsa_level = Gauge(
    "qrg_provenance_slsa_level",
    "SLSA provenance level",
    ["qrg_id"]
)

qrg_signature_verifications_total = Counter(
    "qrg_signature_verifications_total",
    "Total signature verifications",
    ["status"]
)

# Cognitive load metrics
qrg_cognitive_load = Histogram(
    "qrg_cognitive_load",
    "Estimated cognitive load of artifacts",
    ["tier_level"],
    buckets=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
)
```

**Alerting Rules**:
```yaml
# Example Prometheus alerting rules
groups:
  - name: qrg_alerts
    rules:
      - alert: QRGHighRejectionRate
        expr: rate(qrg_safety_rejections_total[5m]) > 0.1
        for: 10m
        annotations:
          summary: "QRG safety rejection rate >10%"
          description: "Safety gates rejecting {{ $value }}% of artifacts"

      - alert: QRGSlowGeneration
        expr: histogram_quantile(0.95, qrg_generation_duration_seconds) > 5.0
        for: 5m
        annotations:
          summary: "QRG p95 generation latency >5s"
          description: "95th percentile generation time: {{ $value }}s"
```

---

## 9. Performance & Cost Targets

### 9.1 Latency Budget

| Operation | Target p50 | Target p95 | Target p99 | Notes |
|-----------|-----------|-----------|-----------|-------|
| **Generate** | <500ms | <2s | <5s | Full artifact generation including safety checks |
| **Validate** | <100ms | <250ms | <500ms | Signature verification + hash check |
| **Health Check** | <50ms | <100ms | <200ms | Adapter health endpoint |

**Timeout Defaults**:
- Default `timeout_ms`: 5000 (5 seconds)
- Min timeout: 100ms (for health checks)
- Max timeout: 30000 (30 seconds, for complex consensus operations)

### 9.2 Resource Usage Estimates

| Resource | Per-Request Estimate | Notes |
|----------|---------------------|-------|
| **Memory** | 50-100 MB | Depends on artifact complexity and consciousness state processing |
| **CPU** | 0.1-0.5 core-seconds | Cryptographic operations, safety gate inference, provenance generation |
| **Storage (per artifact)** | 1-10 KB | Metadata + SBOM ref + attestation ref (actual artifact stored separately) |
| **Network (per request)** | 5-50 KB | Request + response payload (excludes artifact content if large) |

### 9.3 Job Model for Mesh Consensus

**Consensus Jobs** (when `consensus_required: true`):
- Distributed artifact generation across N nodes (N = 3 for Phase 2)
- Each node generates independently and submits result
- Consensus coordinator aggregates and validates results
- Agreement threshold: 2/3 (67%) for approval

**Job Lifecycle**:
1. **Submitted**: User requests QRG with `consensus_required: true`
2. **Distributed**: Coordinator distributes job to N nodes
3. **Generating**: Each node generates artifact independently
4. **Voting**: Nodes submit results and vote on validity
5. **Consensus**: Coordinator checks if ≥2/3 nodes agree
6. **Completed**: Consensus artifact returned to user
7. **Failed**: If <2/3 agreement, retry or reject

**Job Timeout**: 3x normal generation timeout (default 15s)

**Metrics**:
```python
qrg_consensus_jobs_total = Counter(
    "qrg_consensus_jobs_total",
    "Total consensus jobs",
    ["status"]  # submitted, completed, failed, timeout
)

qrg_consensus_agreement_score = Histogram(
    "qrg_consensus_agreement_score",
    "Consensus agreement score",
    buckets=[0.0, 0.33, 0.5, 0.67, 0.8, 0.9, 1.0]
)
```

---

## 10. Integration Points

### 10.1 LUKHAS Core Integration

| System | Integration Point | Purpose |
|--------|-------------------|---------|
| **Consciousness Engine** | `consciousness.core_consciousness` | Adapt artifact generation to emotional state |
| **Guardian System** | `core.interfaces.as_agent.core.gatekeeper` | Constitutional compliance checks |
| **Cultural Safety** | `utils.cultural_safety_checker` | Validate symbolic content safety |
| **Cognitive Load** | `utils.cognitive_load_estimator` | Estimate and warn about artifact complexity |
| **Identity** | `lukhas.identity.lambda_id` | User authentication and tier validation |
| **MATRIZ** | `matriz/` | Distributed consensus orchestration |

### 10.2 LUKHAS Wrappers Integration

| Wrapper | Location | Purpose |
|---------|----------|---------|
| **Consciousness Wrapper** | `lukhas/consciousness/` | High-level consciousness API |
| **Dreams Wrapper** | `lukhas/dreams/` | Dream generation and interpretation |
| **Glyphs Wrapper** | `lukhas/glyphs/` | Glyph rendering and visualization |

**Note**: QRG adapters will call wrappers (not core directly) for better abstraction and versioning.

---

## 11. Acceptance Criteria

### Phase 0 → Phase 1 (Spec Approval)

- [ ] **Specification reviewed** by Security, Safety, and Consciousness stewards
- [ ] **ADR approved** with phased rollout plan and gating criteria
- [ ] **Cryptography reviewer assigned** for PQC/attestation decisions
- [ ] **No unresolved critical questions** in spec or ADR
- [ ] **Merge to main** as documentation-only change (no code)

### Phase 1 (Adapter & Sandbox)

- [ ] **Adapter interface implemented** (`lukhas/quantum/qrg_adapter.py`) with full type hints
- [ ] **MockQRGAdapter** implemented in `docs/examples/mock_qrg_adapter.py` with deterministic outputs
- [ ] **Unit tests** for MockQRGAdapter with ≥90% coverage
- [ ] **Sandbox test suite** (`tests/sandbox/test_mock_qrg_adapter.py`) passing
- [ ] **Feature flags** (`QRG_ENABLED`, `QRG_CONSCIOUSNESS_ENABLED`, `QRG_CONSENSUS_ENABLED`) functional
- [ ] **OpenAPI spec** (`docs/examples/qrg_openapi_snippet.yaml`) validated
- [ ] **Developer documentation** for using mock vs production adapters

### Phase 2 (Governed Production)

- [ ] **Production adapter** implemented with real consciousness/Guardian/safety integrations
- [ ] **Zero mock implementations** in production code paths
- [ ] **PQC/attestation** system operational with KMS key management
- [ ] **SBOM generation** automated (syft integration)
- [ ] **Cosign attestation** automated (CI/CD pipeline integration)
- [ ] **SLSA Level 3** provenance achieved
- [ ] **All safety gates** (Constitutional, Cultural, Cognitive) operational
- [ ] **OTEL spans** emitted for all operations
- [ ] **Prometheus metrics** exposed and dashboards created
- [ ] **Performance benchmarks** met (p95 <2s for generate, p95 <250ms for validate)
- [ ] **Cryptographer sign-off** for PQC algorithm choices
- [ ] **Security audit** (external firm) with no critical findings
- [ ] **Incident response playbook** documented

---

## 12. Cryptography & Key Management Guidance

### 12.1 Post-Quantum Cryptography (PQC) Recommendations

**Status**: **RECOMMENDATION ONLY** - Requires cryptographer approval before implementation.

**Candidate Algorithms (NIST PQC Finalists)**:
1. **Key Encapsulation**: Kyber-1024 (ML-KEM)
2. **Digital Signatures**: Dilithium-5 (ML-DSA) or Falcon-1024
3. **Hash Functions**: SHA3-256, BLAKE3

**Fallback (Pre-PQC)**:
- **Signatures**: Ed25519 (current standard until PQC deployed)
- **Key Exchange**: X25519
- **Hashing**: SHA-256

**Decision Point**: Phase 1 - Cryptographer must evaluate and approve PQC algorithm selection based on:
- NIST standardization status (as of 2025-11-10)
- Library maturity and audit status (e.g., liboqs, pq-crystals)
- Performance characteristics (latency, key size)
- Quantum threat timeline assessment

### 12.2 Key Management Recommendations

**DO NOT** implement key generation or storage without steward review. Recommendations:

1. **Key Storage**:
   - **AWS KMS**: `arn:aws:kms:region:account-id:key/key-id`
   - **Google Cloud KMS**: `projects/PROJECT_ID/locations/LOCATION/keyRings/KEY_RING/cryptoKeys/KEY`
   - **Azure Key Vault**: `https://vault-name.vault.azure.net/keys/key-name`

2. **Key Rotation**:
   - Quarterly rotation for signing keys
   - Immediate rotation if compromise suspected
   - Maintain key audit logs (CloudTrail, Cloud Audit Logs, etc.)

3. **Key Access Control**:
   - Service accounts only (no personal credentials)
   - Principle of least privilege (PoLP)
   - Multi-party approval for key operations (if available)

4. **Secrets Management**:
   - **GitHub Secrets** for CI/CD pipelines
   - **Kubernetes Secrets** with encryption at rest
   - **Never** commit keys or secrets to repository

### 12.3 Entropy Sources

**Production** (Phase 2):
- **Primary**: Quantum RNG (vendor TBD - requires evaluation)
- **Fallback**: `secrets.SystemRandom()` (Python) with audit logging

**Development/Sandbox** (Phase 0-1):
- **Mock**: Deterministic PRNG with fixed seed (for testing)
- **Warning logs**: All artifacts generated with non-quantum entropy MUST be logged

---

## 13. Open Questions & Risk Assessment

### 13.1 Open Questions

1. **Q**: Which quantum RNG provider should we use for production entropy?
   **A**: Phase 1 decision - evaluate NIST Randomness Beacon (free), ANU Quantum (research), ID Quantique (enterprise). Decision criteria: cost, reliability, latency, geographic distribution.

2. **Q**: Should QRG artifacts be stored on-chain (blockchain) for immutability?
   **A**: Not in Phase 0-2. SLSA + cosign attestations provide sufficient provenance. Blockchain integration can be considered in Phase 3+ if required by compliance or product needs.

3. **Q**: How do we handle consciousness state unavailable (user blocks telemetry)?
   **A**: Graceful degradation - generate artifact without consciousness adaptation. Set `consciousness_state: null` in context and log as `consciousness_disabled` metric.

4. **Q**: What is the budget for external security audit?
   **A**: TBD - estimate $15K-$30K for PQC + consciousness system review. Product lead approval required.

5. **Q**: Should consensus be synchronous (blocking) or asynchronous (job queue)?
   **A**: Phase 1 decision - async job queue preferred for production scalability. Sync blocking acceptable for Phase 1 sandbox testing.

### 13.2 Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| **PQC algorithm breaks pre-standardization** | High | Low | Use NIST finalists only; plan for algorithm agility; maintain fallback to classical crypto |
| **Safety gate latency >1s** | Medium | Medium | Async safety checks; cache safety models; set aggressive timeouts; fallback to default-deny |
| **Provenance service downtime** | Medium | Low | Fallback to local signing (with degraded SLSA level); queue attestations for retry; alert on-call |
| **KMS rate limiting / outage** | High | Low | Cache KMS responses; use multiple regions; implement exponential backoff; fallback to local keys (with audit) |
| **Consensus nodes disagree (Byzantine fault)** | Medium | Low | Require 2/3 agreement threshold; log all disagreements; manual review for repeated conflicts |
| **Cultural safety false positives** | Low | Medium | Human review queue for edge cases; user appeal process; continuous model retraining |
| **Cognitive load overestimation** | Low | Low | Warnings only (non-blocking for T4+); user feedback loop; model calibration |

---

## 14. References

- [NIST Post-Quantum Cryptography Project](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [SLSA Supply Chain Security Framework](https://slsa.dev)
- [Sigstore Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [CycloneDX SBOM Specification](https://cyclonedx.org)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [LUKHAS Guardian System Architecture](../architecture/guardian_system.md) (if exists)
- [LUKHAS Consciousness Engine Documentation](../../consciousness/core_consciousness/README.md) (if exists)
- [LUKHAS Lambda ID Specification](../../lukhas/identity/lambda_id.py) (if exists)

---

## 15. Document History

- **2025-11-10**: Initial draft (v0.1.0) - Phase 0 specification
- **TBD**: Phase 1 updates (adapter implementation, sandbox testing)
- **TBD**: Phase 2 updates (production deployment, cryptography sign-off)

---

## Appendix A: Glossary

- **QRG**: Quantum Reality Generation - System for generating consciousness-aware symbolic artifacts
- **SLSA**: Supply chain Levels for Software Artifacts - Framework for supply chain security
- **SBOM**: Software Bill of Materials - Inventory of software components and dependencies
- **Cosign**: Sigstore tool for signing and verifying container images and artifacts
- **PQC**: Post-Quantum Cryptography - Cryptographic algorithms resistant to quantum attacks
- **KMS**: Key Management Service - Cloud service for cryptographic key storage and operations
- **OTEL**: OpenTelemetry - Observability framework for distributed tracing and metrics
- **ADR**: Architecture Decision Record - Document capturing important architectural decisions
- **T4**: Tier 4 - High-privilege user tier in LUKHAS identity system
- **ConstitutionalGatekeeper**: Guardian system component enforcing ethical compliance
- **CulturalSafetyChecker**: Safety system component validating cultural appropriateness
- **CognitiveLoadEstimator**: System component estimating mental load of artifacts

---

**END OF SPECIFICATION**
