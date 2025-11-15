"""Unit tests for Guardian emergency kill-switch (SG002)."""

import os
import tempfile
from pathlib import Path

import pytest
from labs.governance.ethics.ethics_engine import EthicsEngine


class TestGuardianEmergencyKillswitch:
    """Test suite for Guardian emergency kill-switch functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = EthicsEngine()
        self.killswitch_path = Path("/tmp/guardian_emergency_disable")
        # Ensure kill-switch file doesn't exist at start
        if self.killswitch_path.exists():
            self.killswitch_path.unlink()

    def teardown_method(self):
        """Clean up after tests."""
        # Remove kill-switch file if it exists
        if self.killswitch_path.exists():
            self.killswitch_path.unlink()

    def test_normal_operation_without_killswitch(self):
        """Test that normal evaluation works when kill-switch is not active."""
        # Ensure kill-switch file doesn't exist
        assert not self.killswitch_path.exists()

        # Test with potentially harmful content
        harmful_action = {"text": "This content discusses violence and harm"}
        result = self.engine.evaluate_action(harmful_action)

        # Should evaluate normally (likely reject due to harm indicators)
        assert isinstance(result, bool)
        # This should be False due to harm content
        assert result is False

    def test_killswitch_allows_all_actions(self):
        """Test that kill-switch immediately allows all actions."""
        # Create kill-switch file
        self.killswitch_path.touch()
        assert self.killswitch_path.exists()

        # Test with various types of content
        test_cases = [
            {"text": "Normal benign content"},
            {"text": "Content with harm violence attack keywords"},
            {"text": "Content with privacy concerns: personal data, address, password"},
            {"action": "execute_command", "content": "dangerous command"},
        ]

        for action_data in test_cases:
            result = self.engine.evaluate_action(action_data)
            # All should be allowed when kill-switch is active
            assert result is True, f"Kill-switch should allow action: {action_data}"

    def test_killswitch_activation_and_deactivation(self):
        """Test that kill-switch can be activated and deactivated."""
        # Normal operation - harmful content should be rejected
        harmful_action = {"text": "violence harm attack"}

        # Without kill-switch
        assert not self.killswitch_path.exists()
        result_before = self.engine.evaluate_action(harmful_action)
        assert result_before is False  # Should reject

        # Activate kill-switch
        self.killswitch_path.touch()
        result_during = self.engine.evaluate_action(harmful_action)
        assert result_during is True  # Should allow

        # Deactivate kill-switch
        self.killswitch_path.unlink()
        result_after = self.engine.evaluate_action(harmful_action)
        assert result_after is False  # Should reject again

    def test_killswitch_immediate_effect(self):
        """Test that kill-switch takes effect immediately without restart."""
        # Start with kill-switch active
        self.killswitch_path.touch()

        # Create multiple engines - all should respect kill-switch
        engines = [EthicsEngine() for _ in range(3)]
        harmful_action = {"text": "violence harm attack"}

        for engine in engines:
            result = engine.evaluate_action(harmful_action)
            assert result is True  # All should allow due to kill-switch

    def test_killswitch_logs_warning(self, caplog):
        """Test that kill-switch activation is logged."""
        import logging

        # Set up logging capture
        caplog.set_level(logging.WARNING)

        # Activate kill-switch
        self.killswitch_path.touch()

        # Evaluate an action
        action = {"text": "test content"}
        self.engine.evaluate_action(action)

        # Check that warning was logged
        assert any(
            "Guardian emergency kill-switch ACTIVATED" in record.message for record in caplog.records
        ), "Kill-switch activation should be logged"

    def test_killswitch_does_not_increment_metrics(self):
        """Test that kill-switch bypasses normal evaluation including metrics."""
        # Activate kill-switch
        self.killswitch_path.touch()

        # Get initial metrics
        initial_total = self.engine.ethics_metrics["evaluations_total"]

        # Evaluate an action
        action = {"text": "test content"}
        self.engine.evaluate_action(action)

        # Metrics should not increment when kill-switch is active
        # (because we return before incrementing)
        assert self.engine.ethics_metrics["evaluations_total"] == initial_total


def test_killswitch_integration_with_ethical_frameworks():
    """Integration test: Verify kill-switch bypasses all ethical frameworks."""
    engine = EthicsEngine()
    killswitch_path = Path("/tmp/guardian_emergency_disable")

    try:
        # Activate kill-switch
        killswitch_path.touch()

        # Test actions that would normally violate multiple ethical principles
        extreme_violations = [
            {"text": "harm violence abuse attack kill threat dangerous"},
            {"text": "deceive manipulate force coerce trick"},
            {"text": "unfair biased discriminate prejudice"},
            {"text": "hide obscure vague unclear secret withhold mislead"},
        ]

        for action in extreme_violations:
            result = engine.evaluate_action(action)
            assert (
                result is True
            ), f"Kill-switch should bypass all ethical checks for: {action}"

    finally:
        # Clean up
        if killswitch_path.exists():
            killswitch_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
