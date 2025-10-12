"""Bridge for lukhas.observability.service_metrics."""
from enum import Enum
from importlib import import_module

__all__ = []

def _try(n: str):
    try: return import_module(n)
    except Exception: return None

for n in ("labs.observability.service_metrics", "lukhas_website.lukhas.observability.service_metrics"):
    m = _try(n)
    if m:
        for k in dir(m):
            if not k.startswith("_"):
                globals()[k] = getattr(m, k); __all__.append(k)
        break

# Fallback MetricType enum
if "MetricType" not in globals():
    class MetricType(Enum):
        """Metric type enumeration."""
        COUNTER = "counter"
        GAUGE = "gauge"
        HISTOGRAM = "histogram"
        SUMMARY = "summary"
    __all__.append("MetricType")
