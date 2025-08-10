"""
Test Suite for VeriFold Unified System
=====================================

Comprehensive tests for the unified VeriFold system that replaces CollapseHash
and integrates with the LAMBDA_TIER framework.

Tests cover:
- VeriFold hash generation and verification
- Tier-based access control
- Collapse monitoring and intervention
- Cross-system integration
- Backward compatibility with CollapseHash

Author: LUKHAS AGI System
Last Updated: 2025-07-26
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Import the unified VeriFold system
from core.verifold.verifold_unified import (
    UnifiedVeriFoldSystem,
    VeriFoldCollapseType,
    VeriFoldPhase,
    VeriFoldRecord,
    VeriFoldSnapshot,
    generate_verifold_hash,
    get_global_verifold_system,
    verify_verifold_hash,
)


class TestVeriFoldUnifiedSystem:
    """Test suite for the main VeriFold unified system."""

    def setup_method(self):
        """Setup test environment."""
        self.system = UnifiedVeriFoldSystem()
        self.test_user_id = "test_user_lambda_tier_3"
        self.test_tier = "LAMBDA_TIER_3"

        # Mock identity context
        self.identity_patcher = patch(
            "lukhas.core.verifold.verifold_unified.IdentityContext"
        )
        self.mock_identity = self.identity_patcher.start()
        self.mock_identity.return_value.__enter__.return_value.get_user_tier.return_value = (
            self.test_tier
        )

        # Mock the require_identity decorator
        self.auth_patcher = patch(
            "lukhas.core.verifold.verifold_unified.require_identity"
        )
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda func: func  # Pass-through decorator

    def teardown_method(self):
        """Cleanup test environment."""
        self.identity_patcher.stop()
        self.auth_patcher.stop()

    def test_system_initialization(self):
        """Test system initializes correctly."""
        assert self.system.active_collapses == {}
        assert self.system.collapse_history == []
        assert self.system.system_entropy == 0.0
        assert self.system.monitoring_enabled is True
        assert len(self.system.phase_thresholds) == 5

    def test_verifold_hash_generation(self):
        """Test VeriFold hash generation with tier integration."""
        collapse_data = {
            "intent_vector": [0.5, 0.3, -0.1],
            "emotional_state": "focused",
            "ethical_context": "tier_3_approved",
            "entropy": 0.4,
            "metadata": {"operation": "memory_consolidation"},
        }

        record = self.system.generate_verifold_hash(
            collapse_data,
            self.test_user_id,
            self.test_tier,
            VeriFoldCollapseType.MEMORY,
        )

        # Verify record structure
        assert isinstance(record, VeriFoldRecord)
        assert isinstance(record.snapshot, VeriFoldSnapshot)
        assert record.verifold_hash is not None
        assert len(record.verifold_hash) == 64  # SHA3-256 hex

        # Verify snapshot content
        snapshot = record.snapshot
        assert snapshot.user_id == self.test_user_id
        assert snapshot.lambda_tier == self.test_tier
        assert snapshot.collapse_type == VeriFoldCollapseType.MEMORY
        assert snapshot.intent_vector == [0.5, 0.3, -0.1]
        assert snapshot.emotional_state == "focused"
        assert snapshot.ethical_context == "tier_3_approved"
        assert 0.0 <= snapshot.entropy_score <= 1.0

        # Verify system state updated
        assert len(self.system.active_collapses) == 1
        assert len(self.system.collapse_history) == 1
        assert self.system.system_entropy > 0.0

    def test_verifold_hash_verification(self):
        """Test VeriFold hash verification."""
        collapse_data = {
            "intent_vector": [0.2, 0.8, 0.1],
            "emotional_state": "confident",
            "entropy": 0.3,
        }

        # Generate record
        record = self.system.generate_verifold_hash(
            collapse_data, self.test_user_id, self.test_tier
        )

        # Verify the record
        is_valid = self.system.verify_verifold_record(record, self.test_user_id)
        assert is_valid is True

        # Test with modified hash (should fail)
        corrupted_record = VeriFoldRecord(
            snapshot=record.snapshot,
            verifold_hash="corrupted_hash_123456789",
            signature=record.signature,
            public_key=record.public_key,
            verified=record.verified,
        )

        is_valid_corrupted = self.system.verify_verifold_record(
            corrupted_record, self.test_user_id
        )
        assert is_valid_corrupted is False

    def test_collapse_type_classification(self):
        """Test different collapse types are handled correctly."""
        test_cases = [
            (VeriFoldCollapseType.MEMORY, "memory_fold_operation"),
            (VeriFoldCollapseType.SYMBOLIC, "glyph_mutation"),
            (VeriFoldCollapseType.EMOTIONAL, "affect_regulation"),
            (VeriFoldCollapseType.COGNITIVE, "reasoning_chain"),
            (VeriFoldCollapseType.ETHICAL, "moral_arbitration"),
            (VeriFoldCollapseType.TEMPORAL, "timeline_sync"),
            (VeriFoldCollapseType.IDENTITY, "self_model_update"),
        ]

        for collapse_type, operation in test_cases:
            collapse_data = {"operation": operation, "entropy": 0.5}

            record = self.system.generate_verifold_hash(
                collapse_data, self.test_user_id, self.test_tier, collapse_type
            )

            assert record.snapshot.collapse_type == collapse_type
            assert record.snapshot.system_context.get("operation") == operation

    def test_phase_determination(self):
        """Test collapse phase determination based on entropy."""
        test_cases = [
            (0.1, VeriFoldPhase.STABLE),
            (0.4, VeriFoldPhase.PERTURBATION),
            (0.6, VeriFoldPhase.CRITICAL),
            (0.8, VeriFoldPhase.CASCADE),
            (0.96, VeriFoldPhase.SINGULARITY),
        ]

        for entropy, expected_phase in test_cases:
            collapse_data = {"entropy": entropy}

            record = self.system.generate_verifold_hash(
                collapse_data, self.test_user_id, self.test_tier
            )

            assert record.snapshot.phase == expected_phase

    @pytest.mark.asyncio
    async def test_collapse_cascade_monitoring(self):
        """Test cascade monitoring functionality."""
        # Generate multiple high-entropy collapses
        for i in range(5):
            collapse_data = {"entropy": 0.8 + i * 0.02}  # Increasing entropy
            self.system.generate_verifold_hash(
                collapse_data, self.test_user_id, self.test_tier
            )

        # Monitor for cascade
        status = await self.system.monitor_collapse_cascade(
            self.test_user_id, threshold=0.7
        )

        assert "cascade_risk" in status
        assert "system_entropy" in status
        assert "active_collapses" in status
        assert "recommendations" in status
        assert status["active_collapses"] == 5

        # High entropy should trigger cascade risk
        if status["system_entropy"] >= 0.7:
            assert status["cascade_risk"] is True
            assert len(status["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_collapse_intervention(self):
        """Test collapse intervention system."""
        # Raise system entropy
        self.system.system_entropy = 0.9

        # Add high-entropy collapses
        for i in range(3):
            collapse_data = {"entropy": 0.9}
            record = self.system.generate_verifold_hash(
                collapse_data,
                self.test_user_id,
                "LAMBDA_TIER_4",  # High tier for intervention access
            )

        # Trigger intervention
        result = await self.system.trigger_collapse_intervention(
            self.test_user_id, intervention_type="moderate"
        )

        assert "intervention_type" in result
        assert "interventions_applied" in result
        assert "system_entropy_post" in result
        assert result["intervention_type"] == "moderate"
        assert len(result["interventions_applied"]) > 0

        # System entropy should be reduced
        assert result["system_entropy_post"] < 0.9

    def test_tier_integration(self):
        """Test integration with tier system."""
        # Test different tier levels
        tier_test_cases = [
            ("LAMBDA_TIER_1", "basic_user"),
            ("LAMBDA_TIER_3", "advanced_user"),
            ("LAMBDA_TIER_5", "admin_user"),
        ]

        for tier, user_id in tier_test_cases:
            collapse_data = {"entropy": 0.5}

            record = self.system.generate_verifold_hash(collapse_data, user_id, tier)

            assert record.snapshot.lambda_tier == tier
            assert record.snapshot.user_id == user_id

    def test_system_metrics(self):
        """Test system metrics collection."""
        # Generate some test data
        for i in range(3):
            collapse_data = {"entropy": 0.3 + i * 0.1}
            self.system.generate_verifold_hash(
                collapse_data, self.test_user_id, self.test_tier
            )

        metrics = self.system.get_system_metrics()

        assert "system_entropy" in metrics
        assert "active_collapses" in metrics
        assert "total_collapses" in metrics
        assert "phase_distribution" in metrics
        assert "tier_activity" in metrics
        assert "pq_enabled" in metrics
        assert "monitoring_enabled" in metrics

        assert metrics["active_collapses"] == 3
        assert metrics["total_collapses"] == 3
        assert metrics["monitoring_enabled"] is True


class TestVeriFoldBackwardCompatibility:
    """Test backward compatibility with CollapseHash system."""

    def setup_method(self):
        """Setup test environment."""
        # Mock the require_identity decorator
        self.auth_patcher = patch(
            "lukhas.core.verifold.verifold_unified.require_identity"
        )
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda func: func  # Pass-through decorator

    def teardown_method(self):
        """Cleanup test environment."""
        self.auth_patcher.stop()

    def test_generate_verifold_hash_function(self):
        """Test the backward compatibility generate function."""
        collapse_data = {
            "intent_vector": [0.7, 0.2, 0.1],
            "emotional_state": "determined",
            "entropy": 0.6,
        }

        record = generate_verifold_hash(collapse_data, "compat_user", "LAMBDA_TIER_2")

        assert isinstance(record, VeriFoldRecord)
        assert record.snapshot.user_id == "compat_user"
        assert record.snapshot.lambda_tier == "LAMBDA_TIER_2"
        assert record.verifold_hash is not None

    def test_verify_verifold_hash_function(self):
        """Test the backward compatibility verify function."""
        collapse_data = {"entropy": 0.4}

        # Generate using compatibility function
        record = generate_verifold_hash(collapse_data, "verify_user", "LAMBDA_TIER_1")

        # Verify using compatibility function
        is_valid = verify_verifold_hash(record, "verify_user")
        assert is_valid is True


class TestVeriFoldCryptography:
    """Test cryptographic functionality of VeriFold."""

    def setup_method(self):
        """Setup test environment."""
        self.system = UnifiedVeriFoldSystem()

        # Mock the require_identity decorator
        self.auth_patcher = patch(
            "lukhas.core.verifold.verifold_unified.require_identity"
        )
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda func: func

    def teardown_method(self):
        """Cleanup test environment."""
        self.auth_patcher.stop()

    def test_hash_determinism(self):
        """Test that identical snapshots produce identical hashes."""
        snapshot_data = {
            "collapse_id": "test_123",
            "collapse_type": VeriFoldCollapseType.SYMBOLIC,
            "user_id": "hash_test_user",
            "lambda_tier": "LAMBDA_TIER_2",
            "intent_vector": [0.5, 0.5, 0.0],
            "emotional_state": "neutral",
            "ethical_context": "standard",
            "temporal_context": "present",
            "system_context": {},
            "phase": VeriFoldPhase.STABLE,
            "entropy_score": 0.3,
            "timestamp": "2025-07-26T12:00:00Z",
            "metadata": {},
        }

        snapshot1 = VeriFoldSnapshot(**snapshot_data)
        snapshot2 = VeriFoldSnapshot(**snapshot_data)

        hash1 = self.system._compute_verifold_hash(snapshot1)
        hash2 = self.system._compute_verifold_hash(snapshot2)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA3-256 produces 64 char hex

    def test_hash_uniqueness(self):
        """Test that different snapshots produce different hashes."""
        base_data = {
            "collapse_id": "unique_test",
            "collapse_type": VeriFoldCollapseType.MEMORY,
            "user_id": "unique_user",
            "lambda_tier": "LAMBDA_TIER_1",
            "intent_vector": [0.1, 0.2, 0.3],
            "emotional_state": "curious",
            "ethical_context": "exploratory",
            "temporal_context": "present",
            "system_context": {},
            "phase": VeriFoldPhase.STABLE,
            "entropy_score": 0.2,
            "timestamp": "2025-07-26T12:00:00Z",
            "metadata": {},
        }

        # Create snapshots with small differences
        snapshot1 = VeriFoldSnapshot(**base_data)

        modified_data = base_data.copy()
        modified_data["entropy_score"] = 0.21  # Tiny change
        snapshot2 = VeriFoldSnapshot(**modified_data)

        hash1 = self.system._compute_verifold_hash(snapshot1)
        hash2 = self.system._compute_verifold_hash(snapshot2)

        assert hash1 != hash2

    @patch("lukhas.core.verifold.verifold_unified.PQ_AVAILABLE", True)
    @patch("lukhas.core.verifold.verifold_unified.oqs")
    def test_post_quantum_signatures(self, mock_oqs):
        """Test post-quantum signature generation and verification."""
        # Mock OQS behavior
        mock_signer = MagicMock()
        mock_signer.generate_keypair.return_value = b"mock_public_key"
        mock_signer.export_secret_key.return_value = b"mock_private_key"
        mock_signer.sign.return_value = b"mock_signature"
        mock_signer.verify.return_value = True
        mock_signer.set_public_key.return_value = None

        mock_oqs.Signature.return_value.__enter__.return_value = mock_signer
        mock_oqs.Signature.return_value.__exit__.return_value = None

        test_hash = "test_hash_for_signing"

        # Test signature generation
        signature_hex, public_key_hex = self.system._sign_verifold_hash(test_hash)

        assert signature_hex == b"mock_signature".hex()
        assert public_key_hex == b"mock_public_key".hex()

        # Test signature verification
        is_valid = self.system._verify_signature(
            test_hash, signature_hex, public_key_hex
        )
        assert is_valid is True

        # Verify OQS was called correctly
        mock_oqs.Signature.assert_called_with("SPHINCS+-SHAKE256-128f-simple")
        mock_signer.generate_keypair.assert_called_once()
        mock_signer.sign.assert_called_with(test_hash.encode())
        mock_signer.verify.assert_called_with(test_hash.encode(), b"mock_signature")


class TestVeriFoldIntegration:
    """Test integration with other LUKHAS systems."""

    def setup_method(self):
        """Setup test environment."""
        # Mock the require_identity decorator
        self.auth_patcher = patch(
            "lukhas.core.verifold.verifold_unified.require_identity"
        )
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda func: func

    def teardown_method(self):
        """Cleanup test environment."""
        self.auth_patcher.stop()

    def test_global_instance_singleton(self):
        """Test that global instance is a singleton."""
        instance1 = get_global_verifold_system()
        instance2 = get_global_verifold_system()

        assert instance1 is instance2
        assert isinstance(instance1, UnifiedVeriFoldSystem)

    def test_memory_system_integration(self):
        """Test integration with memory system."""
        system = get_global_verifold_system()

        # Simulate memory fold collapse
        memory_collapse_data = {
            "operation": "memory_fold_consolidation",
            "fold_count": 5,
            "semantic_loss": 0.02,
            "entropy": 0.45,
            "metadata": {
                "fold_type": "episodic",
                "consolidation_strategy": "temporal_clustering",
            },
        }

        record = system.generate_verifold_hash(
            memory_collapse_data,
            "memory_user",
            "LAMBDA_TIER_2",
            VeriFoldCollapseType.MEMORY,
        )

        assert record.snapshot.collapse_type == VeriFoldCollapseType.MEMORY
        assert (
            record.snapshot.system_context.get("operation")
            == "memory_fold_consolidation"
        )
        assert record.snapshot.metadata["fold_type"] == "episodic"

    def test_emotional_system_integration(self):
        """Test integration with emotional system."""
        system = get_global_verifold_system()

        # Simulate emotional regulation collapse
        emotion_collapse_data = {
            "operation": "emotional_regulation",
            "baseline_shift": 0.3,
            "regulation_strategy": "adaptive_dampening",
            "entropy": 0.6,
            "emotional_state": "transitioning",
            "ethical_context": "emotional_stability_protocol",
        }

        record = system.generate_verifold_hash(
            emotion_collapse_data,
            "emotion_user",
            "LAMBDA_TIER_3",
            VeriFoldCollapseType.EMOTIONAL,
        )

        assert record.snapshot.collapse_type == VeriFoldCollapseType.EMOTIONAL
        assert record.snapshot.emotional_state == "transitioning"
        assert (
            record.snapshot.system_context.get("regulation_strategy")
            == "adaptive_dampening"
        )


# Performance and stress tests
class TestVeriFoldPerformance:
    """Test performance characteristics of VeriFold system."""

    def setup_method(self):
        """Setup test environment."""
        self.system = UnifiedVeriFoldSystem()

        # Mock the require_identity decorator
        self.auth_patcher = patch(
            "lukhas.core.verifold.verifold_unified.require_identity"
        )
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda func: func

    def teardown_method(self):
        """Cleanup test environment."""
        self.auth_patcher.stop()

    def test_bulk_hash_generation(self):
        """Test generating many hashes efficiently."""
        collapse_count = 100

        start_time = datetime.now()

        for i in range(collapse_count):
            collapse_data = {
                "entropy": 0.3 + (i % 10) * 0.05,
                "operation": f"bulk_test_{i}",
                "iteration": i,
            }

            self.system.generate_verifold_hash(
                collapse_data,
                f"bulk_user_{i % 5}",  # 5 different users
                f"LAMBDA_TIER_{(i % 5) + 1}",  # Tiers 1-5
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Should complete in reasonable time (less than 10 seconds)
        assert duration < 10.0

        # Verify all hashes were generated
        assert len(self.system.active_collapses) == collapse_count
        assert len(self.system.collapse_history) == collapse_count

        # System entropy should be reasonable
        assert 0.0 <= self.system.system_entropy <= 1.0

    def test_memory_usage_bounded(self):
        """Test that memory usage stays bounded with many collapses."""
        # Generate many collapses to test history trimming
        for i in range(1500):  # More than the 1000 history limit
            collapse_data = {"entropy": 0.4, "iteration": i}

            self.system.generate_verifold_hash(
                collapse_data, "memory_test_user", "LAMBDA_TIER_2"
            )

        # History should be trimmed to 500 most recent
        assert len(self.system.collapse_history) == 500

        # Most recent collapses should be preserved
        latest_collapse = self.system.collapse_history[-1]
        assert latest_collapse.snapshot.system_context.get("iteration") == 1499


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
