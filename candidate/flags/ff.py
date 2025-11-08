"""Simplified feature flag client for candidate tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(slots=True)
class Flags:
    """Minimal feature flag facade to unblock candidate level tests."""

    _enabled: ClassVar[set[str]] = set()

    @classmethod
    def enable(cls, flag: str) -> None:
        cls._enabled.add(flag)

    @classmethod
    def disable(cls, flag: str) -> None:
        cls._enabled.discard(flag)

    @classmethod
    def is_enabled(cls, flag: str) -> bool:
        return flag in cls._enabled
