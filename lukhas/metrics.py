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
from lukhas.observability import counter, histogram

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

arbitration_decisions_total = counter(
    "lukhas_arbitration_decisions_total",
    "Total arbitration decisions",
    labelnames=("decision_type", "outcome"),
)

oscillation_detections_total = counter(
    "lukhas_oscillation_detections_total",
    "Total oscillation detections",
    labelnames=("pattern", "severity"),
)

parallel_batch_duration = histogram(
    "lukhas_parallel_batch_duration_seconds",
    "Duration of parallel batch operations",
    labelnames=("batch_type", "size_bucket"),
)

parallel_execution_mode_total = counter(
    "lukhas_parallel_execution_mode_total",
    "Execution mode for parallel operations",
    labelnames=("mode", "worker_count"),
)

retry_attempts_total = counter(
    "lukhas_retry_attempts_total",
    "Total retry attempts",
    labelnames=("operation", "outcome"),
)

mtrx_stage_duration_seconds = histogram(
    "lukhas_mtrx_stage_duration_seconds",
    "MATRIZ stage execution duration",
    labelnames=("stage", "outcome"),
)

mtrx_orch_timeout_total = counter(
    "lukhas_mtrx_orch_timeout_total",
    "MATRIZ orchestration timeouts",
    labelnames=("component", "reason"),
)

mtrx_orch_retry_total = counter(
    "lukhas_mtrx_orch_retry_total",
    "MATRIZ orchestration retry attempts",
    labelnames=("component", "attempt"),
)

mtrx_orch_circuit_open_total = counter(
    "lukhas_mtrx_orch_circuit_open_total",
    "MATRIZ orchestration circuit breaker open events",
    labelnames=("component", "reason"),
)

__all__.extend(["stage_latency", "stage_timeouts", "guardian_band", "reasoning_chain_length", "ethics_risk_distribution", "node_confidence_scores", "constellation_star_activations", "arbitration_decisions_total", "oscillation_detections_total", "parallel_batch_duration", "parallel_execution_mode_total", "retry_attempts_total", "mtrx_stage_duration_seconds", "mtrx_orch_timeout_total", "mtrx_orch_retry_total", "mtrx_orch_circuit_open_total"])

