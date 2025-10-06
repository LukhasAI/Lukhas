# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.service_discovery
# criticality: P1

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bridge.adapters.service_adapter_base import AdapterState, ResilienceManager, with_resilience


@pytest.mark.tier3
@pytest.mark.integration
class TestResilienceManager:
    """
    Tests for the ResilienceManager (circuit breaker).
    """

    def test_circuit_breaker_opens_after_threshold(self):
        """Tests that the circuit breaker opens after enough failures."""
        manager = ResilienceManager(failure_threshold=3, recovery_timeout=10)

        assert manager.can_attempt_request() is True
        manager.record_failure()
        assert manager.can_attempt_request() is True
        manager.record_failure()
        assert manager.can_attempt_request() is True
        manager.record_failure()

        assert manager.get_state() == AdapterState.OPEN.value
        assert manager.can_attempt_request() is False

    def test_circuit_breaker_moves_to_half_open(self):
        """Tests that the circuit breaker moves to half-open after the recovery timeout."""
        manager = ResilienceManager(failure_threshold=1, recovery_timeout=0.1)
        manager.record_failure()
        assert manager.get_state() == AdapterState.OPEN.value

        async def wait_for_half_open():
            await asyncio.sleep(0.2)
            assert manager.can_attempt_request() is True
            assert manager.get_state() == AdapterState.HALF_OPEN.value

        asyncio.run(wait_for_half_open())

    def test_circuit_breaker_closes_after_success_in_half_open(self):
        """Tests that the circuit breaker closes after successful requests in half-open state."""
        manager = ResilienceManager(failure_threshold=1, recovery_timeout=0.1)
        manager.record_failure() # state -> OPEN

        async def check_recovery():
            await asyncio.sleep(0.2)
            # Call can_attempt_request to trigger the state transition to HALF_OPEN
            manager.can_attempt_request()
            assert manager.get_state() == AdapterState.HALF_OPEN.value

            manager.record_success()
            manager.record_success()
            manager.record_success()

            assert manager.get_state() == AdapterState.CLOSED.value

        asyncio.run(check_recovery())

@pytest.mark.asyncio
@pytest.mark.tier3
@pytest.mark.integration
class TestWithResilienceDecorator:
    """
    Tests for the @with_resilience decorator.
    """

    class MockAdapter:
        def __init__(self):
            self.resilience = ResilienceManager(failure_threshold=2, recovery_timeout=10)
            self.telemetry = MagicMock()
            self.telemetry.record_request = MagicMock()

        @with_resilience
        async def successful_operation(self, *args, **kwargs):
            return {"status": "ok"}

        @with_resilience
        async def failing_operation(self, *args, **kwargs):
            raise ValueError("Operation failed")

    @pytest.fixture
    def adapter(self):
        return self.MockAdapter()

    async def test_decorator_returns_result_on_success(self, adapter):
        """Tests that the decorator returns the result of the function on success."""
        result = await adapter.successful_operation()
        assert result["status"] == "ok"
        adapter.telemetry.record_request.assert_called_once()
        assert adapter.resilience.get_state() == AdapterState.CLOSED.value

    async def test_decorator_retries_on_failure(self, adapter):
        """Tests that the decorator retries the operation on failure."""
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(ValueError):
                await adapter.failing_operation()

            assert mock_sleep.call_count == 2 # retries twice
            assert adapter.telemetry.record_request.call_count == 1 # only called on final failure
            assert adapter.resilience.failure_count == 3
            assert adapter.resilience.get_state() == AdapterState.OPEN.value

    async def test_decorator_opens_circuit_and_blocks_requests(self, adapter):
        """Tests that the decorator opens the circuit and blocks subsequent requests."""
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(ValueError):
                await adapter.failing_operation() # This will open the circuit

        # Now, the circuit should be open
        assert adapter.resilience.get_state() == AdapterState.OPEN.value

        # This call should be blocked by the circuit breaker
        result = await adapter.successful_operation()

        assert result["error"] == "service_unavailable"
        assert result["circuit_state"] == "open"
