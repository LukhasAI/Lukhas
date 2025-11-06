import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys

# Mock dependencies of async_orchestrator
sys.modules['metrics'] = MagicMock()
sys.modules['core.orchestration.consensus_arbitrator'] = MagicMock()
mock_meta_controller_module = MagicMock()
mock_meta_controller_instance = MagicMock()
mock_meta_controller_instance.step.return_value = False
mock_meta_controller_module.MetaController.return_value = mock_meta_controller_instance
sys.modules['core.orchestration.meta_controller'] = mock_meta_controller_module
sys.modules['core.orchestration.otel'] = MagicMock()

from core.orchestration.async_orchestrator import AsyncOrchestrator

class MockCognitiveNode:
    def __init__(self, name):
        self.name = name
        self.call_count = 0

@pytest.mark.asyncio
async def test_timeout_on_slow_node():
    """
    Given a cognitive node that is too slow to respond,
    When the orchestrator processes a query,
    Then it should time out and return a failure result.
    """
    class SlowNode(MockCognitiveNode):
        async def process(self, context):
            self.call_count += 1
            await asyncio.sleep(0.2) # 200ms sleep
            return {"result": f"processed by {self.name}"}

    slow_node = SlowNode("slow_node")

    with patch("core.orchestration.async_orchestrator.resolve") as mock_resolve:
        mock_resolve.return_value = slow_node

        orchestrator = AsyncOrchestrator()
        orchestrator.configure_stages([
            {
                "name": "test_stage",
                "node": "slow_node",
                "timeout_ms": 100, # 100ms timeout
                # TODO: The `max_retries` parameter appears to control the total number of
                # attempts, not the number of retries. A value of 1 is required for
                # a single attempt.
                "max_retries": 1,
            }
        ])

        result = await orchestrator.process_query({"query": "test"})

        assert not result.success
        assert slow_node.call_count == 1
        assert result.escalation_reason == "no_viable_results"

@pytest.mark.asyncio
async def test_retry_on_failure():
    """
    Given a cognitive node that fails on the first attempt with a retryable error,
    When the orchestrator processes a query,
    Then it should retry and succeed on the second attempt.
    """
    class FlakyNode(MockCognitiveNode):
        async def process(self, context):
            self.call_count += 1
            if self.call_count == 1:
                err = ValueError("Simulated transient failure")
                setattr(err, 'retryable', True)
                raise err
            return {"result": f"processed by {self.name}"}

    flaky_node = FlakyNode("flaky_node")

    with patch("core.orchestration.async_orchestrator.resolve") as mock_resolve:
        mock_resolve.return_value = flaky_node

        orchestrator = AsyncOrchestrator()
        orchestrator.configure_stages([
            {
                "name": "test_stage",
                "node": "flaky_node",
                "timeout_ms": 200, # Long enough timeout
                # TODO: The `max_retries` parameter appears to control the total number of
                # attempts, not the number of retries. A value of 2 is required for
                # one retry. This might be a bug in the orchestrator.
                "max_retries": 2,
                "backoff_base_ms": 10,
            }
        ])

        result = await orchestrator.process_query({"query": "test"})

        assert result.success
        assert flaky_node.call_count == 2
        assert result.output["result"] == "processed by flaky_node"
