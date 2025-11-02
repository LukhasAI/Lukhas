#!/usr/bin/env python3
"""
LUKHAS Advanced Circuit Breaker & Fault Tolerance System

Enterprise-grade circuit breaker implementation with adaptive thresholds,
intelligent recovery, and comprehensive failure pattern analysis.

# ΛTAG: circuit_breaker, fault_tolerance, resilience, auto_healing
"""

import asyncio
import logging
import random
import statistics
import time
from abc import ABC, abstractmethod
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


class FailurePattern(Enum):
    """Types of failure patterns detected."""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    SLOW_RESPONSE = "slow_response"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    # Failure thresholds
    failure_threshold: int = 5              # Failures before opening
    failure_rate_threshold: float = 0.5     # Failure rate (0-1) before opening
    slow_call_threshold: float = 2.0        # Slow call duration threshold (seconds)
    slow_call_rate_threshold: float = 0.5   # Slow call rate before opening

    # Time windows
    failure_window_sec: float = 60.0        # Window for counting failures
    recovery_timeout_sec: float = 30.0      # Time in OPEN before trying HALF_OPEN
    half_open_calls: int = 3                # Test calls in HALF_OPEN state

    # Advanced features
    adaptive_thresholds: bool = True        # Enable adaptive threshold learning
    exponential_backoff: bool = True        # Use exponential backoff for recovery
    jitter: bool = True                     # Add jitter to prevent thundering herd

    # Health scoring
    health_check_interval: float = 10.0     # Health check frequency
    auto_healing_enabled: bool = True       # Enable automatic healing attempts


@dataclass
class CallResult:
    """Result of a circuit breaker protected call."""

    timestamp: float
    duration_sec: float
    success: bool
    failure_pattern: Optional[FailurePattern] = None
    error_message: Optional[str] = None
    response_data: Any = None


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    slow_calls: int = 0

    current_failure_rate: float = 0.0
    current_slow_rate: float = 0.0
    average_response_time: float = 0.0

    state_changes: int = 0
    last_state_change: Optional[float] = None
    time_in_open: float = 0.0
    time_in_half_open: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "slow_calls": self.slow_calls,
            "current_failure_rate": self.current_failure_rate,
            "current_slow_rate": self.current_slow_rate,
            "average_response_time": self.average_response_time,
            "state_changes": self.state_changes,
            "last_state_change": self.last_state_change,
            "time_in_open": self.time_in_open,
            "time_in_half_open": self.time_in_half_open
        }


class FailureDetector(ABC):
    """Abstract base class for failure detection strategies."""

    @abstractmethod
    def is_failure(self, result: CallResult) -> bool:
        """Determine if a call result represents a failure."""
        pass


class DefaultFailureDetector(FailureDetector):
    """Default failure detection strategy."""

    def __init__(self,
                 slow_call_threshold: float = 2.0,
                 timeout_threshold: float = 30.0):
        self.slow_call_threshold = slow_call_threshold
        self.timeout_threshold = timeout_threshold

    def is_failure(self, result: CallResult) -> bool:
        """Determine if call is a failure."""
        if not result.success:
            return True

        if result.duration_sec > self.slow_call_threshold:
            return True

        return False


class AdaptiveThresholdCalculator:
    """Calculates adaptive thresholds based on historical performance."""

    def __init__(self,
                 history_size: int = 1000,
                 percentile: float = 0.95):
        self.history_size = history_size
        self.percentile = percentile
        self.response_times: deque = deque(maxlen=history_size)
        self.success_rates: deque = deque(maxlen=100)  # Last 100 windows

    def add_response_time(self, duration: float) -> None:
        """Add response time to history."""
        self.response_times.append(duration)

    def add_success_rate(self, rate: float) -> None:
        """Add success rate to history."""
        self.success_rates.append(rate)

    def get_adaptive_slow_threshold(self) -> float:
        """Calculate adaptive slow call threshold."""
        if len(self.response_times) < 10:
            return 2.0  # Default

        # Use 95th percentile of recent response times
        return statistics.quantile(list(self.response_times), self.percentile)

    def get_adaptive_failure_threshold(self) -> float:
        """Calculate adaptive failure rate threshold."""
        if len(self.success_rates) < 5:
            return 0.5  # Default

        # Use mean success rate minus 2 standard deviations
        mean_success = statistics.mean(self.success_rates)
        if len(self.success_rates) > 1:
            std_success = statistics.stdev(self.success_rates)
            threshold = max(0.1, mean_success - (2 * std_success))
        else:
            threshold = 0.5

        # Convert success rate threshold to failure rate threshold
        return 1.0 - threshold


class CircuitBreaker:
    """Advanced circuit breaker with adaptive behavior."""

    def __init__(self,
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None,
                 failure_detector: Optional[FailureDetector] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker identifier
            config: Configuration parameters
            failure_detector: Strategy for detecting failures
        """

        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.failure_detector = failure_detector or DefaultFailureDetector(
            slow_call_threshold=self.config.slow_call_threshold
        )

        # State management
        self.state = CircuitState.CLOSED
        self.state_change_time = time.time()
        self.half_open_calls_made = 0

        # Call history and statistics
        self.call_history: deque = deque(maxlen=1000)
        self.recent_calls: deque = deque()  # Sliding window
        self.stats = CircuitBreakerStats()

        # Adaptive behavior
        if self.config.adaptive_thresholds:
            self.adaptive_calculator = AdaptiveThresholdCalculator()
        else:
            self.adaptive_calculator = None

        # Health monitoring
        self.last_health_check = time.time()
        self.consecutive_health_failures = 0

        # Backoff calculation
        self.backoff_multiplier = 1.0
        self.max_backoff = 300.0  # 5 minutes max

        # Telemetry integration
        try:
            from observability.telemetry_system import get_telemetry
            self.telemetry = get_telemetry()
        except ImportError:
            self.telemetry = None

    def _emit_telemetry(self, event_type: str, message: str, **kwargs) -> None:
        """Emit telemetry event if available."""
        if self.telemetry:
            self.telemetry.emit_event(
                component=f"circuit_breaker.{self.name}",
                event_type=event_type,
                message=message,
                **kwargs
            )

    def _emit_metric(self, metric_name: str, value: float, **kwargs) -> None:
        """Emit telemetry metric if available."""
        if self.telemetry:
            self.telemetry.emit_metric(
                component=f"circuit_breaker.{self.name}",
                metric_name=metric_name,
                value=value,
                **kwargs
            )

    def _clean_old_calls(self) -> None:
        """Remove calls outside the failure window."""
        cutoff_time = time.time() - self.config.failure_window_sec

        while self.recent_calls and self.recent_calls[0].timestamp < cutoff_time:
            self.recent_calls.popleft()

    def _calculate_current_rates(self) -> tuple[float, float]:
        """Calculate current failure and slow call rates."""
        self._clean_old_calls()

        if not self.recent_calls:
            return 0.0, 0.0

        total_calls = len(self.recent_calls)
        failed_calls = sum(1 for call in self.recent_calls
                          if self.failure_detector.is_failure(call))
        slow_calls = sum(1 for call in self.recent_calls
                        if call.duration_sec > self.config.slow_call_threshold)

        failure_rate = failed_calls / total_calls
        slow_rate = slow_calls / total_calls

        return failure_rate, slow_rate

    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened."""
        self._clean_old_calls()

        if len(self.recent_calls) < self.config.failure_threshold:
            return False

        failure_rate, slow_rate = self._calculate_current_rates()

        # Get thresholds (adaptive or static)
        if self.adaptive_calculator:
            failure_threshold = self.adaptive_calculator.get_adaptive_failure_threshold()
            slow_threshold = self.config.slow_call_rate_threshold  # Keep static for now
        else:
            failure_threshold = self.config.failure_rate_threshold
            slow_threshold = self.config.slow_call_rate_threshold

        # Check thresholds
        if failure_rate >= failure_threshold:
            self._emit_telemetry("circuit_opening",
                               f"Circuit opening due to failure rate: {failure_rate:.2f}")
            return True

        if slow_rate >= slow_threshold:
            self._emit_telemetry("circuit_opening",
                               f"Circuit opening due to slow rate: {slow_rate:.2f}")
            return True

        return False

    def _should_attempt_reset(self) -> bool:
        """Determine if should attempt to reset from OPEN state."""
        time_in_open = time.time() - self.state_change_time

        # Calculate recovery timeout with exponential backoff
        if self.config.exponential_backoff:
            recovery_timeout = self.config.recovery_timeout_sec * self.backoff_multiplier
            recovery_timeout = min(recovery_timeout, self.max_backoff)
        else:
            recovery_timeout = self.config.recovery_timeout_sec

        # Add jitter to prevent thundering herd
        if self.config.jitter:
            jitter_factor = 0.1  # ±10%
            jitter = random.uniform(-jitter_factor, jitter_factor)
            recovery_timeout *= (1 + jitter)

        return time_in_open >= recovery_timeout

    def _transition_to_state(self, new_state: CircuitState) -> None:
        """Transition to new circuit state."""
        old_state = self.state
        self.state = new_state
        self.state_change_time = time.time()
        self.stats.state_changes += 1
        self.stats.last_state_change = self.state_change_time

        # Reset half-open counter
        if new_state != CircuitState.HALF_OPEN:
            self.half_open_calls_made = 0

        # Adjust backoff multiplier
        if new_state == CircuitState.CLOSED:
            self.backoff_multiplier = 1.0  # Reset on successful recovery
        elif new_state == CircuitState.OPEN and old_state == CircuitState.HALF_OPEN:
            self.backoff_multiplier = min(self.backoff_multiplier * 2,
                                        self.max_backoff / self.config.recovery_timeout_sec)

        self._emit_telemetry("state_change",
                           f"Circuit state: {old_state.value} → {new_state.value}")
        self._emit_metric("circuit_state", float(list(CircuitState).index(new_state)))

    def _record_call(self, result: CallResult) -> None:
        """Record call result and update statistics."""
        # Add to history
        self.call_history.append(result)
        self.recent_calls.append(result)

        # Update statistics
        self.stats.total_calls += 1

        if result.success:
            self.stats.successful_calls += 1
        else:
            self.stats.failed_calls += 1

        if result.duration_sec > self.config.slow_call_threshold:
            self.stats.slow_calls += 1

        # Update adaptive calculator
        if self.adaptive_calculator:
            self.adaptive_calculator.add_response_time(result.duration_sec)

        # Calculate current rates
        failure_rate, slow_rate = self._calculate_current_rates()
        self.stats.current_failure_rate = failure_rate
        self.stats.current_slow_rate = slow_rate

        # Calculate average response time
        if self.recent_calls:
            self.stats.average_response_time = statistics.mean(
                call.duration_sec for call in self.recent_calls
            )

        # Update adaptive calculator with success rate
        if self.adaptive_calculator and len(self.recent_calls) >= 10:
            success_rate = 1.0 - failure_rate
            self.adaptive_calculator.add_success_rate(success_rate)

        # Emit metrics
        self._emit_metric("call_duration", result.duration_sec)
        self._emit_metric("failure_rate", failure_rate)
        self._emit_metric("slow_rate", slow_rate)

    @asynccontextmanager
    async def protect(self, operation_name: str = "operation"):
        """
        Context manager for circuit breaker protection.
        
        Args:
            operation_name: Name of the operation being protected
            
        Yields:
            None if call is allowed, raises CircuitBreakerOpenError if rejected
            
        Raises:
            CircuitBreakerOpenError: If circuit is open and call is rejected
        """

        # Check if call should be allowed
        if not self._is_call_allowed():
            self.stats.rejected_calls += 1
            self._emit_telemetry("call_rejected",
                               f"Call rejected in {self.state.value} state")
            raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is {self.state.value}")

        start_time = time.time()
        success = False
        error_message = None
        failure_pattern = None

        try:
            # Use telemetry tracing if available
            if self.telemetry:
                async with self.telemetry.trace_operation(
                    operation_name=f"circuit_breaker.{operation_name}",
                    component=f"circuit_breaker.{self.name}"
                ) as span:
                    span.add_log(f"Circuit state: {self.state.value}")
                    yield
                    success = True
            else:
                yield
                success = True

        except asyncio.TimeoutError as e:
            failure_pattern = FailurePattern.TIMEOUT
            error_message = str(e)
            raise
        except Exception as e:
            failure_pattern = FailurePattern.EXCEPTION
            error_message = str(e)
            raise
        finally:
            # Record call result
            duration = time.time() - start_time
            result = CallResult(
                timestamp=start_time,
                duration_sec=duration,
                success=success,
                failure_pattern=failure_pattern,
                error_message=error_message
            )

            self._record_call(result)
            self._update_state_based_on_result(result)

    def _is_call_allowed(self) -> bool:
        """Determine if call should be allowed based on current state."""

        if self.state == CircuitState.CLOSED:
            return True

        elif self.state == CircuitState.OPEN:
            # Check if should attempt reset
            if self._should_attempt_reset():
                self._transition_to_state(CircuitState.HALF_OPEN)
                return True
            return False

        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited test calls
            if self.half_open_calls_made < self.config.half_open_calls:
                self.half_open_calls_made += 1
                return True
            return False

        return False

    def _update_state_based_on_result(self, result: CallResult) -> None:
        """Update circuit state based on call result."""

        if self.state == CircuitState.CLOSED:
            # Check if should open
            if self._should_open_circuit():
                self._transition_to_state(CircuitState.OPEN)

        elif self.state == CircuitState.HALF_OPEN:
            # Check if should close or re-open
            if self.failure_detector.is_failure(result):
                # Failure in half-open, go back to open
                self._transition_to_state(CircuitState.OPEN)
            elif self.half_open_calls_made >= self.config.half_open_calls:
                # All test calls successful, close circuit
                self._transition_to_state(CircuitState.CLOSED)

    async def health_check(self) -> bool:
        """
        Perform health check for the protected service.
        
        Returns:
            True if service is healthy, False otherwise
        """

        current_time = time.time()

        # Only check if enough time has passed
        if current_time - self.last_health_check < self.config.health_check_interval:
            return True  # Assume healthy if checked recently

        self.last_health_check = current_time

        try:
            # This would typically ping the actual service
            # For now, we'll use circuit metrics to determine health
            failure_rate, slow_rate = self._calculate_current_rates()

            # Consider healthy if rates are below thresholds
            is_healthy = (
                failure_rate < self.config.failure_rate_threshold * 0.5 and
                slow_rate < self.config.slow_call_rate_threshold * 0.5
            )

            if is_healthy:
                self.consecutive_health_failures = 0

                # If in OPEN state and health check passes, consider half-open
                if self.state == CircuitState.OPEN and self.config.auto_healing_enabled:
                    self._emit_telemetry("auto_healing", "Health check passed, attempting recovery")
                    self._transition_to_state(CircuitState.HALF_OPEN)
            else:
                self.consecutive_health_failures += 1

                # If too many consecutive failures, force open
                if (self.consecutive_health_failures >= 3 and
                    self.state != CircuitState.OPEN):
                    self._emit_telemetry("health_degraded",
                                       "Multiple health check failures, opening circuit")
                    self._transition_to_state(CircuitState.OPEN)

            self._emit_metric("health_check_success", 1.0 if is_healthy else 0.0)
            return is_healthy

        except Exception as e:
            self.consecutive_health_failures += 1
            self._emit_telemetry("health_check_error", f"Health check failed: {e}")
            self._emit_metric("health_check_success", 0.0)
            return False

    def get_stats(self) -> CircuitBreakerStats:
        """Get current circuit breaker statistics."""

        # Update time-based stats
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            self.stats.time_in_open += current_time - max(
                self.state_change_time, current_time - 1.0
            )
        elif self.state == CircuitState.HALF_OPEN:
            self.stats.time_in_half_open += current_time - max(
                self.state_change_time, current_time - 1.0
            )

        return self.stats

    def reset(self) -> None:
        """Manually reset circuit breaker to closed state."""

        self._emit_telemetry("manual_reset", "Circuit breaker manually reset")
        self._transition_to_state(CircuitState.CLOSED)

        # Clear recent history
        self.recent_calls.clear()
        self.consecutive_health_failures = 0
        self.backoff_multiplier = 1.0


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.health_check_task: Optional[asyncio.Task] = None

    def register(self,
                 name: str,
                 config: Optional[CircuitBreakerConfig] = None,
                 failure_detector: Optional[FailureDetector] = None) -> CircuitBreaker:
        """Register a new circuit breaker."""

        if name in self.circuit_breakers:
            raise ValueError(f"Circuit breaker {name} already registered")

        cb = CircuitBreaker(name, config, failure_detector)
        self.circuit_breakers[name] = cb
        return cb

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self.circuit_breakers.get(name)

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""

        return {
            name: {
                "state": cb.state.value,
                "stats": cb.get_stats().to_dict()
            }
            for name, cb in self.circuit_breakers.items()
        }

    async def start_health_monitoring(self) -> None:
        """Start background health monitoring for all circuit breakers."""

        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_check_loop())

    async def stop_health_monitoring(self) -> None:
        """Stop background health monitoring."""

        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None

    async def _health_check_loop(self) -> None:
        """Background health check loop."""

        while True:
            try:
                # Run health checks for all circuit breakers
                tasks = [
                    cb.health_check()
                    for cb in self.circuit_breakers.values()
                ]

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                await asyncio.sleep(10)  # Check every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Brief pause on error


# Global registry instance
_global_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry."""
    global _global_registry

    if _global_registry is None:
        _global_registry = CircuitBreakerRegistry()

    return _global_registry


def circuit_breaker(name: str,
                   config: Optional[CircuitBreakerConfig] = None,
                   failure_detector: Optional[FailureDetector] = None):
    """
    Decorator for circuit breaker protection.
    
    Args:
        name: Circuit breaker name
        config: Circuit breaker configuration
        failure_detector: Failure detection strategy
    """

    def decorator(func):
        registry = get_circuit_breaker_registry()

        # Register circuit breaker if not exists
        if registry.get(name) is None:
            registry.register(name, config, failure_detector)

        cb = registry.get(name)

        async def wrapper(*args, **kwargs):
            async with cb.protect(operation_name=func.__name__):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Example usage
    async def demo_circuit_breaker():

        # Create circuit breaker
        config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_rate_threshold=0.5,
            recovery_timeout_sec=10.0
        )

        cb = CircuitBreaker("demo_service", config)

        # Simulate some calls
        for i in range(10):
            try:
                async with cb.protect(f"call_{i}"):
                    # Simulate random failures
                    if random.random() < 0.3:  # 30% failure rate
                        raise Exception(f"Simulated failure {i}")

                    # Simulate processing time
                    await asyncio.sleep(random.uniform(0.1, 0.5))

                    print(f"Call {i}: Success")

            except Exception as e:
                print(f"Call {i}: Failed - {e}")

            await asyncio.sleep(0.5)

        # Print final stats
        stats = cb.get_stats()
        print(f"\nFinal Stats: {stats.to_dict()}")
        print(f"Circuit State: {cb.state.value}")

    asyncio.run(demo_circuit_breaker())
