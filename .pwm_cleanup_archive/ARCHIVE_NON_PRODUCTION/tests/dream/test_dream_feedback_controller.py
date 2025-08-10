import unittest
from unittest.mock import MagicMock

from dream.core.dream_feedback_controller import DreamFeedbackController


class TestDreamFeedbackController(unittest.TestCase):
    def test_check_drift_event(self):
        controller = DreamFeedbackController(drift_threshold=0.5)
        self.assertTrue(controller.check_drift_event(0.6))
        self.assertFalse(controller.check_drift_event(0.4))

    def test_trigger_redirection(self):
        controller = DreamFeedbackController()
        controller.snapshot_store = MagicMock()
        controller.snapshot_store.get_recent_snapshots.return_value = [
            {"dream_id": "dream1"},
            {"dream_id": "dream2"},
        ]
        redirection = controller.trigger_redirection("user1", {"emotion": "happy"})
        self.assertEqual(redirection["action"], "redirect")
        self.assertEqual(redirection["target_snapshot"]["dream_id"], "dream2")


if __name__ == "__main__":
    unittest.main()
