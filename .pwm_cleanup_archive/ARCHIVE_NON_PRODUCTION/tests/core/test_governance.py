import unittest

from core.governance import GovernanceLayer


class TestGovernanceLayer(unittest.TestCase):
    def setUp(self):
        self.governance = GovernanceLayer()

    def test_deny_unethical_tag_propagation(self):
        unethical_action = {"type": "symbolic_propagation", "drift_score": 0.9}
        self.assertFalse(self.governance.validate_action(unethical_action))

    def test_allow_ethical_tag_propagation(self):
        ethical_action = {"type": "symbolic_propagation", "drift_score": 0.5}
        self.assertTrue(self.governance.validate_action(ethical_action))

    def test_deny_high_entropy_dream(self):
        high_entropy_dream = {"type": "dream_session", "entropy": 0.95}
        self.assertFalse(self.governance.validate_action(high_entropy_dream))

    def test_allow_low_entropy_dream(self):
        low_entropy_dream = {"type": "dream_session", "entropy": 0.7}
        self.assertTrue(self.governance.validate_action(low_entropy_dream))

    def test_deny_dream_with_contradictory_states(self):
        # This is a simplified simulation. A real implementation would have
        # a more sophisticated way of detecting contradictory states.
        contradictory_dream = {
            "type": "dream_session",
            "entropy": 0.5,
            "states": ["peace", "war"],
        }

        # We'll add a rule to the governance layer to check for this
        def check_contradictory_states(action):
            if action["type"] == "dream_session":
                if "states" in action:
                    if "peace" in action["states"] and "war" in action["states"]:
                        print(
                            "GovernanceLayer: Denied dream with contradictory states."
                        )
                        return False
            return True

        self.governance.add_rule(check_contradictory_states)
        self.assertFalse(self.governance.validate_action(contradictory_dream))


if __name__ == "__main__":
    unittest.main()
