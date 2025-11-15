"""
Smoke tests for the Enhanced Consciousness Engine.
"""
import asyncio
import time
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest


# The EnhancedDreamEngine is a complex class, so we need to mock its dependencies.
# We will use stubs to avoid importing the actual classes, which may have their own dependencies.
class BioOrchestratorStub:
    pass

class UnifiedIntegrationStub:
    def register_component(self, name, handler):
        pass
    async def get_data(self, store_name):
        pass
    async def store_data(self, store_name, data):
        pass

@pytest.fixture
def mock_engine():
    """
    Fixture to create a mocked EnhancedDreamEngine.
    This uses sys.modules patching to inject mocks before the engine is imported,
    which is necessary because the engine uses try/except blocks for its imports.
    """
    mock_qi_adapter_module = MagicMock()
    mock_qi_adapter_class = MagicMock()
    mock_adapter_instance = AsyncMock()
    mock_adapter_instance.start_dream_cycle = AsyncMock()
    mock_adapter_instance.stop_dream_cycle = AsyncMock()
    mock_adapter_instance.get_quantum_like_state = AsyncMock(return_value={'coherence': 0.0})
    mock_qi_adapter_class.return_value = mock_adapter_instance
    mock_qi_adapter_module.QIDreamAdapter = mock_qi_adapter_class

    # We also need to mock the config object that is imported
    mock_config_class = MagicMock()
    mock_config_instance = MagicMock()
    mock_config_instance.coherence_threshold = 0.9
    mock_config_class.return_value = mock_config_instance
    mock_qi_adapter_module.DreamQuantumConfig = mock_config_class

    modules_to_patch = {
        'qi.qi_dream_adapter': mock_qi_adapter_module,
    }

    with patch.dict('sys.modules', modules_to_patch):
        from labs.consciousness.dream.core.dream_engine import EnhancedDreamEngine

        mock_orchestrator = BioOrchestratorStub()
        mock_integration = AsyncMock(spec=UnifiedIntegrationStub)
        mock_integration.register_component = MagicMock()
        mock_integration.get_data = AsyncMock(return_value=[])
        mock_integration.store_data = AsyncMock()

        engine = EnhancedDreamEngine(
            orchestrator=mock_orchestrator,
            integration=mock_integration,
        )

        # Attach the mock adapter instance for easy access in tests
        engine.mock_qi_adapter = mock_adapter_instance
        engine.integration = mock_integration
        yield engine


@pytest.mark.smoke
def test_consciousness_engine_initialization(mock_engine):
    """Verify the EnhancedDreamEngine can be initialized."""
    assert mock_engine is not None
    assert not mock_engine.active
    assert mock_engine.processing_task is None

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_consciousness_engine_state_transitions(mock_engine):
    """Verify the engine's start and stop state transitions."""
    assert not mock_engine.active

    # Start the cycle
    await mock_engine.start_dream_cycle(duration_minutes=1)

    assert mock_engine.active
    processing_task = mock_engine.processing_task
    assert processing_task is not None
    mock_engine.mock_qi_adapter.start_dream_cycle.assert_awaited_once()

    # Stop the cycle
    await mock_engine.stop_dream_cycle()

    await asyncio.sleep(0) # Yield to the event loop

    assert not mock_engine.active
    assert processing_task.done()
    mock_engine.mock_qi_adapter.stop_dream_cycle.assert_awaited_once()

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_consciousness_engine_matriz_integration_loop(mock_engine):
    """Verify the core processing loop integrates with its dependencies."""
    # Configure mocks to return data and trigger processing logic
    mock_engine.mock_qi_adapter.get_quantum_like_state.return_value = {
        'coherence': 0.95, 'entanglement': 0.5, 'insights': []
    }
    mock_engine.integration.get_data.return_value = [{'id': 1, 'data': 'test memory'}]

    # Patch sleep to force the loop to run once and then exit
    with patch('labs.consciousness.dream.core.dream_engine.asyncio.sleep', side_effect=asyncio.CancelledError):
        await mock_engine.start_dream_cycle(duration_minutes=1)

        # Wait for the task to complete (it will be cancelled by the patched sleep)
        try:
            await mock_engine.processing_task
        except asyncio.CancelledError:
            pass # This is the expected outcome

    # Verify interactions that should have happened in the single loop iteration
    mock_engine.mock_qi_adapter.get_quantum_like_state.assert_called()
    mock_engine.integration.get_data.assert_awaited_with("unconsolidated_memories")
    mock_engine.integration.store_data.assert_any_await("dream_insights", ANY)
    mock_engine.integration.store_data.assert_any_await("enhanced_memories", ANY)

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_consciousness_engine_error_handling(mock_engine):
    """Verify the engine's main loop handles errors gracefully."""
    # Simulate a failure in one of the sub-tasks
    mock_engine.integration.get_data.side_effect = Exception("Test error")

    # The loop should catch the exception and continue running.
    # We will patch sleep to run the loop a few times and then exit.
    async def sleep_controller(*args, **kwargs):
        if len(sleep_controller.calls) > 2:
            raise asyncio.CancelledError
        sleep_controller.calls.append(1)
        await asyncio.sleep(0)
    sleep_controller.calls = []

    with patch('labs.consciousness.dream.core.dream_engine.asyncio.sleep', side_effect=sleep_controller):
        await mock_engine.start_dream_cycle(duration_minutes=1)

        try:
            await mock_engine.processing_task
        except asyncio.CancelledError:
            pass # Expected

    # Verify that the loop ran multiple times, despite the errors
    assert len(sleep_controller.calls) > 1
    # Verify that the failed method was called
    mock_engine.integration.get_data.assert_called()

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_consciousness_engine_resource_cleanup(mock_engine):
    """Verify the engine's shutdown process properly cleans up resources."""
    await mock_engine.start_dream_cycle(duration_minutes=1)

    processing_task = mock_engine.processing_task
    assert not processing_task.done()

    await mock_engine.stop_dream_cycle()
    await asyncio.sleep(0) # Yield to the event loop

    assert processing_task.cancelled()

@pytest.mark.smoke
@pytest.mark.asyncio
async def test_consciousness_engine_performance(benchmark):
    """Validate the engine's basic performance."""

    async def run_full_cycle():
        mock_qi_adapter_module = MagicMock()
        mock_qi_adapter_class = MagicMock()
        mock_adapter_instance = AsyncMock()
        mock_adapter_instance.start_dream_cycle = AsyncMock()
        mock_adapter_instance.stop_dream_cycle = AsyncMock()
        mock_adapter_instance.get_quantum_like_state = AsyncMock(return_value={'coherence': 0.95})
        mock_qi_adapter_class.return_value = mock_adapter_instance
        mock_qi_adapter_module.QIDreamAdapter = mock_qi_adapter_class

        mock_config_class = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.coherence_threshold = 0.9
        mock_config_class.return_value = mock_config_instance
        mock_qi_adapter_module.DreamQuantumConfig = mock_config_class

        modules_to_patch = {
            'qi.qi_dream_adapter': mock_qi_adapter_module,
        }

        with patch.dict('sys.modules', modules_to_patch):
            from labs.consciousness.dream.core.dream_engine import EnhancedDreamEngine

            mock_orchestrator = BioOrchestratorStub()
            mock_integration = AsyncMock(spec=UnifiedIntegrationStub)
            mock_integration.register_component = MagicMock()
            mock_integration.get_data = AsyncMock(return_value=[])
            mock_integration.store_data = AsyncMock()

            engine = EnhancedDreamEngine(
                orchestrator=mock_orchestrator,
                integration=mock_integration,
            )

            await engine.start_dream_cycle(duration_minutes=0.01)
            await asyncio.sleep(0.01)
            await engine.stop_dream_cycle()

    # Benchmark the async function
    await benchmark.pedantic(run_full_cycle, iterations=10, rounds=5)

    # Assert that the max is under 250ms (a stricter check than p95)
    max_time = benchmark.stats.stats.max
    assert max_time < 0.25, f"Max latency of {max_time:.4f}s is over the 250ms budget"
