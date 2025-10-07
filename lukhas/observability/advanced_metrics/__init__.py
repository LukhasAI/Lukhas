"""Bridge for advanced metrics with safe fallbacks when backends are missing."""
from __future__ import annotations

from lukhas._bridgeutils import export_from, safe_guard

__all__: list[str] = []

_exports: dict[str, object] = {}

try:
    import core.metrics as _metrics
except Exception:  # noqa: BLE001
    _metrics = None
else:
    _exports = export_from(_metrics)
    for _sym in (
        "router_cascade_preventions_total",
        "router_no_rule_total",
        "router_signal_processing_time",
        "network_coherence_score",
        "bio_processor_signals_total",
    ):
        if _sym in _exports:
            globals()[_sym] = _exports[_sym]
            __all__.append(_sym)


def _register_stub(name: str, obj: object) -> None:
    if name not in globals():
        globals()[name] = obj
    if name not in __all__:
        __all__.append(name)


class AdvancedMetricsSystem:
    """Stubbed advanced metrics interface used in pre-freeze collection."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs

    def record(self, *args: object, **kwargs: object) -> None:
        return None


class LatencyHistogram:
    """Simple histogram shim capturing observed values in memory."""

    def __init__(self) -> None:
        self.values: list[object] = []

    def observe(self, value: object) -> None:
        self.values.append(value)


class TraceExporter:
    """No-op trace exporter stub."""

    def export(self, *args: object, **kwargs: object) -> None:
        return None


_register_stub("AdvancedMetricsSystem", AdvancedMetricsSystem)
_register_stub("LatencyHistogram", LatencyHistogram)
_register_stub("TraceExporter", TraceExporter)

safe_guard(__name__, __all__)

del _metrics, _exports, _sym, _register_stub
