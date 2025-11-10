"""
Mock QRG Adapter - Sandbox-only implementation for testing

⚠️ WARNING: This is a SANDBOX-ONLY mock implementation.
NEVER use this adapter in production code paths.

Purpose:
- Provide deterministic QRG artifact generation for integration testing
- Enable development and testing without consciousness/safety/provenance dependencies
- Serve as reference implementation for QRGAdapter protocol

Usage:
    from docs.examples.mock_qrg_adapter import MockQRGAdapter

    adapter = MockQRGAdapter()
    response = await adapter.generate(
        user_id="lid:test123",
        seed="test-seed-deterministic",
        context={"tier_level": 4},
        options={"entropy_source": "pseudo_rng"}
    )

Python Version: 3.9.6+
"""

import asyncio
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

# Type aliases for clarity
QRGRequest = Dict[str, Any]
QRGResponse = Dict[str, Any]


@dataclass
class MockQRGAdapter:
    """
    Sandbox-only deterministic QRG adapter for integration testing.

    This adapter generates predictable QRG artifacts based on input seeds,
    enabling reproducible testing without external dependencies.

    Attributes:
        deterministic_mode: If True, use seed for deterministic UUIDs (default: True)
        mock_builder_id: Builder ID for provenance (default: "mock-qrg-builder")
        version: Adapter version for health checks (default: "0.1.0-mock")
    """

    deterministic_mode: bool = True
    mock_builder_id: str = "mock-qrg-builder"
    version: str = "0.1.0-mock"

    async def generate(
        self,
        user_id: str,
        seed: str,
        context: Dict[str, Any],
        options: Dict[str, Any] | None = None
    ) -> QRGResponse:
        """
        Generate a deterministic mock QRG artifact.

        Args:
            user_id: Lambda ID or internal user identifier (e.g., lid:abc123...)
            seed: Cryptographic seed for deterministic artifact generation
            context: Contextual metadata including consciousness_state, cultural_context, tier_level
            options: Optional parameters (entropy_source, consensus_required, timeout_ms)

        Returns:
            QRGResponse dict conforming to QRG_SPEC.md Section 4.2 schema

        Example:
            >>> adapter = MockQRGAdapter()
            >>> response = await adapter.generate(
            ...     user_id="lid:test123",
            ...     seed="test-seed",
            ...     context={"tier_level": 4}
            ... )
            >>> assert response["seed"] == "test-seed"
            >>> assert response["qrg_id"].startswith("qrg:")
        """
        import time

        start_time = time.time()
        options = options or {}

        # Simulate async non-blocking operation
        await asyncio.sleep(0)

        # Generate deterministic QRG ID from seed
        if self.deterministic_mode:
            # Use seed to create deterministic UUID (for testing)
            seed_hash = hashlib.sha256(seed.encode()).hexdigest()
            qrg_id = f"qrg:{seed_hash[:8]}-{seed_hash[8:12]}-{seed_hash[12:16]}-{seed_hash[16:20]}-{seed_hash[20:32]}"
        else:
            qrg_id = f"qrg:{uuid.uuid4()}"

        # Generate mock artifact
        generation_time_ms = 450  # Mock: 450ms generation time
        artifact = {
            "type": "symbolic",
            "location": f"mock://{qrg_id}",
            "hash": f"sha256:{hashlib.sha256(seed.encode()).hexdigest()}",
            "size_bytes": 2048,
            "content_type": "application/json"
        }

        # Generate deterministic symbolic payload from seed
        token_count = len(seed) % 5 + 3  # 3-7 tokens based on seed length
        tokens = [f"token{i}_{seed[:4]}" for i in range(token_count)]

        # Generate affect vector (deterministic based on seed)
        seed_bytes = seed.encode()
        affect_vector = [
            (seed_bytes[i % len(seed_bytes)] / 255.0) for i in range(4)
        ]

        symbolic_payload = {
            "tokens": tokens,
            "affect_vector": affect_vector,
            "metadata": {
                "dimensionality": len(affect_vector),
                "entropy_bits": 256,
                "mock_mode": True
            }
        }

        # Run mock safety checks
        safety_check_time_ms = 120  # Mock: 120ms safety check time
        safety = self._mock_safety_checks(context)

        # Create mock provenance
        provenance = self._mock_provenance(qrg_id, user_id, seed, context, options)

        total_time_ms = int((time.time() - start_time) * 1000)

        return {
            "qrg_id": qrg_id,
            "seed": seed,
            "artifact": artifact,
            "symbolic_payload": symbolic_payload,
            "safety": safety,
            "provenance": provenance,
            "metrics": {
                "generation_time_ms": generation_time_ms,
                "safety_check_time_ms": safety_check_time_ms,
                "total_time_ms": total_time_ms
            }
        }

    def _mock_safety_checks(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock safety check results.

        In production, this would call real ConstitutionalGatekeeper,
        CulturalSafetyChecker, and CognitiveLoadEstimator.

        Args:
            context: Request context with consciousness_state, cultural_context, etc.

        Returns:
            Safety check results dict
        """
        # Mock: Always approve unless context contains "reject" flag
        should_reject = context.get("_mock_reject", False)

        if should_reject:
            return {
                "status": "rejected",
                "gate_checks": {
                    "ConstitutionalGatekeeper": {
                        "status": "rejected",
                        "reason": "Mock rejection for testing",
                        "score": 0.3
                    }
                },
                "warnings": ["Mock rejection enabled via context._mock_reject"]
            }

        # Default: Approve all gates
        return {
            "status": "approved",
            "gate_checks": {
                "ConstitutionalGatekeeper": {
                    "status": "approved",
                    "reason": "Mock approval (sandbox mode)",
                    "score": 0.95
                },
                "CulturalSafetyChecker": {
                    "status": "approved",
                    "reason": "Mock approval (sandbox mode)",
                    "score": 0.92
                },
                "CognitiveLoadEstimator": {
                    "status": "approved",
                    "estimated_load": 0.4,
                    "warnings": []
                }
            },
            "warnings": []
        }

    def _mock_provenance(
        self,
        qrg_id: str,
        user_id: str,
        seed: str,
        context: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate mock provenance block.

        In production, this would generate real SBOM refs, cosign attestations,
        and cryptographic signatures.

        Args:
            qrg_id: Generated QRG artifact ID
            user_id: User identifier
            seed: Generation seed
            context: Request context
            options: Request options

        Returns:
            Provenance dict with SBOM refs, attestations, signatures
        """
        build_time = datetime.now(timezone.utc).isoformat()

        # Mock signature (NOT cryptographically valid)
        mock_payload = f"{qrg_id}:{seed}:{user_id}".encode()
        mock_signature = hashlib.sha256(mock_payload).hexdigest()[:32]

        return {
            "builder_id": self.mock_builder_id,
            "build_time": build_time,
            "sbom_ref": f"mock://sbom/{qrg_id}.cdx.json",
            "attestation_ref": f"mock://attestations/{qrg_id}.att",
            "slsa_level": 0,  # Mock: SLSA Level 0 (no provenance)
            "signature": {
                "algorithm": "mock-sha256",
                "public_key_ref": "mock://keys/qrg-mock.pub",
                "signature_b64": mock_signature
            },
            "consensus": {
                "required": options.get("consensus_required", False),
                "participants": 1,
                "agreement_score": 1.0,
                "job_id": f"mock-job-{qrg_id[:8]}"
            }
        }

    async def validate(
        self,
        qrg_id: str,
        expected_hash: str
    ) -> Dict[str, bool]:
        """
        Validate a mock QRG artifact's integrity.

        In production, this would verify signatures, SBOM integrity, and provenance.

        Args:
            qrg_id: QRG artifact identifier (e.g., qrg:uuid)
            expected_hash: Expected cryptographic hash (e.g., sha256:...)

        Returns:
            Validation results dict:
                {
                    "valid": bool,
                    "hash_match": bool,
                    "signature_valid": bool,
                    "provenance_verified": bool
                }

        Example:
            >>> adapter = MockQRGAdapter()
            >>> result = await adapter.validate(
            ...     qrg_id="qrg:abc123",
            ...     expected_hash="sha256:def456"
            ... )
            >>> assert result["valid"] is True  # Mock always validates
        """
        await asyncio.sleep(0)  # Simulate async operation

        # Mock: Always validate successfully
        return {
            "valid": True,
            "hash_match": True,
            "signature_valid": True,
            "provenance_verified": True
        }

    async def health(self) -> Dict[str, Any]:
        """
        Check mock adapter health.

        Returns:
            Health check dict:
                {
                    "status": "healthy" | "degraded" | "unhealthy",
                    "checks": {
                        "safety_gates": "ok" | "error",
                        "provenance_service": "ok" | "error",
                        "artifact_storage": "ok" | "error"
                    },
                    "version": str,
                    "mode": "mock"
                }

        Example:
            >>> adapter = MockQRGAdapter()
            >>> health = await adapter.health()
            >>> assert health["status"] == "healthy"
            >>> assert health["mode"] == "mock"
        """
        await asyncio.sleep(0)

        return {
            "status": "healthy",
            "checks": {
                "safety_gates": "ok",
                "provenance_service": "ok",
                "artifact_storage": "ok"
            },
            "version": self.version,
            "mode": "mock"
        }


# Example usage (for testing)
async def main():
    """
    Example usage of MockQRGAdapter.

    This demonstrates deterministic artifact generation for testing.
    """
    adapter = MockQRGAdapter()

    # Test 1: Basic generation
    response = await adapter.generate(
        user_id="lid:test123",
        seed="test-seed-deterministic",
        context={
            "consciousness_state": {
                "emotional_valence": 0.7,
                "cognitive_load": 0.3,
                "attention_focus": 0.8
            },
            "cultural_context": {
                "languages": ["en", "es"],
                "regions": ["US", "MX"]
            },
            "tier_level": 4
        },
        options={
            "entropy_source": "pseudo_rng",
            "consensus_required": False,
            "timeout_ms": 5000
        }
    )

    print("✅ Generated QRG artifact:")
    print(f"   QRG ID: {response['qrg_id']}")
    print(f"   Safety Status: {response['safety']['status']}")
    print(f"   Tokens: {response['symbolic_payload']['tokens']}")
    print(f"   Generation Time: {response['metrics']['generation_time_ms']}ms")

    # Test 2: Validation
    validation = await adapter.validate(
        qrg_id=response["qrg_id"],
        expected_hash=response["artifact"]["hash"]
    )
    print(f"\n✅ Validation: {validation}")

    # Test 3: Health check
    health = await adapter.health()
    print(f"\n✅ Health: {health['status']} (mode: {health['mode']})")


if __name__ == "__main__":
    print("MockQRGAdapter - Sandbox-only QRG implementation")
    print("=" * 60)
    asyncio.run(main())
