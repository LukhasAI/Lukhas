"""Advanced observability metrics that tolerate duplicate registration."""
from __future__ import annotations

from typing import Any, Callable

try:
    from prometheus_client import Counter, Gauge, Summary, REGISTRY
except Exception:  # pragma: no cover - prometheus unavailable
    class _Collector:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

        def __call__(self, *args: Any, **kwargs: Any) -> None:
            return None

    class Counter(_Collector):  # type: ignore[assignment]
        pass

    class Gauge(_Collector):  # type: ignore[assignment]
        pass

    class Summary(_Collector):  # type: ignore[assignment]
        pass

    class _Registry:
        _names_to_collectors: dict[str, Any] = {}

    REGISTRY = _Registry()  # type: ignore[assignment]


def _metric(factory: Callable[..., Any], name: str, documentation: str) -> Any:
    try:
        metric = factory(name, documentation)
    except ValueError as exc:
        # Defensively reuse existing collectors when duplicates are detected.
        existing = getattr(REGISTRY, "_names_to_collectors", {}).get(name)
        if existing is not None:
            return existing
        if "Duplicated timeseries" in str(exc):
            return None
        raise
    names = getattr(REGISTRY, "_names_to_collectors", None)
    if isinstance(names, dict):
        names.setdefault(name, metric)
    return metric


router_cascade_preventions_total = _metric(
    Counter,
    "router_cascade_preventions_total",
    "Number of signals blocked by cascade prevention",
)
network_coherence_score = _metric(
    Gauge,
    "network_coherence_score",
    "Current network coherence score (0-1)",
)
signal_processing_time_seconds = _metric(
    Summary,
    "signal_processing_time_seconds",
    "Time spent processing signals in router",
)

__all__ = [
    "router_cascade_preventions_total",
    "network_coherence_score",
    "signal_processing_time_seconds",
]
