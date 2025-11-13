"""Exception definitions for QI security operations."""

from __future__ import annotations

from typing import Any


class SecurityException(RuntimeError):
    """Raised when a security policy violation or integrity failure occurs."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})

    def __repr__(self) -> str:
        base = super().__repr__()
        if not (self.code or self.details):
            return base

        suffix = ")" if base.endswith(")") else ""
        base_without_suffix = base[:-1] if suffix else base
        return (
            f"{base_without_suffix}, code={self.code!r}, details={self.details!r}{suffix}"
        )
