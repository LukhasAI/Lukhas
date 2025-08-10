"""
Governance & Dream Control for the Symbiotic Swarm
Addresses Phase Δ, Step 5

This module provides a GovernanceLayer that acts as a symbolic firewall,
enforcing rules and constraints on the swarm's behavior. It also includes
a simple mechanism for dream control.
"""


class GovernanceLayer:
    """
    A symbolic firewall that enforces governance rules.
    """

    def __init__(self, drift_score_threshold=0.8, max_dream_entropy=0.9):
        self.drift_score_threshold = drift_score_threshold
        self.max_dream_entropy = max_dream_entropy
        self.rules = []

    def add_rule(self, rule):
        """
        Adds a new governance rule. A rule is a function that takes an
        action as input and returns True if the action is allowed, and
        False otherwise.
        """
        self.rules.append(rule)

    def validate_action(self, action):
        """
        Validates an action against the governance rules.
        """
        if action["type"] == "symbolic_propagation":
            if action["drift_score"] > self.drift_score_threshold:
                print(
                    f"GovernanceLayer: Denied action due to high drift score: {action['drift_score']}"
                )
                return False

        if action["type"] == "dream_session":
            if action["entropy"] > self.max_dream_entropy:
                print(
                    f"GovernanceLayer: Denied action due to high dream entropy: {action['entropy']}"
                )
                return False

        for rule in self.rules:
            if not rule(action):
                return False

        print("GovernanceLayer: Action approved.")
        return True


if __name__ == "__main__":
    governance = GovernanceLayer()

    # --- Drift Score Example ---
    high_drift_action = {"type": "symbolic_propagation", "drift_score": 0.9}
    low_drift_action = {"type": "symbolic_propagation", "drift_score": 0.5}
    governance.validate_action(high_drift_action)
    governance.validate_action(low_drift_action)

    # --- Dream Entropy Example ---
    high_entropy_dream = {"type": "dream_session", "entropy": 0.95}
    low_entropy_dream = {"type": "dream_session", "entropy": 0.7}
    governance.validate_action(high_entropy_dream)
    governance.validate_action(low_entropy_dream)
