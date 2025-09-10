# Placeholder for T4EnterpriseLoadTester
from dataclasses import dataclass
from enum import Enum


class ExperimentType(Enum):
    SCALE = "SCALE"


@dataclass
class LoadTestConfig:
    target_url: str
concurrent_users: int
test_duration_minutes: int
expected_latency_p95_ms: float


class T4EnterpriseLoadTester:
    def __init__(self, config: LoadTestConfig):
        self.config = config