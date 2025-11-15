"""Safe subprocess execution utilities to prevent shell injection vulnerabilities.

This module provides secure alternatives to subprocess.run(shell=True) and os.system()
that prevent command injection attacks.

Example usage:
    >>> from lukhas.security.safe_subprocess import safe_run_command
    >>> # Instead of: subprocess.run(f"echo {user_input}", shell=True)
    >>> result = safe_run_command(["echo", user_input])
    >>> print(result.stdout)
"""

import subprocess
import shlex
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SubprocessSecurityError(Exception):
    """Raised when subprocess security validation fails."""
    pass


def safe_run_command(
    command: Union[str, List[str]],
    cwd: Optional[Union[Path, str]] = None,
    timeout: Optional[int] = 30,
    capture_output: bool = True,
    check: bool = True,
    env: Optional[Dict[str, str]] = None,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Safely run a command without shell injection vulnerabilities.

    This function ensures commands are executed safely by:
    1. Never using shell=True
    2. Properly splitting string commands using shlex
    3. Passing commands as lists to subprocess
    4. Setting reasonable timeouts
    5. Validating command inputs

    Args:
        command: Command as string (will be split safely) or list of strings.
                 String example: "git status"
                 List example: ["git", "status"]
        cwd: Working directory for command execution
        timeout: Command timeout in seconds (default: 30, None for no timeout)
        capture_output: Capture stdout/stderr (default: True)
        check: Raise CalledProcessError on non-zero exit (default: True)
        env: Environment variables dictionary
        **kwargs: Additional subprocess.run arguments (except 'shell')

    Returns:
        subprocess.CompletedProcess object with stdout, stderr, returncode

    Raises:
        SubprocessSecurityError: If command validation fails or shell=True is passed
        subprocess.TimeoutExpired: If command exceeds timeout
        subprocess.CalledProcessError: If check=True and command returns non-zero

    Examples:
        >>> # Safe command execution
        >>> result = safe_run_command(["ls", "-la", "/tmp"])
        >>> result = safe_run_command("git status")
        >>>
        >>> # With user input (safe from injection)
        >>> user_file = "test.txt"
        >>> result = safe_run_command(["cat", user_file])
        >>>
        >>> # Without timeout
        >>> result = safe_run_command(["long-running-cmd"], timeout=None)
    """
    # Convert string command to list (safe splitting)
    if isinstance(command, str):
        command_list = shlex.split(command)
    else:
        command_list = list(command)  # Make a copy to avoid modifying original

    # Validate command list
    if not command_list:
        raise SubprocessSecurityError("Empty command provided")

    if not all(isinstance(arg, str) for arg in command_list):
        raise SubprocessSecurityError(
            f"All command arguments must be strings, got: {command_list}"
        )

    # Never allow shell=True
    if 'shell' in kwargs:
        if kwargs['shell']:
            raise SubprocessSecurityError(
                "shell=True is not allowed. Use safe_run_command with a list of arguments instead."
            )
        # Remove shell=False if explicitly passed
        kwargs.pop('shell')

    # Convert cwd to string if Path object
    if isinstance(cwd, Path):
        cwd = str(cwd)

    logger.debug(f"Running command: {command_list}")

    try:
        return subprocess.run(
            command_list,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=check,
            env=env,
            shell=False,  # Explicitly set shell=False for clarity
            **kwargs
        )
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {command_list}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {command_list}")
        raise
    except Exception as e:
        logger.error(f"Command execution failed: {command_list}, error: {e}")
        raise


def safe_run_with_shell_check(
    command_str: str,
    allow_pipes: bool = False,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Run command with automatic shell character detection and validation.

    This function provides an extra layer of security by detecting dangerous
    shell characters that might indicate an injection attempt. Use this when
    you're accepting command strings from potentially untrusted sources.

    Args:
        command_str: Command string to execute (will be validated)
        allow_pipes: Whether to allow pipe (|) character (default: False)
        **kwargs: Additional arguments passed to safe_run_command

    Returns:
        subprocess.CompletedProcess object

    Raises:
        SubprocessSecurityError: If dangerous shell characters detected

    Examples:
        >>> # Safe command
        >>> result = safe_run_with_shell_check("ls -la")
        >>>
        >>> # This will raise SubprocessSecurityError
        >>> result = safe_run_with_shell_check("ls; rm -rf /")  # BLOCKED
    """
    dangerous_chars = [
        (';', 'command separator'),
        ('&', 'background/chain operator'),
        ('$(', 'command substitution'),
        ('`', 'command substitution'),
        ('>', 'output redirection'),
        ('<', 'input redirection'),
        ('\n', 'newline injection'),
        ('||', 'OR operator'),
        ('&&', 'AND operator'),
    ]

    if not allow_pipes:
        dangerous_chars.append(('|', 'pipe operator'))

    for char, description in dangerous_chars:
        if char in command_str:
            raise SubprocessSecurityError(
                f"Dangerous shell character detected: '{char}' ({description}). "
                f"This may indicate a shell injection attempt. "
                f"Command: {command_str[:100]}"
            )

    return safe_run_command(command_str, **kwargs)


def safe_popen(
    command: Union[str, List[str]],
    **kwargs
) -> subprocess.Popen:
    """
    Safely create a Popen object without shell injection vulnerabilities.

    Similar to safe_run_command but returns a Popen object for streaming
    or interactive command execution.

    Args:
        command: Command as string or list
        **kwargs: Arguments passed to subprocess.Popen (except 'shell')

    Returns:
        subprocess.Popen object

    Raises:
        SubprocessSecurityError: If validation fails

    Examples:
        >>> # Safe Popen usage
        >>> proc = safe_popen(["python", "script.py"])
        >>> stdout, stderr = proc.communicate()
    """
    # Convert string command to list
    if isinstance(command, str):
        command_list = shlex.split(command)
    else:
        command_list = list(command)

    # Validate command list
    if not command_list:
        raise SubprocessSecurityError("Empty command provided")

    # Never allow shell=True
    if 'shell' in kwargs:
        if kwargs['shell']:
            raise SubprocessSecurityError(
                "shell=True is not allowed. Use safe_popen with a list of arguments."
            )
        kwargs.pop('shell')

    logger.debug(f"Creating Popen for command: {command_list}")

    return subprocess.Popen(
        command_list,
        shell=False,
        **kwargs
    )


# Backwards compatibility and convenience aliases
run_safe = safe_run_command
popen_safe = safe_popen
