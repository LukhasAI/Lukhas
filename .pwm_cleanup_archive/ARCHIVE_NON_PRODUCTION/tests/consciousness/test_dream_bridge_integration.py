"""
Integration tests for Dream Bridge in Consciousness Hub
Tests the complete integration of dream bridge with consciousness system
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from consciousness.consciousness_hub import (
    ConsciousnessHub,
)
from consciousness.dream_bridge_adapter import DreamBridge


class TestDreamBridgeIntegration:
    """Test suite for dream bridge integration with consciousness hub"""

    @pytest.fixture
    async def consciousness_hub(self):
        """Create a test consciousness hub instance"""
        hub = ConsciousnessHub()
        # Don't fully initialize to avoid loading all services
        return hub

    @pytest.fixture
    async def dream_bridge(self):
        """Create a test dream bridge instance"""
        bridge = DreamBridge()
        # Mock the underlying components to avoid dependencies
        bridge.bridge.consciousness = AsyncMock()
        bridge.bridge.dream_engine = AsyncMock()
        bridge.bridge.memory = AsyncMock()
        return bridge

    @pytest.mark.asyncio
    async def test_dream_bridge_registration(self, consciousness_hub):
        """Test that dream bridge can be registered with consciousness hub"""
        # Create mock dream bridge
        mock_bridge = Mock()
        mock_bridge.initialize = AsyncMock()

        # Register the component
        consciousness_hub.register_cognitive_component("test_dream_bridge", mock_bridge)

        # Verify registration
        assert "test_dream_bridge" in consciousness_hub.cognitive_components
        assert "cognitive_test_dream_bridge" in consciousness_hub.services
        assert (
            consciousness_hub.cognitive_components["test_dream_bridge"] == mock_bridge
        )

    @pytest.mark.asyncio
    async def test_integrate_dream_bridge_success(self, consciousness_hub):
        """Test successful integration of dream bridge"""
        with patch("consciousness.consciousness_hub.DreamBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge.initialize = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            # Integrate dream bridge
            await consciousness_hub.integrate_dream_bridge()

            # Verify integration
            assert hasattr(consciousness_hub, "dream_bridge")
            assert consciousness_hub.dream_bridge == mock_bridge
            assert "dream_bridge" in consciousness_hub.services
            assert "dream_bridge" in consciousness_hub.cognitive_components
            mock_bridge.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_integrate_dream_bridge_failure(self, consciousness_hub):
        """Test handling of dream bridge integration failure"""
        with patch("consciousness.consciousness_hub.logger") as mock_logger:
            # Force an import error
            with patch(
                "consciousness.consciousness_hub.DreamBridge",
                side_effect=ImportError("Test error"),
            ):
                await consciousness_hub.integrate_dream_bridge()

                # Verify error was logged
                mock_logger.error.assert_called_with(
                    "dream_bridge_integration_failed", error="Test error"
                )

    @pytest.mark.asyncio
    async def test_dream_bridge_process_consciousness_state(self, dream_bridge):
        """Test processing consciousness state through dream bridge"""
        # Setup mock responses
        dream_bridge.bridge.process_consciousness_to_dream = AsyncMock(
            return_value={"dream_type": "lucid", "content": "test dream"}
        )

        # Process a consciousness state
        state = {"level": "active", "focus": "creative"}
        result = await dream_bridge.process_consciousness_state(state)

        # Verify result
        assert "dream_id" in result
        assert "dream_data" in result
        assert result["status"] == "active"
        assert result["dream_data"]["dream_type"] == "lucid"

        # Verify dream is stored
        assert len(dream_bridge.active_dreams) == 1

    @pytest.mark.asyncio
    async def test_dream_bridge_integrate_feedback(self, dream_bridge):
        """Test integrating dream feedback back to consciousness"""
        # Setup active dream
        dream_id = "test_dream_123"
        dream_bridge.active_dreams[dream_id] = {"content": "test dream"}

        # Setup mock response
        dream_bridge.bridge.process_dream_to_consciousness = AsyncMock(
            return_value={"insight": "profound", "integration": "complete"}
        )

        # Integrate feedback
        feedback = {"emotional_tone": "positive", "clarity": 0.8}
        result = await dream_bridge.integrate_dream_feedback(dream_id, feedback)

        # Verify result
        assert result["insight"] == "profound"
        assert result["integration"] == "complete"

        # Verify feedback was stored
        assert len(dream_bridge.consciousness_feedback) == 1
        assert dream_bridge.consciousness_feedback[0]["dream_id"] == dream_id

    @pytest.mark.asyncio
    async def test_dream_bridge_awareness_update(self, dream_bridge):
        """Test dream bridge response to awareness updates"""
        # Mock the dream engine
        dream_bridge.bridge.dream_engine.set_vividness = AsyncMock()

        # Update with active awareness
        await dream_bridge.update_awareness({"level": "active"})
        dream_bridge.bridge.dream_engine.set_vividness.assert_called_with(0.8)

        # Update with passive awareness
        await dream_bridge.update_awareness({"level": "passive"})
        dream_bridge.bridge.dream_engine.set_vividness.assert_called_with(0.4)

    @pytest.mark.asyncio
    async def test_consciousness_hub_dream_integration_flow(self):
        """Test the complete integration flow in consciousness hub"""
        # Create hub with mocked components
        with patch("consciousness.consciousness_hub.DreamBridge") as mock_bridge_class:
            mock_bridge = AsyncMock()
            mock_bridge.initialize = AsyncMock()
            mock_bridge.update_awareness = AsyncMock()
            mock_bridge_class.return_value = mock_bridge

            hub = ConsciousnessHub()

            # Integrate dream bridge
            await hub.integrate_dream_bridge()

            # Broadcast awareness state
            await hub.broadcast_awareness_state()

            # Verify dream bridge received awareness update
            mock_bridge.update_awareness.assert_called()
            call_args = mock_bridge.update_awareness.call_args[0][0]
            assert call_args["level"] == "active"
            assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_dream_bridge_initialization_sequence(self, dream_bridge):
        """Test the initialization sequence of dream bridge components"""
        # Setup mocks
        dream_bridge.bridge.consciousness.initialize = AsyncMock()
        dream_bridge.bridge.dream_engine.initialize = AsyncMock()
        dream_bridge.bridge.memory.initialize = AsyncMock()

        # Initialize
        await dream_bridge.initialize()

        # Verify all components initialized
        dream_bridge.bridge.consciousness.initialize.assert_called_once()
        dream_bridge.bridge.dream_engine.initialize.assert_called_once()
        dream_bridge.bridge.memory.initialize.assert_called_once()
        assert dream_bridge.is_initialized is True

    @pytest.mark.asyncio
    async def test_dream_bridge_active_dreams_management(self, dream_bridge):
        """Test management of active dreams"""
        # Process multiple consciousness states
        states = [
            {"level": "active", "id": 1},
            {"level": "passive", "id": 2},
            {"level": "dream", "id": 3},
        ]

        dream_bridge.bridge.process_consciousness_to_dream = AsyncMock(
            side_effect=[{"content": f"dream_{i}"} for i in range(3)]
        )

        dream_ids = []
        for state in states:
            result = await dream_bridge.process_consciousness_state(state)
            dream_ids.append(result["dream_id"])

        # Get active dreams
        active = await dream_bridge.get_active_dreams()
        assert active["count"] == 3
        assert len(active["active_dreams"]) == 3

        # Clear a dream
        cleared = await dream_bridge.clear_dream(dream_ids[0])
        assert cleared is True

        # Verify dream was removed
        active = await dream_bridge.get_active_dreams()
        assert active["count"] == 2

        # Try to clear non-existent dream
        cleared = await dream_bridge.clear_dream("non_existent")
        assert cleared is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
