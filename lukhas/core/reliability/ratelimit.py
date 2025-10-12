"""
Rate limiting for LUKHAS API endpoints.

Implements token bucket algorithm with per-endpoint limits.
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple


class TokenBucket:
    """
    Token bucket rate limiter.

    Allows bursts up to capacity, refills at fixed rate.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = Lock()

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens.

        Returns:
            (success, retry_after_seconds)
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill

            # Refill tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, 0.0
            else:
                # Calculate how long until enough tokens available
                needed = tokens - self.tokens
                retry_after = needed / self.refill_rate
                return False, retry_after


class RateLimiter:
    """
    Rate limiter with per-endpoint token buckets.

    Thread-safe for concurrent requests.
    """

    def __init__(self, default_rps: int = 20):
        """
        Initialize rate limiter.

        Args:
            default_rps: Default requests per second for endpoints
        """
        self.default_rps = default_rps
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(capacity=default_rps * 2, refill_rate=default_rps)
        )
        self.lock = Lock()

    def configure_endpoint(self, endpoint: str, rps: int) -> None:
        """Configure custom rate limit for endpoint."""
        with self.lock:
            self.buckets[endpoint] = TokenBucket(
                capacity=rps * 2,  # Allow 2x burst
                refill_rate=rps
            )

    def check_limit(self, endpoint: str) -> Tuple[bool, float]:
        """
        Check if request is within rate limit.

        Returns:
            (allowed, retry_after_seconds)
        """
        bucket = self.buckets[endpoint]
        return bucket.consume(1)


def rate_limit_error(retry_after_s: float) -> dict:
    """
    Generate OpenAI-compatible rate limit error response.

    Args:
        retry_after_s: Seconds to wait before retry

    Returns:
        Error dict with headers
    """
    retry_after_int = max(1, int(retry_after_s))
    return {
        "error": {
            "type": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Please retry after the specified time.",
            "retry_after": retry_after_int
        },
        "headers": {"Retry-After": str(retry_after_int)}
    }
