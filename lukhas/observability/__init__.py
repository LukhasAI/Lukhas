"""Bridge: lukhas.observability -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.observability",
    "labs.observability",
    "observability",
)
_bridge_all, _exports = bridge_from_candidates(*_CANDIDATES); globals().update(_exports)

# Ensure OTEL surfaces exist even when opentelemetry is not installed.
try:
    from .otel_compat import metrics, trace  # re-export for importers  # noqa: TID252 (relative imports in __init__.py are idiomatic)
except Exception:  # pragma: no cover
    trace = metrics = None  # type: ignore[assignment]

# Prometheus centralized registry & duplicate-tolerant factories
try:
    from .prometheus_registry import (  # noqa: TID252 (relative imports in __init__.py are idiomatic)
        LUKHAS_REGISTRY,
        counter,
        gauge,
        histogram,
        register_lukhas_metric,
        summary,
    )
except Exception:  # pragma: no cover
    LUKHAS_REGISTRY = None  # type: ignore
    def counter(*a, **k): return None  # type: ignore
    def gauge(*a, **k): return None  # type: ignore
    def histogram(*a, **k): return None  # type: ignore
    def summary(*a, **k): return None  # type: ignore
    def register_lukhas_metric(m): return m  # type: ignore

__all__ = list(_bridge_all) + [name for name in (
    "trace", "metrics",
    "LUKHAS_REGISTRY", "counter", "gauge", "histogram", "summary",
    "register_lukhas_metric",
) if name in globals()]
