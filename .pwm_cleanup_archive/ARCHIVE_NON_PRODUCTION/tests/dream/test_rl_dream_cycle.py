import unittest

from dream.rl import RLDreamCycle


class TestRLDreamCycle(unittest.TestCase):
    def test_run_cycle_returns_scores(self):
        cycle = RLDreamCycle()
        dreams = [
            {"dream_id": "d1", "symbols": ["a", "b"]},
            {"dream_id": "d2", "symbols": ["b", "c"]},
        ]
        result = cycle.run_cycle(dreams)
        self.assertIn("cycles", result)
        self.assertEqual(len(result["cycles"]), 2)
        for entry in result["cycles"]:
            self.assertIn("driftScore", entry)
            self.assertIn("value_drift", entry)
        self.assertIn("final_DriftScore", result)


if __name__ == "__main__":
    unittest.main()
