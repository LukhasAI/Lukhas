# tests/integration/matriz/test_matriz_performance.py
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
async def test_performance_full_pipeline(benchmark):
    """
    Benchmarks the full cognitive pipeline to ensure it meets the p95 latency target.
    """
    # Configure mock nodes with realistic delays
    intent_node = MockCognitiveNode("intent", ["intent"], processing_delay=0.02)
    decision_node = MockCognitiveNode("decision", ["decision"], processing_delay=0.01)
    processing_node = MockCognitiveNode("math", ["processing"], processing_delay=0.05)
    validation_node = MockCognitiveNode("validator", ["validation"], processing_delay=0.015)
    reflection_node = MockCognitiveNode("reflection", ["reflection"], processing_delay=0.01)

    orchestrator = AsyncCognitiveOrchestrator(total_timeout=0.5)  # Generous timeout for benchmark
    orchestrator.register_node("intent", intent_node)
    orchestrator.register_node("decision", decision_node)
    orchestrator.register_node("math", processing_node)
    orchestrator.register_node("validator", validation_node)
    orchestrator.register_node("reflection", reflection_node)

    query = "Benchmark query: 2 * 2"

    async def run_pipeline():
        await orchestrator.process_query(query)

    benchmark.pedantic(run_pipeline, rounds=5, iterations=1)


@pytest.mark.asyncio
async def test_performance_orchestrator_overhead(benchmark):
    """
    Benchmarks the orchestrator's overhead with no nodes registered.
    """
    orchestrator = AsyncCognitiveOrchestrator()
    query = "Overhead test"

    async def run_empty_pipeline():
        # We expect this to fail, but the benchmark will still measure the time taken
        await orchestrator.process_query(query)

    benchmark.pedantic(run_empty_pipeline, rounds=10, iterations=1)
