"""LUKHAS Core Metrics and Monitoring helpers with duplicate registration guard."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from prometheus_client import REGISTRY, Counter, Gauge, Histogram, Summary

    PROMETHEUS_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback path exercised in tests
    PROMETHEUS_AVAILABLE = False

    class _StubRegistry:
        def __init__(self) -> None:
            self._names_to_collectors: dict[str, object] = {}

    REGISTRY = _StubRegistry()

    class _BaseCollector:
        def __init__(
            self,
            name: str,
            documentation: str,
            labelnames: tuple[str, ...] | None = None,
            **_kwargs: Any,
        ) -> None:
            self._name = name
            self._documentation = documentation
            self._labelnames = labelnames or ()
            self._values: dict[tuple[Any, ...], Any] = {}

        def labels(self, *label_values: Any, **_unused: Any) -> "_BaseCollector":
            key = label_values if label_values else tuple()
            self._values.setdefault(key, 0)
            _register_collector(self._name, self)
            return self

    class Counter(_BaseCollector):
        def inc(self, amount: int | float = 1) -> None:
            key = tuple()
            self._values[key] = self._values.get(key, 0) + amount

    class Histogram(_BaseCollector):
        def observe(self, value: Any) -> None:
            key = tuple()
            bucket = self._values.setdefault(key, [])
            bucket.append(value)

    class Gauge(_BaseCollector):
        def set(self, value: Any) -> None:
            key = tuple()
            self._values[key] = value

    class Summary(_BaseCollector):  # pragma: no cover - parity with prometheus API
        def observe(self, value: Any) -> None:
            key = tuple()
            bucket = self._values.setdefault(key, [])
            bucket.append(value)


def _register_collector(name: str, collector: object) -> None:
    registry = getattr(REGISTRY, "_names_to_collectors", None)
    if isinstance(registry, dict) and name not in registry:
        registry[name] = collector


def _get_or(
    factory: Callable[..., Any],
    name: str,
    documentation: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Create a Prometheus collector, tolerating duplicate registration."""
    try:
        collector = factory(name, documentation, *args, **kwargs)
    except ValueError:
        existing = getattr(REGISTRY, "_names_to_collectors", {}).get(name)
        if existing is None:
            raise
        return existing

    _register_collector(name, collector)
    return collector


# Router metrics ------------------------------------------------------------
router_no_rule_total = _get_or(
    Counter,
    "lukhas_router_no_rule_total",
    "Signals that matched no routing rule",
    labelnames=("signal_type", "producer_module"),
)

router_signal_processing_time = _get_or(
    Histogram,
    "lukhas_router_signal_processing_seconds",
    "Time spent processing signals in router",
    labelnames=("signal_type", "routing_strategy"),
)

router_cascade_preventions_total = _get_or(
    Counter,
    "lukhas_router_cascade_preventions_total",
    "Number of signals blocked by cascade prevention",
    labelnames=("producer_module",),
)

# Network health metrics ----------------------------------------------------
network_coherence_score = _get_or(
    Gauge,
    "lukhas_network_coherence_score",
    "Current network coherence score (0-1)",
)

network_active_nodes = _get_or(
    Gauge,
    "lukhas_network_active_nodes",
    "Number of active nodes in the network",
)

# Bio-symbolic processing metrics -------------------------------------------
bio_processor_signals_total = _get_or(
    Counter,
    "lukhas_bio_processor_signals_total",
    "Total signals processed by bio-symbolic processor",
    labelnames=("pattern_type",),
)

bio_processor_adaptations_total = _get_or(
    Counter,
    "lukhas_bio_processor_adaptations_total",
    "Total adaptations applied by bio-symbolic processor",
    labelnames=("adaptation_rule",),
)

# Public exports ------------------------------------------------------------
__all__ = [
    "router_no_rule_total",
    "router_signal_processing_time",
    "router_cascade_preventions_total",
    "network_coherence_score",
    "network_active_nodes",
    "bio_processor_signals_total",
    "bio_processor_adaptations_total",
    "PROMETHEUS_AVAILABLE",
    "Summary",
]
