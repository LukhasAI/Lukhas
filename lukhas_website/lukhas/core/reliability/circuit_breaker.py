#!/usr/bin/env python3
"""
Circuit Breaker Pattern for 0.01% Reliability

Implements intelligent circuit breaking with adaptive thresholds,
exponential backoff, and graceful degradation - the kind of subtle
reliability that distinguishes top-tier systems.
"""

import asyncio
import statistics
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitMetrics:
    """Circuit breaker performance metrics."""
    request_count: int = 0
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    average_response_time: float = 0.0
    p95_response_time: float = 0.0


class AdaptiveCircuitBreaker:
    """
    Adaptive circuit breaker with intelligent failure detection.

    0.01% Features:
    - Adaptive thresholds based on historical performance
    - Intelligent recovery with gradual reopening
    - Performance-based failure detection (not just errors)
    - Rich telemetry and correlation IDs
    """

    def __init__(
        self,
        name: str,
        failure_threshold: float = 0.5,  # 50% failure rate
        recovery_timeout: float = 60.0,  # 60 seconds
        min_request_threshold: int = 10,
        performance_threshold_ms: float = 1000.0,  # 1s latency = degraded
        window_size: int = 100
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.min_request_threshold = min_request_threshold
        self.performance_threshold_ms = performance_threshold_ms
        self.window_size = window_size

        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()

        # Sliding window for adaptive thresholds
        self.recent_requests: deque = deque(maxlen=window_size)
        self.response_times: deque = deque(maxlen=window_size)

        # Adaptive threshold calculation
        self.baseline_performance = None
        self.last_state_change = time.time()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        correlation_id = kwargs.pop('correlation_id', f"cb_{int(time.time() * 1000)}")

        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print(f"🔄 Circuit {self.name} attempting recovery (correlation: {correlation_id})")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit {self.name} is OPEN (correlation: {correlation_id})"
                )

        # Execute the function
        start_time = time.time()
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

            # Record success
            response_time = (time.time() - start_time) * 1000  # ms
            self._record_success(response_time, correlation_id)

            return result

        except Exception as e:
            # Record failure
            response_time = (time.time() - start_time) * 1000  # ms
            self._record_failure(response_time, correlation_id, e)
            raise

    def _record_success(self, response_time: float, correlation_id: str):
        """Record successful request with performance analysis."""
        self.metrics.request_count += 1
        self.metrics.success_count += 1

        self.recent_requests.append({
            'success': True,
            'response_time': response_time,
            'timestamp': time.time(),
            'correlation_id': correlation_id
        })
        self.response_times.append(response_time)

        # Update performance metrics
        self._update_performance_metrics()

        # Check if we should close circuit from half-open
        if self.state == CircuitState.HALF_OPEN and self._should_close_circuit():
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            print(f"✅ Circuit {self.name} recovered (correlation: {correlation_id})")

        # Performance-based degradation detection (0.01% feature)
        if self._is_performance_degraded():
            print(f"⚠️ Performance degradation detected in {self.name} (correlation: {correlation_id})")

    def _record_failure(self, response_time: float, correlation_id: str, error: Exception):
        """Record failed request with rich error context."""
        self.metrics.request_count += 1
        self.metrics.failure_count += 1
        self.metrics.last_failure_time = time.time()

        self.recent_requests.append({
            'success': False,
            'response_time': response_time,
            'timestamp': time.time(),
            'correlation_id': correlation_id,
            'error_type': type(error).__name__,
            'error_message': str(error)
        })

        # Check if we should open circuit
        if self._should_open_circuit():
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            print(f"🔴 Circuit {self.name} OPENED due to failures (correlation: {correlation_id})")

    def _should_open_circuit(self) -> bool:
        """Intelligent decision on when to open circuit."""
        if len(self.recent_requests) < self.min_request_threshold:
            return False

        # Calculate recent failure rate
        recent_failures = sum(1 for req in self.recent_requests if not req['success'])
        failure_rate = recent_failures / len(self.recent_requests)

        # Adaptive threshold: higher threshold during known degradation periods
        adjusted_threshold = self._get_adaptive_threshold()

        return failure_rate >= adjusted_threshold

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return time.time() - self.last_state_change >= self.recovery_timeout

    def _should_close_circuit(self) -> bool:
        """Check if circuit should close from half-open state."""
        if len(self.recent_requests) < 5:  # Need some requests to judge
            return False

        recent_successes = sum(1 for req in self.recent_requests[-5:] if req['success'])
        return recent_successes >= 4  # 80% success rate in recent requests

    def _get_adaptive_threshold(self) -> float:
        """Calculate adaptive failure threshold based on historical performance."""
        if not self.baseline_performance:
            return self.failure_threshold

        # During known poor performance periods, be more tolerant
        current_p95 = self._calculate_p95_latency()
        if current_p95 > self.baseline_performance * 2:
            return min(self.failure_threshold * 1.5, 0.8)  # More tolerant, but cap at 80%

        return self.failure_threshold

    def _is_performance_degraded(self) -> bool:
        """Detect performance degradation beyond just failures."""
        if len(self.response_times) < 10:
            return False

        p95_latency = self._calculate_p95_latency()

        # Initialize baseline if not set
        if not self.baseline_performance:
            self.baseline_performance = p95_latency
            return False

        # Consider degraded if P95 latency is 3x baseline
        return p95_latency > self.baseline_performance * 3

    def _calculate_p95_latency(self) -> float:
        """Calculate P95 latency from recent response times."""
        if not self.response_times:
            return 0.0
        if len(self.response_times) < 2:
            return max(self.response_times)
        try:
            return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
        except Exception:
            # Fallback for small datasets
            return max(self.response_times)

    def _update_performance_metrics(self):
        """Update rolling performance metrics."""
        if self.response_times:
            self.metrics.average_response_time = statistics.mean(self.response_times)
            self.metrics.p95_response_time = self._calculate_p95_latency()

    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status for monitoring."""
        if len(self.recent_requests) > 0:
            failure_rate = sum(1 for req in self.recent_requests if not req['success']) / len(self.recent_requests)
        else:
            failure_rate = 0.0

        return {
            'circuit_name': self.name,
            'state': self.state.value,
            'failure_rate': failure_rate,
            'request_count': self.metrics.request_count,
            'success_count': self.metrics.success_count,
            'failure_count': self.metrics.failure_count,
            'average_response_time_ms': self.metrics.average_response_time,
            'p95_response_time_ms': self.metrics.p95_response_time,
            'time_in_current_state': time.time() - self.last_state_change,
            'baseline_performance_ms': self.baseline_performance,
            'performance_degraded': self._is_performance_degraded()
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# 0.01% Feature: Global Circuit Breaker Registry
class CircuitBreakerRegistry:
    """Global registry for managing multiple circuit breakers."""

    def __init__(self):
        self.breakers: Dict[str, AdaptiveCircuitBreaker] = {}

    def get_or_create(self, name: str, **kwargs) -> AdaptiveCircuitBreaker:
        """Get existing circuit breaker or create new one."""
        if name not in self.breakers:
            self.breakers[name] = AdaptiveCircuitBreaker(name, **kwargs)
        return self.breakers[name]

    def get_global_health(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers."""
        return {
            name: breaker.get_health_status()
            for name, breaker in self.breakers.items()
        }

    def get_degraded_services(self) -> List[str]:
        """Get list of services showing performance degradation."""
        degraded = []
        for name, breaker in self.breakers.items():
            if breaker._is_performance_degraded() or breaker.state != CircuitState.CLOSED:
                degraded.append(name)
        return degraded


# Global registry instance
_circuit_registry = CircuitBreakerRegistry()


def circuit_breaker(name: str, **kwargs):
    """Decorator for applying circuit breaker pattern."""
    def decorator(func):
        # Prevent double-wrapping that can cause RecursionError
        if getattr(func, "__lukhas_cb_wrapped__", False):
            return func

        breaker = _circuit_registry.get_or_create(name, **kwargs)

        async def async_wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.__lukhas_cb_wrapped__ = True  # type: ignore
        return wrapper

    return decorator


def get_circuit_health() -> Dict[str, Any]:
    """Get global circuit breaker health status."""
    return _circuit_registry.get_global_health()


def get_degraded_services() -> List[str]:
    """Get list of degraded services."""
    return _circuit_registry.get_degraded_services()
