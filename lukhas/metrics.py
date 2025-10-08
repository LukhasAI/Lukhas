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

stage_timeouts = histogram(
    "lukhas_stage_timeouts_total",
    "Timeout occurrences by stage",
    labelnames=("stage", "reason"),
)

guardian_band = histogram(
    "lukhas_guardian_band_decisions",
    "Guardian decision outcomes by band",
    labelnames=("band", "outcome"),
)

reasoning_chain_length = histogram(
    "lukhas_reasoning_chain_length",
    "Length of reasoning chains",
    labelnames=("chain_type", "outcome"),
)

ethics_risk_distribution = histogram(
    "lukhas_ethics_risk_distribution",
    "Distribution of ethics risk levels",
    labelnames=("risk_level", "source"),
)

node_confidence_scores = histogram(
    "lukhas_node_confidence_scores",
    "Confidence scores for nodes",
    labelnames=("node_type", "confidence_band"),
)

constellation_star_activations = histogram(
    "lukhas_constellation_star_activations",
    "Activation levels for constellation stars",
    labelnames=("star_id", "activation_level"),
)

__all__.extend(["stage_latency", "stage_timeouts", "guardian_band", "reasoning_chain_length", "ethics_risk_distribution", "node_confidence_scores", "constellation_star_activations"])

