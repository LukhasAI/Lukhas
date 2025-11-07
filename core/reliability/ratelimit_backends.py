import time
from abc import ABC, abstractmethod
from typing import Tuple

import redis


class LimiterBackend(ABC):  # ABC
    """Abstract base class for a rate limiter backend."""

    @abstractmethod
    def allow(self, key: str, rate: float, burst: int) -> tuple[bool, int, float]:
        """
        Checks if a request is allowed.

        Args:
            key: The unique key for the rate limit bucket.
            rate: The refill rate of tokens per second.
            burst: The maximum number of tokens (capacity).

        Returns:
            A tuple of (allowed, remaining_tokens, reset_timestamp).
        """
        ...


class RedisTokenBucket(LimiterBackend):
    """
    A token bucket rate limiter backend using Redis and a Lua script for atomicity.
    """

    # LUA Script for atomic token bucket evaluation.
    # KEYS[1]: The key for the bucket (e.g., "rl:org_abc:sk-123:/v1/dreams")
    # ARGV[1]: Burst capacity
    # ARGV[2]: Refill rate (tokens per second)
    # ARGV[3]: Current timestamp (Unix seconds as float)
    # ARGV[4]: Tokens to consume (typically 1)
    LUA_SCRIPT = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])

        local bucket_info = redis.call("HMGET", key, "tokens", "ts")

        local tokens = capacity
        local last_ts = now

        if bucket_info[1] then
            tokens = tonumber(bucket_info[1])
            last_ts = tonumber(bucket_info[2])
        end

        local elapsed = math.max(0, now - last_ts)
        local refilled_tokens = elapsed * rate
        tokens = math.min(capacity, tokens + refilled_tokens)

        local allowed = 0
        if tokens >= requested then
            tokens = tokens - requested
            allowed = 1
        end

        redis.call("HMSET", key, "tokens", tokens, "ts", now)

        -- Expire the key after a while to prevent memory leaks
        local ttl = math.ceil((capacity / rate) * 2)
        redis.call("EXPIRE", key, ttl)

        return {allowed, tokens}
    """

    def __init__(self, url: str):
        self.r = redis.Redis.from_url(url, decode_responses=True)
        self.script_sha = self.r.script_load(self.LUA_SCRIPT)

    def allow(self, key: str, rate: float, burst: int) -> tuple[bool, int, float]:
        now = time.time()

        # evalsha is more efficient as the script is pre-loaded
        result = self.r.evalsha(self.script_sha, 1, key, burst, rate, now, 1)

        allowed, remaining_tokens = bool(result[0]), float(result[1])

        # Calculate reset time: when the bucket will be full again
        if rate > 0:
            time_to_full = (burst - remaining_tokens) / rate
            reset_timestamp = now + time_to_full
        else:
            reset_timestamp = now  # No refill, so never resets in the future

        return allowed, int(remaining_tokens), reset_timestamp
