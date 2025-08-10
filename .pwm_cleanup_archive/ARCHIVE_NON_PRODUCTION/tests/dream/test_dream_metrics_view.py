import unittest

from dream.dashboard.dream_metrics_view import DreamMetricsView


class TestDreamMetricsView(unittest.TestCase):
    def test_metrics_aggregation(self):
        view = DreamMetricsView()
        view.update_dream_metrics(drift_delta=0.2, entropy=0.5, energy=1.0)
        view.update_memory_metrics(hits=3, misses=1)
        data = view.to_dict()
        self.assertEqual(data["drift_score_delta"], 0.2)
        self.assertEqual(data["symbolic_entropy"], 0.5)
        self.assertEqual(data["recall_hits"], 3)
        self.assertEqual(data["recall_misses"], 1)
        self.assertAlmostEqual(data["energy_consumption"], 1.0)


if __name__ == "__main__":
    unittest.main()
