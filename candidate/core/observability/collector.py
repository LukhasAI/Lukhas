import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

import psutil


@dataclass
class ActorMetric:
    actor_id: str
    metric_name: str
    value: Any
    timestamp: float = field(default_factory=time.time)


class ObservabilityCollector:
    def __init__(self):
        self._metrics: dict[str, list[ActorMetric]] = defaultdict(list)
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self.log_file = open("observability.log", "w")

    def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._collect_system_metrics())

    def stop(self):
        if self._running:
            self._running = False
            if self._worker_task:
                self._worker_task.cancel()
        self.log_file.close()

    def record_metric(self, actor_id: str, metric_name: str, value: Any):
        metric = ActorMetric(actor_id=actor_id, metric_name=metric_name, value=value)
        self._metrics[metric_name].append(metric)
        self.log_file.write(f"{time.time()},{actor_id},{metric_name},{value}\n")

    def get_metrics(self) -> dict[str, Any]:
        return {
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
            },
            "actors": self._metrics,
        }

    async def _collect_system_metrics(self):
        while self._running:
            # In a real implementation, this would collect metrics from all actors
            # and colonies in the system.
            await asyncio.sleep(1)