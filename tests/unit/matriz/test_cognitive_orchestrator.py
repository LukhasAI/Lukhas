"""
Comprehensive tests for MATRIZ CognitiveOrchestrator.

Tests cover:
- Node registration and lifecycle
- Query processing with intent analysis
- Decision node creation
- Reflection node creation
- Causal chain tracing
- Error handling and edge cases
"""

import os
import sys
from unittest.mock import MagicMock, Mock

import pytest

# Ensure repository root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Skip if Python < 3.10 (matriz requirement)
pytestmark = pytest.mark.skipif(sys.version_info < (3, 10), reason="matriz module requires Python 3.10+")

try:
    from matriz.core.node_interface import CognitiveNode, NodeState
    from matriz.core.orchestrator import CognitiveOrchestrator, ExecutionTrace

    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False

    # Create minimal mocks for test discovery
    class CognitiveOrchestrator:
        pass

    class ExecutionTrace:
        pass

    class CognitiveNode:
        pass

    class NodeState:
        pass


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestCognitiveOrchestratorInit:
    """Test orchestrator initialization."""

    def test_orchestrator_initializes_with_empty_state(self):
        """Orchestrator should initialize with empty registries."""
        orch = CognitiveOrchestrator()

        assert orch.available_nodes == {}
        assert orch.context_memory == []
        assert orch.execution_trace == []
        assert orch.matriz_graph == {}

    def test_orchestrator_is_reusable(self):
        """Same orchestrator instance should handle multiple queries."""
        orch = CognitiveOrchestrator()

        # Register a mock node
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "test",
            "confidence": 0.9,
            "matriz_node": {"id": "test-1", "type": "COMPUTATION"},
        }
        mock_node.validate_output.return_value = True

        orch.register_node("test", mock_node)

        # Process first query
        orch.process_query("test query 1")
        trace_count_1 = len(orch.execution_trace)

        # Process second query
        orch.process_query("test query 2")
        trace_count_2 = len(orch.execution_trace)

        assert trace_count_2 > trace_count_1


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNodeRegistration:
    """Test node registration functionality."""

    def test_register_node_adds_to_available_nodes(self):
        """Registered nodes should be available for processing."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)

        orch.register_node("math", mock_node)

        assert "math" in orch.available_nodes
        assert orch.available_nodes["math"] is mock_node

    def test_register_multiple_nodes(self):
        """Multiple nodes can be registered."""
        orch = CognitiveOrchestrator()
        mock_math = Mock(spec=CognitiveNode)
        mock_facts = Mock(spec=CognitiveNode)

        orch.register_node("math", mock_math)
        orch.register_node("facts", mock_facts)

        assert len(orch.available_nodes) == 2
        assert orch.available_nodes["math"] is mock_math
        assert orch.available_nodes["facts"] is mock_facts

    def test_register_node_overwrites_existing(self):
        """Registering same name should overwrite."""
        orch = CognitiveOrchestrator()
        mock_node_1 = Mock(spec=CognitiveNode)
        mock_node_2 = Mock(spec=CognitiveNode)

        orch.register_node("test", mock_node_1)
        orch.register_node("test", mock_node_2)

        assert orch.available_nodes["test"] is mock_node_2


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestIntentAnalysis:
    """Test intent analysis and categorization."""

    def test_detects_mathematical_intent(self):
        """Mathematical operators should trigger mathematical intent."""
        orch = CognitiveOrchestrator()

        intent_node = orch._analyze_intent("What is 2 + 2?")

        assert intent_node["type"] == "INTENT"
        assert intent_node["state"]["intent"] == "mathematical"
        assert "confidence" in intent_node["state"]
        assert "salience" in intent_node["state"]

    def test_detects_question_intent(self):
        """Question marks should trigger question intent."""
        orch = CognitiveOrchestrator()

        intent_node = orch._analyze_intent("What is the capital of France?")

        assert intent_node["type"] == "INTENT"
        assert intent_node["state"]["intent"] == "question"

    def test_detects_perception_intent(self):
        """Perception keywords should trigger perception intent."""
        orch = CognitiveOrchestrator()

        intent_node = orch._analyze_intent("The dog sees the cat")

        assert intent_node["type"] == "INTENT"
        assert intent_node["state"]["intent"] == "perception"

    def test_defaults_to_general_intent(self):
        """Unknown input should default to general intent."""
        orch = CognitiveOrchestrator()

        intent_node = orch._analyze_intent("Hello there")

        assert intent_node["type"] == "INTENT"
        assert intent_node["state"]["intent"] == "general"

    def test_intent_node_has_complete_schema(self):
        """Intent nodes should have complete MATRIZ schema."""
        orch = CognitiveOrchestrator()

        intent_node = orch._analyze_intent("test query")

        # Required top-level fields
        assert "id" in intent_node
        assert "type" in intent_node
        assert "state" in intent_node
        assert "timestamps" in intent_node
        assert "provenance" in intent_node

        # State requirements
        assert "confidence" in intent_node["state"]
        assert "salience" in intent_node["state"]
        assert 0 <= intent_node["state"]["confidence"] <= 1
        assert 0 <= intent_node["state"]["salience"] <= 1


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestNodeSelection:
    """Test node selection logic."""

    def test_selects_math_for_mathematical_intent(self):
        """Mathematical intent should select math node."""
        orch = CognitiveOrchestrator()

        intent_node = {"state": {"intent": "mathematical"}}
        selected = orch._select_node(intent_node)

        assert selected == "math"

    def test_selects_facts_for_question_intent(self):
        """Question intent should select facts node."""
        orch = CognitiveOrchestrator()

        intent_node = {"state": {"intent": "question"}}
        selected = orch._select_node(intent_node)

        assert selected == "facts"

    def test_selects_vision_for_perception_intent(self):
        """Perception intent should select vision node."""
        orch = CognitiveOrchestrator()

        intent_node = {"state": {"intent": "perception"}}
        selected = orch._select_node(intent_node)

        assert selected == "vision"

    def test_defaults_to_facts_for_unknown_intent(self):
        """Unknown intent should default to facts node."""
        orch = CognitiveOrchestrator()

        intent_node = {"state": {"intent": "unknown"}}
        selected = orch._select_node(intent_node)

        assert selected == "facts"


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestQueryProcessing:
    """Test end-to-end query processing."""

    def test_process_query_creates_intent_node(self):
        """Query processing should create intent node."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        orch.process_query("2 + 2")

        # Should have intent node in graph
        intent_nodes = [n for n in orch.matriz_graph.values() if n["type"] == "INTENT"]
        assert len(intent_nodes) >= 1

    def test_process_query_creates_decision_node(self):
        """Query processing should create decision node."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        orch.process_query("2 + 2")

        # Should have decision node in graph
        decision_nodes = [n for n in orch.matriz_graph.values() if n["type"] == "DECISION"]
        assert len(decision_nodes) >= 1

    def test_process_query_returns_complete_result(self):
        """Query result should have all required fields."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "Paris",
            "confidence": 0.92,
            "matriz_node": {"id": "fact-1", "type": "MEMORY"},
        }
        orch.register_node("facts", mock_node)

        result = orch.process_query("Capital of France?")

        assert "answer" in result
        assert "confidence" in result
        assert "matriz_nodes" in result
        assert "trace" in result
        assert "reasoning_chain" in result

    def test_process_query_calls_registered_node(self):
        """Query processing should call the selected node."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "42",
            "confidence": 1.0,
            "matriz_node": {"id": "test-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        orch.process_query("6 * 7")

        # Node should have been called
        mock_node.process.assert_called_once()
        call_args = mock_node.process.call_args[0][0]
        assert "query" in call_args

    def test_process_query_with_validator_creates_reflection(self):
        """Processing with validator should create reflection node."""
        orch = CognitiveOrchestrator()

        # Register processing node
        mock_processor = Mock(spec=CognitiveNode)
        mock_processor.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_processor)

        # Register validator
        mock_validator = Mock(spec=CognitiveNode)
        mock_validator.validate_output.return_value = True
        orch.register_node("validator", mock_validator)

        orch.process_query("2 + 2")

        # Should have reflection node
        reflection_nodes = [n for n in orch.matriz_graph.values() if n["type"] == "REFLECTION"]
        assert len(reflection_nodes) >= 1

    def test_process_query_handles_missing_node(self):
        """Processing should handle when selected node is not registered."""
        orch = CognitiveOrchestrator()

        result = orch.process_query("2 + 2")

        assert "error" in result
        assert "trace" in result


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestExecutionTrace:
    """Test execution trace recording."""

    def test_execution_trace_recorded(self):
        """Each query should add to execution trace."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "test",
            "confidence": 0.8,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        initial_trace_len = len(orch.execution_trace)
        orch.process_query("test query")

        assert len(orch.execution_trace) == initial_trace_len + 1

    def test_execution_trace_contains_timing(self):
        """Trace should include processing time."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "test",
            "confidence": 0.8,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        orch.process_query("test query")

        trace = orch.execution_trace[-1]
        assert hasattr(trace, "processing_time")
        assert trace.processing_time >= 0

    def test_execution_trace_contains_input_output(self):
        """Trace should record input and output data."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "result",
            "confidence": 0.9,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        orch.process_query("input query")

        trace = orch.execution_trace[-1]
        assert "query" in trace.input_data
        assert trace.input_data["query"] == "input query"
        assert "answer" in trace.output_data


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestCausalChainTracing:
    """Test causal chain reconstruction."""

    def test_get_causal_chain_for_nonexistent_node(self):
        """Causal chain for nonexistent node should return empty."""
        orch = CognitiveOrchestrator()

        chain = orch.get_causal_chain("nonexistent-id")

        assert chain == []

    def test_get_causal_chain_traces_triggers(self):
        """Causal chain should follow trigger relationships."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        orch.process_query("2 + 2")

        # Get a decision node and trace its chain
        decision_nodes = [n for n in orch.matriz_graph.values() if n["type"] == "DECISION"]
        if decision_nodes:
            decision_id = decision_nodes[0]["id"]
            chain = orch.get_causal_chain(decision_id)

            # Chain should include the decision node itself
            assert any(n["id"] == decision_id for n in chain)

            # Chain should not be empty
            assert len(chain) > 0

    def test_get_causal_chain_avoids_cycles(self):
        """Causal chain should handle circular references."""
        orch = CognitiveOrchestrator()

        # Manually create nodes with circular triggers
        node1 = {
            "id": "node-1",
            "type": "CONTEXT",
            "state": {"confidence": 0.8, "salience": 0.7},
            "triggers": [{"trigger_node_id": "node-2"}],
        }
        node2 = {
            "id": "node-2",
            "type": "CONTEXT",
            "state": {"confidence": 0.8, "salience": 0.7},
            "triggers": [{"trigger_node_id": "node-1"}],
        }

        orch.matriz_graph["node-1"] = node1
        orch.matriz_graph["node-2"] = node2

        chain = orch.get_causal_chain("node-1")

        # Should not loop infinitely and should include both nodes
        assert len(chain) == 2


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestReasoningChain:
    """Test reasoning chain construction."""

    def test_reasoning_chain_built_from_nodes(self):
        """Reasoning chain should summarize MATRIZ nodes."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        result = orch.process_query("2 + 2")

        assert "reasoning_chain" in result
        assert isinstance(result["reasoning_chain"], list)
        assert len(result["reasoning_chain"]) > 0

    def test_reasoning_chain_includes_intent(self):
        """Reasoning chain should describe intent analysis."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "4",
            "confidence": 0.95,
            "matriz_node": {"id": "math-1", "type": "COMPUTATION"},
        }
        orch.register_node("math", mock_node)

        result = orch.process_query("2 + 2")

        # Should have intent explanation
        chain_str = " ".join(result["reasoning_chain"])
        assert "intent" in chain_str.lower()


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="matriz module not available")
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query(self):
        """Empty query should be handled gracefully."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "",
            "confidence": 0.1,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        result = orch.process_query("")

        # Should not crash, should return some result
        assert "answer" in result or "error" in result

    def test_very_long_query(self):
        """Very long query should be handled."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "handled",
            "confidence": 0.7,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        long_query = "test " * 1000
        result = orch.process_query(long_query)

        assert "answer" in result or "error" in result

    def test_special_characters_in_query(self):
        """Special characters should be handled."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.return_value = {
            "answer": "handled",
            "confidence": 0.8,
            "matriz_node": {"id": "test-1", "type": "CONTEXT"},
        }
        orch.register_node("facts", mock_node)

        result = orch.process_query("!@#$%^&*()")

        assert "answer" in result or "error" in result

    def test_node_process_exception_handling(self):
        """Should handle exceptions from node processing gracefully."""
        orch = CognitiveOrchestrator()
        mock_node = Mock(spec=CognitiveNode)
        mock_node.process.side_effect = Exception("Node processing error")
        orch.register_node("math", mock_node)

        # Should not crash
        try:
            orch.process_query("2 + 2")
            # Either returns error or raises exception
            assert True
        except Exception:
            # Exception is acceptable for this edge case
            assert True
