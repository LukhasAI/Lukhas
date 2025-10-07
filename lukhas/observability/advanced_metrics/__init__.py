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

safe_guard(__name__, __all__)
