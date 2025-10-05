"""
LUKHAS Core Metrics and Monitoring

Centralized metrics collection for Prometheus/Grafana monitoring
"""

try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Fallback stubs for environments without prometheus_client
    PROMETHEUS_AVAILABLE = False

    class Counter:
        def __init__(self, *args, **kwargs):
            self._value = 0
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            self._value += amount

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, **kwargs):
            return self
        def observe(self, value):
            pass

    class Gauge:
        def __init__(self, *args, **kwargs):
            self._value = 0
        def labels(self, **kwargs):
            return self
        def set(self, value):
            self._value = value

# Router metrics
router_no_rule_total = Counter(
    'lukhas_router_no_rule_total',
    'Signals that matched no routing rule',
    ['signal_type', 'producer_module']
)

router_signal_processing_time = Histogram(
    'lukhas_router_signal_processing_seconds',
    'Time spent processing signals in router',
    ['signal_type', 'routing_strategy']
)

router_cascade_preventions_total = Counter(
    'lukhas_router_cascade_preventions_total',
    'Number of signals blocked by cascade prevention',
    ['producer_module']
)

# Network health metrics
network_coherence_score = Gauge(
    'lukhas_network_coherence_score',
    'Current network coherence score (0-1)',
    []
)

network_active_nodes = Gauge(
    'lukhas_network_active_nodes',
    'Number of active nodes in the network',
    []
)

# Bio-symbolic processing metrics
bio_processor_signals_total = Counter(
    'lukhas_bio_processor_signals_total',
    'Total signals processed by bio-symbolic processor',
    ['pattern_type']
)

bio_processor_adaptations_total = Counter(
    'lukhas_bio_processor_adaptations_total',
    'Total adaptations applied by bio-symbolic processor',
    ['adaptation_rule']
)

# Export for easy access
__all__ = [
    'router_no_rule_total',
    'router_signal_processing_time',
    'router_cascade_preventions_total',
    'network_coherence_score',
    'network_active_nodes',
    'bio_processor_signals_total',
    'bio_processor_adaptations_total',
    'PROMETHEUS_AVAILABLE'
]
