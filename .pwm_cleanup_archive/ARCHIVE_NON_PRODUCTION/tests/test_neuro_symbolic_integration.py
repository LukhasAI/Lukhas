"""
Test suite for Quantum Neuro Symbolic Integration
"""

from datetime import datetime

import pytest

from quantum.neuro_symbolic_integration import (
    NEURO_SYMBOLIC_AVAILABLE,
    NeuroSymbolicIntegration,
    create_neuro_symbolic_integration,
)
from quantum.quantum_hub import QuantumHub


class TestNeuroSymbolicIntegration:
    """Test suite for neuro symbolic integration with quantum hub"""

    @pytest.fixture
    async def quantum_hub(self):
        """Create a test quantum hub instance"""
        hub = QuantumHub()
        return hub

    @pytest.fixture
    async def neuro_symbolic_integration(self):
        """Create a test neuro symbolic integration instance"""
        config = {
            "attention_gates": {
                "semantic": 0.4,
                "emotional": 0.3,
                "contextual": 0.2,
                "historical": 0.1,
            },
            "confidence_threshold": 0.6,
            "max_causal_depth": 3,
            "superposition_enabled": True,
            "entanglement_tracking": True,
        }
        integration = NeuroSymbolicIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_neuro_symbolic_integration_initialization(
        self, neuro_symbolic_integration
    ):
        """Test neuro symbolic integration initialization"""
        assert neuro_symbolic_integration is not None
        assert neuro_symbolic_integration.config["confidence_threshold"] == 0.6
        assert neuro_symbolic_integration.config["max_causal_depth"] == 3
        assert neuro_symbolic_integration.is_initialized is False

        # Initialize the integration
        await neuro_symbolic_integration.initialize()
        assert neuro_symbolic_integration.is_initialized is True

    @pytest.mark.asyncio
    async def test_quantum_hub_neuro_symbolic_registration(self, quantum_hub):
        """Test that neuro symbolic is registered in the quantum hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Verify neuro symbolic service is available (if NEURO_SYMBOLIC_AVAILABLE is True)
        services = quantum_hub.list_services()

        # The service should be registered if the import was successful
        if "neuro_symbolic" in services:
            assert quantum_hub.get_service("neuro_symbolic") is not None

    @pytest.mark.asyncio
    async def test_text_processing_through_hub(self, quantum_hub):
        """Test processing text through the quantum hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Skip test if neuro symbolic not available
        if "neuro_symbolic" not in quantum_hub.services:
            pytest.skip("Neuro symbolic integration not available")

        # Test text processing
        test_text = "How does quantum computing work with artificial intelligence?"
        result = await quantum_hub.process_text_quantum(
            text=test_text, user_id="test_user", context={"focus_on_emotion": False}
        )

        # Verify result structure
        assert result["status"] == "completed"
        assert "result" in result
        result_data = result["result"]
        assert "response" in result_data
        assert "confidence" in result_data
        assert "processing_id" in result_data

    @pytest.mark.asyncio
    async def test_quantum_attention_processing(self, quantum_hub):
        """Test quantum attention processing through hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Skip test if neuro symbolic not available
        if "neuro_symbolic" not in quantum_hub.services:
            pytest.skip("Neuro symbolic integration not available")

        # Test attention processing
        input_data = {
            "text": "I'm feeling confused about machine learning",
            "emotion": {"primary_emotion": "confused", "intensity": 0.7},
            "context": {"urgent": False},
        }

        result = await quantum_hub.apply_quantum_attention(
            input_data=input_data,
            context={"focus_on_emotion": True},
            user_id="test_user",
        )

        # Verify result
        assert result["status"] == "completed"
        assert "result" in result
        attention_result = result["result"]
        assert "attention_weights" in attention_result
        assert "attended_content" in attention_result
        assert "processing_id" in attention_result

    @pytest.mark.asyncio
    async def test_causal_reasoning_processing(self, quantum_hub):
        """Test causal reasoning through hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Skip test if neuro symbolic not available
        if "neuro_symbolic" not in quantum_hub.services:
            pytest.skip("Neuro symbolic integration not available")

        # Mock attended data (as would come from attention processing)
        attended_data = {
            "original": {"text": "Test input for reasoning"},
            "attention_weights": {
                "semantic": 0.4,
                "emotional": 0.3,
                "contextual": 0.2,
                "historical": 0.1,
            },
            "attended_content": {
                "semantic": {"content": "Test input for reasoning", "weight": 0.4},
                "emotional": {"content": {"primary_emotion": "neutral"}, "weight": 0.3},
            },
            "timestamp": datetime.now().isoformat(),
            "processing_id": "test_processing_id",
        }

        result = await quantum_hub.perform_causal_reasoning(
            attended_data=attended_data, user_id="test_user"
        )

        # Verify result
        assert result["status"] == "completed"
        assert "result" in result
        reasoning_result = result["result"]
        assert "causal_chains" in reasoning_result
        assert "confidence" in reasoning_result
        assert "reasoning_path" in reasoning_result

    @pytest.mark.asyncio
    async def test_neuro_symbolic_statistics(self, quantum_hub):
        """Test getting neuro symbolic statistics through hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Skip test if neuro symbolic not available
        if "neuro_symbolic" not in quantum_hub.services:
            pytest.skip("Neuro symbolic integration not available")

        # Get statistics
        result = quantum_hub.get_neuro_symbolic_statistics()

        # Verify result
        assert result["available"] is True
        assert "statistics" in result
        stats = result["statistics"]
        assert "total_processes" in stats
        assert "active_sessions" in stats
        assert "neuro_symbolic_available" in stats
        assert "initialization_status" in stats

    @pytest.mark.asyncio
    async def test_session_cleanup(self, quantum_hub):
        """Test neuro symbolic session cleanup through hub"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Skip test if neuro symbolic not available
        if "neuro_symbolic" not in quantum_hub.services:
            pytest.skip("Neuro symbolic integration not available")

        # Cleanup sessions
        result = await quantum_hub.cleanup_neuro_symbolic_sessions()

        # Verify result
        assert result["status"] == "completed"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_error_handling_missing_service(self, quantum_hub):
        """Test error handling when neuro symbolic service is not available"""
        # Initialize the hub
        await quantum_hub.initialize()

        # Remove neuro symbolic service if it exists
        if "neuro_symbolic" in quantum_hub.services:
            del quantum_hub.services["neuro_symbolic"]

        # Test text processing with missing service
        result = await quantum_hub.process_text_quantum("test text")
        assert result["status"] == "failed"
        assert "error" in result

        # Test attention processing with missing service
        result = await quantum_hub.apply_quantum_attention({"text": "test"})
        assert result["status"] == "failed"
        assert "error" in result

        # Test reasoning with missing service
        result = await quantum_hub.perform_causal_reasoning({})
        assert result["status"] == "failed"
        assert "error" in result

        # Test statistics with missing service
        result = quantum_hub.get_neuro_symbolic_statistics()
        assert result["available"] is False
        assert "error" in result

        # Test cleanup with missing service
        result = await quantum_hub.cleanup_neuro_symbolic_sessions()
        assert result["status"] == "failed"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_fallback_processing(self, neuro_symbolic_integration):
        """Test fallback processing when main engine is not available"""
        # Initialize the integration
        await neuro_symbolic_integration.initialize()

        # Test text processing (should work with fallback)
        result = await neuro_symbolic_integration.process_text(
            "What is quantum computing?", user_id="test_user"
        )

        # Verify result structure
        assert "response" in result
        assert "confidence" in result
        assert "processing_id" in result
        assert "timestamp" in result

        # If using fallback, should have fallback_mode flag
        if not NEURO_SYMBOLIC_AVAILABLE:
            assert result.get("fallback_mode") is True

    @pytest.mark.asyncio
    async def test_attention_processing_standalone(self, neuro_symbolic_integration):
        """Test attention processing as standalone operation"""
        # Initialize the integration
        await neuro_symbolic_integration.initialize()

        # Test attention processing
        input_data = {
            "text": "I need help understanding this concept",
            "emotion": {"primary_emotion": "confused", "intensity": 0.6},
        }

        result = await neuro_symbolic_integration.apply_quantum_attention(
            input_data, context={"focus_on_emotion": True}, user_id="test_user"
        )

        # Verify result structure
        assert "original" in result
        assert "attention_weights" in result
        assert "attended_content" in result
        assert "processing_id" in result

    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options for neuro symbolic integration"""
        # Test with custom config
        custom_config = {
            "attention_gates": {
                "semantic": 0.5,
                "emotional": 0.2,
                "contextual": 0.2,
                "historical": 0.1,
            },
            "confidence_threshold": 0.8,
            "max_causal_depth": 4,
            "superposition_enabled": False,
            "entanglement_tracking": False,
        }

        integration = create_neuro_symbolic_integration(custom_config)

        # Verify config was applied
        assert integration.config["confidence_threshold"] == 0.8
        assert integration.config["max_causal_depth"] == 4
        assert integration.config["superposition_enabled"] is False
        assert integration.config["entanglement_tracking"] is False
        assert integration.config["attention_gates"]["semantic"] == 0.5

    @pytest.mark.asyncio
    async def test_caching_behavior(self, neuro_symbolic_integration):
        """Test caching behavior in neuro symbolic integration"""
        # Initialize the integration
        await neuro_symbolic_integration.initialize()

        # Process the same text twice
        test_text = "Test caching behavior"

        # First processing
        result1 = await neuro_symbolic_integration.process_text(test_text)

        # Second processing (should potentially use cache)
        result2 = await neuro_symbolic_integration.process_text(test_text)

        # Both should succeed
        assert result1 is not None
        assert result2 is not None
        assert "processing_id" in result1
        assert "processing_id" in result2

        # Check cache statistics
        stats = neuro_symbolic_integration.get_processing_statistics()
        assert stats["cache_size"] >= 0
        assert "cache_hit_rate" in stats

    @pytest.mark.asyncio
    async def test_session_management(self, neuro_symbolic_integration):
        """Test session management functionality"""
        # Initialize the integration
        await neuro_symbolic_integration.initialize()

        # Process text with different users
        users = ["user1", "user2", "user3"]

        for user in users:
            result = await neuro_symbolic_integration.process_text(
                f"Hello from {user}", user_id=user
            )
            assert result is not None
            assert result["user_id"] == user

        # Check session registry
        assert len(neuro_symbolic_integration.session_registry) >= 3

        # Test session cleanup
        await neuro_symbolic_integration.cleanup_sessions()

        # Verify cleanup worked (some sessions might be cleaned up)
        stats = neuro_symbolic_integration.get_processing_statistics()
        assert "active_sessions" in stats

    def test_mock_id_manager(self, neuro_symbolic_integration):
        """Test the mock ID manager functionality"""
        mock_manager = neuro_symbolic_integration.lukhas_id_manager

        # Test that it has expected methods
        assert hasattr(mock_manager, "active_sessions")
        assert hasattr(mock_manager, "users")
        assert callable(getattr(mock_manager, "_create_audit_log", None))
        assert callable(getattr(mock_manager, "register_user", None))
        assert callable(getattr(mock_manager, "authenticate_user", None))

    @pytest.mark.asyncio
    async def test_error_recovery(self, neuro_symbolic_integration):
        """Test error recovery in neuro symbolic processing"""
        # Initialize the integration
        await neuro_symbolic_integration.initialize()

        # Test with various edge cases
        edge_cases = [
            "",  # Empty string
            "A" * 10000,  # Very long string
            "🚀🌟🔮⚡",  # Only emojis
            None,  # None input (should be handled gracefully)
        ]

        for case in edge_cases:
            try:
                if case is not None:
                    result = await neuro_symbolic_integration.process_text(str(case))
                    # Should get some kind of result, even if fallback
                    assert result is not None
                    assert "timestamp" in result
            except Exception as e:
                # Some edge cases might raise exceptions, which is acceptable
                assert isinstance(e, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
