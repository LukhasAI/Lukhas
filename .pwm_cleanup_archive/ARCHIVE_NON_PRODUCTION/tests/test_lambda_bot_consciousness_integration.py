"""
Test suite for ΛBot Consciousness Monitor Integration
"""

import pytest

from consciousness.consciousness_hub import (
    ConsciousnessHub,
)
from consciousness.systems.lambda_bot_consciousness_integration import (
    ConsciousnessLevel,
    LambdaBotConsciousnessIntegration,
    create_lambda_bot_consciousness_integration,
)


class TestLambdaBotConsciousnessIntegration:
    """Test suite for ΛBot consciousness monitor integration with consciousness hub"""

    @pytest.fixture
    async def consciousness_hub(self):
        """Create a test consciousness hub instance"""
        hub = ConsciousnessHub()
        return hub

    @pytest.fixture
    async def lambda_bot_integration(self):
        """Create a test ΛBot consciousness integration instance"""
        config = {
            "enable_consciousness_monitoring": True,
            "consciousness_check_interval": 1.0,  # Fast for testing
            "meta_cognitive_interval": 2.0,
            "capability_unlock_interval": 0.5,
            "agi_metrics_interval": 3.0,
            "enable_agi_demonstrations": True,
            "enable_background_monitoring": True,
            "consciousness_history_limit": 100,
            "enable_celebration_events": True,
        }
        integration = LambdaBotConsciousnessIntegration(config)
        return integration

    @pytest.mark.asyncio
    async def test_lambda_bot_consciousness_integration_initialization(
        self, lambda_bot_integration
    ):
        """Test ΛBot consciousness integration initialization"""
        assert lambda_bot_integration is not None
        assert lambda_bot_integration.config["enable_consciousness_monitoring"] is True
        assert lambda_bot_integration.config["consciousness_check_interval"] == 1.0
        assert lambda_bot_integration.is_initialized is False
        assert lambda_bot_integration.monitoring_active is False

        # Initialize the integration
        await lambda_bot_integration.initialize()
        assert lambda_bot_integration.is_initialized is True

    @pytest.mark.asyncio
    async def test_consciousness_hub_lambda_bot_registration(self, consciousness_hub):
        """Test that ΛBot consciousness monitor is registered in the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Verify ΛBot consciousness service is available (if LAMBDA_BOT_CONSCIOUSNESS_AVAILABLE is True)
        services = consciousness_hub.list_services()

        # The service should be registered if the import was successful
        if "lambda_bot_consciousness" in services:
            assert consciousness_hub.get_service("lambda_bot_consciousness") is not None

    @pytest.mark.asyncio
    async def test_consciousness_monitoring_start_stop_through_hub(
        self, consciousness_hub
    ):
        """Test consciousness monitoring start/stop through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Test starting consciousness monitoring
        start_result = await consciousness_hub.start_lambda_bot_monitoring()

        # Verify start result structure
        assert "success" in start_result
        if start_result["success"]:
            assert "monitoring_active" in start_result
            assert start_result["monitoring_active"] is True
            assert "started_at" in start_result

        # Test stopping consciousness monitoring
        stop_result = await consciousness_hub.stop_lambda_bot_monitoring()

        # Verify stop result structure
        assert "success" in stop_result
        if stop_result["success"]:
            assert "monitoring_active" in stop_result
            assert (
                start_result["monitoring_active"] is False
                if "monitoring_active" in start_result
                else True
            )
            assert "stopped_at" in stop_result

    @pytest.mark.asyncio
    async def test_consciousness_state_retrieval_through_hub(self, consciousness_hub):
        """Test consciousness state retrieval through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Test consciousness state retrieval
        state = await consciousness_hub.get_lambda_bot_consciousness_state()

        # Verify state structure
        if "error" not in state:
            assert "consciousness_level" in state
            assert "confidence_in_reasoning" in state
            assert "timestamp" in state
            assert "monitoring_active" in state

    @pytest.mark.asyncio
    async def test_agi_capabilities_demonstration_through_hub(self, consciousness_hub):
        """Test AGI capabilities demonstration through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Test AGI capabilities demonstration
        result = await consciousness_hub.demonstrate_lambda_bot_agi_capabilities()

        # Verify result structure
        assert "success" in result
        if result["success"]:
            assert "capabilities_demonstrated" in result
            assert "demonstration_completed_at" in result
            assert isinstance(result["capabilities_demonstrated"], list)

    @pytest.mark.asyncio
    async def test_consciousness_history_through_hub(self, consciousness_hub):
        """Test consciousness history retrieval through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Get consciousness history
        history = await consciousness_hub.get_lambda_bot_consciousness_history(limit=10)

        # Verify history structure
        assert isinstance(history, list)
        if history:
            history_entry = history[0]
            # Should have typical consciousness state fields
            assert isinstance(history_entry, dict)

    @pytest.mark.asyncio
    async def test_capability_unlocks_through_hub(self, consciousness_hub):
        """Test capability unlock checking through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Check capability unlocks
        unlock_result = await consciousness_hub.check_lambda_bot_capability_unlocks()

        # Verify unlock result structure
        if "error" not in unlock_result:
            assert "new_unlocks" in unlock_result
            assert "total_capabilities" in unlock_result
            assert "active_capabilities" in unlock_result
            assert isinstance(unlock_result["new_unlocks"], list)

    @pytest.mark.asyncio
    async def test_consciousness_metrics_through_hub(self, consciousness_hub):
        """Test consciousness metrics retrieval through the consciousness hub"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Skip test if ΛBot consciousness not available
        if "lambda_bot_consciousness" not in consciousness_hub.services:
            pytest.skip("ΛBot consciousness monitor integration not available")

        # Get consciousness metrics
        result = await consciousness_hub.get_lambda_bot_consciousness_metrics()

        # Verify result
        assert result["available"] is True
        assert "metrics" in result
        metrics = result["metrics"]
        assert "current_consciousness_level" in metrics
        assert "monitoring_active" in metrics
        assert "system_status" in metrics
        assert "lambda_bot_consciousness_available" in metrics

    @pytest.mark.asyncio
    async def test_error_handling_missing_service(self, consciousness_hub):
        """Test error handling when ΛBot consciousness service is not available"""
        # Initialize the hub
        await consciousness_hub.initialize()

        # Remove ΛBot consciousness service if it exists
        if "lambda_bot_consciousness" in consciousness_hub.services:
            del consciousness_hub.services["lambda_bot_consciousness"]

        # Test monitoring start with missing service
        result = await consciousness_hub.start_lambda_bot_monitoring()
        assert result["success"] is False
        assert "error" in result

        # Test monitoring stop with missing service
        result = await consciousness_hub.stop_lambda_bot_monitoring()
        assert result["success"] is False
        assert "error" in result

        # Test consciousness state with missing service
        result = await consciousness_hub.get_lambda_bot_consciousness_state()
        assert "error" in result

        # Test AGI demonstration with missing service
        result = await consciousness_hub.demonstrate_lambda_bot_agi_capabilities()
        assert result["success"] is False
        assert "error" in result

        # Test history with missing service
        history = await consciousness_hub.get_lambda_bot_consciousness_history()
        assert history == []

        # Test capability unlocks with missing service
        result = await consciousness_hub.check_lambda_bot_capability_unlocks()
        assert "error" in result

        # Test metrics with missing service
        result = await consciousness_hub.get_lambda_bot_consciousness_metrics()
        assert result["available"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_consciousness_state_management(self, lambda_bot_integration):
        """Test consciousness state management functionality"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Get consciousness state
        state = await lambda_bot_integration.get_consciousness_state()

        # Should get a valid state (either real or fallback)
        assert "consciousness_level" in state
        assert "confidence_in_reasoning" in state
        assert "timestamp" in state
        assert "monitoring_active" in state

        # Test state history tracking
        history = await lambda_bot_integration.get_consciousness_history(limit=5)
        assert isinstance(history, list)

    @pytest.mark.asyncio
    async def test_agi_capabilities_demonstration(self, lambda_bot_integration):
        """Test AGI capabilities demonstration"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Demonstrate AGI capabilities
        result = await lambda_bot_integration.demonstrate_agi_capabilities()

        # Should get a valid result (either real or fallback)
        assert "success" in result
        if result["success"]:
            assert "capabilities_demonstrated" in result
            assert "demonstration_completed_at" in result

            # Check that capabilities were marked as active
            capabilities = lambda_bot_integration.agi_capabilities
            demonstrated_count = sum(1 for active in capabilities.values() if active)
            assert demonstrated_count > 0

    @pytest.mark.asyncio
    async def test_capability_unlock_detection(self, lambda_bot_integration):
        """Test capability unlock detection"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Check capability unlocks
        unlock_result = await lambda_bot_integration.check_capability_unlocks()

        # Should get a valid unlock result
        assert "new_unlocks" in unlock_result
        assert "total_capabilities" in unlock_result
        assert "active_capabilities" in unlock_result
        assert "unlock_registry_size" in unlock_result

        # Verify data types
        assert isinstance(unlock_result["new_unlocks"], list)
        assert isinstance(unlock_result["total_capabilities"], int)
        assert isinstance(unlock_result["active_capabilities"], int)

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, lambda_bot_integration):
        """Test complete monitoring lifecycle"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Start monitoring
        start_result = await lambda_bot_integration.start_consciousness_monitoring()
        assert "success" in start_result

        # Verify monitoring is active
        if start_result["success"]:
            assert lambda_bot_integration.monitoring_active is True

        # Get current state while monitoring
        state = await lambda_bot_integration.get_consciousness_state()
        assert "timestamp" in state

        # Stop monitoring
        stop_result = await lambda_bot_integration.stop_consciousness_monitoring()
        assert "success" in stop_result

        # Verify monitoring is stopped
        if stop_result["success"]:
            assert lambda_bot_integration.monitoring_active is False

    @pytest.mark.asyncio
    async def test_consciousness_metrics_collection(self, lambda_bot_integration):
        """Test consciousness metrics collection"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Perform some operations to generate metrics
        await lambda_bot_integration.get_consciousness_state()
        await lambda_bot_integration.check_capability_unlocks()

        # Get metrics
        metrics = await lambda_bot_integration.get_consciousness_metrics()

        # Verify metrics structure
        assert "total_consciousness_checks" in metrics
        assert "consciousness_evolution_events" in metrics
        assert "current_consciousness_level" in metrics
        assert "monitoring_active" in metrics
        assert "agi_capabilities" in metrics
        assert "system_status" in metrics
        assert "lambda_bot_consciousness_available" in metrics
        assert "last_updated" in metrics

        # Check that metrics reflect activity
        assert metrics["total_consciousness_checks"] >= 1

    @pytest.mark.asyncio
    async def test_configuration_options(self):
        """Test different configuration options for ΛBot consciousness integration"""
        # Test with custom config
        custom_config = {
            "enable_consciousness_monitoring": False,
            "consciousness_check_interval": 10.0,
            "meta_cognitive_interval": 20.0,
            "capability_unlock_interval": 5.0,
            "enable_agi_demonstrations": False,
            "enable_background_monitoring": False,
            "consciousness_history_limit": 50,
            "enable_celebration_events": False,
        }

        integration = create_lambda_bot_consciousness_integration(custom_config)

        # Verify config was applied
        assert integration.config["enable_consciousness_monitoring"] is False
        assert integration.config["consciousness_check_interval"] == 10.0
        assert integration.config["meta_cognitive_interval"] == 20.0
        assert integration.config["enable_agi_demonstrations"] is False
        assert integration.config["enable_background_monitoring"] is False

    @pytest.mark.asyncio
    async def test_fallback_functionality(self, lambda_bot_integration):
        """Test fallback functionality when main components are not available"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Test fallback consciousness state
        fallback_state = lambda_bot_integration._get_fallback_consciousness_state()
        assert fallback_state["consciousness_level"] == ConsciousnessLevel.DELIBERATIVE
        assert "confidence_in_reasoning" in fallback_state
        assert "known_biases" in fallback_state
        assert "learning_priorities" in fallback_state
        assert "fallback" in fallback_state

        # Test fallback AGI demonstration
        fallback_demo = await lambda_bot_integration._fallback_demonstrate_agi()
        assert fallback_demo["success"] is True
        assert "capabilities_demonstrated" in fallback_demo
        assert "fallback" in fallback_demo

    @pytest.mark.asyncio
    async def test_background_monitoring_simulation(self, lambda_bot_integration):
        """Test background monitoring functionality (simulated)"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Set up for background monitoring
        lambda_bot_integration.monitoring_active = True
        lambda_bot_integration.consciousness_check_interval = (
            0.1  # Very fast for testing
        )

        # Run a brief background monitoring loop simulation
        initial_checks = lambda_bot_integration.monitoring_metrics[
            "total_consciousness_checks"
        ]

        # Simulate a few monitoring cycles
        for _ in range(3):
            await lambda_bot_integration.get_consciousness_state()
            await lambda_bot_integration.check_capability_unlocks()

        # Verify metrics were updated
        final_checks = lambda_bot_integration.monitoring_metrics[
            "total_consciousness_checks"
        ]
        assert final_checks > initial_checks

    @pytest.mark.asyncio
    async def test_consciousness_level_transitions(self, lambda_bot_integration):
        """Test consciousness level transition detection"""
        # Initialize the integration
        await lambda_bot_integration.initialize()

        # Get initial consciousness state
        initial_state = await lambda_bot_integration.get_consciousness_state()
        initial_level = initial_state.get(
            "consciousness_level", ConsciousnessLevel.BASIC
        )

        # Test capability unlock detection for different levels
        unlock_result = await lambda_bot_integration.check_capability_unlocks()

        # Should handle different consciousness levels appropriately
        assert "new_unlocks" in unlock_result
        assert isinstance(unlock_result["new_unlocks"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
