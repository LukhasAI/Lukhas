import logging

logger = logging.getLogger(__name__)
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Security utilities for AGI Consolidation Repo
Provides secure alternatives to dangerous functions like exec(), eval(), subprocess.call()
"""

import ast
import os
import subprocess
from typing import Any, Optional

from candidate.core.common import LukhasError, get_logger

logger = get_logger(__name__)


class SecurityError(LukhasError):
    """Raised when a security check fails"""


def safe_eval(expression: str, allowed_names: Optional[dict[str, Any]] = None) -> Any:
    """
    Safely evaluate a Python expression using ast.literal_eval

    Args:
        expression: Python expression to evaluate
        allowed_names: Dictionary of allowed variable names and their values

    Returns:
        The evaluated result

    Raises:
        SecurityError: If the expression is not safe to evaluate
        ValueError: If the expression cannot be parsed
    """
    if allowed_names is None:
        allowed_names = {}

    try:
        # First try ast.literal_eval for literals
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        # For more complex expressions, parse and validate the AST
        try:
            tree = ast.parse(expression, mode="eval")
            if not _is_safe_ast(tree):
                raise SecurityError(f"Expression contains unsafe operations: {expression}")

            # Create a restricted environment
            safe_env = {
                "__builtins__": {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "abs": abs,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "round": round,
                },
                **allowed_names,
            }

            return eval(compile(tree, "<string>", "eval"), safe_env)
        except Exception as e:
            raise SecurityError(f"Failed to safely evaluate expression: {e}")


def _is_safe_ast(node: ast.AST) -> bool:
    """
    Check if an AST node is safe to evaluate

    Args:
        node: AST node to check

    Returns:
        True if the node is safe, False otherwise
    """
    # Define unsafe node types (compatible with Python 3.8+)
    unsafe_nodes = {
        ast.Import,
        ast.ImportFrom,
        ast.Call,
        ast.Attribute,
        ast.FunctionDef,
        ast.ClassDef,
        ast.Lambda,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    }

    # Add ast.Exec only if it exists (Python < 3.8)
    if hasattr(ast, "Exec"):
        unsafe_nodes.add(ast.Exec)

    for child in ast.walk(node):
        if type(child) in unsafe_nodes:
            return False

        # Check for dangerous built-in functions
        if isinstance(child, ast.Name) and child.id in {
            "exec",
            "eval",
            "compile",
            "open",
            "file",
            "input",
            "raw_input",
            "__import__",
            "reload",
            "vars",
            "globals",
            "locals",
            "dir",
            "getattr",
            "setattr",
            "delattr",
            "hasattr",
        }:
            return False

    return True


def safe_subprocess_run(
    command: list[str], check_command: bool = True, timeout: int = 30, **kwargs
) -> subprocess.CompletedProcess:
    """
    Safely run a subprocess command with security checks

    Args:
        command: List of command arguments
        check_command: Whether to validate the command
        timeout: Maximum execution time in seconds
        **kwargs: Additional arguments for subprocess.run

    Returns:
        CompletedProcess object

    Raises:
        SecurityError: If the command is not safe to run
    """
    if not isinstance(command, list):
        raise SecurityError("Command must be a list, not a string")

    if not command:
        raise SecurityError("Command cannot be empty")

    if check_command:
        _validate_command(command)

    # Set secure defaults
    secure_kwargs = {
        "check": True,
        "timeout": timeout,
        "capture_output": True,
        "text": True,
        "shell": False,  # Never use shell=True
        **kwargs,
    }

    try:
        logger.info(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, **secure_kwargs)
        return result
    except subprocess.TimeoutExpired:
        raise SecurityError(f"Command timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        raise SecurityError(f"Command failed with exit code {e.returncode}: {e.stderr}")
    except Exception as e:
        raise SecurityError(f"Unexpected error running command: {e}")


def _validate_command(command: list[str]) -> None:
    """
    Validate that a command is safe to run

    Args:
        command: List of command arguments

    Raises:
        SecurityError: If the command is not safe
    """
    if not command:
        raise SecurityError("Empty command")

    # List of allowed commands (whitelist approach)
    allowed_commands = {
        "git",
        "python",
        "python3",
        "pip",
        "pip3",
        "node",
        "npm",
        "yarn",
        "ls",
        "cat",
        "grep",
        "find",
        "head",
        "tail",
        "wc",
        "sort",
        "uniq",
        "echo",
        "date",
        "pwd",
        "whoami",
        "which",
        "type",
        "afplay",
        "say",  # Audio commands for the audio exporter
    }

    executable = command[0]

    # Check if it's an absolute path
    if os.path.isabs(executable):
        raise SecurityError(f"Absolute paths not allowed: {executable}")

    # Check if it's a relative path with directory traversal
    if "/" in executable or "\\" in executable:
        raise SecurityError(f"Path traversal not allowed: {executable}")

    # Check against whitelist
    if executable not in allowed_commands:
        raise SecurityError(f"Command not allowed: {executable}")

    # Check for dangerous arguments
    dangerous_args = {
        "--eval",
        "--exec",
        "-e",
        "-c",
        "--command",
        "|",
        ";",
        "&",
        "&&",
        "||",
        "$(",
        "`",
        "<",
        ">",
        ">>",
    }

    for arg in command[1:]:
        if any(dangerous in str(arg) for dangerous in dangerous_args):
            raise SecurityError(f"Dangerous argument detected: {arg}")


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        SecurityError: If input is too long or contains dangerous content
    """
    if len(input_str) > max_length:
        raise SecurityError(f"Input too long: {len(input_str)} > {max_length}")

    # Remove null bytes
    input_str = input_str.replace("\x00", "")

    # Check for dangerous patterns
    dangerous_patterns = [
        "$(",
        "`",
        "|",
        ";",
        "&",
        "&&",
        "||",
        "<script",
        "</script",
        "javascript:",
        "data:",
        "exec(",
        "eval(",
        "__import__",
    ]

    for pattern in dangerous_patterns:
        if pattern in input_str.lower():
            raise SecurityError(f"Dangerous pattern detected: {pattern}")

    return input_str


def secure_file_path(path: str, base_dir: str) -> str:
    """
    Ensure a file path is safe and within the base directory

    Args:
        path: File path to validate
        base_dir: Base directory to constrain to

    Returns:
        Validated absolute path

    Raises:
        SecurityError: If path is unsafe
    """
    # Resolve both paths
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(base_dir)

    # Check if the path is within base_dir
    if not abs_path.startswith(abs_base):
        raise SecurityError(f"Path outside base directory: {path}")

    # Check for dangerous characters
    if any(char in path for char in ["..", "~", "$", "`"]):
        raise SecurityError(f"Dangerous characters in path: {path}")

    return abs_path


def get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Safely get an environment variable

    Args:
        name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value

    Raises:
        SecurityError: If required variable is missing
    """
    value = os.getenv(name, default)

    if required and value is None:
        raise SecurityError(f"Required environment variable not set: {name}")

    return value