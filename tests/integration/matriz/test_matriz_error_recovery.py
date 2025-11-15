# tests/integration/matriz/test_matriz_error_recovery.py
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
async def test_error_recovery_critical_stage_failure():
    """
    Tests that the pipeline fails gracefully when a critical stage encounters an error.
    """
    processing_node = MockCognitiveNode(
        "math", ["processing"], exception_to_raise=ValueError("Critical processing error")
    )

    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", processing_node)

    query = "This will fail"
    result = await orchestrator.process_query(query)

    assert "error" in result
    assert "Processing failed" in result["error"]
    assert len(result["stages"]) > 0
    assert result["orchestrator_metrics"]["error_count"] >= 1


@pytest.mark.asyncio
async def test_error_recovery_stage_timeout_failure():
    """
    Tests that the pipeline correctly handles a timeout in a single stage.
    """
    # This delay will exceed the default stage timeout (0.12s), but not the total timeout (0.25s)
    processing_node = MockCognitiveNode("math", ["processing"], processing_delay=0.15)

    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", processing_node)

    query = "This will have a stage timeout"
    result = await orchestrator.process_query(query)

    assert "error" in result
    assert "Processing failed" in result["error"]
    assert any(stage.get("timeout", False) for stage in result["stages"])
    assert result["orchestrator_metrics"]["timeout_count"] >= 1


@pytest.mark.asyncio
async def test_fallback_non_critical_stage_failure():
    """
    Tests that the pipeline can successfully fallback when a non-critical stage fails.
    """
    processing_node = MockCognitiveNode("math", ["processing"])
    validation_node = MockCognitiveNode(
        "validator", ["validation"], exception_to_raise=ValueError("Non-critical validation error")
    )

    orchestrator = AsyncCognitiveOrchestrator(
        stage_critical={StageType.VALIDATION: False}
    )
    orchestrator.register_node("math", processing_node)
    orchestrator.register_node("validator", validation_node)

    query = "This will succeed with a non-critical failure"
    result = await orchestrator.process_query(query)

    assert "error" not in result
    assert result["answer"] == "Mock response from processing_node"
    assert result["metrics"]["stages_completed"] > 0
    assert result["orchestrator_metrics"]["error_count"] >= 1
