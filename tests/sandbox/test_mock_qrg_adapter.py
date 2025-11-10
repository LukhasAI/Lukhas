"""
Unit tests for MockQRGAdapter (sandbox-only)

Tests the deterministic behavior of the mock QRG adapter
for integration testing purposes.

Test Coverage:
- Deterministic artifact generation
- Safety gate simulation (approve/reject)
- Provenance block generation
- Validation endpoint
- Health check endpoint

Python Version: 3.9.6+
Test Framework: pytest + pytest-asyncio

Run tests:
    pytest tests/sandbox/test_mock_qrg_adapter.py -v
"""

import pytest
import sys
from pathlib import Path

# Add docs/examples to path for importing MockQRGAdapter
docs_examples_path = Path(__file__).parent.parent.parent / "docs" / "examples"
sys.path.insert(0, str(docs_examples_path))

from mock_qrg_adapter import MockQRGAdapter


class TestMockQRGAdapterGenerate:
    """Test suite for MockQRGAdapter.generate() method"""

    @pytest.mark.asyncio
    async def test_basic_generation(self):
        """Test basic QRG artifact generation with minimal context"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed-basic",
            context={"tier_level": 4},
            options=None
        )

        # Assert response structure
        assert "qrg_id" in response
        assert response["qrg_id"].startswith("qrg:")
        assert response["seed"] == "test-seed-basic"
        assert "artifact" in response
        assert "symbolic_payload" in response
        assert "safety" in response
        assert "provenance" in response
        assert "metrics" in response

    @pytest.mark.asyncio
    async def test_deterministic_qrg_id(self):
        """Test that same seed produces same QRG ID (deterministic)"""
        adapter = MockQRGAdapter(deterministic_mode=True)

        seed = "deterministic-seed-123"
        response1 = await adapter.generate(
            user_id="lid:user1",
            seed=seed,
            context={"tier_level": 4}
        )

        response2 = await adapter.generate(
            user_id="lid:user2",
            seed=seed,
            context={"tier_level": 4}
        )

        # Same seed should produce same QRG ID
        assert response1["qrg_id"] == response2["qrg_id"]

    @pytest.mark.asyncio
    async def test_different_seeds_different_qrg_ids(self):
        """Test that different seeds produce different QRG IDs"""
        adapter = MockQRGAdapter(deterministic_mode=True)

        response1 = await adapter.generate(
            user_id="lid:user1",
            seed="seed-one",
            context={"tier_level": 4}
        )

        response2 = await adapter.generate(
            user_id="lid:user1",
            seed="seed-two",
            context={"tier_level": 4}
        )

        # Different seeds should produce different QRG IDs
        assert response1["qrg_id"] != response2["qrg_id"]

    @pytest.mark.asyncio
    async def test_artifact_structure(self):
        """Test artifact structure conforms to spec"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed-artifact",
            context={"tier_level": 4}
        )

        artifact = response["artifact"]
        assert artifact["type"] == "symbolic"
        assert artifact["location"].startswith("mock://")
        assert artifact["hash"].startswith("sha256:")
        assert artifact["size_bytes"] > 0
        assert artifact["content_type"] == "application/json"

    @pytest.mark.asyncio
    async def test_symbolic_payload_deterministic(self):
        """Test symbolic payload is deterministic based on seed"""
        adapter = MockQRGAdapter(deterministic_mode=True)

        seed = "payload-seed-xyz"
        response1 = await adapter.generate(
            user_id="lid:user1",
            seed=seed,
            context={"tier_level": 4}
        )

        response2 = await adapter.generate(
            user_id="lid:user2",
            seed=seed,
            context={"tier_level": 4}
        )

        # Same seed should produce same tokens and affect vector
        assert response1["symbolic_payload"]["tokens"] == response2["symbolic_payload"]["tokens"]
        assert response1["symbolic_payload"]["affect_vector"] == response2["symbolic_payload"]["affect_vector"]

    @pytest.mark.asyncio
    async def test_symbolic_payload_structure(self):
        """Test symbolic payload structure"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-payload",
            context={"tier_level": 4}
        )

        payload = response["symbolic_payload"]
        assert "tokens" in payload
        assert isinstance(payload["tokens"], list)
        assert len(payload["tokens"]) > 0
        assert "affect_vector" in payload
        assert isinstance(payload["affect_vector"], list)
        assert len(payload["affect_vector"]) == 4
        assert all(0.0 <= v <= 1.0 for v in payload["affect_vector"])


class TestMockQRGAdapterSafety:
    """Test suite for safety gate simulation"""

    @pytest.mark.asyncio
    async def test_safety_approved_by_default(self):
        """Test that safety gates approve by default"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        safety = response["safety"]
        assert safety["status"] == "approved"
        assert "gate_checks" in safety
        assert safety["gate_checks"]["ConstitutionalGatekeeper"]["status"] == "approved"
        assert safety["gate_checks"]["CulturalSafetyChecker"]["status"] == "approved"
        assert safety["gate_checks"]["CognitiveLoadEstimator"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_safety_rejection_via_context(self):
        """Test that safety gates can reject via context flag"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4, "_mock_reject": True}
        )

        safety = response["safety"]
        assert safety["status"] == "rejected"
        assert safety["gate_checks"]["ConstitutionalGatekeeper"]["status"] == "rejected"
        assert len(safety["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_safety_gate_scores(self):
        """Test that safety gate scores are present and valid"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        safety = response["safety"]
        constitutional_score = safety["gate_checks"]["ConstitutionalGatekeeper"]["score"]
        cultural_score = safety["gate_checks"]["CulturalSafetyChecker"]["score"]

        assert 0.0 <= constitutional_score <= 1.0
        assert 0.0 <= cultural_score <= 1.0


class TestMockQRGAdapterProvenance:
    """Test suite for provenance block generation"""

    @pytest.mark.asyncio
    async def test_provenance_structure(self):
        """Test provenance block structure"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        provenance = response["provenance"]
        assert "builder_id" in provenance
        assert provenance["builder_id"] == adapter.mock_builder_id
        assert "build_time" in provenance
        assert "sbom_ref" in provenance
        assert provenance["sbom_ref"].startswith("mock://sbom/")
        assert "attestation_ref" in provenance
        assert provenance["attestation_ref"].startswith("mock://attestations/")
        assert "slsa_level" in provenance
        assert provenance["slsa_level"] == 0  # Mock: SLSA Level 0
        assert "signature" in provenance
        assert "consensus" in provenance

    @pytest.mark.asyncio
    async def test_signature_structure(self):
        """Test signature block structure"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        signature = response["provenance"]["signature"]
        assert signature["algorithm"] == "mock-sha256"
        assert signature["public_key_ref"] == "mock://keys/qrg-mock.pub"
        assert len(signature["signature_b64"]) > 0

    @pytest.mark.asyncio
    async def test_consensus_metadata(self):
        """Test consensus metadata structure"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4},
            options={"consensus_required": True}
        )

        consensus = response["provenance"]["consensus"]
        assert consensus["required"] is True
        assert consensus["participants"] == 1
        assert consensus["agreement_score"] == 1.0
        assert "job_id" in consensus


class TestMockQRGAdapterMetrics:
    """Test suite for metrics block"""

    @pytest.mark.asyncio
    async def test_metrics_structure(self):
        """Test metrics block structure"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        metrics = response["metrics"]
        assert "generation_time_ms" in metrics
        assert "safety_check_time_ms" in metrics
        assert "total_time_ms" in metrics
        assert metrics["generation_time_ms"] > 0
        assert metrics["safety_check_time_ms"] > 0
        assert metrics["total_time_ms"] > 0


class TestMockQRGAdapterValidate:
    """Test suite for MockQRGAdapter.validate() method"""

    @pytest.mark.asyncio
    async def test_validate_success(self):
        """Test validation endpoint always succeeds (mock)"""
        adapter = MockQRGAdapter()

        # Generate artifact first
        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={"tier_level": 4}
        )

        # Validate artifact
        validation = await adapter.validate(
            qrg_id=response["qrg_id"],
            expected_hash=response["artifact"]["hash"]
        )

        assert validation["valid"] is True
        assert validation["hash_match"] is True
        assert validation["signature_valid"] is True
        assert validation["provenance_verified"] is True

    @pytest.mark.asyncio
    async def test_validate_structure(self):
        """Test validation response structure"""
        adapter = MockQRGAdapter()

        validation = await adapter.validate(
            qrg_id="qrg:test-id",
            expected_hash="sha256:test-hash"
        )

        # Mock always returns True for all checks
        assert "valid" in validation
        assert "hash_match" in validation
        assert "signature_valid" in validation
        assert "provenance_verified" in validation


class TestMockQRGAdapterHealth:
    """Test suite for MockQRGAdapter.health() method"""

    @pytest.mark.asyncio
    async def test_health_structure(self):
        """Test health check structure"""
        adapter = MockQRGAdapter()

        health = await adapter.health()

        assert "status" in health
        assert health["status"] == "healthy"
        assert "checks" in health
        assert health["checks"]["safety_gates"] == "ok"
        assert health["checks"]["provenance_service"] == "ok"
        assert health["checks"]["artifact_storage"] == "ok"
        assert "version" in health
        assert health["version"] == adapter.version
        assert "mode" in health
        assert health["mode"] == "mock"

    @pytest.mark.asyncio
    async def test_health_always_healthy(self):
        """Test that mock adapter always reports healthy"""
        adapter = MockQRGAdapter()

        health = await adapter.health()

        assert health["status"] == "healthy"


class TestMockQRGAdapterEdgeCases:
    """Test suite for edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_empty_context(self):
        """Test generation with empty context"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="test-seed",
            context={},
            options=None
        )

        # Should still generate valid artifact
        assert response["qrg_id"].startswith("qrg:")
        assert response["safety"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_minimal_seed(self):
        """Test generation with minimal seed length"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="x" * 16,  # Minimum 16 chars per spec
            context={"tier_level": 4}
        )

        assert response["qrg_id"].startswith("qrg:")
        assert len(response["symbolic_payload"]["tokens"]) > 0

    @pytest.mark.asyncio
    async def test_long_seed(self):
        """Test generation with maximum seed length"""
        adapter = MockQRGAdapter()

        long_seed = "x" * 256  # Maximum 256 chars per spec
        response = await adapter.generate(
            user_id="lid:test123",
            seed=long_seed,
            context={"tier_level": 4}
        )

        assert response["qrg_id"].startswith("qrg:")
        assert response["seed"] == long_seed

    @pytest.mark.asyncio
    async def test_consciousness_context(self):
        """Test generation with full consciousness context"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="consciousness-seed",
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
            }
        )

        # Mock doesn't use consciousness state but should accept it
        assert response["safety"]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_all_options(self):
        """Test generation with all options specified"""
        adapter = MockQRGAdapter()

        response = await adapter.generate(
            user_id="lid:test123",
            seed="options-seed",
            context={"tier_level": 4},
            options={
                "entropy_source": "quantum_rng",
                "consensus_required": True,
                "timeout_ms": 10000
            }
        )

        assert response["provenance"]["consensus"]["required"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
