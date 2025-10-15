"""
Prometheus metrics for rate-limit observability.

Exports gauges for current window state (limit/remaining/reset) and
counters for 429 rejections. Uses hashed principals to prevent cardinality
explosions while maintaining tenant isolation visibility.

Phase 3: Added for production-grade rate-limit monitoring.
"""

import hashlib
import os
import random
from typing import Any

try:
    from prometheus_client import Counter, Gauge

    PROMETHEUS_AVAILABLE = True
except Exception:  # pragma: no cover
    # Soft-disable if prometheus_client isn't present (keeps app booting)
    PROMETHEUS_AVAILABLE = False

    class _Nop:
        """No-op metric that does nothing (graceful degradation)."""

        def labels(self, *args, **kwargs):
            return self

        def set(self, *_a, **_kw):
            pass

        def inc(self, *_a, **_kw):
            pass

    Gauge = Counter = lambda *a, **kw: _Nop()  # type: ignore


# Gauges for the *current* limiter window (requests dimension)
RL_LIMIT = Gauge(
    "lukhas_ratelimit_limit_requests",
    "Max requests allowed in the current token-bucket window.",
    ["route", "principal"],
)

RL_REMAINING = Gauge(
    "lukhas_ratelimit_remaining_requests",
    "Remaining requests in the current token-bucket window.",
    ["route", "principal"],
)

RL_RESET = Gauge(
    "lukhas_ratelimit_reset_requests_seconds",
    "Seconds until the bucket fully refills (approx).",
    ["route", "principal"],
)

# Counter for 429 events
RL_HITS = Counter(
    "lukhas_ratelimit_exceeded_total",
    "Total number of rate-limit rejections (HTTP 429).",
    ["route", "principal"],
)


def _enabled() -> bool:
    """Check if rate-limit metrics are enabled via environment variable."""
    return os.getenv("LUKHAS_RL_METRICS", "1").lower() not in ("0", "false", "off")


def _sample_ok() -> bool:
    """
    Optional sampling to cap label churn in very high-cardinality bursts.

    Returns:
        True if this metric update should be recorded (based on sample rate)
    """
    try:
        s = float(os.getenv("LUKHAS_RL_METRICS_SAMPLE", "1.0"))
    except ValueError:
        s = 1.0
    s = max(0.0, min(1.0, s))
    return random.random() < s


def fingerprint(principal: str) -> str:
    """
    Hash principal to 8-char hex fingerprint for metrics.

    Prevents raw token exposure while maintaining tenant isolation visibility.

    Args:
        principal: Raw principal string (token hash, IP, etc.)

    Returns:
        8-character hex fingerprint
    """
    if not principal:
        return "anon"
    return hashlib.sha256(principal.encode("utf-8")).hexdigest()[:8]


def route_key(path: str) -> str:
    """
    Normalize to a tiny set of labels (prevents cardinality explosions).

    Args:
        path: Request path

    Returns:
        Normalized route label
    """
    if path.startswith("/v1/embeddings"):
        return "/v1/embeddings"
    if path.startswith("/v1/responses"):
        return "/v1/responses"
    if path.startswith("/v1/dreams"):
        return "/v1/dreams"
    if path.startswith("/v1/models"):
        return "/v1/models"

    # Fallback: strip query params
    return path.split("?", 1)[0]


def record_window(route: str, principal: str, limiter: Any, key: str) -> None:
    """
    Record current rate-limit window state to Prometheus gauges.

    Args:
        route: Request route path
        principal: Principal identifier (will be hashed)
        limiter: RateLimiter instance
        key: Rate limit key
    """
    if not _enabled() or not _sample_ok() or not PROMETHEUS_AVAILABLE:
        return

    try:
        win = limiter.current_window(key)  # {limit, remaining, reset_seconds}
        r = route_key(route)
        p = fingerprint(principal)

        RL_LIMIT.labels(r, p).set(win["limit"])
        RL_REMAINING.labels(r, p).set(win["remaining"])
        RL_RESET.labels(r, p).set(win["reset_seconds"])
    except Exception:
        # Never crash request processing due to metrics
        pass


def record_hit(route: str, principal: str) -> None:
    """
    Record a rate-limit rejection (429 response).

    Args:
        route: Request route path
        principal: Principal identifier (will be hashed)
    """
    if not _enabled() or not _sample_ok() or not PROMETHEUS_AVAILABLE:
        return

    try:
        RL_HITS.labels(route_key(route), fingerprint(principal)).inc()
    except Exception:
        # Never crash request processing due to metrics
        pass
