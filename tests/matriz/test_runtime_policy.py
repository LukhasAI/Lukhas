import pytest
from lukhas.matriz.runtime.policy import PolicyEngine

class TestPolicyEngine:

    def test_initialization(self):
        """Test that the PolicyEngine can be initialized."""
        engine = PolicyEngine()
        assert engine.constitution_rules is None

        rules = ["rule1", "rule2"]
        engine = PolicyEngine(constitution_rules=rules)
        assert engine.constitution_rules == rules

    def test_evaluate_trigger_allowed(self):
        """Test that a trigger is allowed if it does not contain a 'forbidden' label."""
        engine = PolicyEngine()
        trigger = {"constitution": ["allowed", "safe"]}
        assert engine.evaluate_trigger(trigger) is True

    def test_evaluate_trigger_forbidden(self):
        """Test that a trigger is rejected if it contains a 'forbidden' label."""
        engine = PolicyEngine()
        trigger = {"constitution": ["allowed", "forbidden"]}
        assert engine.evaluate_trigger(trigger) is False

    def test_evaluate_trigger_no_constitution(self):
        """Test that a trigger is allowed if it has no constitution labels."""
        engine = PolicyEngine()
        trigger = {"other_key": "value"}
        assert engine.evaluate_trigger(trigger) is True

    def test_evaluate_trigger_not_a_list(self):
        """Test that a trigger is allowed if 'constitution' is not a list."""
        engine = PolicyEngine()
        trigger = {"constitution": "not-a-list"}
        assert engine.evaluate_trigger(trigger) is True

    def test_evaluate_trigger_not_a_mapping(self):
        """Test that non-mapping triggers are allowed."""
        engine = PolicyEngine()
        trigger = "just a string"
        assert engine.evaluate_trigger(trigger) is True

        trigger = None
        assert engine.evaluate_trigger(trigger) is True
