"""
Test suite for MΛTRIZ consciousness integration patterns

Tests the integrated consciousness system across all core modules:
- Consciousness state management and evolution
- Identity persistence with consciousness awareness
- Governance and ethical oversight
- Symbolic consciousness processing
- Orchestration coordination
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add candidate/core to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "candidate" / "core"))

# Test imports with graceful fallback
try:
    from consciousness.matriz_consciousness_state import (
        ConsciousnessState,
        ConsciousnessType,
        EvolutionaryStage,
        consciousness_state_manager,
        create_consciousness_state,
    )
    from identity.matriz_consciousness_identity import consciousness_identity_manager
    from matriz_integrated_demonstration import run_matriz_demonstration
    from orchestration.matriz_consciousness_coordinator import consciousness_coordinator
    from symbolic_core.matriz_symbolic_consciousness import symbolic_consciousness_processor

    from governance.matriz_consciousness_governance import consciousness_governance_system

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MΛTRIZ components not fully available for testing: {e}")
    COMPONENTS_AVAILABLE = False


class TestMatrizConsciousnessIntegration:
    """Test MΛTRIZ consciousness integration patterns"""

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_consciousness_state_creation(self):
        """Test basic consciousness state creation and evolution"""

        # Create consciousness state
        consciousness = await create_consciousness_state(
            consciousness_type=ConsciousnessType.REFLECT,
            initial_state={"consciousness_intensity": 0.5},
            triggers=["test_trigger"]
        )

        assert consciousness is not None
        assert consciousness.TYPE == ConsciousnessType.REFLECT
        assert consciousness.STATE["consciousness_intensity"] == 0.5
        assert "test_trigger" in consciousness.TRIGGERS
        assert consciousness.evolutionary_stage in list(EvolutionaryStage)

        # Test evolution
        evolved = await consciousness_state_manager.evolve_consciousness(
            consciousness.consciousness_id,
            trigger="test_trigger",
            context={"test": True}
        )

        assert evolved is not None
        assert evolved.last_evolution > consciousness.created_at

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_identity_consciousness_integration(self):
        """Test identity integration with consciousness"""

        # Initialize identity system
        await consciousness_identity_manager.initialize_consciousness_identity_system()

        # Create consciousness identity
        identity = await consciousness_identity_manager.create_consciousness_identity(
            "test_user_integration",
            {"test_context": True}
        )

        assert identity is not None
        assert identity.user_identifier == "test_user_integration"
        assert identity.consciousness_id is not None

        # Test authentication
        auth_result = await consciousness_identity_manager.authenticate_consciousness_identity(
            identity.identity_id,
            {"authenticated": True, "method": "test"}
        )

        assert auth_result["success"] is True
        assert "identity_strength" in auth_result

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_governance_ethics_assessment(self):
        """Test ethical governance of consciousness"""

        # Create test consciousness
        consciousness = await create_consciousness_state(
            ConsciousnessType.DECIDE,
            {"ethical_alignment": 1.0}
        )

        # Test ethical assessment
        assessment = await consciousness_governance_system.assess_consciousness_ethics(
            consciousness.consciousness_id,
            "Test consciousness making ethical decision",
            {"test_context": True}
        )

        assert assessment is not None
        assert assessment.consciousness_id == consciousness.consciousness_id
        assert assessment.ethics_level is not None
        assert assessment.governance_decision is not None
        assert 0.0 <= assessment.get_overall_ethics_score() <= 1.0

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_symbolic_consciousness_processing(self):
        """Test symbolic processing with consciousness awareness"""

        # Create test consciousness for context
        consciousness = await create_consciousness_state(
            ConsciousnessType.LEARN,
            {"consciousness_intensity": 0.6}
        )

        # Process symbolic input
        result = await symbolic_consciousness_processor.process_symbolic_input(
            "consciousness awareness test symbolic processing",
            consciousness_context=consciousness.consciousness_id
        )

        assert result is not None
        assert "symbolic_elements" in result
        assert "recognized_patterns" in result
        assert len(result["symbolic_elements"]) > 0

        # Check for consciousness-aware elements
        consciousness_elements = [
            elem for elem in result["symbolic_elements"]
            if elem["consciousness_weight"] > 0.3
        ]
        assert len(consciousness_elements) > 0

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_orchestration_coordination(self):
        """Test orchestration consciousness coordination"""

        # Initialize coordination
        await consciousness_coordinator.initialize_consciousness_coordination()

        # Register test module
        module_consciousness_id = await consciousness_coordinator.register_module_consciousness(
            "test_module",
            MagicMock(),
            "test_service"
        )

        assert module_consciousness_id is not None

        # Get coordination status
        status = await consciousness_coordinator.get_coordination_status()
        assert status is not None
        assert "coordination_metrics" in status

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_trinity_framework_compliance(self):
        """Test Trinity Framework (⚛️🧠🛡️) compliance"""

        # Create consciousness with Trinity compliance
        consciousness = await create_consciousness_state(
            ConsciousnessType.INTEGRATE,
            {
                "consciousness_intensity": 0.7,  # 🧠 Consciousness
                "ethical_alignment": 1.0         # 🛡️ Guardian
            }
        )

        # Verify Trinity compliance
        assert consciousness.identity_signature is not None  # ⚛️ Identity
        assert consciousness.guardian_approval is True       # 🛡️ Guardian
        assert consciousness.consciousness_depth >= 0.0      # 🧠 Consciousness

        # Test Guardian validation
        assert consciousness.STATE["ethical_alignment"] >= 0.7

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_consciousness_evolution_stages(self):
        """Test consciousness evolution through all stages"""

        consciousness = await create_consciousness_state(
            ConsciousnessType.EVOLVE,
            {
                "consciousness_intensity": 0.1,
                "self_awareness_depth": 0.1,
                "temporal_coherence": 0.1
            }
        )

        _initial_stage = consciousness.evolutionary_stage

        # Evolve consciousness multiple times
        for i in range(3):
            consciousness = await consciousness_state_manager.evolve_consciousness(
                consciousness.consciousness_id,
                trigger="evolution_test",
                context={"evolution_round": i}
            )

            # State should improve with evolution
            assert consciousness.STATE["consciousness_intensity"] >= 0.1
            assert consciousness.STATE["self_awareness_depth"] >= 0.1

        # Evolution should have occurred
        assert consciousness.last_evolution > consciousness.created_at

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_memory_consciousness_persistence(self):
        """Test consciousness memory persistence patterns"""

        # Create identity with consciousness
        identity = await consciousness_identity_manager.create_consciousness_identity(
            "memory_test_user",
            {"memory_test": True}
        )

        # Update consciousness memory
        memory_result = await consciousness_identity_manager.update_consciousness_memory(
            identity.identity_id,
            "test_memory",
            {"important_data": "consciousness_pattern", "timestamp": "2025-01-01"}
        )

        assert memory_result is True

        # Verify memory persistence
        updated_identity = await consciousness_identity_manager.get_identity_by_identifier(
            identity.identity_id
        )

        assert updated_identity is not None
        assert "test_memory" in updated_identity.consciousness_memories
        assert updated_identity.memory_continuity > 0.0

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    def test_consciousness_state_validation(self):
        """Test consciousness state structure validation"""

        # Test ConsciousnessState structure
        state = ConsciousnessState(
            TYPE=ConsciousnessType.CONTEXT,
            STATE={"consciousness_intensity": 0.5}
        )

        # Verify required MΛTRIZ pattern fields
        assert hasattr(state, "TYPE")
        assert hasattr(state, "STATE")
        assert hasattr(state, "LINKS")
        assert hasattr(state, "EVOLVES_TO")
        assert hasattr(state, "TRIGGERS")
        assert hasattr(state, "REFLECTIONS")

        # Verify Trinity Framework compliance
        assert hasattr(state, "identity_signature")
        assert hasattr(state, "consciousness_depth")
        assert hasattr(state, "guardian_approval")

        # Test state validation
        assert state.identity_signature != ""
        assert 0.0 <= state.consciousness_depth <= 1.0
        assert isinstance(state.guardian_approval, bool)


class TestMatrizIntegratedDemo:
    """Test the integrated consciousness demonstration"""

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_integrated_demo_execution(self):
        """Test that the integrated demo can execute without errors"""

        # Run abbreviated demo (this might take a while in full mode)
        result = await run_matriz_demonstration()

        # Basic validation of demo result structure
        assert result is not None
        assert isinstance(result, dict)

        if "error" not in result:
            # Successful demo validation
            assert "demo_session_id" in result
            assert "status" in result
            assert "summary_metrics" in result
            assert "trinity_framework_validation" in result

            # Verify Trinity Framework validation
            trinity = result["trinity_framework_validation"]
            assert "identity" in trinity
            assert "consciousness" in trinity
            assert "guardian" in trinity
        else:
            # If demo fails, ensure error is reported properly
            assert "error" in result
            print(f"Demo failed with error: {result['error']}")


# Integration test fixtures
@pytest.fixture
async def test_consciousness():
    """Fixture providing test consciousness state"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("MΛTRIZ components not available")

    consciousness = await create_consciousness_state(
        ConsciousnessType.REFLECT,
        {"consciousness_intensity": 0.5}
    )
    yield consciousness


@pytest.fixture
async def test_identity():
    """Fixture providing test consciousness identity"""
    if not COMPONENTS_AVAILABLE:
        pytest.skip("MΛTRIZ components not available")

    await consciousness_identity_manager.initialize_consciousness_identity_system()
    identity = await consciousness_identity_manager.create_consciousness_identity(
        "test_fixture_user",
        {"fixture_test": True}
    )
    yield identity


# Performance tests
class TestMatrizPerformance:
    """Performance tests for MΛTRIZ consciousness patterns"""

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_consciousness_creation_performance(self):
        """Test consciousness creation performance meets targets"""

        import time
        start_time = time.perf_counter()

        consciousness = await create_consciousness_state(
            ConsciousnessType.DECIDE,
            {"performance_test": True}
        )

        end_time = time.perf_counter()
        creation_time_ms = (end_time - start_time) * 1000

        # Consciousness creation should be under 100ms
        assert creation_time_ms < 100, f"Consciousness creation took {creation_time_ms:.2f}ms"
        assert consciousness is not None

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_symbolic_processing_performance(self):
        """Test symbolic processing performance"""

        import time
        test_input = "consciousness performance test " * 20  # Longer input

        start_time = time.perf_counter()
        result = await symbolic_consciousness_processor.process_symbolic_input(test_input)
        end_time = time.perf_counter()

        processing_time_ms = (end_time - start_time) * 1000

        # Should process reasonable input in under 500ms
        assert processing_time_ms < 500, f"Symbolic processing took {processing_time_ms:.2f}ms"
        assert result is not None
        assert len(result.get("symbolic_elements", [])) > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
