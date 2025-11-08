"""
Token Bucket Backpressure Management
====================================

Adaptive backpressure control for memory service operations.
Implements token bucket algorithm with dynamic rate adjustment
to maintain T4/0.01% excellence under load.

Features:
- Token bucket rate limiting with burst capacity
- Adaptive rate adjustment based on system metrics
- Circuit breaker integration for cascade prevention
- Prometheus metrics for observability
- Graceful degradation under overload
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from async_utils import create_background_task

logger = logging.getLogger(__name__)


class BackpressureMode(Enum):
    """Backpressure control modes"""
    DISABLED = "disabled"           # No rate limiting
    SOFT = "soft"                   # Warning logs, allow through
    MODERATE = "moderate"           # Rate limiting with bursts
    STRICT = "strict"               # Strict rate limiting
    EMERGENCY = "emergency"         # Emergency throttling


@dataclass
class BackpressureConfig:
    """Configuration for token bucket backpressure"""

    # Token bucket parameters
    max_tokens: int = 1000                    # Maximum tokens in bucket
    refill_rate: float = 100.0               # Tokens per second
    initial_tokens: int = 1000               # Starting tokens

    # Adaptive parameters
    enable_adaptation: bool = True            # Enable dynamic rate adjustment
    adaptation_window_sec: int = 60          # Window for rate adaptation
    target_p95_ms: float = 100.0             # Target p95 latency
    max_rate_increase: float = 1.5           # Max rate increase factor
    max_rate_decrease: float = 0.5           # Max rate decrease factor

    # Emergency parameters
    emergency_threshold_p95: float = 500.0   # Emergency mode threshold
    emergency_rate_factor: float = 0.1       # Emergency rate reduction

    # Monitoring
    metrics_enabled: bool = True             # Enable Prometheus metrics
    sample_size: int = 1000                  # Sample size for statistics


@dataclass
class BackpressureMetrics:
    """Runtime backpressure metrics"""
    tokens_available: int = 0
    requests_per_second: float = 0.0
    rejection_rate: float = 0.0
    avg_wait_time_ms: float = 0.0
    p95_latency_ms: float = 0.0
    mode: BackpressureMode = BackpressureMode.MODERATE
    last_adaptation: float = 0.0


class TokenBucket:
    """
    Thread-safe token bucket implementation with adaptive rate control.

    Uses asyncio-native primitives for optimal performance in async contexts.
    Supports burst capacity while maintaining steady-state rate limits.
    """

    def __init__(self, config: BackpressureConfig):
        self.config = config
        self.tokens = config.initial_tokens
        self.max_tokens = config.max_tokens
        self.refill_rate = config.refill_rate
        self.last_refill = time.monotonic()

        # Adaptive control
        self.mode = BackpressureMode.MODERATE
        self.latency_samples: deque = deque(maxlen=config.sample_size)
        self.request_times: deque = deque(maxlen=config.sample_size)
        self.rejection_count = 0
        self.total_requests = 0
        self.last_adaptation = time.monotonic()

        # Synchronization
        self._lock = asyncio.Lock()

        logger.info(f"TokenBucket initialized: {config.max_tokens} tokens, {config.refill_rate}/sec")

    async def acquire_token(self, tokens_needed: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket.

        Args:
            tokens_needed: Number of tokens to acquire
            timeout: Maximum wait time in seconds

        Returns:
            True if tokens acquired, False if rejected or timeout
        """
        start_time = time.monotonic()
        self.total_requests += 1

        # Quick check without lock for common case
        if self.mode == BackpressureMode.DISABLED:
            return True

        if self.mode == BackpressureMode.EMERGENCY and self.total_requests % 10 != 0:
            self.rejection_count += 1
            return False

        async with self._lock:
            # Refill tokens based on elapsed time
            await self._refill_tokens()

            # Check if tokens available
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed

                # Record successful acquisition
                (time.monotonic() - start_time) * 1000
                self.request_times.append(time.monotonic())

                return True

            # Handle token shortage based on mode
            if self.mode == BackpressureMode.SOFT:
                # Log warning but allow through
                logger.warning(f"Soft backpressure: {self.tokens} tokens available, {tokens_needed} needed")
                return True

            # For moderate/strict modes, attempt to wait for tokens
            if timeout and timeout > 0:
                return await self._wait_for_tokens(tokens_needed, timeout, start_time)

            # Immediate rejection
            self.rejection_count += 1
            return False

    async def _wait_for_tokens(self, tokens_needed: int, timeout: float, start_time: float) -> bool:
        """Wait for tokens to become available"""
        deadline = start_time + timeout

        while time.monotonic() < deadline:
            # Calculate wait time based on refill rate
            tokens_short = tokens_needed - self.tokens
            wait_time = min(tokens_short / self.refill_rate, 0.1)  # Max 100ms wait

            await asyncio.sleep(wait_time)

            # Refill and check again
            await self._refill_tokens()
            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                (time.monotonic() - start_time) * 1000
                return True

        # Timeout exceeded
        self.rejection_count += 1
        return False

    async def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.monotonic()
        elapsed = now - self.last_refill

        if elapsed > 0:
            tokens_to_add = int(elapsed * self.refill_rate)
            if tokens_to_add > 0:
                self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
                self.last_refill = now

    def record_latency(self, latency_ms: float):
        """Record operation latency for adaptive control"""
        if self.config.enable_adaptation:
            self.latency_samples.append(latency_ms)

            # Trigger adaptation check periodically
            now = time.monotonic()
            if now - self.last_adaptation >= self.config.adaptation_window_sec:
                create_background_task(self._adapt_rate())

    async def _adapt_rate(self):
        """Adapt refill rate based on observed latencies"""
        if not self.latency_samples or len(self.latency_samples) < 20:
            return

        try:
            # Calculate current p95 latency
            sorted_latencies = sorted(self.latency_samples)
            p95_idx = int(len(sorted_latencies) * 0.95)
            current_p95 = sorted_latencies[p95_idx]

            # Determine rate adjustment
            target_p95 = self.config.target_p95_ms
            rate_factor = 1.0
            new_mode = self.mode

            if current_p95 > self.config.emergency_threshold_p95:
                # Emergency: drastically reduce rate
                rate_factor = self.config.emergency_rate_factor
                new_mode = BackpressureMode.EMERGENCY
                logger.warning(f"Emergency backpressure activated: p95={current_p95:.1f}ms")

            elif current_p95 > target_p95 * 1.5:
                # High latency: reduce rate
                rate_factor = max(self.config.max_rate_decrease,
                                target_p95 / current_p95)
                new_mode = BackpressureMode.STRICT

            elif current_p95 < target_p95 * 0.7:
                # Low latency: can increase rate
                rate_factor = min(self.config.max_rate_increase,
                                target_p95 / current_p95)
                new_mode = BackpressureMode.MODERATE

            # Apply rate adjustment
            if abs(rate_factor - 1.0) > 0.05:  # Only adjust if significant change
                old_rate = self.refill_rate
                self.refill_rate *= rate_factor
                self.refill_rate = max(10.0, min(10000.0, self.refill_rate))  # Bounds

                logger.info(f"Rate adapted: {old_rate:.1f} -> {self.refill_rate:.1f}/sec "
                          f"(p95: {current_p95:.1f}ms, target: {target_p95:.1f}ms)")

            self.mode = new_mode
            self.last_adaptation = time.monotonic()

        except Exception as e:
            logger.error(f"Rate adaptation failed: {e}")

    async def get_metrics(self) -> BackpressureMetrics:
        """Get current backpressure metrics"""
        async with self._lock:
            await self._refill_tokens()

            # Calculate request rate
            now = time.monotonic()
            recent_requests = [t for t in self.request_times if now - t <= 60]  # Last minute
            rps = len(recent_requests) / 60 if recent_requests else 0.0

            # Calculate rejection rate
            rejection_rate = (self.rejection_count / self.total_requests
                            if self.total_requests > 0 else 0.0)

            # Calculate p95 latency
            p95_latency = 0.0
            if len(self.latency_samples) >= 20:
                sorted_latencies = sorted(self.latency_samples)
                p95_idx = int(len(sorted_latencies) * 0.95)
                p95_latency = sorted_latencies[p95_idx]

            return BackpressureMetrics(
                tokens_available=self.tokens,
                requests_per_second=rps,
                rejection_rate=rejection_rate,
                avg_wait_time_ms=0.0,  # TODO: Track wait times
                p95_latency_ms=p95_latency,
                mode=self.mode,
                last_adaptation=self.last_adaptation
            )

    async def reset_stats(self):
        """Reset statistics for testing"""
        async with self._lock:
            self.latency_samples.clear()
            self.request_times.clear()
            self.rejection_count = 0
            self.total_requests = 0
            self.tokens = self.config.initial_tokens
            self.mode = BackpressureMode.MODERATE


class AdaptiveBackpressure:
    """
    High-level adaptive backpressure controller.

    Manages multiple token buckets for different operation types
    and provides centralized backpressure control with metrics.
    """

    def __init__(self, configs: dict[str, BackpressureConfig]):
        self.buckets: dict[str, TokenBucket] = {}
        self.global_config = configs.get('global', BackpressureConfig())

        # Create token buckets for different operation types
        for operation_type, config in configs.items():
            if operation_type != 'global':
                self.buckets[operation_type] = TokenBucket(config)

        # Default bucket for unspecified operations
        if 'default' not in self.buckets:
            self.buckets['default'] = TokenBucket(self.global_config)

        logger.info(f"AdaptiveBackpressure initialized with {len(self.buckets)} buckets")

    async def acquire_token(self, operation_type: str = 'default',
                          tokens_needed: int = 1,
                          timeout: Optional[float] = None) -> bool:
        """Acquire tokens for a specific operation type"""
        bucket = self.buckets.get(operation_type, self.buckets['default'])
        return await bucket.acquire_token(tokens_needed, timeout)

    def record_latency(self, operation_type: str, latency_ms: float):
        """Record operation latency for adaptive control"""
        bucket = self.buckets.get(operation_type, self.buckets['default'])
        bucket.record_latency(latency_ms)

    async def get_metrics(self, operation_type: Optional[str] = None) -> dict[str, BackpressureMetrics]:
        """Get metrics for all or specific operation types"""
        if operation_type:
            bucket = self.buckets.get(operation_type)
            if bucket:
                return {operation_type: await bucket.get_metrics()}
            return {}

        # Get metrics for all buckets
        metrics = {}
        for op_type, bucket in self.buckets.items():
            metrics[op_type] = await bucket.get_metrics()

        return metrics

    async def set_mode(self, mode: BackpressureMode, operation_type: Optional[str] = None):
        """Set backpressure mode for specific or all operation types"""
        if operation_type:
            bucket = self.buckets.get(operation_type)
            if bucket:
                bucket.mode = mode
        else:
            # Set mode for all buckets
            for bucket in self.buckets.values():
                bucket.mode = mode

        logger.info(f"Backpressure mode set to {mode.value}" +
                   (f" for {operation_type}" if operation_type else " globally"))

    async def health_check(self) -> dict[str, Any]:
        """Health check for backpressure system"""
        health = {
            'healthy': True,
            'buckets': {},
            'global_mode': BackpressureMode.MODERATE,
            'total_rejection_rate': 0.0
        }

        total_rejections = 0
        total_requests = 0
        emergency_buckets = 0

        for op_type, bucket in self.buckets.items():
            metrics = await bucket.get_metrics()

            bucket_health = {
                'healthy': metrics.mode != BackpressureMode.EMERGENCY,
                'tokens_available': metrics.tokens_available,
                'rejection_rate': metrics.rejection_rate,
                'mode': metrics.mode.value,
                'p95_latency_ms': metrics.p95_latency_ms
            }

            health['buckets'][op_type] = bucket_health

            # Aggregate stats
            total_rejections += bucket.rejection_count
            total_requests += bucket.total_requests

            if metrics.mode == BackpressureMode.EMERGENCY:
                emergency_buckets += 1

        # Overall health assessment
        if emergency_buckets > 0:
            health['healthy'] = False
            health['global_mode'] = BackpressureMode.EMERGENCY

        if total_requests > 0:
            health['total_rejection_rate'] = total_rejections / total_requests

        return health


# Factory for creating standard backpressure configurations
class BackpressureFactory:
    """Factory for creating standard backpressure configurations"""

    @staticmethod
    def create_memory_service_config() -> dict[str, BackpressureConfig]:
        """Create backpressure configuration for memory service"""
        return {
            'search': BackpressureConfig(
                max_tokens=2000,
                refill_rate=200.0,
                target_p95_ms=50.0,      # T4 requirement for search
                emergency_threshold_p95=200.0
            ),
            'upsert': BackpressureConfig(
                max_tokens=1000,
                refill_rate=100.0,
                target_p95_ms=100.0,     # T4 requirement for writes
                emergency_threshold_p95=500.0
            ),
            'batch': BackpressureConfig(
                max_tokens=500,
                refill_rate=50.0,
                target_p95_ms=200.0,     # Higher latency OK for batches
                emergency_threshold_p95=1000.0
            ),
            'default': BackpressureConfig(
                max_tokens=1500,
                refill_rate=150.0,
                target_p95_ms=100.0,
                emergency_threshold_p95=400.0
            )
        }

    @staticmethod
    def create_high_throughput_config() -> dict[str, BackpressureConfig]:
        """Create configuration optimized for high throughput"""
        return {
            'default': BackpressureConfig(
                max_tokens=5000,
                refill_rate=1000.0,
                target_p95_ms=200.0,
                max_rate_increase=2.0,
                emergency_threshold_p95=1000.0
            )
        }

    @staticmethod
    def create_strict_latency_config() -> dict[str, BackpressureConfig]:
        """Create configuration optimized for strict latency"""
        return {
            'default': BackpressureConfig(
                max_tokens=1000,
                refill_rate=100.0,
                target_p95_ms=50.0,
                max_rate_decrease=0.3,
                emergency_threshold_p95=200.0
            )
        }
