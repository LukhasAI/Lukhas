"""Provider registry with token bucket rate limiting."""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TokenBucket:
    """Simple token bucket for rate limiting."""
    capacity: int
    refill_rate: float
    tokens: float = 0.0
    last_refill: float = 0.0

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()

    def refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens."""
        self.refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class ProviderRegistry:
    """Registry for external providers with rate limiting."""

    def __init__(self, default_capacity: int = 100, default_refill_rate: float = 10.0):
        self.providers: Dict[str, Any] = {}
        self.buckets: Dict[str, TokenBucket] = {}
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate

    def register(self, name: str, provider: Any, capacity: Optional[int] = None, refill_rate: Optional[float] = None) -> None:
        """Register a provider with rate limiting."""
        self.providers[name] = provider
        self.buckets[name] = TokenBucket(
            capacity=capacity or self.default_capacity,
            refill_rate=refill_rate or self.default_refill_rate
        )

    def call(self, name: str, *args, **kwargs) -> Any:
        """Call provider through rate limit."""
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not registered")
        bucket = self.buckets[name]
        if not bucket.consume():
            raise RuntimeError(f"Rate limit exceeded for provider '{name}'")
        provider = self.providers[name]
        if callable(provider):
            return provider(*args, **kwargs)
        return provider
