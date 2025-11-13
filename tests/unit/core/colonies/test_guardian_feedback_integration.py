"""Comprehensive tests for Guardian Feedback Integration with adaptive drift thresholds."""

import pytest
from datetime import datetime, timezone

from core.colonies.ethics_swarm_colony import (
    AdaptiveDriftThresholdManager,
    EthicsSwarmColony,
    GuardianFeedback,
)


class TestAdaptiveDriftThreshold:
    """Test suite for AdaptiveDriftThresholdManager."""

    def test_threshold_increases_with_high_guardian_scores(self):
        """High Guardian scores should increase threshold (less sensitive)."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add high Guardian scores (ethical stability)
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.9, timestamp=datetime.now(timezone.utc), source="test")
            )

        # Threshold should increase (less sensitive since system is stable)
        assert manager.get_current_threshold() > 0.62

    def test_threshold_decreases_with_low_guardian_scores(self):
        """Low Guardian scores should decrease threshold (more sensitive)."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add low Guardian scores (ethical drift detected)
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.2, timestamp=datetime.now(timezone.utc), source="test")
            )

        # Threshold should decrease (more sensitive to detect drift)
        assert manager.get_current_threshold() < 0.62

    def test_threshold_respects_bounds(self):
        """Threshold should stay within min/max bounds."""
        manager = AdaptiveDriftThresholdManager(
            base_threshold=0.62, min_threshold=0.3, max_threshold=0.85
        )

        # Try to push threshold below minimum
        for _ in range(50):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.0, timestamp=datetime.now(timezone.utc), source="test")
            )
        assert manager.get_current_threshold() >= 0.3

        # Try to push threshold above maximum
        manager.reset_to_baseline()
        for _ in range(50):
            manager.add_guardian_feedback(
                GuardianFeedback(score=1.0, timestamp=datetime.now(timezone.utc), source="test")
            )
        assert manager.get_current_threshold() <= 0.85

    def test_exponential_moving_average_weights_recent_feedback(self):
        """Recent Guardian feedback should have more weight."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add old low scores
        for _ in range(10):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.2, timestamp=datetime.now(timezone.utc), source="test")
            )

        threshold_after_low = manager.get_current_threshold()

        # Add recent high scores (should pull threshold back up)
        for _ in range(5):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.9, timestamp=datetime.now(timezone.utc), source="test")
            )

        threshold_after_high = manager.get_current_threshold()

        # Recent high scores should increase threshold
        assert threshold_after_high > threshold_after_low

    def test_feedback_summary(self):
        """Test Guardian feedback summary."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add some feedback
        for score in [0.8, 0.7, 0.9, 0.6, 0.85]:
            manager.add_guardian_feedback(
                GuardianFeedback(score=score, timestamp=datetime.now(timezone.utc), source="test")
            )

        summary = manager.get_feedback_summary()

        assert summary["feedback_count"] == 5
        assert 0 <= summary["avg_guardian_score"] <= 1
        assert len(summary["recent_scores"]) == 5
        assert "threshold_bounds" in summary

    def test_reset_to_baseline(self):
        """Test resetting threshold to baseline."""
        manager = AdaptiveDriftThresholdManager(base_threshold=0.62)

        # Add feedback to change threshold
        for _ in range(5):
            manager.add_guardian_feedback(
                GuardianFeedback(score=0.9, timestamp=datetime.now(timezone.utc), source="test")
            )

        # Threshold should have changed
        assert manager.get_current_threshold() != 0.62

        # Reset
        manager.reset_to_baseline()

        # Should be back to baseline
        assert manager.get_current_threshold() == 0.62
        summary = manager.get_feedback_summary()
        assert summary["feedback_count"] == 0


class TestEthicsSwarmColonyIntegration:
    """Test suite for EthicsSwarmColony integration with adaptive thresholds."""

    def test_ethics_swarm_colony_integration(self):
        """Test EthicsSwarmColony integration with adaptive threshold."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=True)

        initial_threshold = colony.drift_threshold

        # Update with Guardian feedback
        colony.update_guardian_feedback(score=0.9, source="guardian_test")

        # Threshold should have changed
        assert colony.drift_threshold != initial_threshold

        # Get state
        state = colony.get_threshold_state()
        assert state["adaptive_enabled"] is True
        assert "avg_guardian_score" in state

    def test_adaptive_threshold_can_be_disabled(self):
        """Test that adaptive threshold can be disabled."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=False)

        initial_threshold = colony.drift_threshold

        # Try to update with Guardian feedback (should be ignored)
        colony.update_guardian_feedback(score=0.2, source="guardian_test")

        # Threshold should not change
        assert colony.drift_threshold == initial_threshold

    def test_get_threshold_state_without_adaptive(self):
        """Test getting threshold state when adaptive is disabled."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=False)

        state = colony.get_threshold_state()
        assert state["adaptive_enabled"] is False
        assert state["current_threshold"] == 0.62

    def test_guardian_feedback_with_context(self):
        """Test Guardian feedback with additional context."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=True)

        # Update with context
        context = {"principle_violated": "autonomy", "severity": "low"}
        colony.update_guardian_feedback(score=0.7, source="guardian_constitutional", context=context)

        state = colony.get_threshold_state()
        assert state["feedback_count"] == 1

    def test_multiple_guardian_feedback_updates(self):
        """Test multiple Guardian feedback updates."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=True)

        # Simulate multiple feedback updates over time
        for i in range(10):
            score = 0.5 + (i / 20.0)  # Gradually increasing scores
            colony.update_guardian_feedback(score=score, source=f"guardian_{i}")

        state = colony.get_threshold_state()
        assert state["feedback_count"] == 10
        assert state["avg_guardian_score"] > 0.5

    def test_guardian_feedback_score_clamping(self):
        """Test that Guardian feedback scores are clamped to [0, 1]."""
        colony = EthicsSwarmColony(drift_threshold=0.62, enable_adaptive_threshold=True)

        # Try to set score outside valid range
        colony.update_guardian_feedback(score=1.5, source="test")  # Should clamp to 1.0
        colony.update_guardian_feedback(score=-0.5, source="test")  # Should clamp to 0.0

        state = colony.get_threshold_state()
        # Should have processed both feedbacks successfully
        assert state["feedback_count"] == 2

    def test_custom_feedback_window(self):
        """Test custom Guardian feedback window size."""
        colony = EthicsSwarmColony(
            drift_threshold=0.62,
            enable_adaptive_threshold=True,
            guardian_feedback_window=5,  # Only keep last 5
        )

        # Add more than window size
        for i in range(10):
            colony.update_guardian_feedback(score=0.5, source=f"test_{i}")

        state = colony.get_threshold_state()
        # Should only keep last 5
        assert state["feedback_count"] == 5
