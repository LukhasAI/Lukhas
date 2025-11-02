#!/usr/bin/env python3
"""Contract tests for MATRIZ orchestrator input adaptation."""

import asyncio
import sys
import types
from pathlib import Path

import pytest

tests_unit_path = Path(__file__).resolve().parents[2]
if str(tests_unit_path) not in sys.path:
    sys.path.append(str(tests_unit_path))

if "streamlit" not in sys.modules:
    streamlit_stub = types.SimpleNamespace()

    def _cache_decorator(*_, **__):  # pragma: no cover - stubbed cache
        def wrapper(func):
            return func

        return wrapper

    streamlit_stub.cache_resource = _cache_decorator
    streamlit_stub.cache_data = _cache_decorator
    sys.modules["streamlit"] = streamlit_stub

from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.nodes.fact_node import FactNode
from matriz.nodes.math_node import MathNode
from matriz.nodes.validator_node import ValidatorNode


class TestMatrizInputAdapter:
    """Validate that the async orchestrator maps inputs to node schemas."""

    def setup_method(self):
        self.orchestrator = AsyncCognitiveOrchestrator(total_timeout=0.5)

    def test_adapter_shapes(self):
        """Adapter should map raw inputs into node-specific payloads."""
        math_payload = self.orchestrator._adapt_input_for_node("math", "1+1")
        assert math_payload == {"expression": "1+1"}

        fact_payload = self.orchestrator._adapt_input_for_node("facts", "What is the capital of France?")
        assert fact_payload == {"question": "What is the capital of France?"}

        default_payload = self.orchestrator._adapt_input_for_node("other", "hello")
        assert default_payload == {"query": "hello"}

        validator_payload = {"target_output": {"answer": "ok"}}
        adapted_validator = self.orchestrator._adapt_input_for_node("validator", validator_payload)
        assert adapted_validator is validator_payload

        with pytest.raises(TypeError):
            self.orchestrator._adapt_input_for_node("validator", "raw string")

    def test_math_node_pipeline(self):
        """Math queries should produce numeric answers via adapted payload."""
        math_node = MathNode()
        fact_node = FactNode()
        validator_node = ValidatorNode()

        self.orchestrator.register_node("math", math_node)
        self.orchestrator.register_node("facts", fact_node)
        self.orchestrator.register_node("validator", validator_node)

        result = asyncio.run(self.orchestrator.process_query("(2+3)*4"))
        assert "20" in result["answer"]
        assert result["confidence"] > 0.5

    def test_fact_node_pipeline(self):
        """Fact queries should return knowledge answers with confidence."""
        math_node = MathNode()
        fact_node = FactNode()

        self.orchestrator.register_node("math", math_node)
        self.orchestrator.register_node("facts", fact_node)

        result = asyncio.run(self.orchestrator.process_query("What is the capital of France?"))
        assert "Paris" in result["answer"]
        assert result["confidence"] > 0.5

    def test_validator_processes_structured_output(self):
        """Validator nodes should accept structured outputs from other nodes."""
        validator_node = ValidatorNode()
        math_output = MathNode().process({"expression": "(2+3)*4"})

        payload = self.orchestrator._adapt_input_for_node("validator", {"target_output": math_output})
        result = asyncio.run(self.orchestrator._process_node_async(validator_node, payload))
        assert "PASSED" in result["answer"]
        assert result["confidence"] >= 0.5
