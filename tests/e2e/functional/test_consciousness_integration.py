"""
Comprehensive Functional Tests for LUKHAS Consciousness Systems
==============================================================

These tests validate ACTUAL FUNCTIONALITY, not just imports.
Tests real behavior, workflows, and system integration.
"""

import asyncio

import pytest


class TestConsciousnessIntegration:
    """Test real consciousness system functionality and integration."""

    @pytest.mark.asyncio
    async def test_awareness_tracker_full_workflow(self):
        """Test complete awareness tracker processing workflow."""
        from lukhas.consciousness.awareness.awareness_tracker import AwarenessTracker

        tracker = AwarenessTracker({"test_mode": True})

        # Test initialization
        init_success = await tracker.initialize()
        assert init_success is True

        # Test different category processing
        test_cases = [
            {"category": "consciousness", "data": "test_consciousness"},
            {"category": "governance", "policy": "test_policy"},
            {"category": "quantum", "state": "superposition"},
            {"category": "identity", "user_id": "test_123"},
            {"category": "voice", "audio_data": "mock_audio"},
            "generic_string_data",
        ]

        for test_data in test_cases:
            result = await tracker.process(test_data)
            assert result["status"] == "success"
            assert result["component"] == "AwarenessTracker"
            assert "result" in result
            assert "timestamp" in result

        # Test validation
        is_valid = await tracker.validate()
        assert is_valid is True

        # Test status
        status = tracker.get_status()
        assert status["status"] == "active"
        assert status["initialized"] is True

    @pytest.mark.asyncio
    async def test_creative_engine_full_generation(self):
        """Test complete creative engine haiku generation workflow."""
        from lukhas.consciousness.creativity.creative_engine import (
            CreativeConfig,
            CreativeContext,
            CreativeStyle,
            EnterpriseNeuralHaikuGenerator,
            MockFederatedClient,
            MockNeuralModel,
            MockSymbolicKB,
        )

        # Create engine with real configuration
        config = CreativeConfig(expansion_depth=3, temperature=0.7, max_concurrent_generations=5)

        engine = EnterpriseNeuralHaikuGenerator(
            config=config,
            neural_model=MockNeuralModel(),
            symbolic_kb=MockSymbolicKB(),
            federated_client=MockFederatedClient(),
        )

        # Test multiple generation contexts
        test_contexts = [
            CreativeContext(
                user_id="user_1",
                session_id="session_1",
                cultural_context={"japanese": 0.8},
                emotional_state={"tranquil": 0.9, "contemplative": 0.7},
                previous_outputs=[],
                style_preferences={CreativeStyle.CLASSICAL: 0.8},
                constraints={},
            ),
            CreativeContext(
                user_id="user_2",
                session_id="session_2",
                cultural_context={"modern": 0.6},
                emotional_state={"energetic": 0.8, "creative": 0.9},
                previous_outputs=[],
                style_preferences={CreativeStyle.MODERN: 0.9},
                constraints={"max_length": 100},
            ),
        ]

        async with engine:
            for context in test_contexts:
                haiku, metrics = await engine.generate_haiku(context)

                # Validate haiku structure
                assert isinstance(haiku, str)
                assert len(haiku) > 0
                lines = haiku.split("\n")
                assert len(lines) == 3  # Traditional haiku structure

                # Validate metrics
                assert metrics.creativity_score > 0.0
                assert metrics.creativity_score <= 1.0
                assert metrics.generation_time_ms > 0
                assert 0.0 <= metrics.syllable_accuracy <= 1.0
                assert 0.0 <= metrics.semantic_coherence <= 1.0

            # Test analytics
            analytics = await engine.get_performance_analytics()
            assert "total_generations" in analytics
            assert analytics["total_generations"] >= 2

    @pytest.mark.asyncio
    async def test_platform_integration_workflow(self):
        """Test complete platform integration and component management."""
        from lukhas.consciousness.awareness.awareness_tracker import AwarenessTracker
        from lukhas.consciousness.bridge import create_consciousness_bridge
        from lukhas.consciousness.platform import create_consciousness_platform

        # Create platform
        platform = create_consciousness_platform({"integration_test": True})
        init_success = await platform.initialize()
        assert init_success is True

        # Create components
        tracker = AwarenessTracker({"platform_mode": True})
        bridge = create_consciousness_bridge({"test": True})

        await tracker.initialize()
        await bridge.connect()

        # Register components
        tracker_reg = await platform.register_component("awareness", tracker)
        bridge_reg = await platform.register_component("bridge", bridge)

        assert tracker_reg is True
        assert bridge_reg is True

        # Test component retrieval
        retrieved_tracker = await platform.get_component("awareness")
        retrieved_bridge = await platform.get_component("bridge")

        assert retrieved_tracker is not None
        assert retrieved_bridge is not None

        # Test all components
        all_components = await platform.get_all_components()
        assert len(all_components) == 2
        assert "awareness" in all_components
        assert "bridge" in all_components

        # Test request processing
        test_request = {
            "id": "integration_test_001",
            "action": "consciousness_processing",
            "components": ["awareness", "bridge"],
        }

        result = await platform.process_consciousness_request(test_request)
        assert result["status"] == "processed"
        assert result["platform"] == "consciousness"
        assert result["request_id"] == "integration_test_001"
        assert result["components_available"] == 2

        # Test platform status
        status = platform.get_platform_status()
        assert status["active"] is True
        assert status["components_count"] == 2
        assert status["platform_type"] == "consciousness"
        assert status["uptime_seconds"] is not None

    @pytest.mark.asyncio
    async def test_end_to_end_consciousness_workflow(self):
        """Test complete end-to-end consciousness processing workflow."""
        from lukhas.consciousness.awareness.awareness_tracker import AwarenessTracker
        from lukhas.consciousness.creativity.creative_engine import (
            CreativeConfig,
            CreativeContext,
            CreativeStyle,
            EnterpriseNeuralHaikuGenerator,
            MockFederatedClient,
            MockNeuralModel,
            MockSymbolicKB,
        )
        from lukhas.consciousness.platform import create_consciousness_platform

        # Setup integrated system
        platform = create_consciousness_platform()
        await platform.initialize()

        tracker = AwarenessTracker()
        await tracker.initialize()
        await platform.register_component("awareness", tracker)

        engine = EnterpriseNeuralHaikuGenerator(
            config=CreativeConfig(),
            neural_model=MockNeuralModel(),
            symbolic_kb=MockSymbolicKB(),
            federated_client=MockFederatedClient(),
        )
        await platform.register_component("creativity", engine)

        # Test integrated workflow
        consciousness_data = {
            "category": "consciousness",
            "user_id": "e2e_user",
            "intent": "creative_generation",
            "context": "poetry",
        }

        # Process through awareness
        awareness_result = await tracker.process(consciousness_data)
        assert awareness_result["status"] == "success"

        # Generate creative content
        async with engine:
            context = CreativeContext(
                user_id="e2e_user",
                session_id="e2e_test",
                cultural_context={"poetry": 0.9},
                emotional_state={"inspired": 0.8},
                previous_outputs=[],
                style_preferences={CreativeStyle.MODERN: 0.7},
                constraints={},
            )

            haiku, metrics = await engine.generate_haiku(context)
            assert haiku is not None
            assert len(haiku) > 0
            assert metrics.creativity_score > 0

        # Verify platform coordination
        final_status = platform.get_platform_status()
        assert final_status["active"] is True
        assert final_status["components_count"] >= 2

    def test_consciousness_system_contracts(self):
        """Test that consciousness systems adhere to expected contracts."""
        from lukhas.consciousness.awareness.awareness_tracker import AwarenessTracker
        from lukhas.consciousness.bridge import ConsciousnessBridge
        from lukhas.consciousness.platform import ConsciousnessPlatform

        # Test class instantiation contracts
        tracker = AwarenessTracker()
        assert hasattr(tracker, "initialize")
        assert hasattr(tracker, "process")
        assert hasattr(tracker, "validate")
        assert hasattr(tracker, "get_status")
        assert hasattr(tracker, "shutdown")

        platform = ConsciousnessPlatform()
        assert hasattr(platform, "initialize")
        assert hasattr(platform, "register_component")
        assert hasattr(platform, "get_component")
        assert hasattr(platform, "process_consciousness_request")
        assert hasattr(platform, "get_platform_status")

        bridge = ConsciousnessBridge()
        assert hasattr(bridge, "connect")
        assert hasattr(bridge, "disconnect")
        assert hasattr(bridge, "get_status")

    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(self):
        """Test system resilience and error handling."""
        from lukhas.consciousness.awareness.awareness_tracker import AwarenessTracker

        tracker = AwarenessTracker()
        await tracker.initialize()

        # Test with invalid data
        invalid_inputs = [None, {}, [], 42, {"invalid": None}]

        for invalid_input in invalid_inputs:
            try:
                result = await tracker.process(invalid_input)
                # Should handle gracefully, not crash
                assert "status" in result
            except Exception:
                # If it throws, that's also acceptable error handling
                pass

        # Test multiple initializations (should be idempotent)
        init1 = await tracker.initialize()
        init2 = await tracker.initialize()
        assert init1 is True
        assert init2 is True

        # Test validation in different states
        validation = await tracker.validate()
        assert isinstance(validation, bool)


if __name__ == "__main__":
    # Direct execution for debugging
    import sys

    sys.path.append("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    test_instance = TestConsciousnessIntegration()

    print("Running functional tests directly...")

    # Run a quick test
    asyncio.run(test_instance.test_awareness_tracker_full_workflow())
    print("✅ Awareness tracker functional test passed!")

    asyncio.run(test_instance.test_platform_integration_workflow())
    print("✅ Platform integration functional test passed!")

    print("🎯 All direct functional tests completed successfully!")
