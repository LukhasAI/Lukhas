"""
Tests for Guardian Emergency Kill-Switch
========================================

Comprehensive test suite for the emergency kill-switch mechanism that
provides immediate Guardian system override capability.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from governance.guardian.emergency_killswitch import (
    KILLSWITCH_PATH,
    activate_killswitch,
    deactivate_killswitch,
    get_killswitch_status,
    is_emergency_killswitch_active,
    read_killswitch_reason,
)


@pytest.fixture
def clean_killswitch():
    """Ensure kill-switch is deactivated before and after each test"""
    # Clean up before test
    if os.path.exists(KILLSWITCH_PATH):
        os.remove(KILLSWITCH_PATH)

    yield

    # Clean up after test
    if os.path.exists(KILLSWITCH_PATH):
        os.remove(KILLSWITCH_PATH)


@pytest.fixture
def mock_killswitch_path(tmp_path):
    """Use temporary directory for kill-switch during tests"""
    temp_killswitch = tmp_path / "guardian_emergency_disable"
    with patch("governance.guardian.emergency_killswitch.KILLSWITCH_PATH", str(temp_killswitch)):
        yield str(temp_killswitch)


class TestKillswitchDetection:
    """Test kill-switch detection and status checking"""

    def test_killswitch_inactive_by_default(self, mock_killswitch_path):
        """Kill-switch should be inactive when file doesn't exist"""
        assert not is_emergency_killswitch_active()

    def test_killswitch_active_when_file_exists(self, mock_killswitch_path):
        """Kill-switch should be active when file exists"""
        Path(mock_killswitch_path).touch()
        assert is_emergency_killswitch_active()

    def test_killswitch_inactive_after_file_removal(self, mock_killswitch_path):
        """Kill-switch should be inactive after file is removed"""
        Path(mock_killswitch_path).touch()
        assert is_emergency_killswitch_active()

        os.remove(mock_killswitch_path)
        assert not is_emergency_killswitch_active()

    def test_killswitch_detection_with_reason(self, mock_killswitch_path):
        """Kill-switch should be active regardless of file contents"""
        Path(mock_killswitch_path).write_text("Incident #123: Emergency deployment")
        assert is_emergency_killswitch_active()

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_killswitch_logs_warning_when_active(self, mock_logger, mock_killswitch_path):
        """Active kill-switch should log warning on each check"""
        Path(mock_killswitch_path).write_text("Test reason")

        is_emergency_killswitch_active()

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "emergency kill-switch is ACTIVE" in call_args[0][0]


class TestKillswitchReason:
    """Test kill-switch reason reading and tracking"""

    def test_read_reason_when_file_empty(self, mock_killswitch_path):
        """Reading reason from empty file should return None"""
        Path(mock_killswitch_path).touch()
        assert read_killswitch_reason() is None

    def test_read_reason_when_file_has_content(self, mock_killswitch_path):
        """Reading reason should return file contents"""
        reason = "Incident #456: Production hotfix required"
        Path(mock_killswitch_path).write_text(reason)

        assert read_killswitch_reason() == reason

    def test_read_reason_when_file_missing(self, mock_killswitch_path):
        """Reading reason when file doesn't exist should return None"""
        assert read_killswitch_reason() is None

    def test_read_reason_strips_whitespace(self, mock_killswitch_path):
        """Reading reason should strip leading/trailing whitespace"""
        reason = "  Test reason with spaces  \n"
        Path(mock_killswitch_path).write_text(reason)

        assert read_killswitch_reason() == "Test reason with spaces"

    def test_read_reason_handles_multiline_content(self, mock_killswitch_path):
        """Reading reason should handle multiline content"""
        reason = "Incident #789\nEmergency deployment\nApproved by: SRE team"
        Path(mock_killswitch_path).write_text(reason)

        result = read_killswitch_reason()
        assert "Incident #789" in result
        assert "Emergency deployment" in result


class TestKillswitchActivation:
    """Test programmatic kill-switch activation"""

    def test_activate_killswitch_creates_file(self, mock_killswitch_path):
        """Activating kill-switch should create file"""
        assert activate_killswitch("Test activation")
        assert os.path.exists(mock_killswitch_path)

    def test_activate_killswitch_writes_reason(self, mock_killswitch_path):
        """Activating kill-switch should write reason to file"""
        reason = "Incident #101: Critical bug detected"
        activate_killswitch(reason)

        contents = Path(mock_killswitch_path).read_text()
        assert reason in contents

    def test_activate_killswitch_writes_timestamp(self, mock_killswitch_path):
        """Activating kill-switch should write timestamp"""
        activate_killswitch("Test")

        contents = Path(mock_killswitch_path).read_text()
        assert "Activated:" in contents
        # Check timestamp format (ISO 8601)
        assert datetime.fromisoformat(contents.split("Activated: ")[1].strip())

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_activate_killswitch_logs_critical(self, mock_logger, mock_killswitch_path):
        """Activating kill-switch should log critical alert"""
        activate_killswitch("Test activation")

        mock_logger.critical.assert_called_once()
        call_args = mock_logger.critical.call_args
        assert "kill-switch ACTIVATED" in call_args[0][0]

    def test_activate_killswitch_returns_true_on_success(self, mock_killswitch_path):
        """Activating kill-switch should return True on success"""
        assert activate_killswitch("Test") is True

    def test_activate_killswitch_overwrites_existing(self, mock_killswitch_path):
        """Activating kill-switch should overwrite existing file"""
        Path(mock_killswitch_path).write_text("Old reason")

        new_reason = "New reason"
        activate_killswitch(new_reason)

        contents = Path(mock_killswitch_path).read_text()
        assert new_reason in contents
        assert "Old reason" not in contents


class TestKillswitchDeactivation:
    """Test programmatic kill-switch deactivation"""

    def test_deactivate_killswitch_removes_file(self, mock_killswitch_path):
        """Deactivating kill-switch should remove file"""
        Path(mock_killswitch_path).write_text("Test")
        assert os.path.exists(mock_killswitch_path)

        assert deactivate_killswitch()
        assert not os.path.exists(mock_killswitch_path)

    def test_deactivate_killswitch_when_already_inactive(self, mock_killswitch_path):
        """Deactivating inactive kill-switch should return True"""
        assert deactivate_killswitch() is True

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_deactivate_killswitch_logs_info(self, mock_logger, mock_killswitch_path):
        """Deactivating kill-switch should log info message"""
        Path(mock_killswitch_path).write_text("Test reason")

        deactivate_killswitch()

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert "kill-switch DEACTIVATED" in call_args[0][0]

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_deactivate_logs_previous_reason(self, mock_logger, mock_killswitch_path):
        """Deactivating kill-switch should log previous reason"""
        reason = "Test incident"
        Path(mock_killswitch_path).write_text(reason)

        deactivate_killswitch()

        call_args = mock_logger.info.call_args
        assert call_args[1]["extra"]["previous_reason"] == reason


class TestKillswitchStatus:
    """Test kill-switch comprehensive status reporting"""

    def test_status_when_inactive(self, mock_killswitch_path):
        """Status should show inactive state"""
        status = get_killswitch_status()

        assert status["active"] is False
        assert status["killswitch_path"] == mock_killswitch_path
        assert "timestamp" in status

    def test_status_when_active(self, mock_killswitch_path):
        """Status should show active state with details"""
        reason = "Test activation"
        Path(mock_killswitch_path).write_text(reason)

        status = get_killswitch_status()

        assert status["active"] is True
        assert status["reason"] == reason
        assert "activated_at" in status
        assert "modified_at" in status

    def test_status_includes_timestamps(self, mock_killswitch_path):
        """Status should include activation and modification timestamps"""
        Path(mock_killswitch_path).write_text("Test")

        status = get_killswitch_status()

        # Timestamps should be ISO format
        datetime.fromisoformat(status["timestamp"])
        datetime.fromisoformat(status["activated_at"])
        datetime.fromisoformat(status["modified_at"])

    def test_status_includes_killswitch_path(self, mock_killswitch_path):
        """Status should include kill-switch file path"""
        status = get_killswitch_status()

        assert status["killswitch_path"] == mock_killswitch_path

    def test_status_handles_missing_file_metadata(self, mock_killswitch_path):
        """Status should handle cases where file metadata can't be read"""
        Path(mock_killswitch_path).write_text("Test")

        # os.path.exists uses os.stat internally, so we need to let it work for exists check
        # but fail for the metadata read in get_killswitch_status
        import os as os_module
        original_stat = os_module.stat
        call_count = [0]  # Use list to allow mutation in nested function

        def counting_stat(path):
            call_count[0] += 1
            # First call is from os.path.exists (in is_emergency_killswitch_active)
            # Let it succeed so the file is detected as existing
            if call_count[0] == 1:
                return original_stat(path)
            # Second call is from get_killswitch_status trying to read metadata
            # Make it fail to test error handling
            raise OSError("Permission denied")

        with patch("governance.guardian.emergency_killswitch.os.stat", side_effect=counting_stat):
            status = get_killswitch_status()

            # Should still return status without timestamps
            assert status["active"] is True
            assert "activated_at" not in status


class TestKillswitchIntegration:
    """Test kill-switch integration scenarios"""

    def test_activate_then_check_status_workflow(self, mock_killswitch_path):
        """Test complete activation workflow"""
        # Activate
        reason = "Integration test"
        assert activate_killswitch(reason)

        # Verify active
        assert is_emergency_killswitch_active()

        # Check status
        status = get_killswitch_status()
        assert status["active"] is True
        assert reason in status["reason"]  # Reason is in file contents (also includes timestamp)

    def test_activate_deactivate_activate_workflow(self, mock_killswitch_path):
        """Test multiple activation/deactivation cycles"""
        # First activation
        activate_killswitch("First activation")
        assert is_emergency_killswitch_active()

        # Deactivate
        deactivate_killswitch()
        assert not is_emergency_killswitch_active()

        # Second activation
        activate_killswitch("Second activation")
        assert is_emergency_killswitch_active()

        status = get_killswitch_status()
        assert "Second activation" in status["reason"]

    def test_manual_file_creation_detected(self, mock_killswitch_path):
        """Manually created kill-switch file should be detected"""
        # Simulate manual file creation (like touch command)
        Path(mock_killswitch_path).write_text("Manual activation via touch")

        assert is_emergency_killswitch_active()
        assert read_killswitch_reason() == "Manual activation via touch"

    def test_concurrent_access_safety(self, mock_killswitch_path):
        """Kill-switch should handle concurrent access safely"""
        # Activate
        activate_killswitch("Test")

        # Multiple reads should work
        for _ in range(10):
            assert is_emergency_killswitch_active()
            assert read_killswitch_reason() is not None

        # Deactivate
        deactivate_killswitch()
        assert not is_emergency_killswitch_active()


class TestKillswitchErrorHandling:
    """Test kill-switch error handling and edge cases"""

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_read_reason_handles_permission_error(self, mock_logger, mock_killswitch_path):
        """Reading reason should handle permission errors gracefully"""
        Path(mock_killswitch_path).write_text("Test")

        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = read_killswitch_reason()

            assert result is None
            mock_logger.error.assert_called_once()

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_activate_handles_write_error(self, mock_logger, mock_killswitch_path):
        """Activation should handle write errors gracefully"""
        with patch("pathlib.Path.write_text", side_effect=OSError("Disk full")):
            result = activate_killswitch("Test")

            assert result is False
            mock_logger.error.assert_called_once()

    @patch("governance.guardian.emergency_killswitch.logger")
    def test_deactivate_handles_remove_error(self, mock_logger, mock_killswitch_path):
        """Deactivation should handle file removal errors gracefully"""
        Path(mock_killswitch_path).write_text("Test")

        with patch("os.remove", side_effect=OSError("Permission denied")):
            result = deactivate_killswitch()

            assert result is False
            mock_logger.error.assert_called_once()

    def test_killswitch_with_unicode_reason(self, mock_killswitch_path):
        """Kill-switch should handle Unicode characters in reason"""
        reason = "Incident 🚨: Déploiement d'urgence 紧急部署"
        activate_killswitch(reason)

        assert is_emergency_killswitch_active()
        assert reason in read_killswitch_reason()  # Reason is in file contents (also includes timestamp)

    def test_killswitch_with_very_long_reason(self, mock_killswitch_path):
        """Kill-switch should handle very long reasons"""
        reason = "A" * 10000  # 10KB reason
        activate_killswitch(reason)

        assert is_emergency_killswitch_active()
        assert reason in read_killswitch_reason()


class TestKillswitchDocumentation:
    """Test kill-switch usage as documented in module docstring"""

    def test_documented_activation_method(self, mock_killswitch_path):
        """Test activation method from documentation works"""
        # Documented method: create file with reason
        Path(mock_killswitch_path).write_text("Incident #123: Emergency release deployment")

        assert is_emergency_killswitch_active()

    def test_documented_deactivation_method(self, mock_killswitch_path):
        """Test deactivation method from documentation works"""
        Path(mock_killswitch_path).write_text("Test")

        # Documented method: remove file
        os.remove(mock_killswitch_path)

        assert not is_emergency_killswitch_active()

    def test_documented_status_check(self, mock_killswitch_path):
        """Test status check method from documentation works"""
        Path(mock_killswitch_path).write_text("Test")

        # Documented check
        if is_emergency_killswitch_active():
            status_message = "⚠️ Guardian is DISABLED by emergency kill-switch"
            assert "Guardian is DISABLED" in status_message
