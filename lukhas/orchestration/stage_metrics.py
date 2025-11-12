"""
Centralized Prometheus metrics for LUKHAS orchestration pipelines.
Provides standardized metrics for tracking pipeline and stage-level performance,
including duration, success/failure rates, and throughput.
"""

import os
from typing import Optional

# Mock prometheus_client for environments where it's not installed (e.g., lightweight tests)
try:
    from prometheus_client import REGISTRY, Counter, Histogram
except ImportError:  # pragma: no cover

    class _NoopMetric:
        """A no-op metric class for environments without prometheus_client."""

        def __init__(self, *_, **__):
            pass

        def labels(self, *_, **__):
            """Returns a no-op instance for chained calls."""
            return self

        def observe(self, *_, **__):
            """No-op observe method."""
            return None

        def inc(self, *_, **__):
            """No-op inc method."""
            return None

    Counter = Histogram = _NoopMetric
    REGISTRY = None


_DEFAULT_LANE = os.getenv("LUKHAS_LANE", "production").lower()


def _register_metric(metric_class, name, *args, **kwargs):
    """Safely register a Prometheus metric, reusing it if it already exists."""
    try:
        return metric_class(name, *args, **kwargs)
    except ValueError:
        if REGISTRY is not None:
            # Metric already exists, retrieve and return it.
            existing = REGISTRY._names_to_collectors.get(name)
            if isinstance(existing, metric_class):
                return existing
        raise


# --- Public Metrics ---

PIPELINE_DURATION = _register_metric(
    Histogram,
    "lukhas_orchestration_pipeline_duration_seconds",
    "Orchestration pipeline duration",
    ["lane", "pipeline_name", "status"],
    buckets=[0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.35, 0.5, 1.0, 2.5, 5.0],
)

PIPELINE_TOTAL = _register_metric(
    Counter,
    "lukhas_orchestration_pipeline_total",
    "Orchestration pipeline executions",
    ["lane", "pipeline_name", "status"],
)

STAGE_DURATION = _register_metric(
    Histogram,
    "lukhas_orchestration_stage_duration_seconds",
    "Orchestration stage duration",
    ["lane", "pipeline_name", "stage_name", "outcome"],
    buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
)

STAGE_TOTAL = _register_metric(
    Counter,
    "lukhas_orchestration_stage_total",
    "Orchestration stage executions",
    ["lane", "pipeline_name", "stage_name", "outcome"],
)


def _get_lane() -> str:
    """Resolve the current lane label for orchestrator metrics."""
    return os.getenv("LUKHAS_LANE", _DEFAULT_LANE).lower() or "unknown"


def record_stage_metrics(
    pipeline_name: str, stage_name: str, duration_sec: float, outcome: str
) -> None:
    """
    Record Prometheus metrics for an individual orchestration stage.
    Args:
        pipeline_name: The name of the pipeline the stage belongs to.
        stage_name: The name of the stage.
        duration_sec: The duration of the stage execution in seconds.
        outcome: The result of the stage (e.g., 'success', 'failure', 'timeout').
    """
    outcome_label = outcome if outcome in {"success", "timeout", "error", "failure"} else "unknown"
    lane = _get_lane()
    STAGE_DURATION.labels(
        lane=lane,
        pipeline_name=pipeline_name,
        stage_name=stage_name,
        outcome=outcome_label,
    ).observe(max(duration_sec, 0.0))
    STAGE_TOTAL.labels(
        lane=lane,
        pipeline_name=pipeline_name,
        stage_name=stage_name,
        outcome=outcome_label,
    ).inc()


def record_pipeline_metrics(pipeline_name: str, duration_sec: float, status: str) -> None:
    """
    Record Prometheus metrics for a full pipeline execution.
    Args:
        pipeline_name: The name of the pipeline.
        duration_sec: The total duration of the pipeline in seconds.
        status: The final status of the pipeline (e.g., 'success', 'failure').
    """
    status_label = status if status in {"success", "error", "failure", "timeout"} else "unknown"
    lane = _get_lane()
    PIPELINE_DURATION.labels(
        lane=lane,
        pipeline_name=pipeline_name,
        status=status_label,
    ).observe(max(duration_sec, 0.0))
    PIPELINE_TOTAL.labels(
        lane=lane,
        pipeline_name=pipeline_name,
        status=status_label,
    ).inc()
