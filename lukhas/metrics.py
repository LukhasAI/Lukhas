"""Bridge: lukhas.metrics"""
from __future__ import annotations
from lukhas._bridgeutils import bridge_from_candidates

__all__, _exp = bridge_from_candidates(
    "candidate.core.metrics",
    "candidate.metrics",
    "core.metrics",
)
globals().update(_exp)

# Additional metric exports for test compatibility
from lukhas.observability import histogram

stage_latency = histogram(
    "lukhas_stage_latency_seconds",
    "Processing latency by stage",
    labelnames=("stage", "status"),
)

__all__.append("stage_latency")
