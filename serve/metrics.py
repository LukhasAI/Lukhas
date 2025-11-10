import sys
from prometheus_client import Counter, Histogram, Gauge, Info

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

matriz_operations_total = Counter(
    'matriz_operations_total',
    'Total MATRIZ cognitive operations',
    ['operation_type', 'status']
)

matriz_operation_duration_ms = Histogram(
    'matriz_operation_duration_milliseconds',
    'MATRIZ operation latency',
    ['operation_type'],
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000]
)

active_thoughts = Gauge(
    'matriz_active_thoughts',
    'Number of active thoughts in MATRIZ'
)

memory_entries = Gauge(
    'memory_entries',
    'Total entries in memory system'
)

cache_hits_total = Gauge(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses_total = Gauge(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

system_info = Info(
    'lukhas_system',
    'LUKHAS system information'
)

system_info.info({
    'version': '1.0.0',
    'python_version': sys.version,
    'deployment': 'production'
})

from prometheus_client.core import GaugeMetricFamily
from prometheus_client import REGISTRY

class LUKHASCollector:
    '''Custom collector for LUKHAS metrics'''

    def collect(self):
        # Memory metrics
        yield GaugeMetricFamily(
            'lukhas_memory_bytes',
            'Memory usage in bytes',
            value=self.get_memory_usage()
        )


        memory_entries.set(self.get_memory_entries())

    def get_memory_usage(self):
        import psutil
        return psutil.Process().memory_info().rss

    def get_memory_entries(self):
        try:
            from lukhas.memory import get_index_manager
            index_manager = get_index_manager()
            # Assuming a single tenant for now for simplicity
            index = index_manager.get_index("default")
            if index:
                return len(index)
        except ImportError:
            pass
        return 0

REGISTRY.register(LUKHASCollector())
