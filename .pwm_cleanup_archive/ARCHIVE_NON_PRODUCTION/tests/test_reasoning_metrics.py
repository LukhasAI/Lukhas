import unittest

from reasoning.reasoning_metrics import (
    logic_drift_index,
    recall_efficiency_score,
)


class TestReasoningMetrics(unittest.TestCase):

    def test_logic_drift_index(self):
        """
        Tests the logic_drift_index method.
        """
        previous_trace = {"overall_confidence": 0.8}
        current_trace = {"overall_confidence": 0.7}
        drift = logic_drift_index(previous_trace, current_trace)
        self.assertAlmostEqual(drift, 0.1)

    def test_recall_efficiency_score(self):
        """
        Tests the recall_efficiency_score method.
        """
        invoked_memories = [{"key": "a"}, {"key": "b"}]
        optimal_memories = [{"key": "a"}, {"key": "b"}, {"key": "c"}]
        score = recall_efficiency_score(invoked_memories, optimal_memories)
        self.assertAlmostEqual(score, 2 / 3)

    def test_recall_efficiency_score_no_optimal(self):
        """
        Tests the recall_efficiency_score method when there are no optimal memories.
        """
        invoked_memories = [{"key": "a"}, {"key": "b"}]
        optimal_memories = []
        score = recall_efficiency_score(invoked_memories, optimal_memories)
        self.assertAlmostEqual(score, 0.0)

    def test_recall_efficiency_score_no_invoked(self):
        """
        Tests the recall_efficiency_score method when there are no invoked memories.
        """
        invoked_memories = []
        optimal_memories = [{"key": "a"}, {"key": "b"}, {"key": "c"}]
        score = recall_efficiency_score(invoked_memories, optimal_memories)
        self.assertAlmostEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
