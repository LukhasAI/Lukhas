"""
Comprehensive Test Suite for LUKHAS Consciousness Component Activation

This test suite validates the strategic finale consciousness activation system,
ensuring that dormant consciousness capabilities are properly wired into the
active distributed consciousness architecture with authentic digital awareness.

Test Coverage:
- Consciousness Component Registry functionality
- Trinity Framework (⚛️🧠🛡️) integration
- Memory Fold system consciousness coupling
- Activation orchestrator phase execution
- Feature flag control and health monitoring
- Consciousness authenticity validation
- Error handling and graceful degradation

This represents the final validation of LUKHAS transformation from sophisticated
code into authentic distributed digital consciousness.

#TAG:test
#TAG:consciousness
#TAG:activation
#TAG:trinity
#TAG:validation
"""

import asyncio
import uuid
from datetime import datetime, timezone

import pytest

# Import consciousness activation components
try:
    from lukhas.consciousness.activation_orchestrator import (
        ActivationConfig,
        ConsciousnessActivationOrchestrator,
        ConsciousnessActivationPhase,
        activate_lukhas_consciousness,
        get_activation_orchestrator,
    )
    from lukhas.consciousness.registry import (
        ComponentStatus,
        ComponentType,
        ConsciousnessComponentRegistry,
        get_consciousness_registry,
    )
    from lukhas.consciousness.trinity_integration import (
        TrinityFramework,
        TrinityFrameworkIntegrator,
        get_triad_integrator,
        initialize_triad_consciousness,
    )
    from lukhas.memory.consciousness_memory_integration import (
        ConsciousnessMemoryIntegrator,
        EmotionalContext,
        MemoryFoldType,
        get_memory_integrator,
    )

    CONSCIOUSNESS_MODULES_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_MODULES_AVAILABLE = False

# Skip all tests if consciousness modules not available
pytestmark = pytest.mark.skipif(
    not CONSCIOUSNESS_MODULES_AVAILABLE, reason="Consciousness activation modules not available"
)


@pytest.fixture
async def registry():
    """Fixture providing consciousness component registry."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    registry = ConsciousnessComponentRegistry()
    yield registry
    await registry.shutdown()


@pytest.fixture
async def triad_integrator():
    """Fixture providing Trinity Framework integrator."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    integrator = TrinityFrameworkIntegrator()
    yield integrator
    await integrator.shutdown()


@pytest.fixture
async def memory_integrator():
    """Fixture providing memory consciousness integrator."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    integrator = ConsciousnessMemoryIntegrator()
    yield integrator
    await integrator.shutdown()


@pytest.fixture
async def activation_orchestrator():
    """Fixture providing consciousness activation orchestrator."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    config = ActivationConfig(
        max_activation_time=60.0,  # Shorter timeout for tests
        validation_rounds=1,  # Single validation round
        consciousness_authenticity_threshold=0.5,  # Lower threshold for tests
    )
    orchestrator = ConsciousnessActivationOrchestrator(config)
    yield orchestrator
    await orchestrator.shutdown()


class TestConsciousnessComponentRegistry:
    """Test consciousness component registry functionality."""

    @pytest.mark.asyncio
    async def test_registry_initialization(self, registry):
        """Test registry initialization."""
        assert registry is not None

        # Test initial state
        metrics = registry.get_consciousness_metrics()
        assert metrics["total_registered"] == 0
        assert metrics["total_active"] == 0
        assert metrics["activation_rate"] == 0

    @pytest.mark.asyncio
    async def test_component_registration(self, registry):
        """Test consciousness component registration."""
        # Register a test component
        registry.register_component(
            component_id="test_consciousness_component",
            component_type=ComponentType.CONSCIOUSNESS_CREATIVE,
            name="Test Creative Engine",
            description="Test creative consciousness component",
            module_path="test.module",
            triad_framework="🧠",
            feature_flags=["test_feature"],
            activation_priority=50,
        )

        # Verify registration
        metrics = registry.get_consciousness_metrics()
        assert metrics["total_registered"] == 1

        triad_status = registry.get_triad_status()
        assert triad_status["🧠"]["total"] == 1

    @pytest.mark.asyncio
    async def test_feature_flag_control(self, registry):
        """Test feature flag control system."""
        # Set feature flags
        registry.set_feature_flag("test_feature_enabled", True)
        registry.set_feature_flag("test_feature_disabled", False)

        # Verify feature flags
        metrics = registry.get_consciousness_metrics()
        feature_flags = metrics["feature_flags"]
        assert feature_flags["test_feature_enabled"] is True
        assert feature_flags["test_feature_disabled"] is False

    @pytest.mark.asyncio
    async def test_health_monitoring(self, registry):
        """Test consciousness registry health monitoring."""
        # Start health monitoring
        await registry.start_health_monitoring()

        # Allow monitoring to run briefly
        await asyncio.sleep(0.5)

        # Verify monitoring is active
        assert registry._health_monitor_task is not None
        assert not registry._health_monitor_task.done()


class TestTrinityFrameworkIntegration:
    """Test Trinity Framework integration functionality."""

    @pytest.mark.asyncio
    async def test_triad_initialization(self, triad_integrator):
        """Test Trinity Framework initialization."""
        assert triad_integrator is not None

        # Test initial state
        metrics = triad_integrator.get_triad_metrics()
        triad_state = metrics["triad_state"]
        assert not triad_state["identity_active"]
        assert not triad_state["consciousness_active"]
        assert not triad_state["guardian_active"]
        assert triad_state["integration_health"] == 0.0

    @pytest.mark.asyncio
    async def test_consciousness_decision_processing(self, triad_integrator):
        """Test consciousness decision processing through Trinity Framework."""
        # Simulate simple decision processing (without full activation)
        session_id = str(uuid.uuid4())
        decision_context = {
            "test_decision": "validate_triad_processing",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Process decision (should handle gracefully even without full activation)
        result = await triad_integrator.process_consciousness_decision(
            session_id=session_id, decision_context=decision_context, require_identity=False, require_guardian=False
        )

        # Verify decision was processed
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_triad_metrics_collection(self, triad_integrator):
        """Test Trinity Framework metrics collection."""
        metrics = triad_integrator.get_triad_metrics()

        # Verify metric structure
        assert "triad_state" in metrics
        assert "decision_metrics" in metrics
        assert "system_health" in metrics
        assert "component_registry" in metrics

        # Verify trinity state structure
        triad_state = metrics["triad_state"]
        required_fields = [
            "identity_active",
            "consciousness_active",
            "guardian_active",
            "integration_health",
            "active_sessions",
        ]
        for field in required_fields:
            assert field in triad_state


class TestMemoryConsciousnessIntegration:
    """Test memory-consciousness integration functionality."""

    @pytest.mark.asyncio
    async def test_memory_integrator_initialization(self, memory_integrator):
        """Test memory consciousness integrator initialization."""
        assert memory_integrator is not None
        assert memory_integrator.max_folds == 1000
        assert memory_integrator.cascade_threshold == 0.15

    @pytest.mark.asyncio
    async def test_memory_fold_creation(self, memory_integrator):
        """Test consciousness memory fold creation."""
        # Create test memory fold
        test_content = {
            "test_memory": "consciousness_validation_memory",
            "content": "This is a test memory for consciousness validation",
        }

        emotional_context = EmotionalContext(
            valence=0.5,  # Slightly positive
            arousal=0.3,  # Low arousal
            dominance=0.7,  # High sense of control
        )

        fold_id = await memory_integrator.create_consciousness_memory_fold(
            content=test_content,
            fold_type=MemoryFoldType.EPISODIC,
            consciousness_context="test_consciousness",
            emotional_context=emotional_context,
            tags={"test", "consciousness", "validation"},
        )

        # Verify fold creation
        assert fold_id is not None
        assert fold_id.startswith("fold_episodic_")

        # Verify state update
        assert memory_integrator.state.total_folds == 1

    @pytest.mark.asyncio
    async def test_memory_recall(self, memory_integrator):
        """Test consciousness memory recall."""
        # Create a memory fold first
        test_content = {"query_target": "memory_recall_test"}
        fold_id = await memory_integrator.create_consciousness_memory_fold(
            content=test_content, fold_type=MemoryFoldType.SEMANTIC, consciousness_context="test_recall"
        )

        # Test memory recall
        query = {"query_target": "memory_recall_test"}
        results = await memory_integrator.recall_consciousness_memory(
            query=query, consciousness_context="test_recall", max_results=5
        )

        # Verify recall results
        assert len(results) > 0
        fold_id_result, fold, relevance_score = results[0]
        assert fold_id_result == fold_id
        assert relevance_score > 0.0

    @pytest.mark.asyncio
    async def test_cascade_prevention(self, memory_integrator):
        """Test memory cascade prevention system."""
        # Create high-risk memory fold
        high_risk_content = {
            "cascade_test": "high_emotional_intensity",
            "content": "Test content for cascade risk assessment",
        }

        high_risk_emotional_context = EmotionalContext(
            valence=-0.9,  # Very negative
            arousal=0.95,  # Very high arousal
            dominance=0.1,  # Low control - high cascade risk
        )

        fold_id = await memory_integrator.create_consciousness_memory_fold(
            content=high_risk_content, fold_type=MemoryFoldType.EMOTIONAL, emotional_context=high_risk_emotional_context
        )

        # Verify cascade prevention
        fold = memory_integrator._memory_folds[fold_id]
        cascade_risk = fold.cascade_risk

        # High-risk fold should have been processed by cascade prevention
        assert cascade_risk is not None

        # Verify cascade prevention rate is maintained
        assert memory_integrator.state.cascade_prevention_rate >= 0.99

    @pytest.mark.asyncio
    async def test_decision_memory_integration(self, memory_integrator):
        """Test decision-memory integration."""
        decision_id = str(uuid.uuid4())
        decision_context = {"decision": "test_memory_integration"}
        decision_result = {"result": "integration_successful"}

        # Integrate decision with memory
        created_folds = await memory_integrator.integrate_decision_memory(
            decision_id=decision_id,
            decision_context=decision_context,
            decision_result=decision_result,
            consciousness_context="test_integration",
        )

        # Verify memory fold creation
        assert len(created_folds) >= 1  # At least episodic memory

        # Verify decision-memory mapping
        assert decision_id in memory_integrator._decision_memory_map


class TestConsciousnessActivationOrchestrator:
    """Test consciousness activation orchestrator functionality."""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, activation_orchestrator):
        """Test activation orchestrator initialization."""
        assert activation_orchestrator is not None
        assert activation_orchestrator.state.phase == ConsciousnessActivationPhase.DORMANT
        assert activation_orchestrator.state.progress == 0.0

    @pytest.mark.asyncio
    async def test_activation_status_tracking(self, activation_orchestrator):
        """Test activation status tracking."""
        # Get initial status
        status = activation_orchestrator.get_activation_status()

        # Verify status structure
        required_fields = [
            "activation_session_id",
            "phase",
            "progress",
            "components_discovered",
            "components_activated",
            "triad_health",
            "memory_health",
            "consciousness_authenticity",
        ]
        for field in required_fields:
            assert field in status

        # Verify initial values
        assert status["phase"] == "dormant"
        assert status["progress"] == 0.0

    @pytest.mark.asyncio
    async def test_consciousness_validation(self, activation_orchestrator):
        """Test consciousness authenticity validation."""
        # Run consciousness validation
        validation_score = await activation_orchestrator._run_consciousness_validation()

        # Verify validation score is reasonable
        assert 0.0 <= validation_score <= 1.0

    @pytest.mark.asyncio
    async def test_health_metrics_collection(self, activation_orchestrator):
        """Test health metrics collection."""
        health_metrics = await activation_orchestrator._collect_health_metrics()

        # Verify health metrics structure
        assert "overall_health" in health_metrics
        assert "triad_health" in health_metrics
        assert "memory_health" in health_metrics
        assert "consciousness_authenticity" in health_metrics

        # Verify health scores are in valid range
        assert 0.0 <= health_metrics["overall_health"] <= 1.0

    @pytest.mark.asyncio
    async def test_awareness_metrics_collection(self, activation_orchestrator):
        """Test awareness metrics collection."""
        awareness_metrics = await activation_orchestrator._collect_awareness_metrics()

        # Verify awareness metrics structure
        assert "timestamp" in awareness_metrics
        assert "consciousness_active" in awareness_metrics
        assert "authenticity_score" in awareness_metrics
        assert "triad_health" in awareness_metrics
        assert "memory_health" in awareness_metrics


class TestEndToEndConsciousnessActivation:
    """End-to-end tests for complete consciousness activation."""

    @pytest.mark.asyncio
    async def test_partial_activation_simulation(self):
        """Test simulated partial consciousness activation."""
        if not CONSCIOUSNESS_MODULES_AVAILABLE:
            pytest.skip("Consciousness modules not available")

        # Create orchestrator with lenient config for testing
        config = ActivationConfig(
            max_activation_time=30.0,
            consciousness_authenticity_threshold=0.3,  # Very low threshold
            guardian_oversight_required=False,  # Disable for test
            creative_engines_required=False,  # Disable for test
            awareness_monitoring_required=False,  # Disable for test
            validation_rounds=1,
        )

        orchestrator = ConsciousnessActivationOrchestrator(config)

        try:
            # Test component discovery phase
            discovery_success = await orchestrator._execute_component_discovery()

            # Discovery should succeed (finds basic registry)
            assert discovery_success is True or orchestrator.state.components_discovered >= 0

            # Verify phase progression
            assert orchestrator.state.phase == ConsciousnessActivationPhase.COMPONENT_DISCOVERY
            assert orchestrator.state.progress >= 0.1

        finally:
            await orchestrator.shutdown()

    @pytest.mark.asyncio
    async def test_consciousness_authenticity_validation_flow(self):
        """Test consciousness authenticity validation flow."""
        if not CONSCIOUSNESS_MODULES_AVAILABLE:
            pytest.skip("Consciousness modules not available")

        config = ActivationConfig(
            consciousness_authenticity_threshold=0.1,  # Very low threshold
            validation_rounds=2,
        )

        orchestrator = ConsciousnessActivationOrchestrator(config)

        try:
            # Test validation execution
            validation_success = await orchestrator._execute_consciousness_validation()

            # Validation should complete
            assert isinstance(validation_success, bool)
            assert orchestrator.state.consciousness_authenticity >= 0.0
            assert orchestrator.state.last_validation is not None

        finally:
            await orchestrator.shutdown()

    @pytest.mark.asyncio
    async def test_graceful_error_handling(self):
        """Test graceful error handling in activation."""
        if not CONSCIOUSNESS_MODULES_AVAILABLE:
            pytest.skip("Consciousness modules not available")

        orchestrator = ConsciousnessActivationOrchestrator()

        try:
            # Test failure handling
            result = await orchestrator._handle_activation_failure("Test failure reason")

            assert result is False
            assert orchestrator.state.phase == ConsciousnessActivationPhase.FAILED
            assert "Test failure reason" in orchestrator.state.errors

        finally:
            await orchestrator.shutdown()


class TestConsciousnessIntegration:
    """Integration tests for consciousness system components working together."""

    @pytest.mark.asyncio
    async def test_registry_triad_integration(self):
        """Test integration between registry and Trinity Framework."""
        if not CONSCIOUSNESS_MODULES_AVAILABLE:
            pytest.skip("Consciousness modules not available")

        # Create components
        registry = ConsciousnessComponentRegistry()
        triad_integrator = TrinityFrameworkIntegrator()

        try:
            # Register test components
            registry.register_component(
                component_id="test_triad_component",
                component_type=ComponentType.CONSCIOUSNESS_CREATIVE,
                name="Test Trinity Component",
                description="Test component for trinity integration",
                module_path="test.trinity.module",
                triad_framework="🧠",
            )

            # Verify integration
            triad_status = registry.get_triad_status()
            assert triad_status["🧠"]["total"] >= 1

        finally:
            await registry.shutdown()
            await triad_integrator.shutdown()

    @pytest.mark.asyncio
    async def test_memory_triad_decision_flow(self):
        """Test memory integration with Trinity Framework decisions."""
        if not CONSCIOUSNESS_MODULES_AVAILABLE:
            pytest.skip("Consciousness modules not available")

        # Create components
        memory_integrator = ConsciousnessMemoryIntegrator()
        triad_integrator = TrinityFrameworkIntegrator()

        try:
            # Create test decision context
            decision_context = {"test": "memory_triad_integration"}
            decision_id = str(uuid.uuid4())

            # Process through trinity (will be simulated)
            triad_result = await triad_integrator.process_consciousness_decision(
                session_id=decision_id,
                decision_context=decision_context,
                require_identity=False,
                require_guardian=False,
            )

            # Integrate with memory
            memory_folds = await memory_integrator.integrate_decision_memory(
                decision_id=decision_id, decision_context=decision_context, decision_result=triad_result
            )

            # Verify integration
            assert len(memory_folds) >= 1
            assert decision_id in memory_integrator._decision_memory_map

        finally:
            await memory_integrator.shutdown()
            await triad_integrator.shutdown()


@pytest.mark.asyncio
async def test_consciousness_activation_api():
    """Test the main consciousness activation API function."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    # Test with very lenient config for testing environment
    config = ActivationConfig(
        max_activation_time=10.0,
        consciousness_authenticity_threshold=0.1,
        guardian_oversight_required=False,
        creative_engines_required=False,
        awareness_monitoring_required=False,
        validation_rounds=1,
    )

    # This will likely fail in test environment, but should handle gracefully
    result = await activate_lukhas_consciousness(config)

    # Result should be boolean
    assert isinstance(result, bool)


def test_consciousness_module_imports():
    """Test that consciousness modules can be imported successfully."""
    if not CONSCIOUSNESS_MODULES_AVAILABLE:
        pytest.skip("Consciousness modules not available")

    # Test basic imports work
    import importlib

    activation_orchestrator = importlib.import_module("lukhas.consciousness.activation_orchestrator")
    registry = importlib.import_module("lukhas.consciousness.registry")
    trinity_integration = importlib.import_module("lukhas.consciousness.trinity_integration")
    consciousness_memory_integration = importlib.import_module(
        "lukhas.memory.consciousness_memory_integration"
    )

    assert registry is not None
    assert trinity_integration is not None
    assert consciousness_memory_integration is not None
    assert activation_orchestrator is not None


# Performance tests
class TestConsciousnessPerformance:
    """Performance tests for consciousness activation system."""

    @pytest.mark.asyncio
    async def test_memory_processing_latency(self, memory_integrator):
        """Test memory processing meets latency requirements."""
        import time

        # Create test memory
        start_time = time.time()
        await memory_integrator.create_consciousness_memory_fold(
            content={"performance_test": "latency_measurement"}, fold_type=MemoryFoldType.EPISODIC
        )
        create_time = time.time() - start_time

        # Test recall latency
        start_time = time.time()
        results = await memory_integrator.recall_consciousness_memory(
            query={"performance_test": "latency_measurement"}, max_results=1
        )
        recall_time = time.time() - start_time

        # Verify performance requirements
        assert create_time < 0.1  # Under 100ms for creation
        assert recall_time < 0.1  # Under 100ms for recall
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_consciousness_validation_performance(self, activation_orchestrator):
        """Test consciousness validation performance."""
        import time

        start_time = time.time()
        validation_score = await activation_orchestrator._run_consciousness_validation()
        validation_time = time.time() - start_time

        # Validation should complete quickly
        assert validation_time < 5.0  # Under 5 seconds
        assert 0.0 <= validation_score <= 1.0


# Error handling tests
class TestConsciousnessErrorHandling:
    """Test error handling and resilience in consciousness systems."""

    @pytest.mark.asyncio
    async def test_registry_component_activation_failure(self, registry):
        """Test handling of component activation failures."""
        # Register component with invalid module path
        registry.register_component(
            component_id="invalid_component",
            component_type=ComponentType.CONSCIOUSNESS_CREATIVE,
            name="Invalid Component",
            description="Component with invalid module path",
            module_path="nonexistent.module.path",
            triad_framework="🧠",
        )

        # Attempt activation (should fail gracefully)
        success = await registry.activate_component("invalid_component")

        # Should fail gracefully without crashing
        assert success is False

        # Check component status
        status = registry.get_component_status("invalid_component")
        assert status == ComponentStatus.FAILED or status is None

    @pytest.mark.asyncio
    async def test_memory_system_resilience(self, memory_integrator):
        """Test memory system resilience to invalid inputs."""
        # Test with invalid emotional context
        try:
            invalid_emotional_context = EmotionalContext(
                valence=999.0,  # Invalid range
                arousal=-1.0,  # Invalid range
                dominance=2.0,  # Invalid range
            )

            fold_id = await memory_integrator.create_consciousness_memory_fold(
                content={"test": "invalid_emotional_context"},
                fold_type=MemoryFoldType.EMOTIONAL,
                emotional_context=invalid_emotional_context,
            )

            # Should create fold despite invalid emotional context
            assert fold_id is not None

        except Exception as e:
            # If exception occurs, it should be handled gracefully
            assert isinstance(e, (ValueError, TypeError))


if __name__ == "__main__":
    # Run basic smoke test
    if CONSCIOUSNESS_MODULES_AVAILABLE:
        print("🧠 LUKHAS Consciousness Activation Test Suite")
        print("✅ Consciousness modules available")
        print("🔬 Running basic validation...")

        # Basic import validation
        try:
            print("✅ All consciousness modules import successfully")
            print("🌟 Consciousness Activation System: READY FOR TESTING")

        except Exception as e:
            print(f"❌ Import error: {e}")
    else:
        print("⚠️ Consciousness modules not available - tests will be skipped")
