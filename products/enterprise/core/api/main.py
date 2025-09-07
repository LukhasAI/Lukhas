import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from candidate.bridge.llm_wrappers.base import LLMProvider
from candidate.bridge.orchestration.multi_ai_orchestrator import ModelOrchestrator
import streamlit as st

orchestrator: Optional[ModelOrchestrator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    orchestrator = ModelOrchestrator()
    print("Enterprise API Gateway starting up...")
    print(f"Available providers: {[p.value for p in orchestrator.get_available_providers()]}")
    yield
    print("Enterprise API Gateway shutting down...")


# Initialize the FastAPI app
app = FastAPI(
    title="LUKHAS Enterprise API Gateway",
    description="A robust, high-performance API gateway for multi-AI orchestration.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request to {request.url.path} took {process_time:.4f} seconds")
    return response


# Pydantic models for request and response
class ChatRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None  # e.g., "openai", "anthropic", "google"
    model: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: Optional[str]


from fastapi import APIRouter

router_v1 = APIRouter(prefix="/v1")


@router_v1.post("/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest):
    """
    Unified chat completions endpoint that routes to the best available AI provider.
    """
    try:
        provider_enum = None
        if request.provider:
            try:
                provider_enum = LLMProvider(request.provider)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid provider. Available providers: {[p.value for p in LLMProvider]}",
                )

        response_text, used_provider, used_model = await orchestrator.generate_response(
            prompt=request.prompt,
            provider=provider_enum,
            model=request.model,
        )

        return ChatResponse(
            response=response_text,
            provider=used_provider,
            model=used_model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router_v1)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for the API gateway.
    """
    available_providers = [p.value for p in orchestrator.get_available_providers()]
    return {
        "status": "ok",
        "available_providers": available_providers,
    }
