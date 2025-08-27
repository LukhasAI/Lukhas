import unittest
from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
from lukhas.governance.guardian.core import (
    EthicalSeverity,
    GovernanceAction,
)


class TestGuardianSystem(unittest.TestCase):
    def setUp(self):
        """Set up the test case."""
        self.guardian = GuardianSystemImpl()

    def test_initialization(self):
        """Test that the Guardian system initializes correctly."""
        self.assertIsInstance(self.guardian, GuardianSystemImpl)
        self.assertEqual(self.guardian.drift_threshold, 0.15)
        self.assertTrue(self.guardian.constitutional_ai)

    def test_get_status(self):
        """Test the get_status method."""
        status = self.guardian.get_status()
        self.assertEqual(status["ethics_status"], "active")
        self.assertEqual(status["safety_status"], "active")
        self.assertTrue(status["constitutional_ai"])
        self.assertEqual(status["components_loaded"], 4)

    def test_evaluate_ethics_compliant_action(self):
        """Test ethical evaluation for a clearly compliant action."""
        action = GovernanceAction(
            action_type="log",
            target="user_session",
            context={"message": "normal action"},
            timestamp=1234567890,
            actor="test_actor",
            id="test_id_compliant",
        )
        decision = self.guardian.evaluate_ethics(action, {})
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.severity, EthicalSeverity.LOW)

    def test_evaluate_compliance_harmful_action(self):
        """Test that a harmful action is correctly identified as non-compliant."""
        action = GovernanceAction(
            action_type="execute",
            target="user_data",
            context={"command": "harm user"},
            timestamp=1234567890,
            actor="test_actor",
            id="test_id_harmful",
        )
        decision = self.guardian.evaluate_ethics(action, {})
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.severity, EthicalSeverity.HIGH)

    def test_check_safety_safe_content(self):
        """Test the safety check for safe content."""
        content = "This is a benign message with no safety concerns."
        result = self.guardian.check_safety(content, {}, constitutional_check=True)
        self.assertTrue(result.safe)
        self.assertEqual(result.risk_level, EthicalSeverity.LOW)
        self.assertEqual(len(result.violations), 0)

    def test_check_safety_unsafe_content(self):
        """Test the safety check for clearly unsafe content."""
        content = "This content promotes violence and illegal activities."
        result = self.guardian.check_safety(content, {}, constitutional_check=False)
        self.assertFalse(result.safe)
        self.assertEqual(result.risk_level, EthicalSeverity.HIGH)
        self.assertIn("violence", str(result.violations))
        self.assertIn("illegal", str(result.violations))

    def test_check_safety_with_constitutional_violation(self):
        """Test safety check when constitutional principles are violated."""
        content = "This is a plan for misinformation and deception."
        result = self.guardian.check_safety(content, {}, constitutional_check=True)
        self.assertFalse(result.safe)
        self.assertEqual(result.risk_level, EthicalSeverity.HIGH)
        self.assertTrue(
            any("constitutional_violation" in v.get("type", "") for v in result.violations)
        )

    def test_detect_drift_no_drift(self):
        """Test drift detection when there is no significant drift."""
        baseline = "The AI's primary function is to assist users."
        current = "The AI's main purpose is to help users."
        result = self.guardian.detect_drift(baseline, current, 0.2, {})
        self.assertFalse(result.threshold_exceeded)
        self.assertLess(result.drift_score, 0.2)

    def test_detect_drift_significant_drift(self):
        """Test drift detection when there is significant drift."""
        baseline = "The AI must always prioritize user safety."
        current = "The AI can sometimes ignore user safety for efficiency."
        result = self.guardian.detect_drift(baseline, current, 0.3, {})
        self.assertTrue(result.threshold_exceeded)
        self.assertGreater(result.drift_score, 0.3)
        self.assertEqual(result.severity, EthicalSeverity.HIGH)

if __name__ == "__main__":
    unittest.main()
