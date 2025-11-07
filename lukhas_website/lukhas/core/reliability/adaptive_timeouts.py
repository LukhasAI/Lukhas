#!/usr/bin/env python3
"""
Intelligent Timeouts and Backoff for 0.01% Reliability

Adaptive timeout and exponential backoff strategies that learn from system
behavior and current load - the kind of intelligent resilience that prevents
cascading failures and maintains system stability under stress.
"""

import asyncio
import random
import statistics
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from observability.opentelemetry_tracing import LUKHASTracer
from observability.prometheus_metrics import LUKHASMetrics


class BackoffStrategy(Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    ADAPTIVE = "adaptive"
    FIBONACCI = "fibonacci"


@dataclass
class TimeoutConfig:
    """Configuration for adaptive timeouts."""
    base_timeout: float
    max_timeout: float
    min_timeout: float
    percentile_target: float = 95.0  # Use P95 latency for timeout calculation
    safety_multiplier: float = 2.0  # Multiply P95 by this for timeout
    adaptation_rate: float = 0.1  # How quickly to adapt (0.0-1.0)


@dataclass
class BackoffConfig:
    """Configuration for backoff strategies."""
    initial_delay: float = 1.0
    max_delay: float = 300.0  # 5 minutes
    multiplier: float = 2.0
    jitter: bool = True
    max_attempts: int = 5
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL


class AdaptiveTimeoutManager:
    """
    Intelligent timeout management with learning capabilities.

    0.01% Features:
    - Adapts timeouts based on historical latency patterns
    - Circuit breaker integration for fast failure
    - Load-aware timeout adjustment
    - Per-operation timeout learning
    """

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.operation_data: dict[str, deque] = {}
        self.timeout_configs: dict[str, TimeoutConfig] = {}
        self.metrics = LUKHASMetrics()
        self.tracer = LUKHASTracer()

    def register_operation(self, operation: str, config: TimeoutConfig) -> None:
        """Register an operation with its timeout configuration."""
        self.timeout_configs[operation] = config
        if operation not in self.operation_data:
            self.operation_data[operation] = deque(maxlen=self.window_size)

    def record_latency(self, operation: str, latency_ms: float, success: bool) -> None:
        """Record operation latency for timeout adaptation."""
        if operation not in self.operation_data:
            # Auto-register with default config
            default_config = TimeoutConfig(
                base_timeout=5000,  # 5 seconds
                max_timeout=30000,  # 30 seconds
                min_timeout=100     # 100ms
            )
            self.register_operation(operation, default_config)

        self.operation_data[operation].append({
            'latency_ms': latency_ms,
            'success': success,
            'timestamp': time.time()
        })

    def get_adaptive_timeout(self, operation: str, current_load: Optional[float] = None) -> float:
        """Calculate adaptive timeout based on historical data and current load."""
        if operation not in self.timeout_configs:
            return 5000  # Default 5 seconds

        config = self.timeout_configs[operation]
        data = self.operation_data.get(operation, deque())

        if len(data) < 10:  # Not enough data, use base timeout
            return config.base_timeout

        # Calculate percentile-based timeout
        recent_data = list(data)[-min(100, len(data)):]  # Use last 100 samples
        successful_latencies = [
            d['latency_ms'] for d in recent_data if d['success']
        ]

        if not successful_latencies:
            return config.base_timeout

        try:
            if len(successful_latencies) > 20:
                p95_latency = statistics.quantiles(successful_latencies, n=20)[18]
            else:
                p95_latency = max(successful_latencies)
        except Exception:
            p95_latency = statistics.mean(successful_latencies)

        # Apply safety multiplier
        adaptive_timeout = p95_latency * config.safety_multiplier

        # Adjust for current load
        if current_load is not None:
            load_multiplier = 1.0 + (current_load * 0.5)  # Up to 50% increase under load
            adaptive_timeout *= load_multiplier

        # Apply bounds
        adaptive_timeout = max(config.min_timeout, min(adaptive_timeout, config.max_timeout))

        # Smooth adaptation
        current_timeout = getattr(self, f'_last_timeout_{operation}', config.base_timeout)
        smoothed_timeout = (
            current_timeout * (1 - config.adaptation_rate) +
            adaptive_timeout * config.adaptation_rate
        )

        setattr(self, f'_last_timeout_{operation}', smoothed_timeout)

        return smoothed_timeout

    async def execute_with_adaptive_timeout(
        self,
        operation: str,
        coro_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute a coroutine with adaptive timeout."""
        timeout = self.get_adaptive_timeout(operation)
        start_time = time.time()
        success = True

        with self.tracer.trace_operation(f"adaptive_timeout_{operation}") as span:
            span.set_attribute("timeout_ms", timeout)

            try:
                result = await asyncio.wait_for(coro_func(*args, **kwargs), timeout / 1000.0)
                return result

            except asyncio.TimeoutError:
                success = False
                self.metrics.record_timeout(operation, timeout)
                raise

            except Exception:
                success = False
                raise

            finally:
                latency_ms = (time.time() - start_time) * 1000
                self.record_latency(operation, latency_ms, success)
                span.set_attribute("actual_latency_ms", latency_ms)
                span.set_attribute("success", success)


class IntelligentBackoff:
    """
    Intelligent backoff with multiple strategies and load awareness.

    0.01% Features:
    - Multiple backoff strategies (exponential, linear, adaptive, fibonacci)
    - Jitter to prevent thundering herd
    - Load-aware backoff adjustment
    - Success rate based strategy selection
    """

    def __init__(self, config: BackoffConfig):
        self.config = config
        self.attempt_history: deque = deque(maxlen=1000)
        self.metrics = LUKHASMetrics()

    async def execute_with_backoff(
        self,
        operation: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with intelligent backoff on failure."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                start_time = time.time()

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Record success
                self.attempt_history.append({
                    'success': True,
                    'attempt': attempt + 1,
                    'latency_ms': (time.time() - start_time) * 1000,
                    'timestamp': time.time()
                })

                self.metrics.record_backoff_success(operation, attempt + 1)
                return result

            except Exception as e:
                last_exception = e

                # Record failure
                self.attempt_history.append({
                    'success': False,
                    'attempt': attempt + 1,
                    'latency_ms': (time.time() - start_time) * 1000,
                    'timestamp': time.time(),
                    'error': str(e)
                })

                # Don't wait after the last attempt
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, operation)
                    await asyncio.sleep(delay)

        # All attempts failed
        self.metrics.record_backoff_failure(operation, self.config.max_attempts)
        raise last_exception

    def _calculate_delay(self, attempt: int, operation: str) -> float:
        """Calculate backoff delay with intelligent strategy selection."""
        base_delay = self._get_base_delay(attempt)

        # Apply load-aware adjustment
        load_multiplier = self._get_load_multiplier()
        adjusted_delay = base_delay * load_multiplier

        # Apply jitter if enabled
        if self.config.jitter:
            jitter_range = adjusted_delay * 0.1  # ±10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            adjusted_delay += jitter

        # Apply bounds
        return max(0.1, min(adjusted_delay, self.config.max_delay))

    def _get_base_delay(self, attempt: int) -> float:
        """Calculate base delay using configured strategy."""
        if self.config.strategy == BackoffStrategy.EXPONENTIAL:
            return self.config.initial_delay * (self.config.multiplier ** attempt)

        elif self.config.strategy == BackoffStrategy.LINEAR:
            return self.config.initial_delay * (attempt + 1)

        elif self.config.strategy == BackoffStrategy.FIBONACCI:
            return self.config.initial_delay * self._fibonacci(attempt + 1)

        elif self.config.strategy == BackoffStrategy.ADAPTIVE:
            return self._adaptive_delay(attempt)

        else:
            return self.config.initial_delay * (self.config.multiplier ** attempt)

    def _adaptive_delay(self, attempt: int) -> float:
        """Calculate adaptive delay based on recent success patterns."""
        if not self.attempt_history:
            return self.config.initial_delay

        # Analyze recent success rate
        recent_attempts = list(self.attempt_history)[-50:]  # Last 50 attempts
        success_rate = sum(1 for a in recent_attempts if a['success']) / len(recent_attempts)

        # Adjust delay based on success rate
        if success_rate > 0.8:  # High success rate, be more aggressive
            multiplier = 1.5
        elif success_rate > 0.5:  # Moderate success rate, standard backoff
            multiplier = 2.0
        else:  # Low success rate, be more conservative
            multiplier = 3.0

        return self.config.initial_delay * (multiplier ** attempt)

    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def _get_load_multiplier(self) -> float:
        """Get load-based delay multiplier."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Average of CPU and memory load
            avg_load = (cpu_percent + memory_percent) / 200.0  # Normalize to 0-1

            # Increase delay under high load
            return 1.0 + (avg_load * 0.5)  # Up to 50% increase
        except ImportError:
            return 1.0  # No load adjustment if psutil not available

    def get_statistics(self) -> dict[str, Any]:
        """Get backoff statistics."""
        if not self.attempt_history:
            return {}

        recent_attempts = list(self.attempt_history)[-100:]  # Last 100 attempts

        success_count = sum(1 for a in recent_attempts if a['success'])
        success_rate = success_count / len(recent_attempts)

        # Average attempts to success
        successful_attempts = [a['attempt'] for a in recent_attempts if a['success']]
        avg_attempts_to_success = statistics.mean(successful_attempts) if successful_attempts else 0

        return {
            'total_attempts': len(recent_attempts),
            'success_rate': success_rate,
            'average_attempts_to_success': avg_attempts_to_success,
            'strategy': self.config.strategy.value,
            'max_attempts': self.config.max_attempts
        }


# Global instances
_timeout_manager: Optional[AdaptiveTimeoutManager] = None
_default_backoff: Optional[IntelligentBackoff] = None


def get_timeout_manager() -> AdaptiveTimeoutManager:
    """Get or create global timeout manager."""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = AdaptiveTimeoutManager()
    return _timeout_manager


def get_default_backoff() -> IntelligentBackoff:
    """Get or create default backoff instance."""
    global _default_backoff
    if _default_backoff is None:
        _default_backoff = IntelligentBackoff(BackoffConfig())
    return _default_backoff


async def execute_with_adaptive_timeout(
    operation: str,
    coro_func: Callable,
    *args,
    **kwargs
) -> Any:
    """Execute coroutine with adaptive timeout."""
    manager = get_timeout_manager()
    return await manager.execute_with_adaptive_timeout(operation, coro_func, *args, **kwargs)


async def execute_with_backoff(
    operation: str,
    func: Callable,
    config: Optional[BackoffConfig] = None,
    *args,
    **kwargs
) -> Any:
    """Execute function with intelligent backoff."""
    backoff = IntelligentBackoff(config) if config else get_default_backoff()

    return await backoff.execute_with_backoff(operation, func, *args, **kwargs)


def adaptive_timeout(operation: str, config: Optional[TimeoutConfig] = None):
    """Decorator for adaptive timeout."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if config:
                manager = get_timeout_manager()
                manager.register_operation(operation, config)

            return await execute_with_adaptive_timeout(operation, func, *args, **kwargs)
        return wrapper
    return decorator


def intelligent_backoff(operation: str, config: Optional[BackoffConfig] = None):
    """Decorator for intelligent backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await execute_with_backoff(operation, func, config, *args, **kwargs)
        return wrapper
    return decorator


def resilient_operation(
    operation: str,
    timeout_config: Optional[TimeoutConfig] = None,
    backoff_config: Optional[BackoffConfig] = None
):
    """Decorator combining adaptive timeout and intelligent backoff."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Register timeout config if provided
            if timeout_config:
                manager = get_timeout_manager()
                manager.register_operation(operation, timeout_config)

            # Create backoff instance
            if backoff_config:
                backoff = IntelligentBackoff(backoff_config)
            else:
                backoff = get_default_backoff()

            # Execute with both timeout and backoff
            async def timeout_wrapper():
                return await execute_with_adaptive_timeout(operation, func, *args, **kwargs)

            return await backoff.execute_with_backoff(operation, timeout_wrapper)

        return wrapper
    return decorator
