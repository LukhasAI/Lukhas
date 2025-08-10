import unittest

from reasoning.reasoning_engine import SymbolicEngine


class TestReasoningNode(unittest.TestCase):

    def test_symbolic_prediction_flow(self):
        # ΛTAG: symbolic_reasoning
        engine = SymbolicEngine()
        input_data = {
            "text": "If the system detects a high-priority alert, it should immediately notify the administrator.",
            "context": {"user_id": "test_user"},
        }
        result = engine.reason(input_data)
        self.assertIsNotNone(result)
        self.assertIn("primary_conclusion", result)
        self.assertIsNotNone(result.get("overall_confidence"))
        self.assertIn("reasoning_path_details", result)
        self.assertIn("identified_logical_chains", result)


if __name__ == "__main__":
    unittest.main()
