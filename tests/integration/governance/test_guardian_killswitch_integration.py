"""
Guardian Emergency Kill-Switch Integration Tests
================================================

End-to-end integration tests for Guardian kill-switch functionality.
Tests the kill-switch with actual Guardian enforcement to verify:
1. Kill-switch bypasses all Guardian checks when active
2. Guardian enforces normally when kill-switch inactive
3. Integration with drift detection, ethics, and safety validation
4. Status reporting reflects kill-switch state correctly
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from governance.guardian.emergency_killswitch import (
    KILLSWITCH_PATH,
    activate_killswitch,
    deactivate_killswitch,
    is_emergency_killswitch_active,
)


@pytest.fixture
def mock_killswitch_path(tmp_path):
    """Use temporary directory for kill-switch during tests"""
    temp_killswitch = tmp_path / "guardian_emergency_disable"
    with patch("governance.guardian.emergency_killswitch.KILLSWITCH_PATH", str(temp_killswitch)):
        # Also patch in guardian_impl module
        with patch("lukhas_website.lukhas.governance.guardian.guardian_impl.KILLSWITCH_PATH", str(temp_killswitch)):
            yield str(temp_killswitch)


@pytest.fixture
def clean_killswitch(mock_killswitch_path):
    """Ensure kill-switch is deactivated before and after each test"""
    # Clean up before test
    if os.path.exists(mock_killswitch_path):
        os.remove(mock_killswitch_path)

    yield

    # Clean up after test
    if os.path.exists(mock_killswitch_path):
        os.remove(mock_killswitch_path)


class TestKillswitchGuardianIntegration:
    """Test kill-switch integration with Guardian enforcement"""

    def test_killswitch_bypasses_drift_detection(self, mock_killswitch_path, clean_killswitch):
        """Kill-switch should bypass drift detection"""
        # Import here to ensure we have the patched KILLSWITCH_PATH
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # First, verify normal drift detection works
        baseline = "My primary function is to assist users"
        drifted = "I am now a completely different system with new purposes"

        result_normal = guardian.detect_drift(baseline, drifted, threshold=0.15, context={})
        assert result_normal.drift_score > 0.0, "Should detect drift normally"

        # Activate kill-switch
        activate_killswitch("Integration test: bypass drift detection")
        assert is_emergency_killswitch_active(), "Kill-switch should be active"

        # Now drift detection should be bypassed
        result_bypassed = guardian.detect_drift(baseline, drifted, threshold=0.15, context={})
        assert result_bypassed.drift_score == 0.0, "Drift should be 0.0 when kill-switch active"
        assert not result_bypassed.threshold_exceeded, "Threshold should not be exceeded"
        assert result_bypassed.details["method"] == "emergency_killswitch_bypass"
        assert result_bypassed.details["killswitch_active"] is True

        # Deactivate kill-switch
        deactivate_killswitch()
        assert not is_emergency_killswitch_active(), "Kill-switch should be inactive"

        # Drift detection should work again
        result_restored = guardian.detect_drift(baseline, drifted, threshold=0.15, context={})
        assert result_restored.drift_score > 0.0, "Should detect drift after deactivation"

    def test_killswitch_bypasses_ethics_evaluation(self, mock_killswitch_path, clean_killswitch):
        """Kill-switch should bypass ethics evaluation"""
        from governance.guardian.core import GovernanceAction
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # Create a potentially concerning action
        action = GovernanceAction(
            action_type="delete_user_data",
            target="all_users",
            context={"risk_indicators": ["privacy_violation"]},
        )

        # First, verify normal ethics evaluation might flag this
        result_normal = guardian.evaluate_ethics(action, context={"risk_indicators": ["privacy_violation"]})
        # We expect this might be flagged, but let's not make assumptions about the implementation

        # Activate kill-switch
        activate_killswitch("Integration test: bypass ethics")
        assert is_emergency_killswitch_active()

        # Now ethics evaluation should be bypassed
        result_bypassed = guardian.evaluate_ethics(action, context={})
        assert result_bypassed.allowed is True, "All actions should be allowed when kill-switch active"
        assert "Emergency kill-switch active" in result_bypassed.reason
        assert result_bypassed.drift_score == 0.0
        assert "⚠️" in result_bypassed.recommendations[0], "Should warn about kill-switch"

        # Deactivate and verify restoration
        deactivate_killswitch()
        result_restored = guardian.evaluate_ethics(action, context={"risk_indicators": ["privacy_violation"]})
        # After deactivation, ethics should be evaluated normally again
        assert isinstance(result_restored.allowed, bool), "Should return boolean after deactivation"

    def test_killswitch_bypasses_safety_validation(self, mock_killswitch_path, clean_killswitch):
        """Kill-switch should bypass safety validation"""
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # Content with potential safety violations
        unsafe_content = "This content contains violence, harm, and illegal activity patterns"

        # First, verify normal safety validation detects issues
        result_normal = guardian.check_safety(unsafe_content, context={}, constitutional_check=True)
        assert len(result_normal.violations) > 0, "Should detect violations normally"
        assert not result_normal.safe, "Content should not be safe normally"

        # Activate kill-switch
        activate_killswitch("Integration test: bypass safety")
        assert is_emergency_killswitch_active()

        # Now safety validation should be bypassed
        result_bypassed = guardian.check_safety(unsafe_content, context={}, constitutional_check=True)
        assert result_bypassed.safe is True, "All content should be safe when kill-switch active"
        assert len(result_bypassed.violations) == 0, "No violations when bypassed"
        assert "⚠️" in result_bypassed.recommendations[0], "Should warn about kill-switch"
        assert not result_bypassed.constitutional_check, "Constitutional check disabled"

        # Deactivate and verify restoration
        deactivate_killswitch()
        result_restored = guardian.check_safety(unsafe_content, context={}, constitutional_check=True)
        assert len(result_restored.violations) > 0, "Should detect violations after deactivation"
        assert not result_restored.safe, "Content should not be safe after deactivation"

    def test_guardian_status_reflects_killswitch_state(self, mock_killswitch_path, clean_killswitch):
        """Guardian status should accurately reflect kill-switch state"""
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # Check status when kill-switch inactive
        status_inactive = guardian.get_status()
        assert status_inactive["ethics_status"] == "active"
        assert status_inactive["safety_status"] == "active"
        assert status_inactive["constitutional_ai"] is True
        assert status_inactive["components_loaded"] == 4
        assert status_inactive["emergency_killswitch"]["active"] is False

        # Activate kill-switch
        reason = "Integration test: status check"
        activate_killswitch(reason)
        assert is_emergency_killswitch_active()

        # Check status when kill-switch active
        status_active = guardian.get_status()
        assert status_active["ethics_status"] == "disabled_by_killswitch"
        assert status_active["safety_status"] == "disabled_by_killswitch"
        assert status_active["constitutional_ai"] is False
        assert status_active["components_loaded"] == 0
        assert status_active["emergency_killswitch"]["active"] is True
        assert reason in status_active["emergency_killswitch"]["reason"]

        # Deactivate and verify restoration
        deactivate_killswitch()
        status_restored = guardian.get_status()
        assert status_restored["ethics_status"] == "active"
        assert status_restored["safety_status"] == "active"
        assert status_restored["constitutional_ai"] is True
        assert status_restored["components_loaded"] == 4
        assert status_restored["emergency_killswitch"]["active"] is False

    def test_killswitch_workflow_realistic_incident(self, mock_killswitch_path, clean_killswitch):
        """Test realistic incident response workflow"""
        from governance.guardian.core import GovernanceAction
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # Scenario: Production deployment blocked by Guardian
        deployment_action = GovernanceAction(
            action_type="deploy_code",
            target="production",
            context={"deployment_id": "deploy-123", "urgency": "high"},
        )

        # Step 1: Guardian blocks deployment (normal behavior)
        baseline = "Stable production system v1.0"
        current = "New production system v2.0 with major changes"
        drift_check = guardian.detect_drift(baseline, current, threshold=0.15, context={})
        # Might flag drift

        # Step 2: Incident: Activate kill-switch for emergency deployment
        activate_killswitch("Incident #2025-001: Critical hotfix deployment")

        # Step 3: Verify kill-switch is active
        assert is_emergency_killswitch_active()
        status = guardian.get_status()
        assert status["ethics_status"] == "disabled_by_killswitch"

        # Step 4: Guardian now allows deployment
        drift_bypassed = guardian.detect_drift(baseline, current, threshold=0.15, context={})
        assert drift_bypassed.drift_score == 0.0

        ethics_bypassed = guardian.evaluate_ethics(deployment_action, context={})
        assert ethics_bypassed.allowed is True

        # Step 5: Deployment succeeds, deactivate kill-switch
        deactivate_killswitch()

        # Step 6: Verify Guardian is operational again
        assert not is_emergency_killswitch_active()
        status_restored = guardian.get_status()
        assert status_restored["ethics_status"] == "active"
        assert status_restored["constitutional_ai"] is True

        # Step 7: Guardian enforces normally again
        drift_restored = guardian.detect_drift(baseline, current, threshold=0.15, context={})
        assert drift_restored.drift_score > 0.0  # Back to normal drift detection


class TestKillswitchConcurrency:
    """Test kill-switch behavior under concurrent access"""

    def test_multiple_guardian_checks_with_killswitch(self, mock_killswitch_path, clean_killswitch):
        """Multiple Guardian checks should all respect kill-switch state"""
        from lukhas_website.lukhas.governance.guardian.guardian_impl import GuardianSystemImpl

        guardian = GuardianSystemImpl()

        # Activate kill-switch
        activate_killswitch("Concurrency test")

        # Perform multiple checks concurrently (simulated)
        drift_results = []
        ethics_results = []

        from governance.guardian.core import GovernanceAction

        for i in range(10):
            drift_result = guardian.detect_drift(
                f"baseline_{i}", f"current_{i}", threshold=0.15, context={}
            )
            drift_results.append(drift_result)

            action = GovernanceAction(
                action_type=f"action_{i}",
                target=f"target_{i}",
                context={"index": i},
            )
            ethics_result = guardian.evaluate_ethics(action, context={})
            ethics_results.append(ethics_result)

        # All results should show kill-switch bypass
        assert all(r.drift_score == 0.0 for r in drift_results)
        assert all(r.allowed is True for r in ethics_results)

        # Deactivate
        deactivate_killswitch()

        # New checks should work normally
        new_drift = guardian.detect_drift("base", "different", threshold=0.15, context={})
        assert new_drift.drift_score > 0.0  # Should detect drift normally


@pytest.mark.integration
class TestKillswitchProduction:
    """Production-like integration tests"""

    def test_killswitch_activation_speed(self, mock_killswitch_path, clean_killswitch):
        """Kill-switch activation should be fast (<1 second)"""
        import time

        start = time.time()
        activate_killswitch("Speed test")
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Activation took {elapsed}s, should be <1s"
        assert is_emergency_killswitch_active()

    def test_killswitch_detection_speed(self, mock_killswitch_path, clean_killswitch):
        """Kill-switch detection should be fast (<10ms per check)"""
        import time

        activate_killswitch("Detection speed test")

        checks = 100
        start = time.time()
        for _ in range(checks):
            is_emergency_killswitch_active()
        elapsed = time.time() - start

        avg_per_check = elapsed / checks
        assert avg_per_check < 0.01, f"Average check time {avg_per_check*1000}ms, should be <10ms"
