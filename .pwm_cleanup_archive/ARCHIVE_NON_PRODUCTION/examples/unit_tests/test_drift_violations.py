import unittest

from reasoning.reasoning_engine import SymbolicEngine, SymbolicEthicalWarning


class TestDriftViolations(unittest.TestCase):
    def setUp(self):
        self.engine = SymbolicEngine()

    def test_drift_violation(self):
        with self.assertRaises(SymbolicEthicalWarning):
            self.engine.validate_drift(0.9)

    def test_no_drift_violation(self):
        try:
            self.engine.validate_drift(0.5)
        except SymbolicEthicalWarning:
            self.fail("validate_drift() raised SymbolicEthicalWarning unexpectedly!")


if __name__ == "__main__":
    unittest.main()
