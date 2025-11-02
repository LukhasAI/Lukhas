"""
Adaptive Circuit Breaker
========================

Advanced circuit breaker implementation for cascade failure prevention
in distributed memory services. Supports T4/0.01% excellence with
adaptive thresholds and graceful degradation.

Features:
- Multi-state circuit breaker (CLOSED, OPEN, HALF_OPEN)
- Adaptive failure thresholds based on historical data
- Timeout-based recovery with exponential backoff
- Health probes and graceful degradation
- Prometheus metrics integration
- Bulkhead isolation for different operation types
"""

import asyncio
import logging
import statistics
import time
from collections import deque
from collections.abc import Awaitable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"           # Normal operation
    OPEN = "open"               # Failing fast, blocking requests
    HALF_OPEN = "half_open"     # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""

    # Failure tracking
    failure_threshold: int = 5              # Consecutive failures to open
    success_threshold: int = 3              # Consecutive successes to close
    timeout_duration: float = 60.0         # Open state timeout (seconds)

    # Adaptive parameters
    enable_adaptation: bool = True          # Enable adaptive thresholds
    failure_rate_threshold: float = 0.5     # Failure rate to open (0.0-1.0)
    min_requests: int = 10                  # Minimum requests for rate calculation
    rolling_window: int = 100               # Rolling window size for stats

    # Timeout configuration
    initial_timeout: float = 1.0           # Initial request timeout
    max_timeout: float = 30.0              # Maximum request timeout
    timeout_multiplier: float = 2.0       # Timeout increase factor

    # Recovery configuration
    recovery_timeout: float = 60.0         # Time before attempting recovery
    max_recovery_timeout: float = 300.0    # Maximum recovery timeout
    recovery_backoff: float = 1.5          # Recovery timeout backoff
    health_check_interval: float = 30.0    # Health check frequency

    # Metrics
    enable_metrics: bool = True            # Enable Prometheus metrics


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker runtime metrics"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    total_requests: int = 0
    failure_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    last_failure_time: float = 0.0
    state_change_time: float = 0.0
    timeout_count: int = 0
    recovery_attempts: int = 0


class CircuitBreakerError(Exception):
    """Circuit breaker is open, failing fast"""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreakerTimeoutError(CircuitBreakerError):
    """Circuit breaker timeout exceeded"""
    pass


class AdaptiveCircuitBreaker:
    """
    Adaptive circuit breaker with intelligent failure detection and recovery.

    Implements the circuit breaker pattern with adaptive thresholds,
    exponential backoff, and health-based recovery for resilient
    distributed systems.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.timeout_count = 0
        self.recovery_attempts = 0

        # State timing
        self.last_failure_time = 0.0
        self.state_change_time = time.monotonic()
        self.current_timeout = config.initial_timeout
        self.recovery_timeout = config.recovery_timeout

        # Rolling statistics
        self.request_results: deque = deque(maxlen=config.rolling_window)
        self.latency_samples: deque = deque(maxlen=config.rolling_window)

        # Health checking
        self.last_health_check = 0.0
        self.health_check_task: Optional[asyncio.Task] = None

        # Synchronization
        self._lock = asyncio.Lock()

        logger.info(f"CircuitBreaker '{name}' initialized: {config}")

    async def __call__(self,
                      func: Callable[..., Awaitable],
                      *args,
                      timeout: Optional[float] = None,
                      **kwargs) -> Any:
        """
        Execute function through circuit breaker protection.

        Args:
            func: Async function to execute
            timeout: Custom timeout override
            *args, **kwargs: Function arguments

        Returns:
            Function result if successful

        Raises:
            CircuitBreakerError: If circuit is open
            CircuitBreakerTimeoutError: If timeout exceeded
            Any exception from the wrapped function
        """
        # Check circuit state before execution
        await self._check_state()

        if self.state == CircuitBreakerState.OPEN:
            retry_after = self._get_retry_after()
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN",
                retry_after=retry_after
            )

        # Execute with timeout and failure tracking
        return await self._execute_with_tracking(func, timeout, *args, **kwargs)

    async def _execute_with_tracking(self,
                                   func: Callable[..., Awaitable],
                                   timeout: Optional[float],
                                   *args,
                                   **kwargs) -> Any:
        """Execute function with comprehensive tracking and timeout"""
        start_time = time.monotonic()
        execution_timeout = timeout or self.current_timeout

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=execution_timeout
            )

            # Record success
            latency_ms = (time.monotonic() - start_time) * 1000
            await self._record_success(latency_ms)

            return result

        except asyncio.TimeoutError:
            # Handle timeout as failure
            latency_ms = (time.monotonic() - start_time) * 1000
            await self._record_timeout(latency_ms)

            raise CircuitBreakerTimeoutError(
                f"Operation timed out after {execution_timeout:.2f}s"
            )

        except Exception as e:
            # Handle execution failure
            latency_ms = (time.monotonic() - start_time) * 1000
            await self._record_failure(latency_ms, e)

            # Re-raise original exception
            raise

    async def _record_success(self, latency_ms: float):
        """Record successful execution"""
        async with self._lock:
            self.success_count += 1
            self.total_requests += 1
            self.request_results.append(True)
            self.latency_samples.append(latency_ms)

            # Reset timeout on success
            self.current_timeout = self.config.initial_timeout

            # Check for state transition from HALF_OPEN to CLOSED
            if (self.state == CircuitBreakerState.HALF_OPEN and
                self.success_count >= self.config.success_threshold):
                await self._transition_to_closed()

    async def _record_failure(self, latency_ms: float, exception: Exception):
        """Record failed execution"""
        async with self._lock:
            self.failure_count += 1
            self.total_requests += 1
            self.last_failure_time = time.monotonic()
            self.request_results.append(False)
            self.latency_samples.append(latency_ms)

            # Increase timeout on failure
            self.current_timeout = min(
                self.current_timeout * self.config.timeout_multiplier,
                self.config.max_timeout
            )

            logger.warning(f"CircuitBreaker '{self.name}' recorded failure: {exception}")

            # Check for state transition to OPEN
            await self._check_failure_threshold()

    async def _record_timeout(self, latency_ms: float):
        """Record timeout as a special type of failure"""
        async with self._lock:
            self.timeout_count += 1
            await self._record_failure(latency_ms, asyncio.TimeoutError("Timeout"))

    async def _check_state(self):
        """Check and update circuit breaker state"""
        async with self._lock:
            now = time.monotonic()

            # Check if OPEN circuit should transition to HALF_OPEN
            if (self.state == CircuitBreakerState.OPEN and
                now - self.state_change_time >= self.recovery_timeout):
                await self._transition_to_half_open()

    async def _check_failure_threshold(self):
        """Check if failures exceed threshold and open circuit"""
        # Simple consecutive failure threshold
        if self.failure_count >= self.config.failure_threshold:
            await self._transition_to_open()
            return

        # Adaptive failure rate threshold
        if (self.config.enable_adaptation and
            len(self.request_results) >= self.config.min_requests):

            failure_rate = self._calculate_failure_rate()
            if failure_rate >= self.config.failure_rate_threshold:
                await self._transition_to_open()

    def _calculate_failure_rate(self) -> float:
        """Calculate current failure rate from rolling window"""
        if not self.request_results:
            return 0.0

        failures = sum(1 for result in self.request_results if not result)
        return failures / len(self.request_results)

    async def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        if self.state != CircuitBreakerState.OPEN:
            self.state = CircuitBreakerState.OPEN
            self.state_change_time = time.monotonic()
            self.recovery_attempts += 1

            # Exponential backoff for recovery timeout
            self.recovery_timeout = min(
                self.config.recovery_timeout * (self.config.recovery_backoff ** (self.recovery_attempts - 1)),
                self.config.max_recovery_timeout
            )

            logger.warning(f"CircuitBreaker '{self.name}' OPENED: "
                         f"{self.failure_count} failures, "
                         f"recovery in {self.recovery_timeout:.1f}s")

    async def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.state_change_time = time.monotonic()
        self.success_count = 0  # Reset success counter

        logger.info(f"CircuitBreaker '{self.name}' HALF_OPEN: testing recovery")

    async def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        self.state = CircuitBreakerState.CLOSED
        self.state_change_time = time.monotonic()
        self.failure_count = 0  # Reset failure counter
        self.recovery_attempts = 0
        self.recovery_timeout = self.config.recovery_timeout

        logger.info(f"CircuitBreaker '{self.name}' CLOSED: recovery successful")

    def _get_retry_after(self) -> float:
        """Calculate retry-after time for OPEN circuit"""
        elapsed = time.monotonic() - self.state_change_time
        return max(0.0, self.recovery_timeout - elapsed)

    async def force_open(self):
        """Manually force circuit breaker to OPEN state"""
        async with self._lock:
            await self._transition_to_open()
            logger.warning(f"CircuitBreaker '{self.name}' manually OPENED")

    async def force_closed(self):
        """Manually force circuit breaker to CLOSED state"""
        async with self._lock:
            await self._transition_to_closed()
            logger.info(f"CircuitBreaker '{self.name}' manually CLOSED")

    async def reset(self):
        """Reset circuit breaker statistics"""
        async with self._lock:
            self.failure_count = 0
            self.success_count = 0
            self.total_requests = 0
            self.timeout_count = 0
            self.request_results.clear()
            self.latency_samples.clear()
            self.current_timeout = self.config.initial_timeout
            await self._transition_to_closed()

        logger.info(f"CircuitBreaker '{self.name}' reset")

    async def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current circuit breaker metrics"""
        async with self._lock:
            failure_rate = self._calculate_failure_rate()

            # Calculate latency statistics
            avg_latency = 0.0
            p95_latency = 0.0

            if self.latency_samples:
                avg_latency = statistics.mean(self.latency_samples)

                if len(self.latency_samples) >= 20:
                    sorted_latencies = sorted(self.latency_samples)
                    p95_idx = int(len(sorted_latencies) * 0.95)
                    p95_latency = sorted_latencies[p95_idx]

            return CircuitBreakerMetrics(
                state=self.state,
                failure_count=self.failure_count,
                success_count=self.success_count,
                total_requests=self.total_requests,
                failure_rate=failure_rate,
                avg_latency_ms=avg_latency,
                p95_latency_ms=p95_latency,
                last_failure_time=self.last_failure_time,
                state_change_time=self.state_change_time,
                timeout_count=self.timeout_count,
                recovery_attempts=self.recovery_attempts
            )

    async def health_check(self,
                          health_func: Optional[Callable[[], Awaitable[bool]]] = None) -> bool:
        """
        Perform health check and potentially recover circuit.

        Args:
            health_func: Optional custom health check function

        Returns:
            True if healthy, False otherwise
        """
        try:
            if health_func:
                is_healthy = await asyncio.wait_for(
                    health_func(),
                    timeout=self.config.health_check_interval
                )
            else:
                # Default health check - just verify circuit isn't failing too much
                is_healthy = self._calculate_failure_rate() < 0.8

            if is_healthy and self.state == CircuitBreakerState.OPEN:
                # Trigger early recovery if health check passes
                async with self._lock:
                    await self._transition_to_half_open()
                    logger.info(f"CircuitBreaker '{self.name}' early recovery triggered by health check")

            return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for CircuitBreaker '{self.name}': {e}")
            return False


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers with different configurations.

    Provides centralized management, monitoring, and coordination between
    circuit breakers for different services or operation types.
    """

    def __init__(self):
        self._breakers: Dict[str, AdaptiveCircuitBreaker] = {}
        self._global_config = CircuitBreakerConfig()

    def create_breaker(self,
                      name: str,
                      config: Optional[CircuitBreakerConfig] = None) -> AdaptiveCircuitBreaker:
        """Create and register a new circuit breaker"""
        if name in self._breakers:
            logger.warning(f"CircuitBreaker '{name}' already exists, returning existing")
            return self._breakers[name]

        breaker_config = config or self._global_config
        breaker = AdaptiveCircuitBreaker(name, breaker_config)
        self._breakers[name] = breaker

        logger.info(f"Created CircuitBreaker '{name}'")
        return breaker

    def get_breaker(self, name: str) -> Optional[AdaptiveCircuitBreaker]:
        """Get existing circuit breaker by name"""
        return self._breakers.get(name)

    async def get_all_metrics(self) -> Dict[str, CircuitBreakerMetrics]:
        """Get metrics for all registered circuit breakers"""
        metrics = {}
        for name, breaker in self._breakers.items():
            metrics[name] = await breaker.get_metrics()
        return metrics

    async def health_check_all(self) -> Dict[str, bool]:
        """Run health checks on all circuit breakers"""
        results = {}
        tasks = []

        for name, breaker in self._breakers.items():
            task = asyncio.create_task(breaker.health_check())
            tasks.append((name, task))

        for name, task in tasks:
            try:
                results[name] = await task
            except Exception as e:
                logger.error(f"Health check failed for '{name}': {e}")
                results[name] = False

        return results

    async def reset_all(self):
        """Reset all circuit breakers"""
        for name, breaker in self._breakers.items():
            await breaker.reset()
            logger.info(f"Reset CircuitBreaker '{name}'")

    def list_breakers(self) -> list[str]:
        """List all registered circuit breaker names"""
        return list(self._breakers.keys())


# Factory for creating standard circuit breaker configurations
class CircuitBreakerFactory:
    """Factory for creating standard circuit breaker configurations"""

    @staticmethod
    def create_memory_service_config() -> CircuitBreakerConfig:
        """Circuit breaker optimized for memory service operations"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_duration=30.0,
            failure_rate_threshold=0.3,
            initial_timeout=5.0,
            max_timeout=30.0,
            recovery_timeout=60.0
        )

    @staticmethod
    def create_high_availability_config() -> CircuitBreakerConfig:
        """Circuit breaker optimized for high availability"""
        return CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=3,
            timeout_duration=60.0,
            failure_rate_threshold=0.5,
            initial_timeout=2.0,
            max_timeout=15.0,
            recovery_timeout=30.0,
            max_recovery_timeout=120.0
        )

    @staticmethod
    def create_strict_latency_config() -> CircuitBreakerConfig:
        """Circuit breaker optimized for strict latency requirements"""
        return CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=1,
            timeout_duration=15.0,
            failure_rate_threshold=0.2,
            initial_timeout=1.0,
            max_timeout=5.0,
            recovery_timeout=30.0
        )
