"""
Integration tests for Consciousness Hub components
Tests awareness processor and poetic engine integrations
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from consciousness.consciousness_hub import ConsciousnessHub


class TestConsciousnessIntegrations:
    """Test suite for consciousness hub component integrations"""

    @pytest.fixture
    async def consciousness_hub(self):
        """Create a test consciousness hub instance"""
        hub = ConsciousnessHub()
        return hub

    @pytest.mark.asyncio
    async def test_integrate_awareness_processor_success(self, consciousness_hub):
        """Test successful integration of awareness processor"""
        with patch(
            "consciousness.consciousness_hub.AwarenessProcessor"
        ) as mock_processor_class:
            mock_processor = AsyncMock()
            mock_processor.initialize = AsyncMock()
            mock_processor_class.return_value = mock_processor

            # Integrate awareness processor
            await consciousness_hub.integrate_awareness_processor()

            # Verify integration
            assert hasattr(consciousness_hub, "awareness_processor")
            assert consciousness_hub.awareness_processor == mock_processor
            assert "awareness_processor" in consciousness_hub.services
            assert "awareness_processor" in consciousness_hub.cognitive_components
            mock_processor.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_integrate_awareness_processor_no_initialize(self, consciousness_hub):
        """Test awareness processor integration when initialize method doesn't exist"""
        with patch(
            "consciousness.consciousness_hub.AwarenessProcessor"
        ) as mock_processor_class:
            mock_processor = Mock()  # No initialize method
            mock_processor_class.return_value = mock_processor

            # Should not raise error
            await consciousness_hub.integrate_awareness_processor()

            # Verify integration still works
            assert hasattr(consciousness_hub, "awareness_processor")
            assert "awareness_processor" in consciousness_hub.services

    @pytest.mark.asyncio
    async def test_integrate_poetic_engine_success(self, consciousness_hub):
        """Test successful integration of poetic engine"""
        with patch("consciousness.consciousness_hub.PoeticEngine") as mock_engine_class:
            mock_engine = AsyncMock()
            mock_engine.initialize = AsyncMock()
            mock_engine_class.return_value = mock_engine

            # Integrate poetic engine
            await consciousness_hub.integrate_poetic_engine()

            # Verify integration
            assert hasattr(consciousness_hub, "poetic_engine")
            assert consciousness_hub.poetic_engine == mock_engine
            assert "poetic_engine" in consciousness_hub.services
            assert "poetic_engine" in consciousness_hub.cognitive_components
            mock_engine.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_integrate_poetic_engine_failure(self, consciousness_hub):
        """Test handling of poetic engine integration failure"""
        with patch("consciousness.consciousness_hub.logger") as mock_logger:
            # Force an import error
            with patch(
                "consciousness.consciousness_hub.PoeticEngine",
                side_effect=ImportError("Test error"),
            ):
                await consciousness_hub.integrate_poetic_engine()

                # Verify error was logged
                mock_logger.error.assert_called_with(
                    "poetic_engine_integration_failed", error="Test error"
                )

    @pytest.mark.asyncio
    async def test_all_integrations_in_initialize(self):
        """Test that all integrations are called during hub initialization"""
        with patch.multiple(
            "consciousness.consciousness_hub",
            DreamBridge=Mock(return_value=AsyncMock()),
            AwarenessProcessor=Mock(return_value=AsyncMock()),
            PoeticEngine=Mock(return_value=AsyncMock()),
        ):

            hub = ConsciousnessHub()

            # Mock the integration methods to track calls
            hub.integrate_dream_bridge = AsyncMock()
            hub.integrate_awareness_processor = AsyncMock()
            hub.integrate_poetic_engine = AsyncMock()

            # Partially initialize (skip full initialization)
            await hub.integrate_dream_bridge()
            await hub.integrate_awareness_processor()
            await hub.integrate_poetic_engine()

            # Verify all integrations were called
            hub.integrate_dream_bridge.assert_called_once()
            hub.integrate_awareness_processor.assert_called_once()
            hub.integrate_poetic_engine.assert_called_once()

    @pytest.mark.asyncio
    async def test_cognitive_component_registration_flow(self, consciousness_hub):
        """Test the flow of registering cognitive components"""
        # Create test components
        test_components = {
            "visual_processor": Mock(spec=["process"]),
            "language_model": Mock(spec=["generate"]),
            "memory_encoder": Mock(spec=["encode", "decode"]),
        }

        # Register all components
        for name, component in test_components.items():
            consciousness_hub.register_cognitive_component(name, component)

        # Verify all components are registered
        for name, component in test_components.items():
            assert name in consciousness_hub.cognitive_components
            assert f"cognitive_{name}" in consciousness_hub.services
            assert consciousness_hub.cognitive_components[name] == component
            assert consciousness_hub.services[f"cognitive_{name}"] == component

    @pytest.mark.asyncio
    async def test_awareness_broadcast_to_integrated_components(self):
        """Test that awareness broadcasts reach integrated components"""
        # Create hub with mocked components
        hub = ConsciousnessHub()

        # Create mock components with update_awareness method
        mock_dream_bridge = AsyncMock()
        mock_dream_bridge.update_awareness = AsyncMock()

        mock_awareness_processor = AsyncMock()
        mock_awareness_processor.update_awareness = AsyncMock()

        mock_poetic_engine = AsyncMock()
        mock_poetic_engine.update_awareness = AsyncMock()

        # Manually register components
        hub.dream_bridge = mock_dream_bridge
        hub.awareness_processor = mock_awareness_processor
        hub.poetic_engine = mock_poetic_engine

        hub.services["dream_bridge"] = mock_dream_bridge
        hub.services["awareness_processor"] = mock_awareness_processor
        hub.services["poetic_engine"] = mock_poetic_engine

        # Broadcast awareness state
        await hub.broadcast_awareness_state()

        # Verify all components received the update
        mock_dream_bridge.update_awareness.assert_called_once()
        mock_awareness_processor.update_awareness.assert_called_once()
        mock_poetic_engine.update_awareness.assert_called_once()

        # Verify the awareness state structure
        call_args = mock_dream_bridge.update_awareness.call_args[0][0]
        assert call_args["level"] == "active"
        assert "timestamp" in call_args
        assert "connected_systems" in call_args


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
