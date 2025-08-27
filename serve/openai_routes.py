"""Routes exposing the OpenAI Modulated Service"""

import logging

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from lukhas.bridge.llm_wrappers.openai_modulated_service import OpenAIModulatedService

from .schemas import ModulatedChatRequest
from .schemas import ModulatedChatResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/openai", tags=["openai"])


def get_service() -> OpenAIModulatedService:
    # Basic provider; could be replaced with DI if needed
    return OpenAIModulatedService()


@router.post("/chat", response_model=ModulatedChatResponse)
async def modulated_chat(req: ModulatedChatRequest):
    """Generate a response via OpenAI with LUKHAS modulation applied"""
    try:
        service = get_service()
        result = await service.generate(
            prompt=req.prompt,
            context=req.context,
            task=req.task,
        )
        return ModulatedChatResponse(**result)
    except Exception as e:
        logger.exception("OpenAI modulated chat failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def modulated_chat_stream(req: ModulatedChatRequest):
    """Stream a response via OpenAI with LUKHAS modulation applied"""
    service = get_service()

    async def token_gen():
        async for chunk in await service.generate_stream(
            prompt=req.prompt,
            context=req.context,
            task=req.task,
        ):
            yield chunk

    return StreamingResponse(token_gen(), media_type="text/plain")


@router.get("/metrics")
async def openai_metrics():
    service = get_service()
    # Expose safe subset of counters
    metrics = getattr(service, "metrics", {}) or {}
    return JSONResponse(metrics)
