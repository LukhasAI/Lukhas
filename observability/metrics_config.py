from typing import Optional

"""Lightweight metrics configuration for tests."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

__all__ = ["MetricsConfig"]


@dataclass
class MetricsConfig:
    namespace: str = "lukhas"
    subsystem: Optional[str] = None
    enabled_metrics: Optional[Sequence[str]] = None
