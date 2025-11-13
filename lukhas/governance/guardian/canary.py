"""
Canary enforcement mode for the Guardian system.
"""

import random
from typing import Dict


# Mock prometheus_client for metrics tracking
class MockCounter:
    def inc(self):
        pass

    def collect(self):
        return []

    def __iter__(self):
        return iter(self.collect())

    def __next__(self):
        return next(iter(self.collect()))

    def __call__(self):
        return self

CANARY_REQUESTS_TOTAL = MockCounter()
CANARY_ENFORCED_TOTAL = MockCounter()

def is_canary_enforced(canary_percentage: float = 10.0) -> bool:
    """
    Determines if canary mode should be enforced for the current request.

    Args:
        canary_percentage: The percentage of traffic to apply canary enforcement to.

    Returns:
        True if canary mode should be enforced, False otherwise.
    """
    CANARY_REQUESTS_TOTAL.inc()
    if random.uniform(0, 100) < canary_percentage:
        CANARY_ENFORCED_TOTAL.inc()
        return True
    return False

def get_canary_metrics() -> Dict[str, MockCounter]:
    """
    Returns the canary metrics collectors.
    """
    return {
        "canary_requests_total": CANARY_REQUESTS_TOTAL,
        "canary_enforced_total": CANARY_ENFORCED_TOTAL,
    }
