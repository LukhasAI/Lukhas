"""
Comprehensive tests for the Troubleshooting Assistant CLI.

Tests diagnostic checks, issue detection, and reporting functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import socket
import subprocess

from lukhas.cli.troubleshoot import TroubleshootAssistant, main


@pytest.fixture
def assistant():
    """Fresh TroubleshootAssistant instance."""
    with patch('lukhas.cli.troubleshoot.HAS_RICH', False):
        return TroubleshootAssistant()


@pytest.fixture
def assistant_with_rich():
    """TroubleshootAssistant instance with rich enabled."""
    with patch('lukhas.cli.troubleshoot.HAS_RICH', True):
        from rich.console import Console
        assistant = TroubleshootAssistant()
        assistant.console = Console()
        return assistant


class TestInitialization:
    """Test TroubleshootAssistant initialization."""

    def test_init_without_rich(self, assistant):
        """Test initialization when rich is not available."""
        assert assistant.console is None
        assert assistant.project_root.name == "Lukhas"
        assert assistant.issues_found == []

    def test_init_with_rich(self):
        """Test initialization when rich is available."""
        with patch('lukhas.cli.troubleshoot.HAS_RICH', True):
            assistant = TroubleshootAssistant()
            assert assistant.console is not None

    def test_project_root_detection(self, assistant):
        """Test that project root is detected correctly."""
        # Project root should be 3 levels up from the script
        assert isinstance(assistant.project_root, Path)


class TestPrintMethod:
    """Test the print method wrapper."""

    def test_print_without_rich(self, assistant):
        """Test print falls back to built-in when no rich."""
        with patch('builtins.print') as mock_print:
            assistant.print("Test message")
            mock_print.assert_called_once_with("Test message")

    def test_print_with_rich(self, assistant_with_rich):
        """Test print uses rich console when available."""
        with patch.object(assistant_with_rich.console, 'print') as mock_print:
            assistant_with_rich.print("Test message")
            mock_print.assert_called_once_with("Test message")


class TestPythonVersionCheck:
    """Test Python version checking."""

    def test_python_version_compatible(self, assistant):
        """Test with compatible Python version (3.9+)."""
        assistant.check_python_version()
        # Should not add any issues for Python 3.9+
        errors = [i for i in assistant.issues_found if i["severity"] == "error"]
        assert len(errors) == 0

    @patch('sys.version_info', (3, 8, 0))
    def test_python_version_incompatible(self, assistant):
        """Test with incompatible Python version."""
        assistant.check_python_version()
        # Should add an error for Python 3.8
        errors = [i for i in assistant.issues_found if i["severity"] == "error"]
        assert len(errors) == 1
        assert "Python 3.8" in errors[0]["issue"]
        assert "3.9+ required" in errors[0]["issue"]

    @patch('sys.version_info', (3, 11, 5))
    def test_python_version_newer(self, assistant):
        """Test with newer Python version."""
        assistant.check_python_version()
        errors = [i for i in assistant.issues_found if i["severity"] == "error"]
        assert len(errors) == 0


class TestDependenciesCheck:
    """Test dependencies checking."""

    def test_check_dependencies_no_requirements_file(self, assistant):
        """Test when requirements.txt doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            assistant.check_dependencies()
        # Should print warning but not add critical issue

    def test_check_dependencies_no_venv(self, assistant):
        """Test when virtual environment doesn't exist."""
        with patch.object(Path, 'exists', side_effect=[True, False]):
            assistant.check_dependencies()

        warnings = [i for i in assistant.issues_found if i["severity"] == "warning"]
        assert any("Virtual environment not found" in w["issue"] for w in warnings)

    def test_check_dependencies_venv_exists(self, assistant):
        """Test when virtual environment exists."""
        with patch.object(Path, 'exists', return_value=True):
            assistant.check_dependencies()

        warnings = [i for i in assistant.issues_found if "Virtual environment" in i["issue"]]
        assert len(warnings) == 0


class TestPortConflictsCheck:
    """Test port conflict detection."""

    def test_port_available(self, assistant):
        """Test when port is available."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            mock_sock.connect_ex.return_value = 1  # Connection refused (port available)
            mock_socket.return_value = mock_sock

            assistant.check_port_conflicts()

            errors = [i for i in assistant.issues_found if "Port" in i["issue"]]
            assert len(errors) == 0

    def test_port_8000_in_use(self, assistant):
        """Test when port 8000 is in use."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            # Port 8000 in use (returns 0), others available (returns 1)
            mock_sock.connect_ex.side_effect = [0, 1, 1]
            mock_socket.return_value = mock_sock

            assistant.check_port_conflicts()

            errors = [i for i in assistant.issues_found if i["severity"] == "error"]
            assert any("Port 8000" in e["issue"] for e in errors)

    def test_other_ports_in_use_info_only(self, assistant):
        """Test when PostgreSQL/Redis ports are in use (info only)."""
        with patch('socket.socket') as mock_socket:
            mock_sock = Mock()
            # Port 8000 available, 5432 and 6379 in use
            mock_sock.connect_ex.side_effect = [1, 0, 0]
            mock_socket.return_value = mock_sock

            assistant.check_port_conflicts()

            # Should not add errors for non-8000 ports
            errors = [i for i in assistant.issues_found if i["severity"] == "error"]
            port_errors = [e for e in errors if "Port" in e["issue"]]
            assert len(port_errors) == 0


class TestDockerCheck:
    """Test Docker availability checking."""

    def test_docker_not_installed(self, assistant):
        """Test when Docker is not installed."""
        with patch('shutil.which', return_value=None):
            assistant.check_docker()
        # Should print warning but not add issue (optional)

    def test_docker_running(self, assistant):
        """Test when Docker is running."""
        with patch('shutil.which', return_value="/usr/bin/docker"):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0)
                assistant.check_docker()

        warnings = [i for i in assistant.issues_found if "Docker" in i["issue"]]
        assert len(warnings) == 0

    def test_docker_not_running(self, assistant):
        """Test when Docker is installed but not running."""
        with patch('shutil.which', return_value="/usr/bin/docker"):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1)
                assistant.check_docker()

        warnings = [i for i in assistant.issues_found if i["severity"] == "warning"]
        assert any("Docker installed but not running" in w["issue"] for w in warnings)

    def test_docker_check_timeout(self, assistant):
        """Test when Docker check times out."""
        with patch('shutil.which', return_value="/usr/bin/docker"):
            with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("docker", 5)):
                assistant.check_docker()
        # Should handle timeout gracefully

    def test_docker_check_exception(self, assistant):
        """Test when Docker check raises exception."""
        with patch('shutil.which', return_value="/usr/bin/docker"):
            with patch('subprocess.run', side_effect=Exception("Test error")):
                assistant.check_docker()
        # Should handle exception gracefully


class TestEnvFileCheck:
    """Test environment file checking."""

    def test_env_file_missing(self, assistant):
        """Test when .env file doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            assistant.check_env_file()

        errors = [i for i in assistant.issues_found if i["severity"] == "error"]
        assert any(".env file not found" in e["issue"] for e in errors)

    def test_env_file_exists_with_required_vars(self, assistant):
        """Test when .env file exists with all required variables."""
        env_content = "DATABASE_URL=sqlite:///lukhas.db\nSECRET_KEY=test-key\n"

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=env_content):
                assistant.check_env_file()

        warnings = [i for i in assistant.issues_found if "Missing environment variable" in i["issue"]]
        assert len(warnings) == 0

    def test_env_file_missing_required_vars(self, assistant):
        """Test when .env file is missing required variables."""
        env_content = "SOME_OTHER_VAR=value\n"

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=env_content):
                assistant.check_env_file()

        warnings = [i for i in assistant.issues_found if i["severity"] == "warning"]
        missing_vars = [w for w in warnings if "Missing environment variable" in w["issue"]]
        assert len(missing_vars) == 2  # DATABASE_URL and SECRET_KEY


class TestDatabaseCheck:
    """Test database checking."""

    def test_database_exists(self, assistant):
        """Test when database file exists."""
        with patch.object(Path, 'exists', return_value=True):
            assistant.check_database()
        # Should not add any issues

    def test_database_not_exists(self, assistant):
        """Test when database file doesn't exist."""
        with patch.object(Path, 'exists', return_value=False):
            assistant.check_database()
        # Should print info but not add error (initialization expected)


class TestRunDiagnostics:
    """Test the main diagnostics runner."""

    def test_run_all_diagnostics(self, assistant):
        """Test running all diagnostic checks."""
        with patch.object(assistant, 'check_python_version'):
            with patch.object(assistant, 'check_dependencies'):
                with patch.object(assistant, 'check_port_conflicts'):
                    with patch.object(assistant, 'check_docker'):
                        with patch.object(assistant, 'check_env_file'):
                            with patch.object(assistant, 'check_database'):
                                with patch.object(assistant, 'print_summary'):
                                    assistant.run_diagnostics()

                                    # Verify all checks were called
                                    assistant.check_python_version.assert_called_once()
                                    assistant.check_dependencies.assert_called_once()
                                    assistant.check_port_conflicts.assert_called_once()
                                    assistant.check_docker.assert_called_once()
                                    assistant.check_env_file.assert_called_once()
                                    assistant.check_database.assert_called_once()
                                    assistant.print_summary.assert_called_once()

    def test_run_diagnostics_handles_exceptions(self, assistant):
        """Test that diagnostics continue even if a check fails."""
        with patch.object(assistant, 'check_python_version', side_effect=Exception("Test error")):
            with patch.object(assistant, 'check_dependencies'):
                with patch.object(assistant, 'check_port_conflicts'):
                    with patch.object(assistant, 'check_docker'):
                        with patch.object(assistant, 'check_env_file'):
                            with patch.object(assistant, 'check_database'):
                                with patch.object(assistant, 'print_summary'):
                                    assistant.run_diagnostics()
                                    # Should still call all other checks
                                    assistant.check_dependencies.assert_called_once()


class TestPrintSummary:
    """Test summary printing."""

    def test_print_summary_no_issues(self, assistant):
        """Test summary when no issues found."""
        assistant.print_summary()
        # Should print success message

    def test_print_summary_with_errors(self, assistant):
        """Test summary with error issues."""
        assistant.issues_found = [
            {
                "severity": "error",
                "issue": "Test error",
                "fix": "Fix it",
                "command": "fix-command",
            }
        ]
        assistant.print_summary()
        # Should categorize and print errors

    def test_print_summary_with_warnings(self, assistant):
        """Test summary with warning issues."""
        assistant.issues_found = [
            {
                "severity": "warning",
                "issue": "Test warning",
                "fix": "Fix it",
                "command": "fix-command",
            }
        ]
        assistant.print_summary()
        # Should categorize and print warnings

    def test_print_summary_mixed_issues(self, assistant):
        """Test summary with both errors and warnings."""
        assistant.issues_found = [
            {
                "severity": "error",
                "issue": "Error 1",
                "fix": "Fix 1",
                "command": "cmd1",
            },
            {
                "severity": "warning",
                "issue": "Warning 1",
                "fix": "Fix 2",
                "command": "cmd2",
            },
            {
                "severity": "error",
                "issue": "Error 2",
                "fix": "Fix 3",
                "command": "cmd3",
            },
        ]
        assistant.print_summary()
        # Should print 2 errors and 1 warning


class TestPrintIssue:
    """Test individual issue printing."""

    def test_print_issue_without_rich(self, assistant):
        """Test printing issue without rich."""
        issue = {
            "severity": "error",
            "issue": "Test issue",
            "fix": "Test fix",
            "command": "test-command",
        }
        with patch.object(assistant, 'print') as mock_print:
            assistant.print_issue(1, issue)
            assert mock_print.call_count > 0

    def test_print_issue_with_rich(self, assistant_with_rich):
        """Test printing issue with rich."""
        issue = {
            "severity": "error",
            "issue": "Test issue",
            "fix": "Test fix",
            "command": "test-command",
        }
        with patch.object(assistant_with_rich, 'print') as mock_print:
            assistant_with_rich.print_issue(1, issue)
            assert mock_print.call_count > 0

    def test_print_issue_warning_color(self, assistant):
        """Test that warnings use yellow color."""
        issue = {
            "severity": "warning",
            "issue": "Test warning",
            "fix": "Test fix",
            "command": "test-command",
        }
        with patch.object(assistant, 'print'):
            assistant.print_issue(1, issue)
            # Should use yellow for warnings


class TestMainFunction:
    """Test the main entry point."""

    def test_main_runs_diagnostics(self):
        """Test that main function creates assistant and runs diagnostics."""
        with patch('lukhas.cli.troubleshoot.TroubleshootAssistant') as mock_class:
            mock_assistant = Mock()
            mock_class.return_value = mock_assistant

            main()

            mock_assistant.run_diagnostics.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_multiple_check_calls(self, assistant):
        """Test that checks can be called multiple times."""
        assistant.check_python_version()
        assistant.check_python_version()
        # Should not raise errors

    def test_issues_accumulate(self, assistant):
        """Test that issues accumulate across checks."""
        with patch.object(Path, 'exists', return_value=False):
            assistant.check_env_file()
            assistant.check_database()

        # Should have issues from both checks
        assert len(assistant.issues_found) >= 1

    def test_socket_exception_handling(self, assistant):
        """Test handling of socket exceptions during port check."""
        with patch('socket.socket', side_effect=Exception("Socket error")):
            try:
                assistant.check_port_conflicts()
            except Exception:
                pytest.fail("Port check should handle socket exceptions")

    def test_empty_env_file(self, assistant):
        """Test handling of empty .env file."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value=""):
                assistant.check_env_file()

        # Should detect missing required vars
        warnings = [i for i in assistant.issues_found if "Missing environment variable" in i["issue"]]
        assert len(warnings) == 2

    def test_subprocess_run_with_stderr(self, assistant):
        """Test Docker check with stderr output."""
        with patch('shutil.which', return_value="/usr/bin/docker"):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="Error message"
                )
                assistant.check_docker()

        # Should handle stderr gracefully
        warnings = [i for i in assistant.issues_found if "Docker" in i["issue"]]
        assert len(warnings) > 0


class TestIntegration:
    """Integration tests for full diagnostic runs."""

    def test_full_diagnostic_run_clean_system(self):
        """Test full diagnostic run on a clean system."""
        assistant = TroubleshootAssistant()

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'read_text', return_value="DATABASE_URL=test\nSECRET_KEY=test\n"):
                with patch('socket.socket') as mock_socket:
                    mock_sock = Mock()
                    mock_sock.connect_ex.return_value = 1  # All ports available
                    mock_socket.return_value = mock_sock
                    with patch('shutil.which', return_value=None):  # Docker not installed
                        assistant.run_diagnostics()

        # Should have minimal issues (maybe Docker warning)
        errors = [i for i in assistant.issues_found if i["severity"] == "error"]
        assert len(errors) == 0

    def test_full_diagnostic_run_problematic_system(self):
        """Test full diagnostic run on a system with issues."""
        with patch('lukhas.cli.troubleshoot.HAS_RICH', False):
            assistant = TroubleshootAssistant()

        with patch.object(Path, 'exists', return_value=False):  # No env, no venv, no db
            with patch('socket.socket') as mock_socket:
                mock_sock = Mock()
                mock_sock.connect_ex.return_value = 0  # All ports in use
                mock_socket.return_value = mock_sock
                with patch('shutil.which', return_value=None):
                    assistant.run_diagnostics()

        # Should have multiple issues
        assert len(assistant.issues_found) > 0
