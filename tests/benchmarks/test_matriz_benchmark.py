"""Benchmarks for the MATRIZ Cognitive Engine."""

import asyncio
from typing import List, Dict, Optional

import pytest
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.node_interface import CognitiveNode


class MockCognitiveNode(CognitiveNode):
    """A mock cognitive node for benchmarking."""

    def __init__(self, node_name: str = "mock_node", capabilities: Optional[List[str]] = None):
        """Initializes the mock node."""
        super().__init__(node_name, capabilities or ["mock"])

    def process(self, node_input: dict) -> dict:
        """Simulates processing and returns a mock answer."""
        return {"answer": "mock answer"}

    def validate_output(self, output: dict) -> bool:
        """Mock validation."""
        return True

@pytest.fixture
def orchestrator():
    """Provides an AsyncCognitiveOrchestrator with a mock node."""
    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("mock_node", MockCognitiveNode())
    return orchestrator

@pytest.mark.asyncio
async def test_process_query_benchmark(benchmark, orchestrator):
    """Benchmark the process_query method."""

    @benchmark.pedantic
    async def run_benchmark():
        return await orchestrator.process_query("test query")
