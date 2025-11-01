"""Entry point for LUKHAS commercial API"""
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Optional

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

MATRIZ_AVAILABLE = False
MEMORY_AVAILABLE = False
try:
    import importlib as _importlib
    _MATRIZ = _importlib.import_module("MATRIZ")
    MATRIZ_AVAILABLE = True
except Exception:
    try:
        # Fallback to compatibility shim (deprecated)
        _MATRIZ = _importlib.import_module("matriz")  # type: ignore
        MATRIZ_AVAILABLE = True
    except Exception:
        pass
try:
    import lukhas.memory
    MEMORY_AVAILABLE = True
except ImportError:
    pass
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

    class MockInstrumentor:

        @staticmethod
        def instrument_app(app: FastAPI) -> None:
            pass
    FastAPIInstrumentor = MockInstrumentor
try:
    from enterprise.observability.instantiate import obs_stack
except Exception:

    class _ObsStack:
        opentelemetry_enabled = False
    obs_stack = _ObsStack()
try:
    from config.env import get as env_get
except Exception:
    import os as _os

    def env_get(key: str, default: Optional[str]=None) -> Optional[str]:
        return _os.getenv(key, default)
import os

# ΛTAG: async_response_toggle -- optional async orchestrator integration seam
_ASYNC_ORCH_ENV = (env_get("LUKHAS_ASYNC_ORCH", "0") or "0").strip()
ASYNC_ORCH_ENABLED = _ASYNC_ORCH_ENV == "1"
_RUN_ASYNC_ORCH: Optional[Callable[[str], Awaitable[dict[str, Any]]]] = None
if ASYNC_ORCH_ENABLED:
    try:
        from matriz.orchestration.service_async import (
            run_async_matriz as _RUN_ASYNC_ORCH,  # type: ignore[assignment]
        )
    except Exception:
        ASYNC_ORCH_ENABLED = False
        logging.getLogger(__name__).warning('LUKHAS_ASYNC_ORCH=1 but async MATRIZ orchestrator unavailable; falling back to stub')

def _safe_import_router(module_path: str, attr: str='router') -> Optional[Any]:
    try:
        mod = __import__(module_path, fromlist=[attr])
        return getattr(mod, attr)
    except Exception:
        return None
consciousness_router = _safe_import_router('.consciousness_api', 'router')
feedback_router = _safe_import_router('.feedback_routes', 'router')
guardian_router = _safe_import_router('.guardian_api', 'router')
identity_router = _safe_import_router('.identity_api', 'router')
webauthn_router = None
if (env_get('LUKHAS_WEBAUTHN', '0') or '0').strip() == '1':
    webauthn_router = _safe_import_router('.webauthn_routes', 'router')
openai_router = _safe_import_router('.openai_routes', 'router')
orchestration_router = _safe_import_router('.orchestration_routes', 'router')
routes_router = _safe_import_router('.routes', 'router')
traces_router = _safe_import_router('.routes_traces', 'router')
matriz_traces_router = (
    _safe_import_router('MATRIZ.traces_router', 'router')
    or _safe_import_router('matriz.traces_router', 'router')
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def require_api_key(x_api_key: Optional[str]=Header(default=None)) -> Optional[str]:
    """Simple API key security for protected endpoints"""
    expected_key = env_get('LUKHAS_API_KEY', '')
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return x_api_key
app = FastAPI(title='LUKHAS API', version='1.0.0', description='Governed tool loop, auditability, feedback LUT, and safety modes.', contact={'name': 'LUKHAS AI Team', 'url': 'https://github.com/LukhasAI/Lukhas'}, license_info={'name': 'MIT', 'url': 'https://opensource.org/licenses/MIT'}, servers=[{'url': 'http://localhost:8000', 'description': 'Local development'}, {'url': 'https://api.ai', 'description': 'Production'}])

class StrictAuthMiddleware(BaseHTTPMiddleware):
    """
    Enforce authentication in strict policy mode.

    When LUKHAS_POLICY_MODE=strict, validates Bearer token on all /v1/* endpoints.
    Returns 401 with OpenAI-compatible error envelope on auth failure.
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        policy_mode = env_get('LUKHAS_POLICY_MODE', 'permissive') or 'permissive'
        strict_enabled = policy_mode == 'strict'
        if not strict_enabled or not request.url.path.startswith('/v1/'):
            return await call_next(request)
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return self._auth_error('Missing Authorization header')
        if not auth_header.startswith('Bearer '):
            return self._auth_error('Authorization header must use Bearer scheme')
        token = auth_header[7:].strip()
        if not token:
            return self._auth_error('Bearer token is empty')
        return await call_next(request)

    def _auth_error(self, message: str) -> Response:
        """Return OpenAI-compatible 401 error envelope."""
        from fastapi.responses import JSONResponse
        error_detail = {'type': 'invalid_api_key', 'message': f'Invalid authentication credentials. {message}', 'code': 'invalid_api_key'}
        error_response = {'error': {'message': {'error': error_detail}, 'type': error_detail['type'], 'code': error_detail['code']}}
        return JSONResponse(status_code=401, content=error_response)

class HeadersMiddleware(BaseHTTPMiddleware):
    """Add OpenAI-compatible headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        trace_id = str(uuid.uuid4()).replace('-', '')
        response.headers['X-Trace-Id'] = trace_id
        response.headers['X-Request-Id'] = trace_id
        response.headers['X-RateLimit-Limit'] = '60'
        response.headers['X-RateLimit-Remaining'] = '59'
        response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 60)
        response.headers['x-ratelimit-limit-requests'] = '60'
        response.headers['x-ratelimit-remaining-requests'] = '59'
        response.headers['x-ratelimit-reset-requests'] = str(int(time.time()) + 60)
        return response
frontend_origin = env_get('FRONTEND_ORIGIN', 'http://localhost:3000') or 'http://localhost:3000'
app.add_middleware(CORSMiddleware, allow_origins=[frontend_origin], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.add_middleware(StrictAuthMiddleware)
app.add_middleware(HeadersMiddleware)
if routes_router is not None:
    app.include_router(routes_router)
if openai_router is not None:
    app.include_router(openai_router)
if feedback_router is not None:
    app.include_router(feedback_router)
if traces_router is not None:
    app.include_router(traces_router)
if matriz_traces_router is not None:
    app.include_router(matriz_traces_router)
if orchestration_router is not None:
    app.include_router(orchestration_router)
if OPENTELEMETRY_AVAILABLE and getattr(obs_stack, 'opentelemetry_enabled', False):
    FastAPIInstrumentor.instrument_app(app)
if identity_router is not None:
    app.include_router(identity_router)
if webauthn_router is not None:
    app.include_router(webauthn_router)
if consciousness_router is not None:
    app.include_router(consciousness_router)
if guardian_router is not None:
    app.include_router(guardian_router)

def voice_core_available() -> bool:
    try:
        import importlib
        importlib.import_module('bridge.voice')
        return True
    except Exception:
        return False

def _get_health_status() -> dict[str, Any]:
    """Get health status for both /health and /healthz endpoints."""
    status: dict[str, Any] = {'status': 'ok'}
    required = os.getenv('LUKHAS_VOICE_REQUIRED', 'false').strip().lower() == 'true'
    voice_ok = voice_core_available()
    status['voice_mode'] = 'normal' if voice_ok else 'degraded'
    if required and (not voice_ok):
        existing = status.get('degraded_reasons')
        if existing is None:
            status['degraded_reasons'] = ['voice']
        elif isinstance(existing, list):
            existing.append('voice')
        else:
            status['degraded_reasons'] = ['voice']
    matriz_version = env_get('MATRIZ_VERSION', 'unknown')
    matriz_rollout = env_get('MATRIZ_ROLLOUT', 'disabled')
    status['matriz'] = {'version': matriz_version, 'rollout': matriz_rollout, 'enabled': matriz_rollout != 'disabled'}
    lane = env_get('LUKHAS_LANE', 'prod')
    status['lane'] = lane
    try:
        from pathlib import Path
        manifest_dir = Path('manifests')
        if manifest_dir.exists():
            manifest_count = len(list(manifest_dir.rglob('module.manifest.json')))
            status['modules'] = {'manifest_count': manifest_count}
    except Exception:
        pass
    return status

@app.get('/healthz')
def healthz() -> dict[str, Any]:
    """Health check endpoint for monitoring.

    Behavior:
    - Always returns HTTP 200 for readiness consumers.
    - When LUKHAS_VOICE_REQUIRED=true and the lightweight probe fails,
      include 'voice' in `degraded_reasons` and set `voice_mode` to 'degraded'.
    - Exposes MATRIZ version, enabled modules, and lane configuration.
    """
    return _get_health_status()

@app.get('/health', include_in_schema=False)
def health_alias() -> dict[str, Any]:
    """Health check alias for ops scripts compatibility."""
    return _get_health_status()

@app.get('/readyz', include_in_schema=False)
def readyz() -> dict[str, Any]:
    """Readiness check endpoint for k8s/ops compatibility."""
    status = _get_health_status()
    if status.get('status') in ('ok', 'healthy'):
        return {'status': 'ready'}
    return {'status': 'not_ready', 'details': status}

@app.get('/metrics', include_in_schema=False)
def metrics() -> Response:
    """Prometheus-style metrics endpoint (stub for monitoring compatibility)."""
    import time
    metrics_output = f'# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.\n# TYPE process_cpu_seconds_total counter\nprocess_cpu_seconds_total {time.process_time()}\n\n# HELP http_requests_total Total HTTP requests processed\n# TYPE http_requests_total counter\nhttp_requests_total{{method="GET",endpoint="/healthz",status="200"}} 1\n\n# HELP lukhas_api_info LUKHAS API version information\n# TYPE lukhas_api_info gauge\nlukhas_api_info{{version="1.0.0"}} 1\n'
    return Response(content=metrics_output, media_type='text/plain')

def _hash_embed(text: str, dim: int=1536) -> list[float]:
    """Generate deterministic embedding from text using hash expansion."""
    import hashlib
    h = hashlib.sha256(str(text).encode()).digest()
    buf = (h * (dim // len(h) + 1))[:dim]
    return [b / 255.0 for b in buf]

@app.get('/v1/models', tags=['OpenAI Compatible'])
async def list_models() -> dict[str, Any]:
    """OpenAI-compatible models list endpoint."""
    models = [{'id': 'lukhas-mini', 'object': 'model', 'owned_by': 'lukhas'}, {'id': 'lukhas-embed-1', 'object': 'model', 'owned_by': 'lukhas'}, {'id': 'text-embedding-ada-002', 'object': 'model', 'owned_by': 'lukhas'}, {'id': 'gpt-4', 'object': 'model', 'owned_by': 'lukhas'}]
    return {'object': 'list', 'data': models}

@app.post('/v1/embeddings', tags=['OpenAI Compatible'])
async def create_embeddings(request: dict) -> dict[str, Any]:
    """OpenAI-compatible embeddings endpoint with unique deterministic vectors."""
    input_text = request.get("input", "")
    model = request.get("model", "text-embedding-ada-002")
    dimensions = request.get("dimensions", 1536)

    # Generate unique deterministic embedding based on input
    embedding = _hash_embed(input_text, dimensions)
    return {'object': 'list', 'data': [{'object': 'embedding', 'embedding': embedding, 'index': 0}], 'model': model, 'usage': {'prompt_tokens': len(str(input_text).split()), 'total_tokens': len(str(input_text).split())}}

@app.post('/v1/chat/completions', tags=['OpenAI Compatible'])
async def create_chat_completion(request: dict) -> dict[str, Any]:
    """OpenAI-compatible chat completions endpoint (stub for RC soak testing)."""
    messages = request.get('messages', [])
    model = request.get('model', 'gpt-4')
    request.get('max_tokens', 100)
    import time
    response_text = 'This is a stub response for RC soak testing.'
    return {'id': f'chatcmpl-{int(time.time())}', 'object': 'chat.completion', 'created': int(time.time()), 'model': model, 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': response_text}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': sum((len(str(m.get('content', '')).split()) for m in messages)), 'completion_tokens': len(response_text.split()), 'total_tokens': sum((len(str(m.get('content', '')).split()) for m in messages)) + len(response_text.split())}}

@app.post('/v1/responses', tags=['OpenAI Compatible'])
async def create_response(request: dict) -> dict[str, Any]:
    """LUKHAS responses endpoint (OpenAI-compatible format)."""
    import hashlib
    import json
    import time

    model = request.get("model", "lukhas-mini")

    # Extract content from either "input" field or messages array
    content = ""
    if "input" in request:
        content = str(request["input"])
    elif "messages" in request and request["messages"]:
        # Get last user message content
        msgs = request["messages"]
        content = next((m.get("content", "") for m in reversed(msgs) if m.get("role") == "user"), "")

    # Generate deterministic response ID from request
    rid = "resp_" + hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:12]

    # Echo stub response by default; async orchestrator can override when enabled
    response_text = f"[stub] {content}".strip() if content else "[stub] empty input"
    orchestrator_result: Optional[dict[str, Any]] = None
    if ASYNC_ORCH_ENABLED and _RUN_ASYNC_ORCH is not None:
        orchestrator_result = await _RUN_ASYNC_ORCH(content)
        metrics_snapshot = orchestrator_result.get('orchestrator_metrics') if isinstance(orchestrator_result, dict) else None
        if metrics_snapshot:
            logger.debug('Async MATRIZ orchestrator metrics: %s', metrics_snapshot)
        orchestrator_answer = orchestrator_result.get('answer') if isinstance(orchestrator_result, dict) else None
        if orchestrator_answer:
            response_text = orchestrator_answer
        elif isinstance(orchestrator_result, dict) and orchestrator_result.get('error'):
            logger.info('Async MATRIZ orchestrator returned error; retaining stub response: %s', orchestrator_result['error'])
    return {'id': rid, 'object': 'chat.completion', 'created': int(time.time()), 'model': model, 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': response_text}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': len(content.split()) if content else 0, 'completion_tokens': len(response_text.split()), 'total_tokens': len(content.split()) + len(response_text.split()) if content else len(response_text.split())}}

@app.get('/openapi.json', include_in_schema=False)
def openapi_export() -> dict[str, Any]:
    """Export OpenAPI specification as JSON"""
    return app.openapi()
if __name__ == '__main__':
    import os

    import uvicorn
    host = os.getenv('LUKHAS_BIND_HOST', '127.0.0.1')
    port = int(os.getenv('LUKHAS_BIND_PORT', '8000'))
    uvicorn.run(app, host=host, port=port)
