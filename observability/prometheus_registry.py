"""LUKHAS Prometheus registry (duplicate-tolerant wrappers).

Single shared CollectorRegistry + cached factory functions that avoid
`ValueError: Duplicated timeseries` during pytest collection or repeated
module imports.
"""

from __future__ import annotations

from typing import Dict, Tuple, Type
from collections.abc import Sequence

try:
    from prometheus_client import (  # type: ignore
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Summary,
    )
except Exception:  # pragma: no cover
    # Minimal no-op fallbacks to keep importers alive if prometheus_client
    # is not installed in the current lane.
    class _NoMetric:
        def __init__(self, *a, **k):
            pass

        def labels(self, *a, **k):
            return self

        def observe(self, *a, **k):
            return None

        def inc(self, *a, **k):
            return None

        def dec(self, *a, **k):
            return None

        def set(self, *a, **k):
            return None

    class CollectorRegistry:  # type: ignore
        def __init__(self, *a, **k):
            pass

    Counter = Gauge = Histogram = Summary = _NoMetric  # type: ignore

__all__ = [
    "LUKHAS_REGISTRY",
    "counter",
    "gauge",
    "histogram",
    "summary",
    "register_lukhas_metric",
]

LUKHAS_REGISTRY: CollectorRegistry = CollectorRegistry()  # auto_describe default ok
_CACHE: Dict[Tuple[str, str, Tuple[str, ...]], object] = {}


def _key(
    cls: Type, name: str, labelnames: Sequence[str] | None
) -> Tuple[str, str, Tuple[str, ...]]:
    return (cls.__name__, name, tuple(labelnames or ()))


def _get_or_create(
    cls: Type, name: str, documentation: str, labelnames: Sequence[str] | None = None, **kwargs
):
    k = _key(cls, name, labelnames)
    if k in _CACHE:
        return _CACHE[k]
    try:
        metric = cls(  # type: ignore[call-arg]
            name, documentation, labelnames=labelnames or (), registry=LUKHAS_REGISTRY, **kwargs
        )
    except Exception:
        # If already registered elsewhere or any other dup situation, cache a no-op
        # rather than crash test discovery. Callers can still import and proceed.
        metric = _noop_metric()
    _CACHE[k] = metric
    return metric


def _noop_metric():
    class _Noop:
        def labels(self, *a, **k):
            return self

        def observe(self, *a, **k):
            pass

        def inc(self, *a, **k):
            pass

        def dec(self, *a, **k):
            pass

        def set(self, *a, **k):
            pass

    return _Noop()


def register_lukhas_metric(metric):  # convenience passthrough
    # Best-effort: many client metrics self-register; we rely on factories above.
    return metric


def counter(name: str, documentation: str, labelnames: Sequence[str] | None = None, **kwargs):
    return _get_or_create(Counter, name, documentation, labelnames, **kwargs)


def gauge(name: str, documentation: str, labelnames: Sequence[str] | None = None, **kwargs):
    return _get_or_create(Gauge, name, documentation, labelnames, **kwargs)


def histogram(name: str, documentation: str, labelnames: Sequence[str] | None = None, **kwargs):
    return _get_or_create(Histogram, name, documentation, labelnames, **kwargs)


def summary(name: str, documentation: str, labelnames: Sequence[str] | None = None, **kwargs):
    return _get_or_create(Summary, name, documentation, labelnames, **kwargs)
