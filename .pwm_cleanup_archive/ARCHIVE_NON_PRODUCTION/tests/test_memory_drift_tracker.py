import json
import os
import unittest

from memory.core_memory.memory_drift_tracker import MemoryDriftTracker


class TestMemoryDriftTracker(unittest.TestCase):

    def setUp(self):
        self.log_file_path = "test_drift_log.jsonl"
        self.tracker = MemoryDriftTracker(log_file_path=self.log_file_path)

    def tearDown(self):
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    def test_track_drift(self):
        """
        Tests the track_drift method.
        """
        current_snapshot = {"snapshot_id": "current"}
        prior_snapshot = {"snapshot_id": "prior"}
        drift_vector = self.tracker.track_drift(current_snapshot, prior_snapshot)

        self.assertIn("timestamp_utc", drift_vector)
        self.assertIn("entropy_delta", drift_vector)
        self.assertIn("emotional_delta", drift_vector)
        self.assertIn("symbolic_vector_shift", drift_vector)
        self.assertEqual(drift_vector["current_snapshot_id"], "current")
        self.assertEqual(drift_vector["prior_snapshot_id"], "prior")

        with open(self.log_file_path) as f:
            log_entry = json.loads(f.readline())
            self.assertEqual(log_entry["current_snapshot_id"], "current")


if __name__ == "__main__":
    unittest.main()
