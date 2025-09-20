# lukhas/metrics.py
"""
Prometheus metrics (optional). Falls back to no-op if client missing.
Env:
- ENABLE_PROM=1 to start an exporter on PROM_PORT (default 9108)
"""

from __future__ import annotations
import os
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server  # type: ignore
except Exception:  # pragma: no cover
    Counter = Histogram = Gauge = None
    start_http_server = None


ENABLED = os.getenv("ENABLE_PROM", "0") == "1"
if ENABLED and start_http_server is not None:
    try:
        start_http_server(int(os.getenv("PROM_PORT", "9108")))
    except Exception:
        pass


def _noop_histogram(*_labels):
    @contextmanager
    def _timer():
        yield
    return _timer()


class _NoopCounter:
    def labels(self, *_args, **_kwargs): return self
    def inc(self, *_args, **_kwargs): pass


class _NoopHistogram:
    def labels(self, *_args, **_kwargs): return self
    def time(self): return _noop_histogram()


class _NoopGauge:
    def labels(self, *_args, **_kwargs): return self
    def set(self, *_args, **_kwargs): pass
    def inc(self, *_args, **_kwargs): pass
    def dec(self, *_args, **_kwargs): pass


if Counter is None or Histogram is None or Gauge is None:
    # Core pipeline metrics
    stage_latency = _NoopHistogram()
    stage_timeouts = _NoopCounter()
    guardian_band = _NoopCounter()

    # Domain-specific AI metrics
    memory_cascade_prevention_rate = _NoopGauge()
    guardian_violations_total = _NoopCounter()
    consciousness_state_changes = _NoopCounter()
    reasoning_chain_length = _NoopHistogram()
    ethics_risk_distribution = _NoopHistogram()
    node_confidence_scores = _NoopHistogram()
    pipeline_success_rate = _NoopGauge()
    active_memory_folds = _NoopGauge()
    constellation_star_activations = _NoopCounter()
    arbitration_decisions_total = _NoopCounter()
    oscillation_detections_total = _NoopCounter()

    # Parallel execution metrics
    parallel_batch_duration = _NoopHistogram()
    parallel_speedup_ratio = _NoopGauge()
    parallel_execution_mode_total = _NoopCounter()
else:
    # Core pipeline metrics
    stage_latency = Histogram(
        "matriz_stage_latency_seconds",
        "Latency per MATRIZ stage",
        ["stage", "constellation_star"]
    )
    stage_timeouts = Counter(
        "matriz_stage_timeouts_total",
        "Timeouts per stage",
        ["stage"]
    )
    guardian_band = Counter(
        "guardian_risk_band_total",
        "Guardian decisions per risk band",
        ["band", "action"]
    )

    # Domain-specific AI metrics
    memory_cascade_prevention_rate = Gauge(
        "matriz_memory_cascade_prevention_rate",
        "Rate of prevented memory cascades (target: 0.997)",
        ["memory_type"]
    )

    guardian_violations_total = Counter(
        "matriz_guardian_violations_total",
        "Total Guardian ethics violations detected",
        ["violation_type", "severity"]
    )

    consciousness_state_changes = Counter(
        "matriz_consciousness_state_changes_total",
        "Consciousness state transitions",
        ["from_state", "to_state", "trigger"]
    )

    reasoning_chain_length = Histogram(
        "matriz_reasoning_chain_length",
        "Length of reasoning chains in cognitive processing",
        ["node_type", "complexity"]
    )

    ethics_risk_distribution = Histogram(
        "matriz_ethics_risk_distribution",
        "Distribution of ethics risk scores across decisions",
        ["stage", "risk_band"]
    )

    node_confidence_scores = Histogram(
        "matriz_node_confidence_scores",
        "Confidence scores from cognitive nodes",
        ["node_type", "stage"]
    )

    pipeline_success_rate = Gauge(
        "matriz_pipeline_success_rate",
        "Overall pipeline success rate (rolling window)",
        ["pipeline_type"]
    )

    active_memory_folds = Gauge(
        "matriz_active_memory_folds",
        "Number of active memory folds (target: <1000)",
        ["fold_type"]
    )

    constellation_star_activations = Counter(
        "matriz_constellation_star_activations_total",
        "Constellation star activations by type",
        ["star", "activation_type"]
    )

    arbitration_decisions_total = Counter(
        "matriz_arbitration_decisions_total",
        "Consensus arbitration decisions",
        ["outcome", "proposal_count"]
    )

    oscillation_detections_total = Counter(
        "matriz_oscillation_detections_total",
        "Meta-controller oscillation detections",
        ["pattern_type", "stages_involved"]
    )

    # Parallel execution metrics
    parallel_batch_duration = Histogram(
        "matriz_parallel_batch_duration_seconds",
        "Duration of parallel batch execution",
        ["batch_index", "batch_size"]
    )

    parallel_speedup_ratio = Gauge(
        "matriz_parallel_speedup_ratio",
        "Speedup ratio: sequential_time / parallel_time",
        ["stage_count", "execution_mode"]
    )

    parallel_execution_mode_total = Counter(
        "matriz_parallel_execution_mode_total",
        "Count of executions by mode (sequential/parallel/adaptive)",
        ["mode", "chosen_reason"]
    )

__all__ = [
    # Core metrics
    "stage_latency", "stage_timeouts", "guardian_band",
    # Domain-specific metrics
    "memory_cascade_prevention_rate", "guardian_violations_total",
    "consciousness_state_changes", "reasoning_chain_length",
    "ethics_risk_distribution", "node_confidence_scores",
    "pipeline_success_rate", "active_memory_folds",
    "constellation_star_activations", "arbitration_decisions_total",
    "oscillation_detections_total",
    # Parallel execution metrics
    "parallel_batch_duration", "parallel_speedup_ratio", "parallel_execution_mode_total"
]