"""Resource Efficiency Analysis utilities."""

import logging
from typing import Any, Dict, List

try:
    import psutil
except ImportError:  # pragma: no cover - psutil may not be installed in some envs
    psutil = None

logger = logging.getLogger(__name__)


class ResourceEfficiencyAnalyzer:
    """Analyze system resource usage for energy and memory optimization."""

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect CPU and memory metrics."""
        if psutil is None:
            logger.warning("psutil not available; returning empty metrics")
            return {"cpu_percent": 0.0, "memory_percent": 0.0}

        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
        }


def get_resource_efficiency_table() -> List[Dict[str, str]]:
    """Return table summarizing resource efficiency across architectures."""
    return [
        {
            "Architecture": "Monolithic",
            "Energy": "Low",
            "Memory": "Low",
        },
        {
            "Architecture": "Traditional Microservices",
            "Energy": "Low to Medium",
            "Memory": "Medium",
        },
        {
            "Architecture": "Symbiotic Swarm",
            "Energy": "High",
            "Memory": "High",
        },
    ]
