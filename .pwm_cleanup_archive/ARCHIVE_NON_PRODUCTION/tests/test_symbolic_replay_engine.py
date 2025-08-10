import tempfile
import unittest
from pathlib import Path

from memory.core_memory.symbolic_replay_engine import SymbolicReplayEngine


class TestSymbolicReplayEngine(unittest.TestCase):
    def test_record_and_replay(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "log.jsonl"
            engine = SymbolicReplayEngine(log_path=path)
            engine.record_event({"valence": 0.5}, 0.1, "init")
            engine.save()

            events = engine.replay()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].message, "init")


if __name__ == "__main__":
    unittest.main()
