"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


ΛBot Safe Execution Wrapper
===========================
Prevents system interference that causes VS Code logout issues
"""

import os
import subprocess
from typing import Any, Optional


class SafeSubprocessExecutor:
    """
    Safe subprocess executor that prevents system interference
    Isolates execution to prevent VS Code authentication issues
    """

    def __init__(self):
        self.timeout = 30
        self.isolated_env = self._create_isolated_env()

    def _create_isolated_env(self) -> dict[str, str]:
        """Create isolated environment variables"""
        # Start with minimal environment
        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", ""),
            "SHELL": os.environ.get("SHELL", "/bin/bash"),
            "TERM": "xterm",
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
        }

        # Add Python-specific vars but exclude auth-related ones
        python_vars = ["PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_DEFAULT_ENV"]
        for var in python_vars:
            if var in os.environ:
                safe_env[var] = os.environ[var]

        # Explicitly exclude potentially problematic variables

        return safe_env

    def safe_run(
        self,
        cmd: list[str],
        cwd: Optional[str] = None,
        env_vars: Optional[dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Safely run subprocess with isolation
        """
        timeout = timeout or self.timeout

        # Prepare environment
        exec_env = self.isolated_env.copy()
        if env_vars:
            exec_env.update(env_vars)

        try:
            # Create a process group to better control subprocess
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            return {
                "success": True,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "cmd": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "timeout": timeout,
                "cmd": " ".join(cmd),
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "command_not_found",
                "cmd": " ".join(cmd),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "cmd": " ".join(cmd)}

    def safe_python_run(
        self,
        script_path: str,
        args: Optional[list[str]] = None,
        cwd: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Safely run Python script with isolation
        """
        args = args or []
        cmd = ["python3", script_path, *args]

        # Use isolated Python environment
        python_env = {
            "PYTHONDONTWRITEBYTECODE": "1",  # Don't create .pyc files
            "PYTHONUNBUFFERED": "1",  # Unbuffered output
            "PYTHONISOLATED": "1",  # Isolated mode
        }

        return self.safe_run(cmd, cwd=cwd, env_vars=python_env)

    def safe_git_run(
        self, git_args: list[str], cwd: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Safely run git commands with isolation
        """
        cmd = ["git", *git_args]

        # Git-specific environment isolation
        git_env = {
            "GIT_TERMINAL_PROMPT": "0",  # Disable terminal prompts
            "GIT_ASKPASS": "echo",  # Disable password prompts
        }

        return self.safe_run(cmd, cwd=cwd, env_vars=git_env)


# Global safe executor instance
safe_executor = SafeSubprocessExecutor()


def safe_subprocess_run(*args, **kwargs) -> dict[str, Any]:
    """
    Drop-in replacement for subprocess.run that prevents VS Code logout
    """
    cmd = args[0] if isinstance(args[0], list) else list(args)

    cwd = kwargs.get("cwd")
    timeout = kwargs.get("timeout", 30)

    return safe_executor.safe_run(cmd, cwd=cwd, timeout=timeout)


def safe_python_execution(
    script_path: str, args: Optional[list[str]] = None, cwd: Optional[str] = None
) -> dict[str, Any]:
    """
    Safely execute Python scripts without system interference
    """
    return safe_executor.safe_python_run(script_path, args, cwd)
