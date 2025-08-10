import unittest

from dream import DreamSandbox


class TestDreamSandbox(unittest.TestCase):
    def test_recursive_runs_generate_history(self):
        sandbox = DreamSandbox(iterations=2)
        history = sandbox.run_recursive("A simple seed dream")
        self.assertEqual(len(history), 3)
        for entry in history:
            self.assertIn("dream_id", entry)
            self.assertIn("narrative", entry)


if __name__ == "__main__":
    unittest.main()
