# Placeholder for T4AutoScalingManager
from dataclasses import dataclass


@dataclass
class T4ScalingConfig:
    max_concurrent_users: int


target_latency_p95_ms: float
min_instances: int
max_instances: int


class T4AutoScalingManager:
    def __init__(self, config: T4ScalingConfig):
        self.config = config
