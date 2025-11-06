"""
OpenAI-compatible API routes for LUKHAS.

Provides minimal, production-safe implementations of:
- /v1/models: Model catalog
- /v1/embeddings: Deterministic hash-based embeddings
- /v1/responses: Non-stream response generation (stub)

All endpoints include:
- Rate limit headers (OpenAI-compatible)
- Request/trace ID threading
- Dev-permissive auth (Bearer token required)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any, Dict, List

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse, StreamingResponse

from adapters.openai import TokenClaims, require_bearer
from bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService

from .schemas import ModulatedChatRequest, ModulatedChatResponse

logger = logging.getLogger(__name__)

# Exported router aggregates both legacy and OpenAI-compatible endpoints.
router = APIRouter(tags=["openai"])
_v1_router = APIRouter(prefix="/v1", tags=["openai"])
_legacy_router = APIRouter(prefix="/openai", tags=["openai"])


def get_service() -> OpenAIModulatedService:
    """Retrieve the OpenAI modulation service instance."""
    return OpenAIModulatedService()


# ΛTAG: openai_facade
@_legacy_router.post(
    "/chat",
    response_model=ModulatedChatResponse,
    summary="Modulated Chat",
    description="Generate a response via OpenAI with LUKHAS modulation applied.",
    responses={
        200: {
            "description": "Modulated chat response.",
            "content": {
                "application/json": {
                    "example": {"response": "This is a modulated response."}
                }
            },
        },
        500: {"description": "Internal Server Error"},
    },
)
async def modulated_chat(req: ModulatedChatRequest) -> ModulatedChatResponse:
    """Generate a response via OpenAI with LUKHAS modulation applied."""
    try:
        service = get_service()
        result = await service.generate(
            prompt=req.prompt,
            context=req.context,
            task=req.task,
        )
        return ModulatedChatResponse(**result)
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.exception("OpenAI modulated chat failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@_legacy_router.post(
    "/chat/stream",
    summary="Modulated Chat Stream",
    description="Stream a response via OpenAI with LUKHAS modulation applied.",
    responses={
        200: {
            "description": "Streamed modulated chat response.",
            "content": {"text/plain": {"example": "This is a streamed response."}},
        },
        500: {"description": "Internal Server Error"},
    },
)
async def modulated_chat_stream(req: ModulatedChatRequest) -> StreamingResponse:
    """Stream a response via OpenAI with LUKHAS modulation applied."""
    service = get_service()

    async def token_gen():
        async for chunk in await service.generate_stream(
            prompt=req.prompt,
            context=req.context,
            task=req.task,
        ):
            yield chunk

    return StreamingResponse(token_gen(), media_type="text/plain")


@_legacy_router.get(
    "/metrics",
    summary="OpenAI Modulation Metrics",
    description="Expose safe subset of OpenAI modulation metrics.",
    responses={
        200: {
            "description": "OpenAI modulation metrics.",
            "content": {"application/json": {"example": {"requests": 100, "errors": 5}}},
        },
    },
)
async def openai_metrics() -> JSONResponse:
    """Expose safe subset of OpenAI modulation metrics."""
    service = get_service()
    metrics = getattr(service, "metrics", {}) or {}
    return JSONResponse(metrics)


# ------------------------------------------------------------------------------
# OpenAI facade helpers and endpoints
# ------------------------------------------------------------------------------
# ΛTAG: openai_facade

def require_api_key(
    authorization: str | None = Header(None),
    x_lukhas_project: str | None = Header(default=None, alias="X-Lukhas-Project"),
) -> TokenClaims:
    """Validate Bearer tokens using PolicyGuard-backed dependency."""

    return require_bearer(
        authorization=authorization,
        required_scopes=("api.read",),
        project_id=x_lukhas_project,
    )


def _rl_headers() -> Dict[str, str]:
    """Generate rate limit headers (stub values)."""
    now = int(time.time())
    return {
        "X-RateLimit-Limit": "60",
        "X-RateLimit-Remaining": "59",
        "X-RateLimit-Reset": str(now + 60),
        "x-ratelimit-limit-requests": "60",
        "x-ratelimit-remaining-requests": "59",
        "x-ratelimit-reset-requests": str(now + 60),
    }


def _with_std_headers(resp: Response, trace_id: str | None) -> None:
    """Apply standard headers to response (RL + trace ID)."""
    for key, value in _rl_headers().items():
        resp.headers[key] = value
    req_id = trace_id or uuid.uuid4().hex
    resp.headers["X-Request-Id"] = req_id
    resp.headers["X-Trace-Id"] = req_id


@_v1_router.get(
    "/models",
    summary="List Models",
    description="List available models (OpenAI-compatible format).",
    responses={
        200: {
            "description": "A list of available models.",
            "content": {
                "application/json": {
                    "example": {
                        "object": "list",
                        "data": [
                            {"id": "lukhas-mini", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
                            {"id": "lukhas-embed-1", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
                        ],
                    }
                }
            },
        },
    },
)
def list_models(
    request: Request,
    response: Response,
    _claims=Depends(require_api_key),
) -> Dict[str, Any]:
    """List available models (OpenAI-compatible format)."""
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    _with_std_headers(response, trace_id)
    data = [
        {"id": "lukhas-mini", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
        {"id": "lukhas-embed-1", "object": "model", "created": 1730000000, "owned_by": "lukhas"},
    ]
    return {"object": "list", "data": data}


def _hash_to_vec(text: str, dim: int = 128) -> List[float]:
    """Generate deterministic embedding from text using hash expansion."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    nums: List[float] = []
    seed = bytearray(digest)
    idx = 0
    while len(nums) < dim:
        chunk = hashlib.sha256(seed + bytes([idx & 0xFF])).digest()
        nums.extend([byte / 255.0 for byte in chunk])
        idx += 1
    return nums[:dim]


def _invalid_request(detail: str, param: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "error": {
            "type": "invalid_request_error",
            "message": detail,
            "code": "invalid_request_error",
        }
    }
    if param:
        payload["error"]["param"] = param
    return payload


@_v1_router.post(
    "/embeddings",
    summary="Create Embeddings",
    description="Create deterministic embeddings (OpenAI-compatible format).",
    responses={
        200: {
            "description": "Embeddings created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "object": "list",
                        "data": [
                            {
                                "object": "embedding",
                                "index": 0,
                                "embedding": [0.1, 0.2, 0.3],
                            }
                        ],
                        "model": "lukhas-embed-1",
                        "usage": {"prompt_tokens": 5, "total_tokens": 5},
                    }
                }
            },
        },
        400: {"description": "Invalid request"},
    },
)
def create_embeddings(
    request: Request,
    response: Response,
    payload: Dict[str, Any] = Body(...),
    _claims=Depends(require_api_key),
) -> Dict[str, Any]:
    """Create deterministic embeddings (OpenAI-compatible format)."""
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    _with_std_headers(response, trace_id)

    model = payload.get("model", "lukhas-embed-1")
    inputs = payload.get("input", [])
    if isinstance(inputs, str):
        inputs = [inputs]

    if not isinstance(inputs, list) or not inputs or any(not str(item).strip() for item in inputs):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_invalid_request("`input` must be a non-empty string or list of strings.", param="input"),
        )

    vectors = [
        {
            "object": "embedding",
            "index": idx,
            "embedding": _hash_to_vec(f"{model}:{text}"),
        }
        for idx, text in enumerate(inputs)
    ]

    token_counts = [len(str(text).split()) for text in inputs]
    prompt_tokens = sum(token_counts)

    return {
        "object": "list",
        "data": vectors,
        "model": model,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "total_tokens": prompt_tokens,
        },
    }


def _resolve_stream_plan(text: str, max_tokens: int | None) -> Dict[str, Any]:
    """Determine chunking strategy for streaming responses."""
    normalized_len = max(len(text), 1)
    heavy_request = (max_tokens or 0) >= 1500 or normalized_len >= 200
    chunk_count = 6 if not heavy_request else 12
    target_total_bytes = 800 if not heavy_request else 6000
    per_chunk_bytes = max(64, target_total_bytes // chunk_count)
    return {
        "chunk_count": chunk_count,
        "per_chunk_bytes": per_chunk_bytes,
        "heavy": heavy_request,
    }


def _stream_chunks(text: str, plan: Dict[str, Any]) -> List[str]:
    """Build deterministic chunk payloads for SSE streaming."""
    base = text or "symbolic stream"
    chunks: List[str] = []
    per_chunk = plan["per_chunk_bytes"]
    for idx in range(plan["chunk_count"]):
        prefix = f"chunk-{idx}: "
        body = (base + " ") * ((per_chunk // max(len(base), 1)) + 2)
        chunk_text = (prefix + body)[:per_chunk]
        chunks.append(chunk_text)
    return chunks


@_v1_router.post(
    "/responses",
    summary="Create Response",
    description="Create response (OpenAI Responses API format, non-stream stub).",
    responses={
        200: {
            "description": "Response created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": "resp_123",
                        "object": "response",
                        "created": 1730000000,
                        "model": "lukhas-mini",
                        "output": [{"type": "output_text", "text": "echo: Hello"}],
                        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
                    }
                }
            },
        },
        400: {"description": "Invalid request"},
    },
)
def create_response(
    request: Request,
    response: Response,
    payload: Dict[str, Any] = Body(...),
    _claims=Depends(require_api_key),
) -> Dict[str, Any] | StreamingResponse:
    """Create response (OpenAI Responses API format, non-stream stub)."""
    trace_id = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")

    model = payload.get("model", "lukhas-mini")
    user_text: Any = (
        payload.get("input")
        or payload.get("messages")
        or payload.get("contents")
        or ""
    )

    if isinstance(user_text, list):
        try:
            user_text = next(
                (
                    part.get("text")
                    for message in user_text
                    for part in (message.get("content") or [])
                    if part.get("type") == "input_text"
                ),
                "",
            )
        except Exception:  # pragma: no cover - fallback path
            user_text = ""

    if not isinstance(user_text, str):
        user_text = str(user_text)

    if not user_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_invalid_request("`input` is required for /v1/responses.", param="input"),
        )

    out_text = f"echo: {user_text}".strip()
    now = int(time.time())
    resp_id = f"resp_{uuid.uuid4().hex}"

    input_tokens = len(user_text.split())
    output_tokens = len(out_text.split())

    stream_requested = bool(payload.get("stream"))
    max_tokens = payload.get("max_tokens")

    if stream_requested:
        plan = _resolve_stream_plan(out_text, max_tokens)
        chunks = _stream_chunks(out_text, plan)

        async def sse_generator() -> AsyncGenerator[str, None]:
            for chunk in chunks:
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.12)
            yield "data: [DONE]\n\n"

        stream_response = StreamingResponse(sse_generator(), media_type="text/event-stream")
        _with_std_headers(stream_response, trace_id)
        return stream_response

    _with_std_headers(response, trace_id)

    return {
        "id": resp_id,
        "object": "response",
        "created": now,
        "model": model,
        "output": [{"type": "output_text", "text": out_text}],
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    }


router.include_router(_v1_router)
router.include_router(_legacy_router)

__all__ = ["router"]
