"""
Memory Performance Metrics
==========================
This module provides utilities for tracking and analyzing memory performance.
"""

from typing import List
import numpy as np
import time

class PerformanceMonitor:
    """
    A simulated system for tracking and calculating memory performance metrics.
    """

    def __init__(self):
        self.latencies: List[float] = [] # in seconds
        self.operations_log: List[float] = [] # timestamps

    def log_operation(self, duration: float):
        """
        Logs the duration of a memory operation.
        """
        self.latencies.append(duration)
        self.operations_log.append(time.time())

    def get_latency_metrics(self) -> dict:
        """
        Calculates latency metrics for memory operations.
        """
        if not self.latencies:
            return {}

        return {
            "average": np.mean(self.latencies),
            "p50": np.percentile(self.latencies, 50),
            "p95": np.percentile(self.latencies, 95),
            "min": np.min(self.latencies),
            "max": np.max(self.latencies),
        }

    def get_throughput_metrics(self, window_seconds: int = 60) -> dict:
        """
        Calculates throughput metrics (operations per second).
        """
        now = time.time()
        window_start = now - window_seconds

        recent_ops = [t for t in self.operations_log if t >= window_start]

        ops_per_second = len(recent_ops) / window_seconds

        return {
            "ops_per_second": ops_per_second,
            "window_seconds": window_seconds,
            "total_ops_in_window": len(recent_ops),
        }
