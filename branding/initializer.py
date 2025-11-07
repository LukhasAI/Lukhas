"""Branding initialization helpers used in tests."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Dict

try:
    from branding import APPROVED_TERMS as _APPROVED_TERMS  # type: ignore
except Exception:
    _APPROVED_TERMS: Iterable[str] = ()

try:
    from branding import SYSTEM_NAME as _SYSTEM_NAME  # type: ignore
except Exception:
    _SYSTEM_NAME = "LUKHAS"


def initialize_branding(**overrides: Any) -> dict[str, Any]:
    """Ensure branding globals exist and optionally override them."""

    global APPROVED_TERMS, SYSTEM_NAME  # type: ignore[assignment]

    APPROVED_TERMS = list(_APPROVED_TERMS)
    SYSTEM_NAME = _SYSTEM_NAME

    for key, value in overrides.items():
        globals()[key] = value

    return {
        key: globals()[key]
        for key in ("APPROVED_TERMS", "SYSTEM_NAME")
        if key in globals()
    }


__all__ = ["initialize_branding"]
