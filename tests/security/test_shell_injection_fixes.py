"""
Comprehensive security tests for shell injection fixes.

Tests the safe_subprocess module and verifies that shell injection
vulnerabilities have been properly mitigated across the codebase.
"""

import pytest
import subprocess
from pathlib import Path

from lukhas.security.safe_subprocess import (
    safe_run_command,
    safe_run_with_shell_check,
    safe_popen,
    SubprocessSecurityError,
)


class TestSafeRunCommand:
    """Test safe_run_command function."""

    def test_simple_command_list(self):
        """Test running a simple command with list arguments."""
        result = safe_run_command(["echo", "hello"])
        assert "hello" in result.stdout
        assert result.returncode == 0

    def test_simple_command_string(self):
        """Test running a simple command from string (safely split)."""
        result = safe_run_command("echo world")
        assert "world" in result.stdout
        assert result.returncode == 0

    def test_command_with_arguments(self):
        """Test command with multiple arguments."""
        result = safe_run_command(["echo", "hello", "world", "test"])
        output = result.stdout.strip()
        assert "hello" in output
        assert "world" in output
        assert "test" in output

    def test_blocks_shell_parameter(self):
        """Ensure shell=True parameter is blocked."""
        with pytest.raises(SubprocessSecurityError, match="shell.*not allowed"):
            safe_run_command(["echo", "test"], shell=True)

    def test_empty_command_raises_error(self):
        """Empty command should raise an error."""
        with pytest.raises(SubprocessSecurityError, match="Empty command"):
            safe_run_command([])

        with pytest.raises(SubprocessSecurityError, match="Empty command"):
            safe_run_command("")

    def test_shell_injection_prevention(self):
        """Verify that shell injection attempts are treated as literals."""
        # These malicious strings should be treated as literal arguments
        # and not executed as shell commands
        malicious_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami",
            "$(malicious command)",
            "`whoami`",
        ]

        for malicious in malicious_inputs:
            # When passed as argument to echo, they're treated as literals
            result = safe_run_command(["echo", malicious])
            # The malicious string appears literally in output
            assert malicious in result.stdout

    def test_timeout_parameter(self):
        """Test that timeout parameter works."""
        # This should complete quickly
        result = safe_run_command(["echo", "test"], timeout=5)
        assert result.returncode == 0

        # This should timeout
        with pytest.raises(subprocess.TimeoutExpired):
            safe_run_command(["sleep", "10"], timeout=1)

    def test_check_parameter(self):
        """Test that check parameter works correctly."""
        # Successful command with check=True
        result = safe_run_command(["true"], check=True)
        assert result.returncode == 0

        # Failed command with check=True should raise
        with pytest.raises(subprocess.CalledProcessError):
            safe_run_command(["false"], check=True)

        # Failed command with check=False should not raise
        result = safe_run_command(["false"], check=False)
        assert result.returncode != 0

    def test_capture_output(self):
        """Test capture_output parameter."""
        result = safe_run_command(["echo", "captured"], capture_output=True)
        assert "captured" in result.stdout

    def test_working_directory(self):
        """Test cwd parameter."""
        result = safe_run_command(["pwd"], cwd="/tmp")
        assert "/tmp" in result.stdout

    def test_environment_variables(self):
        """Test env parameter."""
        env = {"TEST_VAR": "test_value"}
        result = safe_run_command(["sh", "-c", "echo $TEST_VAR"], env=env)
        assert "test_value" in result.stdout


class TestSafeRunWithShellCheck:
    """Test safe_run_with_shell_check function."""

    def test_safe_command_passes(self):
        """Safe commands should work normally."""
        result = safe_run_with_shell_check("echo hello")
        assert "hello" in result.stdout

    def test_detects_semicolon(self):
        """Should detect and block semicolon separator."""
        with pytest.raises(SubprocessSecurityError, match="command separator"):
            safe_run_with_shell_check("ls; rm -rf /")

    def test_detects_pipe(self):
        """Should detect and block pipe operator."""
        with pytest.raises(SubprocessSecurityError, match="pipe operator"):
            safe_run_with_shell_check("cat file | grep password")

    def test_detects_ampersand(self):
        """Should detect and block ampersand operators."""
        with pytest.raises(SubprocessSecurityError, match="background/chain operator"):
            safe_run_with_shell_check("ls & whoami")

        with pytest.raises(SubprocessSecurityError, match="AND operator"):
            safe_run_with_shell_check("ls && whoami")

    def test_detects_command_substitution(self):
        """Should detect and block command substitution."""
        with pytest.raises(SubprocessSecurityError, match="command substitution"):
            safe_run_with_shell_check("echo $(whoami)")

        with pytest.raises(SubprocessSecurityError, match="command substitution"):
            safe_run_with_shell_check("echo `whoami`")

    def test_detects_redirection(self):
        """Should detect and block I/O redirection."""
        with pytest.raises(SubprocessSecurityError, match="output redirection"):
            safe_run_with_shell_check("echo test > /tmp/file")

        with pytest.raises(SubprocessSecurityError, match="input redirection"):
            safe_run_with_shell_check("cat < /etc/passwd")

    def test_detects_newline_injection(self):
        """Should detect and block newline injection."""
        with pytest.raises(SubprocessSecurityError, match="newline injection"):
            safe_run_with_shell_check("echo test\nrm -rf /")

    def test_allow_pipes_parameter(self):
        """Test allow_pipes parameter."""
        # Pipe should be blocked by default
        with pytest.raises(SubprocessSecurityError):
            safe_run_with_shell_check("ls | grep test")

        # Pipe should be allowed when allow_pipes=True
        # Note: This will still fail to execute properly without shell,
        # but it won't raise SubprocessSecurityError
        try:
            safe_run_with_shell_check("ls | grep test", allow_pipes=True)
        except subprocess.CalledProcessError:
            # Expected to fail since pipe won't work without shell
            pass


class TestSafePopen:
    """Test safe_popen function."""

    def test_simple_popen(self):
        """Test basic Popen usage."""
        proc = safe_popen(["echo", "test"])
        stdout, stderr = proc.communicate()
        assert b"test" in stdout
        assert proc.returncode == 0

    def test_blocks_shell_parameter(self):
        """Ensure shell=True is blocked in Popen."""
        with pytest.raises(SubprocessSecurityError, match="shell.*not allowed"):
            safe_popen(["echo", "test"], shell=True)

    def test_popen_string_split(self):
        """Test that string commands are safely split."""
        proc = safe_popen("echo hello world")
        stdout, stderr = proc.communicate()
        assert b"hello" in stdout
        assert b"world" in stdout


class TestCodebaseSecurity:
    """Tests to verify the codebase is free of shell injection vulnerabilities."""

    def test_no_subprocess_shell_true_in_production(self):
        """Verify no subprocess.run(shell=True) in production code."""
        import subprocess
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        vulnerable_files = []

        # Exclude archive, tests, and __pycache__
        for py_file in repo_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in ["archive", "tests", "__pycache__", ".pyc"]):
                continue

            try:
                content = py_file.read_text()
                if "shell=True" in content and "subprocess" in content:
                    # Check if it's actually in a subprocess call
                    if "subprocess.run" in content or "subprocess.Popen" in content or "subprocess.call" in content:
                        vulnerable_files.append(str(py_file.relative_to(repo_root)))
            except Exception:
                continue

        assert len(vulnerable_files) == 0, f"Found shell=True in production files: {vulnerable_files}"

    def test_no_os_system_in_production(self):
        """Verify no os.system() calls in production code."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        vulnerable_files = []

        # Exclude archive, tests, and __pycache__
        for py_file in repo_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in ["archive", "tests", "__pycache__", ".pyc"]):
                continue

            try:
                content = py_file.read_text()
                if "os.system" in content:
                    vulnerable_files.append(str(py_file.relative_to(repo_root)))
            except Exception:
                continue

        assert len(vulnerable_files) == 0, f"Found os.system() in production files: {vulnerable_files}"

    def test_safe_subprocess_imported_where_needed(self):
        """Verify safe_subprocess is imported in files that run commands."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        files_needing_import = []

        for py_file in repo_root.rglob("*.py"):
            if any(exclude in str(py_file) for exclude in ["archive", "tests", "__pycache__", ".pyc", "lukhas/security"]):
                continue

            try:
                content = py_file.read_text()
                has_subprocess = "subprocess.run" in content or "subprocess.Popen" in content
                has_safe_import = "from lukhas.security.safe_subprocess import" in content

                if has_subprocess and not has_safe_import:
                    # Check if it's using safe_run_command
                    if "safe_run_command" not in content:
                        files_needing_import.append(str(py_file.relative_to(repo_root)))
            except Exception:
                continue

        # This is informational - some files might legitimately use subprocess directly
        if files_needing_import:
            print(f"Files using subprocess without safe_subprocess import: {files_needing_import}")


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_git_command(self):
        """Test safe execution of git command."""
        try:
            result = safe_run_command(["git", "--version"])
            assert result.returncode == 0
            assert "git version" in result.stdout
        except FileNotFoundError:
            pytest.skip("git not installed")

    def test_python_command(self):
        """Test safe execution of Python command."""
        result = safe_run_command(["python3", "-c", "print('hello')"])
        assert "hello" in result.stdout

    def test_user_input_safety(self):
        """Test that user input is safely handled."""
        # Simulate user providing malicious input
        user_input = "; rm -rf /"

        # This is safe - user input is treated as literal argument
        result = safe_run_command(["echo", user_input])
        assert user_input in result.stdout
        # The semicolon and commands after it are just echoed, not executed

    def test_filename_with_spaces(self):
        """Test handling files with spaces in names."""
        result = safe_run_command(["echo", "file with spaces.txt"])
        assert "file with spaces.txt" in result.stdout

    def test_special_characters_in_arguments(self):
        """Test that special characters in arguments are handled safely."""
        special_chars = ["$HOME", "~", "*", "?", "[test]", "{a,b}"]

        for char in special_chars:
            result = safe_run_command(["echo", char])
            # Characters are treated literally, not expanded
            assert char in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
