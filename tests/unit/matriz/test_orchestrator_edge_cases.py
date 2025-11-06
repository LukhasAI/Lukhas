"""
Edge case tests for MATRIZ CognitiveOrchestrator.
"""

import os
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10), reason="matriz module requires Python 3.10+"
)

try:
    from matriz.core.node_interface import CognitiveNode
    from matriz.core.orchestrator import CognitiveOrchestrator

    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False

    class CognitiveOrchestrator:
        pass

    class CognitiveNode:
        pass


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestErrorHandling:
    def test_process_query_handles_unregistered_node(self):
        """Should return a structured error if the selected node is not registered."""
        orch = CognitiveOrchestrator()
        # Note: Do not register the 'math' node
        result = orch.process_query("1 + 1")

        assert "error" in result
        assert "No node available for math" in result["error"]
        assert "trace" in result

    def test_process_query_handles_node_exception(self):
        """Should return a structured error if a node raises an exception."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.side_effect = ValueError("Test exception")
        orch.register_node("math", mock_node)

        result = orch.process_query("1 + 1")

        assert "error" in result
        assert "failed during processing" in result["error"]
        assert "Test exception" in str(result.get("error_details"))


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestUnusualInputs:
    def test_analyze_intent_with_very_long_string(self):
        """Should handle very long strings without crashing."""
        orch = CognitiveOrchestrator()
        long_string = "a" * 10000
        intent_node = orch._analyze_intent(long_string)
        assert intent_node is not None
        assert intent_node["state"]["intent"] == "general"

    def test_analyze_intent_with_mixed_languages(self):
        """Should handle strings with mixed languages."""
        orch = CognitiveOrchestrator()
        mixed_string = "Hello from the USA, bonjour from France, and ciao from Italy"
        intent_node = orch._analyze_intent(mixed_string)
        assert intent_node is not None
        assert intent_node["state"]["intent"] == "general"

    def test_analyze_intent_with_no_keywords(self):
        """Should default to 'general' intent when no keywords are found."""
        orch = CognitiveOrchestrator()
        no_keywords_string = "This is a test sentence."
        intent_node = orch._analyze_intent(no_keywords_string)
        assert intent_node is not None
        assert intent_node["state"]["intent"] == "general"


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestStressAndLoad:
    def test_repeated_query_processing(self):
        """Should handle many queries in succession without crashing."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "response",
            "confidence": 0.9,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        for i in range(100):
            result = orch.process_query(f"Query number {i}")
            assert "answer" in result or "error" in result


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestComplexCausalChains:
    def test_causal_chain_with_multiple_triggers(self):
        """Should correctly trace a causal chain with multiple triggers."""
        orch = CognitiveOrchestrator()

        # Manually create a more complex graph
        orch.matriz_graph = {
            "node-1": {
                "id": "node-1", "type": "INTENT", "triggers": []
            },
            "node-2": {
                "id": "node-2", "type": "DECISION", "triggers": [{"trigger_node_id": "node-1"}]
            },
            "node-3": {
                "id": "node-3", "type": "COMPUTATION", "triggers": [{"trigger_node_id": "node-2"}]
            },
        }

        chain = orch.get_causal_chain("node-3")
        assert len(chain) == 3
        assert any(node["id"] == "node-1" for node in chain)
        assert any(node["id"] == "node-2" for node in chain)
        assert any(node["id"] == "node-3" for node in chain)

    def test_causal_chain_with_reflections(self):
        """Should correctly trace a causal chain that includes reflection nodes."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)

        def process_side_effect(input_data):
            trigger_id = input_data.get("trigger_node_id")
            return {
                "answer": "4",
                "confidence": 0.95,
                "matriz_node": {
                    "id": "math-1",
                    "type": "COMPUTATION",
                    "triggers": [{"trigger_node_id": trigger_id}],
                },
            }

        mock_node.process.side_effect = process_side_effect
        orch.register_node("math", mock_node)
        mock_validator = Mock(spec=CognitiveNode)
        mock_validator.validate_output.return_value = True
        orch.register_node("validator", mock_validator)

        orch.process_query("2 + 2")

        # Find the reflection node
        reflection_node = next(
            (n for n in orch.matriz_graph.values() if n["type"] == "REFLECTION"), None
        )
        assert reflection_node is not None

        chain = orch.get_causal_chain(reflection_node["id"])
        # The chain should include the reflection, the computation, the decision, and the intent
        assert len(chain) >= 4
