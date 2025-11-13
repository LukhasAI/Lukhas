#!/usr/bin/env python3
"""
Tests for MATRIZ Cognitive Nodes
"""

import unittest
from unittest.mock import MagicMock
import sys

# Add the root directory to the python path
sys.path.append(".")

from matriz.nodes.thought.deductive_reasoning import DeductiveReasoningNode
from matriz.nodes.action.tool_usage import ToolUsageNode
from matriz.nodes.decision.option_selection import OptionSelectionNode
from matriz.nodes.awareness.state_assessment import StateAssessmentNode
from matriz.core.node_interface import CognitiveNode


class TestCognitiveNodes(unittest.TestCase):

    def setUp(self):
        # Mock the CognitiveNode's dependencies to isolate the tests
        def create_matriz_node_side_effect(*args, **kwargs):
            return {
                "additional_data": kwargs.get("additional_data", {})
            }

        CognitiveNode.create_matriz_node = MagicMock(side_effect=create_matriz_node_side_effect)
        CognitiveNode.create_reflection = MagicMock()

    def test_deductive_reasoning_node(self):
        node = DeductiveReasoningNode()
        result = node.process({
            "premises": ["All humans are mortal.", "Socrates is a human."],
            "question": "Is Socrates mortal?"
        })
        self.assertIn("conclusion", result["matriz_node"]["additional_data"])

    def test_tool_usage_node(self):
        node = ToolUsageNode()
        result = node.process({
            "tool_name": "calculator",
            "tool_params": {"expression": "2+2"}
        })
        self.assertEqual(result["matriz_node"]["additional_data"]["tool_result"], 4)

    def test_option_selection_node(self):
        node = OptionSelectionNode()
        result = node.process({
            "options": ["A", "B", "C"],
            "criteria": "Choose the first option"
        })
        self.assertEqual(result["matriz_node"]["additional_data"]["best_option"], "A")

    def test_state_assessment_node(self):
        node = StateAssessmentNode()
        result = node.process({
            "state_to_assess": {"mood": "happy", "energy": "high"}
        })
        self.assertIn("summary", result["matriz_node"]["additional_data"])


if __name__ == "__main__":
    unittest.main()
