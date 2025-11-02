"""Lightweight metrics configuration for tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from collections.abc import Sequence

__all__ = ["MetricsConfig"]


@dataclass
class MetricsConfig:
    namespace: str = "lukhas"
    subsystem: Optional[str] = None
    enabled_metrics: Optional[Sequence[str]] = None
