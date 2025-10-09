"""LUKHAS observability service metrics."""
from __future__ import annotations

from enum import Enum


class MetricType(Enum):
    """Types of metrics collected by LUKHAS services."""

    PERFORMANCE = "performance"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    SAFETY = "safety"
    TRINITY = "trinity"


__all__ = ["MetricType"]
