#!/usr/bin/env python3
"""
Chaos Engineering Toolkit

A collection of tools for systematically injecting failures and stress
into a system to test its resilience and identify weaknesses.

# ΛTAG: chaos_engineering, resilience_testing, failure_injection
"""

import asyncio
import random
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

# --- Failure Injection ---

class FailureInjector:
    """Injects failures into function calls."""

    def __init__(self, failure_rate: float = 0.1, exception_type: type = Exception, error_message: str = "Chaos monkey intervened"):
        self.failure_rate = failure_rate
        self.exception_type = exception_type
        self.error_message = error_message

    def maybe_fail(self):
        """Injects a failure based on the failure rate."""
        if random.random() < self.failure_rate:
            raise self.exception_type(self.error_message)

    def inject(self, func: Callable) -> Callable:
        """Decorator to inject failures into a function."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.maybe_fail()
            return await func(*args, **kwargs)
        return wrapper

# --- Network Partition Simulation ---

class NetworkPartitioner:
    """Simulates network partitions by blocking or delaying calls."""

    def __init__(self, block_rate: float = 0.1, delay_ms: float = 100.0):
        self.block_rate = block_rate
        self.delay_ms = delay_ms

    async def simulate_partition(self):
        """Simulates a network partition."""
        if random.random() < self.block_rate:
            raise ConnectionAbortedError("Network partition simulated")
        await asyncio.sleep(self.delay_ms / 1000.0)

    def inject(self, func: Callable) -> Callable:
        """Decorator to simulate network partitions."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await self.simulate_partition()
            return await func(*args, **kwargs)
        return wrapper

# --- Resource Exhaustion ---

class ResourceExhaustor:
    """Simulates resource exhaustion scenarios."""

    def __init__(self, cpu_load: float = 0.8, memory_usage_mb: int = 1024):
        self.cpu_load = cpu_load
        self.memory_usage_mb = memory_usage_mb

    @contextmanager
    def exhaust_resources(self):
        """Context manager to simulate resource exhaustion."""
        # Simulate CPU load by sleeping. This is a simple approximation.
        # A real implementation would use a busy-loop.
        sleep_duration = self.cpu_load * 0.1 # a factor to make it not too slow
        time.sleep(sleep_duration)

        # Simulate memory usage by allocating a large string.
        # This is a simple approximation.
        try:
            _ = ' ' * (self.memory_usage_mb * 1024 * 1024)
        except MemoryError:
            # If we run out of memory, that's the point.
            # We can just continue.
            pass
        yield

# --- Chaos Monkey ---

class ChaosMonkey:
    """Randomly injects failures into the system."""

    def __init__(self, failure_injectors: List[Any], enabled: bool = True):
        self.failure_injectors = failure_injectors
        self.enabled = enabled

    def attack(self, func: Callable) -> Callable:
        """Decorator to apply a random failure injector."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.enabled and self.failure_injectors:
                injector = random.choice(self.failure_injectors)
                return await injector.inject(func)(*args, **kwargs)
            return await func(*args, **kwargs)
        return wrapper
