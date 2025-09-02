# path: qi/ops/rate_limit.py
from __future__ import annotations

import contextlib
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Prometheus (integrates with the registry from metrics_middleware)
try:
    from prometheus_client import Counter, Gauge

    from qi.ops.metrics_middleware import REGISTRY

    _PROM = True
except Exception:
    _PROM = False
    REGISTRY = None  # type: ignore

if _PROM:
    RL_BLOCKS = Counter(
        "lukhas_rate_limit_blocks_total",
        "Total requests blocked by rate limiter",
        ["bucket", "path"],
        registry=REGISTRY,
    )
    RL_TOKENS = Gauge(
        "lukhas_rate_limit_tokens",
        "Current tokens remaining per bucket (sampling)",
        ["bucket"],
        registry=REGISTRY,
    )


@dataclass
class BucketConfig:
    capacity: int  # max tokens
    refill_per_sec: float  # tokens per second


def _now() -> float:
    return time.monotonic()


class TokenBucket:
    def __init__(self, capacity: int, refill_per_sec: float):
        self.capacity = float(capacity)
        self.refill = float(refill_per_sec)
        self.tokens = float(capacity)
        self.last = _now()

    def take(self, n: float = 1.0) -> bool:
        t = _now()
        elapsed = max(0.0, t - self.last)
        self.last = t
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill)
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False


class RateLimiter(BaseHTTPMiddleware):
    """
    Configurable token-bucket limiter keyed by (user_id|ip, path group).
    - buckets: mapping from name -> BucketConfig
    - rules: list of (matcher, bucket_name) in evaluation order
      where matcher is a callable(Request) -> bool
    If no rule matches, request passes through unmetered.
    """

    def __init__(
        self,
        app,
        buckets: dict[str, BucketConfig],
        rules: list[tuple[Callable[[Request], bool], str]],
    ):
        super().__init__(app)
        self.buckets_cfg = buckets
        self.rules = rules
        self.state: dict[tuple[str, str], TokenBucket] = (
            {}
        )  # (bucket_key, bucket_name) -> bucket

    def _key(self, req: Request) -> str:
        user = req.headers.get("x-user-id")
        if user:
            return f"user:{user}"
        ip = req.headers.get("x-forwarded-for")
        ip = (
            ip.split(",")[0].strip()
            if ip
            else req.client.host if req.client else "unknown"
        )
        return f"ip:{ip}"

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # figure out which bucket (if any) applies
        bucket_name = None
        for match, name in self.rules:
            try:
                if match(request):
                    bucket_name = name
                    break
            except Exception:
                # matcher errors -> ignore rule
                continue

        if bucket_name is None:
            return await call_next(request)

        cfg = self.buckets_cfg.get(bucket_name)
        if not cfg:
            return await call_next(request)

        key = self._key(request)
        path_group = self._normalize_path(request.url.path)
        state_key = (f"{key}|{path_group}", bucket_name)
        bucket = self.state.get(state_key)
        if bucket is None:
            bucket = TokenBucket(cfg.capacity, cfg.refill_per_sec)
            self.state[state_key] = bucket

        ok = bucket.take(1.0)
        if _PROM:
            with contextlib.suppress(Exception):
                RL_TOKENS.labels(bucket=f"{key}:{bucket_name}").set(bucket.tokens)

        if not ok:
            if _PROM:
                with contextlib.suppress(Exception):
                    RL_BLOCKS.labels(bucket=bucket_name, path=path_group).inc()
            retry_after = (
                max(1, int((1.0 - bucket.tokens) / cfg.refill_per_sec))
                if cfg.refill_per_sec > 0
                else 60
            )
            return JSONResponse(
                {
                    "error": "rate_limited",
                    "bucket": bucket_name,
                    "path": path_group,
                    "retry_after_sec": retry_after,
                },
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

    @staticmethod
    def _normalize_path(p: str) -> str:
        # reduce cardinality for provenance endpoints
        if p.startswith("/provenance/"):
            if "/stream" in p:
                return "/provenance/:sha/stream"
            if "/download" in p:
                return "/provenance/:sha/download"
            if "/link" in p:
                return "/provenance/:sha/link"
            if "/receipt" in p:
                return "/provenance/:sha/receipt"
        return p


# convenience factory for common provenance limits
def make_provenance_limiter(app, per_user_per_min: int = 60, per_ip_per_min: int = 120):
    buckets = {
        "prov_user": BucketConfig(
            capacity=per_user_per_min, refill_per_sec=per_user_per_min / 60.0
        ),
        "prov_ip": BucketConfig(
            capacity=per_ip_per_min, refill_per_sec=per_ip_per_min / 60.0
        ),
    }

    def is_prov(req: Request) -> bool:
        p = req.url.path
        return p.startswith("/provenance/") and any(
            seg in p for seg in ("/stream", "/download", "/link")
        )

    rules = [
        (is_prov, "prov_user"),
        (is_prov, "prov_ip"),
    ]
    return RateLimiter(app, buckets=buckets, rules=rules)
