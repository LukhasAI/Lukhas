"""Bridge for lukhas.observability.service_metrics."""

from enum import Enum
from importlib import import_module

__all__ = []


def _try(module_name: str):
    try:
        return import_module(module_name)
    except Exception:
        return None


for candidate in (
    "labs.observability.service_metrics",
    "lukhas_website.lukhas.observability.service_metrics",
):
    module = _try(candidate)
    if module:
        for attr in dir(module):
            if not attr.startswith("_"):
                globals()[attr] = getattr(module, attr)
                __all__.append(attr)
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
