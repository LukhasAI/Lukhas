"""
Rate limiting storage implementations.

Provides sliding window rate limiting algorithm with in-memory storage.
Can be extended to support Redis for distributed rate limiting.
"""

import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from typing import Dict, Optional, Tuple


@dataclass
class RateLimitResult:
    """
    Result of a rate limit check.

    Attributes:
        allowed: Whether the request is allowed
        remaining: Number of requests remaining in window
        reset_time: Unix timestamp when the rate limit resets
        retry_after: Seconds to wait before retrying (if not allowed)
        limit: Maximum requests allowed in window
    """
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: int
    limit: int


class RateLimitStorage(ABC):
    """Abstract base class for rate limit storage backends."""

    @abstractmethod
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check if a request is allowed under the rate limit.

        Uses sliding window algorithm for accurate rate limiting.

        Args:
            key: Unique identifier for this rate limit (e.g., "user:123:path:/api/...")
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            RateLimitResult with decision and metadata
        """
        pass

    @abstractmethod
    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Rate limit key to reset
        """
        pass

    @abstractmethod
    def reset_all(self) -> None:
        """Reset all rate limits (primarily for testing)."""
        pass


class InMemoryRateLimitStorage(RateLimitStorage):
    """
    In-memory rate limit storage using sliding window algorithm.

    Implementation:
    - Uses deque to store timestamps of requests
    - Removes old timestamps outside the window
    - Accurate sliding window (not fixed window approximation)
    - Thread-safe with locks

    Pros:
    - Fast (no network latency)
    - No external dependencies
    - Accurate sliding window

    Cons:
    - Not distributed (single-server only)
    - Lost on restart
    - Memory usage grows with traffic

    For production with multiple servers, use RedisRateLimitStorage instead.
    """

    def __init__(self):
        """Initialize in-memory storage."""
        # Key -> deque of timestamps
        self._windows: Dict[str, deque] = defaultdict(deque)

        # Lock for thread safety
        self._lock = Lock()

        # Track cleanup to prevent memory leaks
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # Clean up every hour

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check rate limit using sliding window algorithm.

        Algorithm:
        1. Get current timestamp
        2. Remove all timestamps older than (now - window_seconds)
        3. Count remaining timestamps
        4. If count < limit, allow request and add timestamp
        5. If count >= limit, deny request

        This provides accurate sliding window rate limiting without the
        memory overhead of token bucket or the inaccuracy of fixed window.

        Args:
            key: Unique identifier for this rate limit
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            RateLimitResult with decision and metadata
        """
        with self._lock:
            current_time = time.time()
            window_start = current_time - window_seconds

            # Get or create window for this key
            window = self._windows[key]

            # Remove timestamps outside the window (sliding window)
            while window and window[0] < window_start:
                window.popleft()

            # Count requests in current window
            current_count = len(window)

            # Calculate reset time (when oldest request expires)
            if window:
                reset_time = window[0] + window_seconds
            else:
                reset_time = current_time + window_seconds

            # Check if request is allowed
            if current_count < limit:
                # Allow request and record timestamp
                window.append(current_time)

                return RateLimitResult(
                    allowed=True,
                    remaining=limit - current_count - 1,
                    reset_time=reset_time,
                    retry_after=0,
                    limit=limit
                )
            else:
                # Deny request
                # Calculate retry_after: time until oldest request expires
                retry_after = int(reset_time - current_time) + 1

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=retry_after,
                    limit=limit
                )

    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Rate limit key to reset
        """
        with self._lock:
            if key in self._windows:
                del self._windows[key]

    def reset_all(self) -> None:
        """Reset all rate limits (primarily for testing)."""
        with self._lock:
            self._windows.clear()

    def cleanup_old_windows(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up old windows to prevent memory leaks.

        Removes windows that haven't been accessed recently.

        Args:
            max_age_seconds: Remove windows older than this

        Returns:
            Number of windows removed
        """
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - max_age_seconds

            keys_to_remove = []
            for key, window in self._windows.items():
                # If window is empty or all timestamps are old, remove it
                if not window or window[-1] < cutoff_time:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._windows[key]

            self._last_cleanup = current_time
            return len(keys_to_remove)

    def get_stats(self) -> Dict[str, int]:
        """
        Get storage statistics.

        Returns:
            Dictionary with statistics about storage state
        """
        with self._lock:
            total_keys = len(self._windows)
            total_timestamps = sum(len(w) for w in self._windows.values())

            return {
                "total_keys": total_keys,
                "total_timestamps": total_timestamps,
                "last_cleanup": int(self._last_cleanup),
            }


# For future Redis implementation:
class RedisRateLimitStorage(RateLimitStorage):
    """
    Redis-based rate limit storage (distributed).

    TODO: Implement for production multi-server deployments
    Uses Redis sorted sets for sliding window algorithm
    """

    def __init__(self, redis_url: str):
        """
        Initialize Redis storage.

        Args:
            redis_url: Redis connection URL
        """
        raise NotImplementedError(
            "Redis rate limiting not yet implemented. "
            "Use InMemoryRateLimitStorage for single-server deployments."
        )

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitResult:
        """Check rate limit using Redis sorted sets."""
        raise NotImplementedError()

    def reset(self, key: str) -> None:
        """Reset rate limit in Redis."""
        raise NotImplementedError()

    def reset_all(self) -> None:
        """Reset all rate limits in Redis."""
        raise NotImplementedError()
