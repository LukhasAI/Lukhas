"""Bridge: lukhas.observability.advanced_metrics (map to core metrics safely)."""
from __future__ import annotations
from lukhas._bridgeutils import export_from, safe_guard

__all__ = []
try:
    import core.metrics as _metrics
    e = export_from(_metrics)
    for sym in (
        "router_cascade_preventions_total",
        "router_no_rule_total",
        "router_signal_processing_time",
        "network_coherence_score",
        "bio_processor_signals_total",
    ):
        if sym in e:
            globals()[sym] = e[sym]
            __all__.append(sym)
except Exception:
    pass

# Add stubs for commonly expected classes
if not __all__ or "AdvancedMetricsSystem" not in globals():
    class AdvancedMetricsSystem:
        """Stub for Advanced Metrics System."""
        def __init__(self, *a, **k):
            raise NotImplementedError("AdvancedMetricsSystem not wired")

    class LatencyHistogram:
        """Stub for Latency Histogram."""
        pass

    class TraceExporter:
        """Stub for Trace Exporter."""
        pass

    if not __all__:
        __all__ = []
    for name in ("AdvancedMetricsSystem", "LatencyHistogram", "TraceExporter"):
        if name not in globals():
            __all__.append(name)

safe_guard(__name__, __all__)
