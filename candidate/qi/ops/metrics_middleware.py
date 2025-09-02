# path: qi/ops/metrics_middleware.py
from __future__ import annotations

import time
from collections.abc import Awaitable
from typing import Callable

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Global registry (shared across uvicorn workers if using --workers=1)
REGISTRY = CollectorRegistry(auto_describe=True)

REQ_COUNT = Counter(
    "lukhas_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=REGISTRY,
)
REQ_LATENCY = Histogram(
    "lukhas_http_request_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
    registry=REGISTRY,
)

# Provenance-focused metrics
PROV_STREAM_REQ = Counter(
    "lukhas_prov_stream_requests_total",
    "Provenance stream requests by backend",
    ["backend"],
    registry=REGISTRY,
)
PROV_STREAM_BYTES = Counter(
    "lukhas_prov_stream_bytes_total",
    "Total bytes streamed to clients",
    ["backend"],
    registry=REGISTRY,
)
PROV_STREAM_LAT = Histogram(
    "lukhas_prov_stream_seconds",
    "Provenance stream duration in seconds",
    ["backend"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 5, 10, 30, 60, 120, 300),
    registry=REGISTRY,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Normalize path (avoid cardinality explosion; trim numeric/sha-like segments)
        path = request.url.path
        for marker in ("/provenance/", "/metrics"):
            if path.startswith(marker):
                # Keep the static prefix only for provenance/download/stream endpoints
                if path.startswith("/provenance/"):
                    if "/stream" in path:
                        path = "/provenance/:sha/stream"
                    elif "/download" in path:
                        path = "/provenance/:sha/download"
                    elif "/link" in path:
                        path = "/provenance/:sha/link"
                break

        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
            raise
        finally:
            elapsed = time.perf_counter() - start
            REQ_COUNT.labels(request.method, path, status).inc()
            REQ_LATENCY.labels(request.method, path).observe(elapsed)
        return response


def metrics_endpoint():
    def _handler(_: Request) -> Response:
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return _handler


__all__ = [
    "PROV_STREAM_BYTES",
    "PROV_STREAM_LAT",
    "PROV_STREAM_REQ",
    "PrometheusMiddleware",
    "metrics_endpoint",
]
