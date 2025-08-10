import unittest

from memory.governance.ethical_drift_governor import evaluate_memory_action


class TestEthicalDriftGovernor(unittest.TestCase):
    def test_violation_detection(self):
        event = {"action": "falsify_data"}
        result = evaluate_memory_action(event)
        self.assertTrue(result.get("violation"))

    def test_intervention_trigger(self):
        event = {"action": "security_breach"}
        result = evaluate_memory_action(event)
        self.assertEqual(result.get("intervention"), "freeze")


if __name__ == "__main__":
    unittest.main()
