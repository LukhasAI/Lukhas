import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock dependencies of async_orchestrator
sys.modules['metrics'] = MagicMock()
sys.modules['core.orchestration.consensus_arbitrator'] = MagicMock()
# Configure the MetaController mock to prevent oscillation detection
mock_meta_controller_module = MagicMock()
mock_meta_controller_instance = MagicMock()
mock_meta_controller_instance.step.return_value = False  # Prevent oscillation
mock_meta_controller_module.MetaController.return_value = mock_meta_controller_instance
sys.modules['core.orchestration.meta_controller'] = mock_meta_controller_module
sys.modules['core.orchestration.otel'] = MagicMock()


from core.orchestration.async_orchestrator import AsyncOrchestrator

class MockCognitiveNode:
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail
        self.was_called = False

    async def process(self, context):
        self.was_called = True
        if self.should_fail:
            # Simulate a transient, retryable error
            err = ValueError("Simulated service failure")
            setattr(err, 'retryable', True)
            raise err
        return {"result": f"processed by {self.name}"}

@pytest.mark.asyncio
async def test_service_outage_fallback():
    """
    Given a primary cognitive node that is unavailable,
    When the orchestrator processes a query,
    Then it should fall back to a secondary node and successfully complete the operation.
    """
    primary_node = MockCognitiveNode("primary", should_fail=True)
    fallback_node = MockCognitiveNode("fallback")

    with patch("core.orchestration.async_orchestrator.resolve") as mock_resolve:
        def resolve_node(name):
            if name == "node:primary":
                return primary_node
            if name == "node:fallback":
                return fallback_node
            raise LookupError(f"Node '{name}' not found")

        mock_resolve.side_effect = resolve_node

        orchestrator = AsyncOrchestrator()
        orchestrator.configure_stages([
            {
                "name": "test_stage",
                "node": "primary",
                "fallback_nodes": ["fallback"],
                "max_retries": 1,
            }
        ])

        result = await orchestrator.process_query({"query": "test"})

        assert result.success
        assert result.output["result"] == "processed by fallback"
        assert "_fallback" in result.output
        assert result.output["_fallback"]["failed_primary"]
        assert fallback_node.was_called
        assert primary_node.was_called
