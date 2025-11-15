# lukhas/observability/slo_monitoring.py

"""
SLI/SLO definitions and Prometheus recording rules for key LUKHAS subsystems.
"""

from unittest.mock import MagicMock

# Mock missing modules that would provide the metrics registries and rule objects
try:
    from lukhas.observability.metrics import DECILE_QUANTILES, registry
    from lukhas.observability.rules import RecordingRule
except ImportError:
    registry = MagicMock()
    DECILE_QUANTILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    RecordingRule = MagicMock()


# SLI/SLO Definitions

# 1. Memory Recall Latency
# SLI: The proportion of memory recall operations that complete in under 100ms.
# SLO: 99.0% of memory recall operations should complete in under 100ms.

MEMORY_RECALL_LATENCY_SLO_MS = 100
MEMORY_RECALL_LATENCY_SLO_PERCENT = 99.0

# 2. Pipeline Execution Latency (p95)
# SLI: The 95th percentile of end-to-end pipeline execution latency.
# SLO: The p95 latency should be less than 250ms.

PIPELINE_LATENCY_P95_SLO_MS = 250

# 3. Cascade Prevention Success Rate
# SLI: The proportion of potential cascading failures that are successfully prevented.
# SLO: 99.7% of cascading failures should be prevented.

CASCADE_PREVENTION_SLO_PERCENT = 99.7


# Prometheus Recording Rules

# Rule for Memory Recall SLI
memory_recall_sli_rule = RecordingRule(
    record="lukhas:memory:recall_latency_100ms:sli",
    expr=(
        f"sum(rate(lukhas_memory_recall_latency_seconds_bucket{{le='{MEMORY_RECALL_LATENCY_SLO_MS / 1000.0}'}}[5m])) "
        f"/ "
        f"sum(rate(lukhas_memory_recall_latency_seconds_count[5m]))"
    ),
    labels={"slo": "memory_recall_latency"},
)

# Rule for Pipeline Latency p95
pipeline_latency_p95_rule = RecordingRule(
    record="lukhas:pipeline:execution_latency_seconds:p95",
    expr="histogram_quantile(0.95, sum(rate(lukhas_pipeline_execution_latency_seconds_bucket[5m])) by (le))",
    labels={"slo": "pipeline_latency"},
)

# Rule for Cascade Prevention SLI
cascade_prevention_sli_rule = RecordingRule(
    record="lukhas:resilience:cascade_prevention:sli",
    expr=(
        "sum(rate(lukhas_cascade_prevented_total[5m]))"
        "/ "
        "(sum(rate(lukhas_cascade_prevented_total[5m])) + sum(rate(lukhas_cascade_failure_total[5m])))"
    ),
    labels={"slo": "cascade_prevention"},
)


# Register rules if a registry is available
if hasattr(registry, 'register'):
    registry.register(memory_recall_sli_rule)
    registry.register(pipeline_latency_p95_rule)
    registry.register(cascade_prevention_sli_rule)
