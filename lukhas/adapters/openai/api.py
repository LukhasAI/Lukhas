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
import logging
import math
import os
import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Any, Dict, List, Optional

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from lukhas.adapters.openai.auth import TokenClaims, require_bearer
from lukhas.core.reliability.ratelimit import RateLimiter, rate_limit_error
from lukhas.observability.tracing import get_trace_id_hex, setup_otel, traced_operation

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
    from lukhas.memory.index_manager import IndexManager
    MEMORY_AVAILABLE = True
except ImportError:
    logger.warning("Memory system not available, using stub embeddings")
    MEMORY_AVAILABLE = False
    EmbeddingIndex = None  # type: ignore
    IndexManager = None  # type: ignore

# Try to import policy guard for RBAC (graceful fallback)
try:
    from lukhas.core.policy_guard import PolicyGuard
    POLICY_GUARD_AVAILABLE = True
except ImportError:
    logger.warning("PolicyGuard not available, RBAC checks will be permissive")
    POLICY_GUARD_AVAILABLE = False
    PolicyGuard = None  # type: ignore

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

    # ---------- OpenAI-style error envelope normalizer ----------
    OPENAI_ERROR_CODE_BY_STATUS = {
        401: "invalid_api_key",
        403: "authorization_error",
        429: "rate_limit_exceeded",
    }

    def _trace_headers(request: Request) -> dict:
        tid = getattr(getattr(request, "state", object()), "trace_id", None)
        return {"X-Trace-Id": tid} if tid else {}

    def _payload(code: str, message: str) -> dict:
        return {"error": {"type": code, "message": message, "code": code}}

    async def _http_exc_handler(request: Request, exc: StarletteHTTPException):
        code = OPENAI_ERROR_CODE_BY_STATUS.get(exc.status_code, "http_error")
        # Prefer explicit detail; fall back to canonical messages.
        detail_str = str(exc.detail) if exc.detail else ""
        if exc.status_code == 401 and not detail_str.strip():
            message = "Invalid authentication credentials"
        elif exc.status_code == 403 and not detail_str.strip():
            message = "Forbidden"
        elif exc.status_code == 429 and not detail_str.strip():
            message = "Rate limit exceeded"
        else:
            message = detail_str or "HTTP error"
        return JSONResponse(
            _payload(code, message),
            status_code=exc.status_code,
            headers=_trace_headers(request),
        )

    async def _generic_exc_handler(request: Request, exc: Exception):
        # Optionally log with your structured logger here.
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            _payload("internal_error", "Internal server error"),
            status_code=500,
            headers=_trace_headers(request),
        )

    app.add_exception_handler(StarletteHTTPException, _http_exc_handler)
    app.add_exception_handler(Exception, _generic_exc_handler)
    # ---------- /OpenAI-style error envelope normalizer ----------

    # Phase 3: Add security and observability middlewares
    try:
        from lukhas.observability.security_headers import (
            SecurityHeadersMiddleware,
            VersionHeaderMiddleware,
        )
        from lukhas.observability.tracing import TraceHeaderMiddleware
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(VersionHeaderMiddleware)
        if TraceHeaderMiddleware:
            app.add_middleware(TraceHeaderMiddleware)
        logger.info("Phase 3 middlewares initialized (security, version, trace headers)")
    except Exception as e:
        logger.warning(f"Failed to load Phase 3 middlewares: {e}")

    # Install log redaction globally
    try:
        from lukhas.observability.log_redaction import install_global_redaction
        install_global_redaction()
        logger.info("Log redaction filter installed")
    except Exception as e:
        logger.warning(f"Failed to install log redaction: {e}")

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
        except Exception:
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

        # Check rate limit (now keys by route + bearer token/IP)
        allowed, retry_after = rate_limiter.check_limit(request)
        rl_key = rate_limiter.key_for_request(request)
        principal = rate_limiter.principal_for_request(request)
        route = request.url.path

        if not allowed:
            # Phase 3: Add OpenAI-style headers and metrics on 429
            try:
                from lukhas.observability.ratelimit_metrics import record_hit
                record_hit(route, principal)
            except Exception:
                pass

            headers = rate_limiter.headers_for(rl_key)
            headers["Retry-After"] = str(int(math.ceil(retry_after))) if retry_after else "1"

            error_response = rate_limit_error(retry_after)
            return JSONResponse(
                status_code=429,
                content=error_response["error"],
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Phase 3: Add rate-limit headers to successful responses
        try:
            response.headers.update(rate_limiter.headers_for(rl_key))

            # Record metrics for successful requests
            from lukhas.observability.ratelimit_metrics import record_window
            record_window(route, principal, rate_limiter, rl_key)
        except Exception:
            # Never crash due to metrics
            pass

        return response

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
    index_manager: Optional[Any] = None
    if MEMORY_AVAILABLE and EmbeddingIndex:
        try:
            memory_index = EmbeddingIndex(dimension=1536)  # OpenAI ada-002 dimension
            logger.info("Memory embedding index initialized")

            # Initialize index manager for API routes
            if IndexManager:
                index_manager = IndexManager()
                logger.info("Index manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize memory index: {e}")
            memory_index = None
            index_manager = None

    # Initialize policy guard (if available)
    policy_guard: Optional[Any] = None
    if POLICY_GUARD_AVAILABLE and PolicyGuard:
        try:
            policy_guard = PolicyGuard(lane="openai-api")
            logger.info("PolicyGuard initialized for RBAC")
        except Exception as e:
            logger.warning(f"Failed to initialize PolicyGuard: {e}, RBAC will be permissive")
            policy_guard = None

    # Include indexes router (if index_manager available)
    if index_manager is not None:
        try:
            from lukhas.adapters.openai.routes import indexes_router
            from lukhas.adapters.openai.routes.indexes import set_index_manager, set_policy_guard

            # Set global instances for router dependencies
            set_index_manager(index_manager)
            if policy_guard is not None:
                set_policy_guard(policy_guard)

            # Include router
            app.include_router(indexes_router)
            logger.info("Indexes router included at /v1/indexes")
        except Exception as e:
            logger.error(f"Failed to include indexes router: {e}")

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
            checks["lukhas.memory"] = memory_index is not None

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
            checks["lukhas.memory"] = memory_index is not None
        else:
            checks["lukhas.memory"] = "not_required"

        # Service is ready if core dependencies are available
        # MATRIZ and memory are optional (can run in stub mode)
        core_ready = checks["api"] and checks["rate_limiter"]
        matriz_ok = not MATRIZ_AVAILABLE or checks.get("matriz") is not False
        memory_ok = not MEMORY_AVAILABLE or checks.get("lukhas.memory") is not False

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
    def models(claims: TokenClaims = Depends(require_bearer)):
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
    async def embeddings(request: Request, claims: TokenClaims = Depends(require_bearer)):
        """Generate embeddings for text input."""
        # Phase 3: Check for idempotency key
        idem_key = request.headers.get("Idempotency-Key")
        if idem_key:
            try:
                from lukhas.core.reliability import idempotency as idem
                body_bytes = await request.body()
                cache_key = idem.cache_key(request.url.path, idem_key, body_bytes)
                cached = idem.get(cache_key)
                if cached:
                    status, body, ctype = cached
                    return Response(content=body, media_type=ctype, status_code=status)
            except Exception as e:
                logger.warning(f"Idempotency check failed: {e}")

        payload = await request.json()
        text = payload.get("input", "")
        if not text:
            raise HTTPException(status_code=400, detail="Input text required")

        # Try to use real memory system, fallback to deterministic stub
        if memory_index and MEMORY_AVAILABLE:
            try:
                # Generate a simple embedding (in production, use actual model)
                # For now, create a deterministic 1536-dim vector based on text hash
                import hashlib
                # Use multiple hashes to generate 1536 dimensions (1536/32 = 48 hashes)
                vec = []
                for i in range(48):
                    # Hash text with counter to get different values
                    hash_input = f"{text}:{i}".encode()
                    text_hash = hashlib.sha256(hash_input).digest()
                    vec.extend([float(int(b) % 256) / 255.0 for b in text_hash])
                vec = vec[:1536]  # Ensure exactly 1536 dimensions
                logger.debug(f"Generated embedding for text (length={len(text)})")
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}, using fallback")
                # Fallback: simple deterministic 1536-dim vector
                import hashlib
                vec = []
                for i in range(48):
                    hash_input = f"{text}:{i}".encode()
                    text_hash = hashlib.sha256(hash_input).digest()
                    vec.extend([float(int(b) % 256) / 255.0 for b in text_hash])
                vec = vec[:1536]
        else:
            # Stub mode - deterministic 1536-dim vector based on text hash
            import hashlib
            vec = []
            for i in range(48):
                hash_input = f"{text}:{i}".encode()
                text_hash = hashlib.sha256(hash_input).digest()
                vec.extend([float(int(b) % 256) / 255.0 for b in text_hash])
            vec = vec[:1536]

        result_dict = _maybe_trace({"data": [{"embedding": vec, "index": 0}]})

        # Phase 3: Cache response if idempotency key provided
        if idem_key:
            try:
                import json

                from lukhas.core.reliability import idempotency as idem
                resp_bytes = json.dumps(result_dict).encode('utf-8')
                idem.put(cache_key, 200, resp_bytes, "application/json")
            except Exception as e:
                logger.warning(f"Idempotency caching failed: {e}")

        return result_dict

    @app.post("/v1/responses")
    async def responses(request: Request, claims: TokenClaims = Depends(require_bearer)):
        """Generate AI responses using MATRIZ orchestrator."""
        payload = await request.json()
        user_input = str(payload.get("input", ""))
        stream = payload.get("stream", False)

        if not user_input:
            raise HTTPException(status_code=400, detail="Input required")

        # Phase 3: Check for idempotency key (non-streaming only)
        idem_key = request.headers.get("Idempotency-Key")
        if idem_key and not stream:
            try:
                from lukhas.core.reliability import idempotency as idem
                body_bytes = await request.body()
                cache_key = idem.cache_key(request.url.path, idem_key, body_bytes)
                cached = idem.get(cache_key)
                if cached:
                    status, body, ctype = cached
                    return Response(content=body, media_type=ctype, status_code=status)
            except Exception as e:
                logger.warning(f"Idempotency check failed: {e}")

        request_id = f"resp_{uuid.uuid4().hex[:8]}"

        # Phase 3: Streaming support
        if stream:
            import json

            from fastapi.responses import StreamingResponse

            async def _generate_stream():
                """Generate SSE stream for responses."""
                # TODO: Integrate with MATRIZ for real streaming deltas
                # For now, stub implementation
                yield "data: " + json.dumps({
                    "id": request_id,
                    "object": "response.part",
                    "delta": {"text": "Thinking"}
                }) + "\n\n"

                yield "data: " + json.dumps({
                    "id": request_id,
                    "object": "response.part",
                    "delta": {"text": "..."}
                }) + "\n\n"

                # Final result (echo for now)
                yield "data: " + json.dumps({
                    "id": request_id,
                    "object": "response.part",
                    "delta": {"text": f" {user_input}"}
                }) + "\n\n"

                yield "data: [DONE]\n\n"

            return StreamingResponse(_generate_stream(), media_type="text/event-stream")

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
                    "MATRIZ processed request",
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

        result_json = JSONResponse(_maybe_trace(out))

        # Phase 3: Cache response if idempotency key provided (non-streaming only)
        if idem_key and not stream:
            try:
                import json

                from lukhas.core.reliability import idempotency as idem
                resp_bytes = json.dumps(out).encode('utf-8')
                idem.put(cache_key, 200, resp_bytes, "application/json")
            except Exception as e:
                logger.warning(f"Idempotency caching failed: {e}")

        return result_json

    @app.post("/v1/dreams")
    async def dreams(request: Request, claims: TokenClaims = Depends(require_bearer)):
        """Generate dream scenarios (consciousness exploration)."""
        payload = await request.json()
        seed = payload.get("seed", "dream")
        constraints = payload.get("constraints", {})

        # Stub implementation - in production, integrate with consciousness/dreams module
        traces = [
            {"step": "imagine", "content": f"{seed} unfolds in quantum superposition"},
            {"step": "expand", "content": "Patterns emerge: recursive, fractal, alive"},
            {"step": "critique", "content": "Coherence check: maintaining ethical boundaries"}
        ]

        return _maybe_trace({
            "id": f"dream_{uuid.uuid4().hex[:8]}",
            "model": "lukhas-consciousness",
            "seed": seed,
            "traces": traces,
            "constraints": constraints
        })

    return app
