"""Security utility helpers for the legacy security stack."""

from __future__ import annotations

import ast
import html
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Optional, Sequence

logger = logging.getLogger("ΛTRACE.products.legacy.security.utils")


class SecurityError(RuntimeError):
    """Raised when a potentially unsafe security operation is attempted."""


# ΛTAG: sanitize_input_guardian
_DANGEROUS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"eval\s*\(",
    r"exec\s*\(",
]


def sanitize_input(value: Any) -> str:
    """Return a sanitized representation of user-controlled data."""

    if not isinstance(value, str):
        value = str(value)

    sanitized = value
    for pattern in _DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    return html.escape(sanitized)


# ΛTAG: safe_eval_guardian
def safe_eval(expression: str, allowed_literals: Optional[Mapping[str, Any]] = None) -> Any:
    """Safely evaluate literal expressions with optional whitelisted names."""

    if not isinstance(expression, str):
        raise SecurityError("Expression must be a string")

    expression = expression.strip()
    try:
        return ast.literal_eval(expression)
    except (ValueError, SyntaxError) as exc:
        if allowed_literals and expression in allowed_literals:
            return allowed_literals[expression]
        raise SecurityError("Unsafe expression rejected") from exc


_UNSAFE_SUBPROCESS_CHARS = {";", "|", "&", ">", "<", "$", "`"}


# ΛTAG: safe_subprocess_guardian
def safe_subprocess_run(
    command: Sequence[str],
    *,
    timeout: int = 10,
    check: bool = True,
    cwd: Optional[Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with defensive checks to prevent command injection."""

    if isinstance(command, (str, bytes)):
        raise SecurityError("Commands must be provided as a sequence of arguments")

    if not command:
        raise SecurityError("Cannot execute empty command")

    sanitized_command = []
    for part in command:
        if not isinstance(part, str):
            raise SecurityError("Command arguments must be strings")
        if any(symbol in part for symbol in _UNSAFE_SUBPROCESS_CHARS):
            raise SecurityError(f"Unsafe shell metacharacter detected in argument: {part}")
        sanitized_command.append(part)

    logger.debug(
        "Executing secured subprocess",
        extra={"command": sanitized_command, "cwd": str(cwd) if cwd else None},
    )

    sanitized_env: Optional[MutableMapping[str, str]] = None
    if env is not None:
        sanitized_env = {str(key): str(value) for key, value in env.items()}

    return subprocess.run(  # noqa: PLW1510 - we intentionally surface exceptions to callers
        sanitized_command,
        check=check,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        env=sanitized_env,
        timeout=timeout,
    )


__all__ = [
    "SecurityError",
    "safe_eval",
    "safe_subprocess_run",
    "sanitize_input",
]
