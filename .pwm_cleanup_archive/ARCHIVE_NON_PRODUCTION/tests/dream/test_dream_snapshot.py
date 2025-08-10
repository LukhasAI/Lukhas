# LUKHAS_TAG: test_snapshot

import unittest

from dream.oneiric_engine.oneiric_core.modules.dream_reflection_loop import (
    DreamReflectionLoop,
)


class TestDreamSnapshot(unittest.TestCase):
    def test_dream_snapshot_valid(self):
        dream_loop = DreamReflectionLoop()
        dream_loop.stats["last_dream_id"] = "dream_id_1"
        dream_loop.stats["last_dream_tags"] = ["tag1", "tag2"]
        dream_loop.stats["last_dream_emotion"] = "joy"
        dream_loop.stats["drift_score"] = 0.5
        dream_loop.stats["affect_delta"] = 0.2

        snapshot = dream_loop.dream_snapshot()

        self.assertEqual(snapshot["dream_id"], "dream_id_1")
        self.assertEqual(snapshot["tags"], ["tag1", "tag2"])
        self.assertEqual(snapshot["emotion"], "joy")
        self.assertEqual(snapshot["drift_score"], 0.5)
        self.assertEqual(snapshot["affect_delta"], 0.2)

    def test_dream_snapshot_malformed(self):
        dream_loop = DreamReflectionLoop()
        snapshot = dream_loop.dream_snapshot()

        self.assertIsNone(snapshot["dream_id"])
        self.assertEqual(snapshot["tags"], [])
        self.assertIsNone(snapshot["emotion"])
        self.assertEqual(snapshot["drift_score"], 0.0)
        self.assertEqual(snapshot["affect_delta"], 0.0)


if __name__ == "__main__":
    unittest.main()
