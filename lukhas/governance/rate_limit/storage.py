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
        self._windows: dict[str, deque] = defaultdict(deque)

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

    def get_stats(self) -> dict[str, int]:
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


class RedisRateLimitStorage(RateLimitStorage):
    """
    Redis-based rate limit storage for distributed deployments.

    Implementation:
    - Uses Redis sorted sets for sliding window algorithm
    - Score = timestamp, allows efficient range queries
    - Atomic operations via Lua scripts for accuracy
    - Distributed and persistent across server restarts
    - Auto-cleanup of expired timestamps

    Pros:
    - Multi-server support (distributed state)
    - Persistent (survives restarts)
    - Accurate sliding window with atomic operations
    - Horizontal scaling

    Cons:
    - Network latency (typically <1ms for local Redis)
    - Requires Redis infrastructure
    - Slightly more complex than in-memory

    For single-server deployments, InMemoryRateLimitStorage is simpler and faster.
    """

    def __init__(self, redis_url: str):
        """
        Initialize Redis storage.

        Args:
            redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")

        Raises:
            ImportError: If redis package not installed
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis rate limiting requires the 'redis' package. "
                "Install with: pip install redis"
            )

        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self._key_prefix = "rate_limit:"

        # Lua script for atomic rate limit check
        # This ensures accurate sliding window even under high concurrency
        self._check_script = self.redis_client.register_script("""
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])

            -- Remove old timestamps outside window
            redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)

            -- Count requests in current window
            local count = redis.call('ZCARD', key)

            -- Check if limit exceeded
            if count < limit then
                -- Add current timestamp
                redis.call('ZADD', key, now, now)
                -- Set expiry to window duration (auto-cleanup)
                redis.call('EXPIRE', key, window)
                return {1, limit - count - 1, now + window}
            else
                -- Get oldest timestamp to calculate reset time
                local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
                local reset_time = tonumber(oldest[2]) + window
                return {0, 0, reset_time}
            end
        """)

    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> RateLimitResult:
        """
        Check if a request is allowed under the rate limit.

        Uses Redis sorted sets with atomic Lua script for accurate
        sliding window algorithm in distributed environments.

        Args:
            key: Unique identifier for this rate limit
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            RateLimitResult with decision and metadata
        """
        now = time.time()
        redis_key = f"{self._key_prefix}{key}"

        # Execute atomic Lua script
        result = self._check_script(
            keys=[redis_key],
            args=[now, window_seconds, limit]
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        reset_time = float(result[2])

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            retry_after=int(reset_time - now) if not allowed else 0,
            limit=limit
        )

    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Rate limit key to reset
        """
        redis_key = f"{self._key_prefix}{key}"
        self.redis_client.delete(redis_key)

    def reset_all(self) -> None:
        """
        Reset all rate limits.

        Warning: This scans all keys with rate_limit: prefix.
        Use sparingly in production (primarily for testing).
        """
        pattern = f"{self._key_prefix}*"
        cursor = 0
        while True:
            cursor, keys = self.redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=100
            )
            if keys:
                self.redis_client.delete(*keys)
            if cursor == 0:
                break

    def get_diagnostics(self, key: str) -> dict:
        """
        Get diagnostic information for a rate limit key.

        Args:
            key: Rate limit key

        Returns:
            Dict with diagnostic information
        """
        redis_key = f"{self._key_prefix}{key}"

        # Get all timestamps
        timestamps = self.redis_client.zrange(redis_key, 0, -1, withscores=True)

        # Get TTL
        ttl = self.redis_client.ttl(redis_key)

        return {
            "key": key,
            "redis_key": redis_key,
            "timestamp_count": len(timestamps),
            "timestamps": [float(score) for _, score in timestamps],
            "ttl_seconds": ttl,
            "exists": self.redis_client.exists(redis_key) > 0
        }
