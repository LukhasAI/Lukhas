#!/usr/bin/env python3
"""
Integration Tests for the MATRIZ Cognitive Engine
"""

import time
import unittest
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState
from matriz.core.orchestrator import CognitiveOrchestrator


class MockMathNode(CognitiveNode):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple math operation for testing
        parts = input_data["query"].split()
        if len(parts) == 3 and parts[1] == "+":
            try:
                result = int(parts[0]) + int(parts[2])
                answer = str(result)
                confidence = 1.0
            except ValueError:
                answer = "Invalid math query"
                confidence = 0.2
        else:
            answer = "Unsupported math operation"
            confidence = 0.3

        trigger_id = input_data.get("trigger_node_id")
        triggers = (
            [{"event_type": "process_start", "trigger_node_id": trigger_id}] if trigger_id else []
        )

        matriz_node = self.create_matriz_node(
            node_type="COMPUTATION",
            state=NodeState(confidence=confidence, salience=0.8),
            triggers=triggers,
            additional_data={"answer": answer},
        )
        return {"answer": answer, "confidence": confidence, "matriz_node": matriz_node}

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "answer" in output


class MockFactsNode(CognitiveNode):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple fact retrieval for testing
        if "capital of France" in input_data["query"]:
            answer = "Paris"
            confidence = 0.99
        else:
            answer = "I don't know"
            confidence = 0.4

        trigger_id = input_data.get("trigger_node_id")
        triggers = (
            [{"event_type": "process_start", "trigger_node_id": trigger_id}] if trigger_id else []
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=NodeState(confidence=confidence, salience=0.7),
            triggers=triggers,
            additional_data={"answer": answer},
        )
        return {"answer": answer, "confidence": confidence, "matriz_node": matriz_node}

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "answer" in output


class MockVisionNode(CognitiveNode):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simple vision simulation for testing
        if "boy sees dog" in input_data["query"]:
            answer = "A boy is looking at a dog."
            confidence = 0.9
        else:
            answer = "I see nothing of interest."
            confidence = 0.5

        trigger_id = input_data.get("trigger_node_id")
        triggers = (
            [{"event_type": "process_start", "trigger_node_id": trigger_id}] if trigger_id else []
        )

        matriz_node = self.create_matriz_node(
            node_type="SENSORY_IMG",
            state=NodeState(confidence=confidence, salience=0.9),
            triggers=triggers,
            additional_data={"answer": answer},
        )
        return {"answer": answer, "confidence": confidence, "matriz_node": matriz_node}

    def validate_output(self, output: Dict[str, Any]) -> bool:
        return "answer" in output


class MockValidatorNode(CognitiveNode):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # The validator node is not meant to be called directly via `process`.
        # It is used by the orchestrator to validate the output of other nodes.
        raise NotImplementedError("Validator node does not process queries directly.")

    def validate_output(self, output: Dict[str, Any]) -> bool:
        # Simple validation for testing
        if "answer" in output and output["answer"] is not None:
            return True
        return False


class TestMatrizIntegration(unittest.TestCase):
    def setUp(self):
        self.orchestrator = CognitiveOrchestrator()
        self.orchestrator.register_node("math", MockMathNode("math", ["arithmetic"]))
        self.orchestrator.register_node("facts", MockFactsNode("facts", ["qa"]))
        self.orchestrator.register_node("vision", MockVisionNode("vision", ["image_recognition"]))
        self.orchestrator.register_node("validator", MockValidatorNode("validator", ["validation"]))

    def test_full_pipeline_math_query(self):
        result = self.orchestrator.process_query("2 + 2")
        self.assertEqual(result["answer"], "4")
        self.assertIn("trace", result)
        self.assertTrue(result["trace"]["validation_result"])

    def test_full_pipeline_fact_query(self):
        result = self.orchestrator.process_query("What is the capital of France?")
        self.assertEqual(result["answer"], "Paris")
        self.assertIn("trace", result)
        self.assertTrue(result["trace"]["validation_result"])

    def test_state_is_preserved_across_separate_queries(self):
        # Process a math query first
        self.orchestrator.process_query("10 + 5")
        self.assertEqual(len(self.orchestrator.matriz_graph), 4)

        # Then a fact query
        self.orchestrator.process_query("What is the capital of France?")
        self.assertEqual(len(self.orchestrator.matriz_graph), 8)

        # Check that the MATRIZ graph contains nodes from both queries
        node_types = [node["type"] for node in self.orchestrator.matriz_graph.values()]
        self.assertIn("COMPUTATION", node_types)
        self.assertIn("MEMORY", node_types)

    def test_pipeline_node_creation_and_causal_chain(self):
        """
        Tests that a single query creates the correct chain of nodes (INTENT -> DECISION -> COMPUTATION -> REFLECTION)
        and that they are correctly linked.
        """
        self.orchestrator.process_query("5 + 8")

        # 1. Verify that all expected nodes were created
        graph = self.orchestrator.matriz_graph
        self.assertEqual(len(graph), 4)

        node_types = [node["type"] for node in graph.values()]
        self.assertIn("INTENT", node_types)
        self.assertIn("DECISION", node_types)
        self.assertIn("COMPUTATION", node_types)
        self.assertIn("REFLECTION", node_types)

        # 2. Find each node to verify the causal chain
        intent_node = next((n for n in graph.values() if n["type"] == "INTENT"), None)
        decision_node = next((n for n in graph.values() if n["type"] == "DECISION"), None)
        computation_node = next((n for n in graph.values() if n["type"] == "COMPUTATION"), None)
        reflection_node = next((n for n in graph.values() if n["type"] == "REFLECTION"), None)

        self.assertIsNotNone(intent_node)
        self.assertIsNotNone(decision_node)
        self.assertIsNotNone(computation_node)
        self.assertIsNotNone(reflection_node)

        # 3. Verify the causal chain using the `triggers` attribute
        # DECISION is triggered by INTENT
        self.assertEqual(decision_node["triggers"][0]["trigger_node_id"], intent_node["id"])
        # COMPUTATION is triggered by DECISION
        self.assertEqual(computation_node["triggers"][0]["trigger_node_id"], decision_node["id"])
        # REFLECTION is triggered by COMPUTATION
        self.assertEqual(reflection_node["triggers"][0]["trigger_node_id"], computation_node["id"])

    def test_error_recovery_unsupported_operation(self):
        result = self.orchestrator.process_query("5 / 0")
        self.assertEqual(result["answer"], "Unsupported math operation")

    def test_error_recovery_node_not_found(self):
        # Unregister a node to simulate its absence
        self.orchestrator.available_nodes.pop("math")
        result = self.orchestrator.process_query("1 + 1")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No node available for math")

    def test_performance_target(self):
        start_time = time.time()
        self.orchestrator.process_query("A boy sees a dog")
        end_time = time.time()
        self.assertLess(end_time - start_time, 0.1, "Processing time should be less than 100ms")
