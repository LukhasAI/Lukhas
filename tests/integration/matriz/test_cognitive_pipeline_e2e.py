# tests/integration/matriz/test_cognitive_pipeline_e2e.py
import asyncio
import time
from typing import Any, Dict, List
import pytest

# The CognitiveNode is defined in a different directory, so I'll need to
# temporarily add the project root to the path for the import to work correctly.
import sys
sys.path.insert(0, '/app')

from matriz.core.node_interface import CognitiveNode
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator, StageType


class MockCognitiveNode(CognitiveNode):
    """A mock cognitive node for testing purposes."""

    def __init__(
        self,
        node_name: str,
        capabilities: List[str],
        tenant: str = "test-tenant",
        processing_delay: float = 0.01,
        response_data: Dict[str, Any] = None,
        exception_to_raise: Exception = None,
    ):
        super().__init__(node_name, capabilities, tenant)
        self.processing_delay = processing_delay
        self.response_data = response_data or {"answer": f"Mock response from {node_name}"}
        self.exception_to_raise = exception_to_raise
        self.call_history = []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates node processing."""
        self.call_history.append(input_data)
        time.sleep(self.processing_delay)

        if self.exception_to_raise:
            raise self.exception_to_raise

        matriz_node = self.create_matriz_node(
            node_type="COMPUTATION",
            state={"confidence": 0.99, "salience": 0.9},
            additional_data=self.response_data,
        )

        return {
            "answer": self.response_data.get("answer"),
            "confidence": 0.99,
            "matriz_node": matriz_node,
            "processing_time": self.processing_delay,
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """A simple validation for testing."""
        return "answer" in output and "matriz_node" in output

    def reset(self):
        """Resets the call history for clean tests."""
        self.call_history = []


@pytest.fixture
def mock_intent_node():
    return MockCognitiveNode(node_name="intent_node", capabilities=["intent"])

@pytest.fixture
def mock_decision_node():
    return MockCognitiveNode(node_name="decision_node", capabilities=["decision"])

@pytest.fixture
def mock_processing_node():
    return MockCognitiveNode(node_name="processing_node", capabilities=["processing"])

@pytest.fixture
def mock_validation_node():
    return MockCognitiveNode(node_name="validation_node", capabilities=["validation"])

@pytest.fixture
def mock_reflection_node():
    return MockCognitiveNode(node_name="reflection_node", capabilities=["reflection"])


@pytest.mark.asyncio
async def test_full_cognitive_cycle_e2e(
    mock_intent_node,
    mock_decision_node,
    mock_processing_node,
    mock_validation_node,
    mock_reflection_node,
):
    """
    Tests a successful run of the full cognitive pipeline, end-to-end.
    """
    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("intent", mock_intent_node)
    orchestrator.register_node("decision", mock_decision_node)
    orchestrator.register_node("math", mock_processing_node)  # Registering as 'math' for intent mapping
    orchestrator.register_node("validator", mock_validation_node)
    orchestrator.register_node("reflection", mock_reflection_node)

    query = "What is 2 + 2?"
    result = await orchestrator.process_query(query)

    assert "error" not in result
    assert result["answer"] == "Mock response from processing_node"
    assert len(result["stages"]) >= 4  # Should have at least 4 stages on success
    assert result["metrics"]["total_duration_ms"] > 0
    assert result["metrics"]["stages_completed"] >= 4

    # Verify that the correct nodes were called
    assert len(mock_intent_node.call_history) == 0 # The orchestrator's internal methods are called, not the node's process()
    assert len(mock_decision_node.call_history) == 0
    assert len(mock_processing_node.call_history) == 1
    assert mock_processing_node.call_history[0] == {"expression": query}


@pytest.mark.asyncio
async def test_state_preservation_across_pipelines():
    """
    Tests that context can be preserved and restored across different orchestrator instances.
    """
    orchestrator1 = AsyncCognitiveOrchestrator()
    context_data = {"user_id": "123", "session_id": "abc"}
    context_id = orchestrator1.preserve_context(context_data)

    orchestrator2 = AsyncCognitiveOrchestrator()
    # To simulate a real-world scenario, we'll transfer the context memory
    orchestrator2.context_memory = orchestrator1.context_memory

    restored_context = orchestrator2.restore_context(context_id)

    assert restored_context is not None
    assert restored_context["user_id"] == "123"
    assert restored_context["session_id"] == "abc"


@pytest.mark.asyncio
async def test_concurrent_processing_no_state_leakage(
    mock_processing_node,
):
    """
    Tests that the orchestrator can handle multiple concurrent queries without state leakage.
    """
    async def run_query(orchestrator, query, expected_answer):
        result = await orchestrator.process_query(query)
        assert result["answer"] == expected_answer

    # Each orchestrator needs its own instance of the node to avoid shared state in the mock
    node1 = MockCognitiveNode("p_node_1", ["processing"], response_data={"answer": "response 1"})
    node2 = MockCognitiveNode("p_node_2", ["processing"], response_data={"answer": "response 2"})

    orchestrator1 = AsyncCognitiveOrchestrator()
    orchestrator1.register_node("math", node1)

    orchestrator2 = AsyncCognitiveOrchestrator()
    orchestrator2.register_node("math", node2)

    tasks = [
        run_query(orchestrator1, "query 1", "response 1"),
        run_query(orchestrator2, "query 2", "response 2"),
    ]

    await asyncio.gather(*tasks)

    # Verify that each node was called once with the correct query
    assert len(node1.call_history) == 1
    assert node1.call_history[0]["expression"] == "query 1"
    assert len(node2.call_history) == 1
    assert node2.call_history[0]["expression"] == "query 2"
