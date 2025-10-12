"""
OpenAI-compatible façade for LUKHAS MATRIZ.

Provides OpenAI-style endpoints while leveraging MATRIZ cognitive orchestrator,
memory systems, and consciousness capabilities.

Endpoints:
- GET  /healthz   -> {"status":"ok"}
- GET  /readyz    -> {"status":"ready"}
- GET  /metrics   -> Prometheus text
- GET  /v1/models -> {"data":[{"id":"lukhas-matriz","object":"model"}]}
- POST /v1/embeddings -> {"data":[{"embedding":[...]}]}
- POST /v1/responses  -> {"id": "...", "model":"lukhas-matriz", "output":{"text":"..."}}
- POST /v1/dreams     -> {"id":"dream_...","traces":[...]}
"""
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from threading import Lock
import os, time, uuid, logging

from lukhas.core.reliability.ratelimit import RateLimiter, rate_limit_error
from lukhas.observability.tracing import setup_otel, traced_operation, get_trace_id_hex

logger = logging.getLogger(__name__)

# Global metrics storage (thread-safe)
_metrics_lock = Lock()
_request_counts: Dict[str, int] = defaultdict(int)
_request_latencies: Dict[str, List[float]] = defaultdict(list)
_error_counts: Dict[str, int] = defaultdict(int)

# Try to import MATRIZ orchestrator (graceful fallback to stub mode)
try:
    from matriz.core.orchestrator import CognitiveOrchestrator
    MATRIZ_AVAILABLE = True
except ImportError:
    logger.warning("MATRIZ orchestrator not available, running in stub mode")
    MATRIZ_AVAILABLE = False
    CognitiveOrchestrator = None  # type: ignore

# Try to import memory system (graceful fallback)
try:
    from lukhas.memory.embedding_index import EmbeddingIndex
    MEMORY_AVAILABLE = True
except ImportError:
    logger.warning("Memory system not available, using stub embeddings")
    MEMORY_AVAILABLE = False
    EmbeddingIndex = None  # type: ignore

def _metrics_text() -> str:
    """Generate Prometheus format metrics from tracked data."""
    with _metrics_lock:
        lines = []

        # Request counts by endpoint
        lines.append("# HELP http_requests_total Total HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for endpoint, count in _request_counts.items():
            lines.append(f'http_requests_total{{endpoint="{endpoint}",status="200"}} {count}')
        if not _request_counts:
            lines.append('http_requests_total{endpoint="/v1/responses",status="200"} 0')

        # Error counts
        lines.append("# HELP http_errors_total Total HTTP errors")
        lines.append("# TYPE http_errors_total counter")
        for endpoint, count in _error_counts.items():
            lines.append(f'http_errors_total{{endpoint="{endpoint}"}} {count}')
        if not _error_counts:
            lines.append('http_errors_total{endpoint="/v1/responses"} 0')

        # Latency percentiles
        lines.append("# HELP http_request_duration_ms Request latency in milliseconds")
        lines.append("# TYPE http_request_duration_ms summary")
        for endpoint, latencies in _request_latencies.items():
            if latencies:
                p50 = sorted(latencies)[len(latencies) // 2]
                p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]
                lines.append(f'http_request_duration_ms{{endpoint="{endpoint}",quantile="0.5"}} {p50:.2f}')
                lines.append(f'http_request_duration_ms{{endpoint="{endpoint}",quantile="0.95"}} {p95:.2f}')

        # Process CPU (stub for now)
        lines.append("# HELP process_cpu_seconds_total Total CPU time")
        lines.append("# TYPE process_cpu_seconds_total counter")
        lines.append("process_cpu_seconds_total 0.0")

        # Total LUKHAS requests
        total = sum(_request_counts.values()) or 1
        lines.append("# HELP lukhas_requests_total Total LUKHAS requests")
        lines.append("# TYPE lukhas_requests_total counter")
        lines.append(f"lukhas_requests_total {total}")

        return "\n".join(lines) + "\n"

def _maybe_trace(body: Dict[str, Any]) -> Dict[str, Any]:
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        body.setdefault("trace_id", uuid.uuid4().hex)
    return body

def get_app() -> FastAPI:
    """Create and configure the LUKHAS OpenAI façade application."""
    app = FastAPI(
        title="Lukhas OpenAI Facade",
        version="0.1.0",
        description="OpenAI-compatible API powered by LUKHAS MATRIZ cognitive engine"
    )

    # Initialize OpenTelemetry tracing (optional)
    tracer = setup_otel(service_name="lukhas-openai-facade")

    # Initialize rate limiter
    rate_limiter = RateLimiter(default_rps=20)
    rate_limiter.configure_endpoint("/v1/responses", rps=20)
    rate_limiter.configure_endpoint("/v1/embeddings", rps=50)
    rate_limiter.configure_endpoint("/v1/dreams", rps=5)

    # OpenTelemetry tracing middleware (outermost layer)
    @app.middleware("http")
    async def tracing_middleware(request: Request, call_next):
        if tracer:
            with tracer.start_as_current_span(
                f"{request.method} {request.url.path}",
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.route": request.url.path,
                }
            ) as span:
                try:
                    response = await call_next(request)

                    # Add span attributes for response
                    span.set_attribute("http.status_code", response.status_code)

                    # Add trace ID to response headers
                    trace_id = get_trace_id_hex(span)
                    if trace_id:
                        response.headers["X-Trace-Id"] = trace_id

                    return response
                except Exception as e:
                    # Record exception in span
                    span.set_attribute("error", True)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        else:
            # No tracing, pass through
            return await call_next(request)

    # Metrics tracking middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()

        try:
            response = await call_next(request)
            latency_ms = (time.time() - start_time) * 1000

            # Track metrics (skip health/metrics endpoints to avoid noise)
            if request.url.path not in ["/healthz", "/readyz", "/metrics"]:
                with _metrics_lock:
                    _request_counts[request.url.path] += 1
                    _request_latencies[request.url.path].append(latency_ms)
                    # Keep only last 1000 latencies per endpoint
                    if len(_request_latencies[request.url.path]) > 1000:
                        _request_latencies[request.url.path] = _request_latencies[request.url.path][-1000:]

            return response
        except Exception as e:
            # Track errors
            with _metrics_lock:
                _error_counts[request.url.path] += 1
            raise

    # Rate limiting middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        # Skip rate limiting for health/metrics endpoints
        if request.url.path in ["/healthz", "/readyz", "/metrics"]:
            return await call_next(request)

        # Check rate limit
        allowed, retry_after = rate_limiter.check_limit(request.url.path)
        if not allowed:
            error_response = rate_limit_error(retry_after)
            return JSONResponse(
                status_code=429,
                content=error_response["error"],
                headers=error_response["headers"]
            )

        return await call_next(request)

    # Initialize MATRIZ orchestrator (if available)
    orchestrator: Optional[Any] = None
    if MATRIZ_AVAILABLE and CognitiveOrchestrator:
        try:
            orchestrator = CognitiveOrchestrator()
            logger.info("MATRIZ orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MATRIZ orchestrator: {e}")
            orchestrator = None

    # Initialize memory system (if available)
    memory_index: Optional[Any] = None
    if MEMORY_AVAILABLE and EmbeddingIndex:
        try:
            memory_index = EmbeddingIndex(dimension=1536)  # OpenAI ada-002 dimension
            logger.info("Memory embedding index initialized")
        except Exception as e:
            logger.error(f"Failed to initialize memory index: {e}")
            memory_index = None

    @app.get("/healthz")
    def healthz():
        """Liveness probe - is the service running?"""
        checks = {
            "api": True,  # If this responds, API is up
            "metrics": True,  # Metrics system is always available
        }

        # Optional dependency checks (don't fail liveness if missing)
        if MATRIZ_AVAILABLE:
            checks["matriz"] = orchestrator is not None
        if MEMORY_AVAILABLE:
            checks["memory"] = memory_index is not None

        # Liveness passes even if optional dependencies are down
        return {
            "status": "ok",
            "checks": checks,
            "timestamp": time.time()
        }

    @app.get("/readyz")
    def readyz():
        """Readiness probe - can the service handle requests?"""
        checks = {
            "api": True,  # API is always ready if this endpoint responds
            "rate_limiter": rate_limiter is not None,
        }

        # Check MATRIZ orchestrator availability
        if MATRIZ_AVAILABLE:
            checks["matriz"] = orchestrator is not None
            if orchestrator:
                # Try a simple health check on orchestrator
                try:
                    # Check if orchestrator has required methods
                    checks["matriz_callable"] = hasattr(orchestrator, "process_query")
                except Exception as e:
                    logger.warning(f"MATRIZ health check failed: {e}")
                    checks["matriz_callable"] = False
        else:
            checks["matriz"] = "not_required"

        # Check memory system availability
        if MEMORY_AVAILABLE:
            checks["memory"] = memory_index is not None
        else:
            checks["memory"] = "not_required"

        # Service is ready if core dependencies are available
        # MATRIZ and memory are optional (can run in stub mode)
        core_ready = checks["api"] and checks["rate_limiter"]
        matriz_ok = not MATRIZ_AVAILABLE or checks.get("matriz") is not False
        memory_ok = not MEMORY_AVAILABLE or checks.get("memory") is not False

        all_ready = core_ready and matriz_ok and memory_ok

        return {
            "status": "ready" if all_ready else "degraded",
            "checks": checks,
            "timestamp": time.time(),
            "mode": "full" if (orchestrator and memory_index) else "stub"
        }

    @app.get("/metrics")
    def metrics():
        """Prometheus-format metrics endpoint."""
        return PlainTextResponse(_metrics_text(), media_type="text/plain; version=0.0.4")

    @app.get("/v1/models")
    def models():
        """List available models."""
        return {
            "data": [
                {
                    "id": "lukhas-matriz",
                    "object": "model",
                    "created": 1699564800,
                    "owned_by": "lukhas-ai",
                    "capabilities": ["responses", "embeddings", "dreams"]
                }
            ]
        }

    @app.post("/v1/embeddings")
    async def embeddings(payload: Dict[str, Any]):
        """Generate embeddings for text input."""
        text = payload.get("input", "")
        if not text:
            raise HTTPException(status_code=400, detail="Input text required")

        # Try to use real memory system, fallback to deterministic stub
        if memory_index and MEMORY_AVAILABLE:
            try:
                # Generate a simple embedding (in production, use actual model)
                # For now, create a deterministic vector based on text hash
                import hashlib
                text_hash = hashlib.sha256(text.encode()).digest()
                vec = [float(int(b) % 256) / 255.0 for b in text_hash[:1536]]
                logger.debug(f"Generated embedding for text (length={len(text)})")
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}, using fallback")
                vec = [float(len(text) % 7), 0.0, 1.0]
        else:
            # Stub mode - deterministic vector
            vec = [float(len(text) % 7), 0.0, 1.0]

        return _maybe_trace({"data": [{"embedding": vec, "index": 0}]})

    @app.post("/v1/responses")
    async def responses(payload: Dict[str, Any]):
        """Generate AI responses using MATRIZ orchestrator."""
        user_input = str(payload.get("input", ""))
        if not user_input:
            raise HTTPException(status_code=400, detail="Input required")

        request_id = f"resp_{uuid.uuid4().hex[:8]}"

        # Try to use MATRIZ orchestrator, fallback to echo
        if orchestrator and MATRIZ_AVAILABLE:
            try:
                start_time = time.time()

                # Trace MATRIZ orchestrator call
                with traced_operation(
                    tracer,
                    "matriz.process_query",
                    request_id=request_id,
                    input_length=len(user_input)
                ) as span:
                    result = orchestrator.process_query(user_input)
                    processing_time = time.time() - start_time

                    # Add span attributes
                    if span:
                        span.set_attribute("matriz.processing_time_ms", processing_time * 1000)
                        span.set_attribute("matriz.has_trace", "trace" in result)

                # Extract text from MATRIZ result
                output_text = result.get("response", f"echo: {user_input}")
                trace_info = result.get("trace", {})

                logger.info(
                    f"MATRIZ processed request",
                    extra={
                        "request_id": request_id,
                        "processing_time": processing_time,
                        "has_trace": bool(trace_info)
                    }
                )

                out = {
                    "id": request_id,
                    "model": "lukhas-matriz",
                    "output": {"text": output_text},
                    "usage": {
                        "processing_time_ms": round(processing_time * 1000, 2)
                    }
                }
            except Exception as e:
                logger.error(f"MATRIZ processing failed: {e}, using fallback")
                out = {
                    "id": request_id,
                    "model": "lukhas-matriz",
                    "output": {"text": f"echo: {user_input}"},
                    "error_mode": "fallback"
                }
        else:
            # Stub mode - simple echo
            out = {
                "id": request_id,
                "model": "lukhas-matriz",
                "output": {"text": f"echo: {user_input}"},
                "mode": "stub"
            }

        return JSONResponse(_maybe_trace(out))

    @app.post("/v1/dreams")
    async def dreams(payload: Dict[str, Any]):
        """Generate dream scenarios (consciousness exploration)."""
        seed = payload.get("seed", "dream")
        constraints = payload.get("constraints", {})

        # Stub implementation - in production, integrate with consciousness/dreams module
        traces = [
            {"step": "imagine", "content": f"{seed} unfolds in quantum superposition"},
            {"step": "expand", "content": f"Patterns emerge: recursive, fractal, alive"},
            {"step": "critique", "content": f"Coherence check: maintaining ethical boundaries"}
        ]

        return _maybe_trace({
            "id": f"dream_{uuid.uuid4().hex[:8]}",
            "seed": seed,
            "traces": traces,
            "constraints": constraints
        })

    return app
