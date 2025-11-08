import unittest
from typing import Any

from matriz.core.example_node import MathReasoningNode
from matriz.core.node_interface import CognitiveNode, NodeState
from matriz.core.orchestrator import CognitiveOrchestrator


class MockCognitiveNode(CognitiveNode):
    """A base mock node for testing."""

    def __init__(self, node_name: str, capabilities: list[str]):
        super().__init__(node_name, capabilities)
        self.call_count = 0
        self.last_input = None

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self.call_count += 1
        self.last_input = input_data
        state = NodeState(confidence=0.9, salience=0.9)
        matriz_node = self.create_matriz_node(
            node_type="COMPUTATION",
            state=state,
            additional_data={"mock_output": f"processed by {self.node_name}"},
        )
        return {
            "answer": f"Answer from {self.node_name}",
            "confidence": 0.9,
            "matriz_node": matriz_node,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        return True

class MockMemoryNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("memory", ["memory_access"])

class MockAttentionNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("attention", ["attention_focus"])

class MockThoughtNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("thought", ["reasoning"])

class MockRiskNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("risk", ["risk_assessment"])

class MockIntentNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("intent", ["intent_detection"])

class MockActionNode(MockCognitiveNode):
    def __init__(self):
        super().__init__("action", ["action_selection"])


class PipelineOrchestrator(CognitiveOrchestrator):
    """A test orchestrator that runs a fixed pipeline."""

    PIPELINE = ["memory", "attention", "thought", "risk", "intent", "action"]

    def process_query(self, user_input: str) -> dict[str, Any]:
        """Overrides the base method to run a fixed pipeline."""

        last_output = {"query": user_input}

        for node_name in self.PIPELINE:
            if node_name in self.available_nodes:
                node = self.available_nodes[node_name]
                # Pass the output of the previous node as input to the current one
                result = node.process(last_output)
                matriz_node = result.get("matriz_node", {})
                if "id" in matriz_node:
                    self.matriz_graph[matriz_node["id"]] = matriz_node
                last_output = result # Chain the outputs
            else:
                raise RuntimeError(f"Node '{node_name}' not registered for pipeline processing")

        return last_output


class TestMatrizIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a new orchestrator for each test."""
        self.orchestrator = CognitiveOrchestrator()
        self.pipeline_orchestrator = PipelineOrchestrator()

    def test_orchestrator_instantiation(self):
        """Test that the CognitiveOrchestrator can be instantiated."""
        self.assertIsNotNone(self.orchestrator)

    def test_multi_node_workflow_selection(self):
        """Test that the orchestrator selects the correct node."""
        math_node = MathReasoningNode()
        facts_node = MockCognitiveNode("facts", ["fact_checking"])

        self.orchestrator.register_node("math", math_node)
        self.orchestrator.register_node("facts", facts_node)

        # This query should be routed to the math node
        result = self.orchestrator.process_query("What is 2 + 2?")

        # The MathReasoningNode should have been called, but not the facts_node
        self.assertIn("The result is 4.0", result.get("answer", ""))
        self.assertEqual(facts_node.call_count, 0)

        # Verify the graph contains the expected nodes
        graph_nodes = self.orchestrator.matriz_graph
        self.assertTrue(len(graph_nodes) >= 3, "Graph should have at least INTENT, DECISION, and COMPUTATION nodes")

        node_types = {node["type"] for node in graph_nodes.values()}
        self.assertIn("INTENT", node_types)
        self.assertIn("DECISION", node_types)

        # Verify the causal chain
        final_node_id = result.get("trace", {}).get("matriz_node", {}).get("id")
        self.assertIsNotNone(final_node_id)

        causal_chain = self.orchestrator.get_causal_chain(final_node_id)
        self.assertTrue(len(causal_chain) >= 2, "Causal chain should have at least two nodes")
        chain_ids = {node['id'] for node in causal_chain}
        self.assertIn(final_node_id, chain_ids)

    def test_state_preservation_across_calls(self):
        """Test that orchestrator state is preserved across multiple calls."""
        facts_node = MockCognitiveNode("facts", ["fact_checking"])
        self.orchestrator.register_node("facts", facts_node)

        # First call
        self.orchestrator.process_query("What is the capital of France?")

        self.assertEqual(len(self.orchestrator.execution_trace), 1)
        graph_size_after_first_call = len(self.orchestrator.matriz_graph)
        self.assertTrue(graph_size_after_first_call >= 2)

        # Second call
        self.orchestrator.process_query("What is the tallest mountain?")

        self.assertEqual(len(self.orchestrator.execution_trace), 2, "Execution trace should grow")
        self.assertTrue(len(self.orchestrator.matriz_graph) > graph_size_after_first_call, "Matriz graph should grow")

    def test_error_recovery(self):
        """Test that the orchestrator handles node processing errors."""

        class FailingNode(MockCognitiveNode):
            def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
                raise ValueError("This node always fails")

        failing_node = FailingNode("failing", ["failing"])
        self.orchestrator.register_node("math", failing_node) # Register as math to force routing

        result = self.orchestrator.process_query("1 + 1")

        self.assertIn("error", result)
        self.assertIn("failed during processing", result["error"])

        # Even on failure, the trace should be recorded.
        self.assertEqual(len(self.orchestrator.execution_trace), 0) # No successful trace

    def test_performance_targets(self):
        """Test that a simple workflow meets performance targets."""
        facts_node = MockCognitiveNode("facts", ["fact_checking"])
        self.orchestrator.register_node("facts", facts_node)

        result = self.orchestrator.process_query("some query")

        processing_time = result.get("trace", {}).get("processing_time", float('inf'))
        self.assertLess(processing_time, 0.1, "Processing time should be under 100ms for simple workflows")

    def test_matria_pipeline_end_to_end(self):
        """Test the full M-A-T-R-I-A pipeline from end to end."""
        # Register all the mock nodes required for the pipeline
        nodes = {
            "memory": MockMemoryNode(),
            "attention": MockAttentionNode(),
            "thought": MockThoughtNode(),
            "risk": MockRiskNode(),
            "intent": MockIntentNode(),
            "action": MockActionNode(),
        }

        for name, node in nodes.items():
            self.pipeline_orchestrator.register_node(name, node)

        # Process a query to run the full pipeline
        final_result = self.pipeline_orchestrator.process_query("Run the full pipeline")

        # Verify that every node in the pipeline was called exactly once
        for name, node in nodes.items():
            self.assertEqual(node.call_count, 1, f"Node '{name}' should have been called once")

        # The final answer should be from the last node in the pipeline
        self.assertEqual(final_result["answer"], "Answer from action")

        # Verify that the matriz graph contains a node for each step
        self.assertEqual(len(self.pipeline_orchestrator.matriz_graph), len(nodes))


class TestMathReasoningNode(unittest.TestCase):
    """Unit tests specifically for the MathReasoningNode."""

    def setUp(self):
        """Set up a new node for each test."""
        self.math_node = MathReasoningNode()

    def test_process_non_math_query(self):
        """Test that the node handles non-mathematical queries gracefully."""
        result = self.math_node.process({"query": "Hello, world!"})
        self.assertEqual(result["confidence"], 0.1)
        self.assertIn("No mathematical expression found", result["matriz_node"]["state"]["error"])

    def test_process_evaluation_error(self):
        """Test that the node handles errors during expression evaluation."""
        result = self.math_node.process({"query": "1 / 0"})
        self.assertEqual(result["confidence"], 0.2)
        self.assertIn("Division by zero", result["matriz_node"]["state"]["error"])

    def test_validate_output_valid(self):
        """Test that the validate_output method correctly identifies valid output."""
        valid_output = self.math_node.process({"query": "2 + 2"})
        self.assertTrue(self.math_node.validate_output(valid_output))

    def test_validate_output_invalid(self):
        """Test that the validate_output method catches various invalid outputs."""
        # Missing required field
        invalid_output_1 = self.math_node.process({"query": "2 + 2"})
        del invalid_output_1["confidence"]
        self.assertFalse(self.math_node.validate_output(invalid_output_1))

        # Invalid confidence range
        invalid_output_2 = self.math_node.process({"query": "2 + 2"})
        invalid_output_2["confidence"] = 99.0 # Should be between 0 and 1
        self.assertFalse(self.math_node.validate_output(invalid_output_2))

        # Mismatched confidence and result
        invalid_output_3 = self.math_node.process({"query": "2 + 2"})
        invalid_output_3["confidence"] = 0.1 # High confidence result with low confidence value
        self.assertFalse(self.math_node.validate_output(invalid_output_3))


if __name__ == '__main__':
    unittest.main()
