"""Bridge: lukhas.observability.advanced_metrics."""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates, export_from, safe_guard

__all__, _exp = bridge_from_candidates(
    "lukhas_website.lukhas.observability.advanced_metrics",
    "candidate.observability.advanced_metrics",
    "observability.advanced_metrics",
    "core.metrics",  # pragmatic fallback where metrics actually live
)
globals().update(_exp)

# promote key metric names when exporting from `core.metrics`
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
        if sym in e and sym not in globals():
            globals()[sym] = e[sym]
            if "__all__" in globals():
                __all__.append(sym)
except Exception:
    pass

safe_guard(__name__, __all__)
