import pytest
import os
from unittest.mock import patch, MagicMock
from lukhas.governance.guardian import guardian_wrapper
from lukhas.governance.guardian.core import GovernanceAction

class TestGuardianWrapper:

    @pytest.fixture
    def mock_guardian_impl(self):
        """Fixture to mock the GuardianSystemImpl."""
        mock_instance = MagicMock()
        mock_instance.detect_drift.return_value = MagicMock(drift_score=0.1, threshold_exceeded=False, severity=MagicMock(value='low'), remediation_needed=False, details={})
        mock_instance.evaluate_ethics.return_value = MagicMock(allowed=True, reason="OK", severity=MagicMock(value='low'), confidence=0.9, recommendations=[], drift_score=0.05)
        mock_instance.check_safety.return_value = MagicMock(safe=True, risk_level=MagicMock(value='low'), violations=[], recommendations=[], constitutional_check=True)
        mock_instance.get_status.return_value = {"constitutional_ai_enabled": True, "ethics_engine_status": "active", "safety_validator_status": "active"}
        return mock_instance

    def test_detect_drift_dry_run(self):
        """Test detect_drift in dry_run mode."""
        result = guardian_wrapper.detect_drift("baseline", "current")
        assert result["mode"] == "dry_run"
        assert "drift_score" in result
        assert result["ok"]

    @patch.dict(os.environ, {"GUARDIAN_ACTIVE": "true"})
    def test_detect_drift_live_mode(self, mock_guardian_impl):
        """Test detect_drift in live mode with mocked implementation."""
        import importlib
        # The module needs to be reloaded for the GUARDIAN_ACTIVE flag to be read
        importlib.reload(guardian_wrapper)
        # We also need to re-patch the instance inside the reloaded module
        with patch.object(guardian_wrapper, '_guardian_instance', mock_guardian_impl):
            result = guardian_wrapper.detect_drift("baseline", "current", mode="live")

            assert result["mode"] == "live"
            assert result["drift_score"] == 0.1
            mock_guardian_impl.detect_drift.assert_called_once()

        # Reset for other tests
        importlib.reload(guardian_wrapper)

    def test_evaluate_ethics_dry_run(self):
        """Test evaluate_ethics in dry_run mode."""
        action = GovernanceAction(action_type="test", target="system", context={})
        result = guardian_wrapper.evaluate_ethics(action)
        assert result["mode"] == "dry_run"
        assert "allowed" in result

    @patch.dict(os.environ, {"GUARDIAN_ACTIVE": "true"})
    def test_evaluate_ethics_live_mode(self, mock_guardian_impl):
        """Test evaluate_ethics in live mode."""
        import importlib
        importlib.reload(guardian_wrapper)
        with patch.object(guardian_wrapper, '_guardian_instance', mock_guardian_impl):
            action = GovernanceAction(action_type="test", target="system", context={})
            result = guardian_wrapper.evaluate_ethics(action, mode="live")

            assert result["mode"] == "live"
            assert result["allowed"]
            mock_guardian_impl.evaluate_ethics.assert_called_once()

        importlib.reload(guardian_wrapper)

    def test_check_safety_dry_run(self):
        """Test check_safety in dry_run mode."""
        result = guardian_wrapper.check_safety("safe content")
        assert result["mode"] == "dry_run"
        assert result["safe"]

    def test_get_guardian_status_dry_run(self):
        """Test get_guardian_status in dry_run mode."""
        result = guardian_wrapper.get_guardian_status()
        assert result["mode"] == "dry_run"
        assert result["ethics_engine_status"] == "simulated"

    @patch.dict(os.environ, {"GUARDIAN_ACTIVE": "true"})
    def test_get_guardian_status_live_mode(self, mock_guardian_impl):
        """Test get_guardian_status in live mode."""
        import importlib
        importlib.reload(guardian_wrapper)
        with patch.object(guardian_wrapper, '_guardian_instance', mock_guardian_impl):
            result = guardian_wrapper.get_guardian_status(mode="live")

            assert result["mode"] == "live"
            assert result["ethics_engine_status"] == "active"
            mock_guardian_impl.get_status.assert_called_once()

        importlib.reload(guardian_wrapper)
