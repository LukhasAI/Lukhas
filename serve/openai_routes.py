"""
OpenAI-compatible API routes for LUKHAS.
"""
import asyncio
import hashlib
import json
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator
from matriz.core.memory_system import MemorySystem, MemoryQuery, MemoryType

from .openai_schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    EmbeddingRequest,
    EmbeddingResponse,
    Embedding,
    Usage,
)

router = APIRouter(prefix="/v1", tags=["openai"])

class StreamCognitiveOrchestrator(AsyncCognitiveOrchestrator):
    async def process_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """A simple streaming processor for the orchestrator."""
        query = " ".join([msg["content"] for msg in messages])
        response = await self.process_query_async(query)
        answer = response.get("answer", "No answer found.")
        for word in answer.split():
            yield word
            await asyncio.sleep(0.1)

# Instantiate the MATRIZ engine and MemorySystem
matriz_engine = StreamCognitiveOrchestrator()
memory_system = MemorySystem()


def _hash_to_vec(text: str, dim: int = 1536) -> List[float]:
    """Generate a deterministic embedding from text using SHA-256."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    seed = int.from_bytes(h, "big")
    rng = lambda s: (s * 1103515245 + 12345) & 0x7FFFFFFF
    vec = []
    for _ in range(dim):
        seed = rng(seed)
        vec.append(seed / 0x7FFFFFFF)
    return vec


class OpenAIErrorHandler:
    """Formats errors into OpenAI-compatible JSON responses."""

    @staticmethod
    def format_error(error: Exception, status_code: int) -> Dict[str, Any]:
        error_type = "invalid_request_error"
        if status_code == 429:
            error_type = "rate_limit_exceeded"
        elif status_code >= 500:
            error_type = "api_error"

        return {
            "error": {
                "message": str(error),
                "type": error_type,
                "param": None,
                "code": None,
            }
        }

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    if not request.messages:
        raise HTTPException(
            status_code=400,
            detail=OpenAIErrorHandler.format_error(
                Exception("messages required"), 400
            ),
        )

    if request.stream:
        return StreamingResponse(
            stream_chat_completion(request),
            media_type="text/event-stream",
        )

    try:
        query = " ".join([msg["content"] for msg in request.messages])
        matriz_response = await matriz_engine.process_query_async(query)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=OpenAIErrorHandler.format_error(e, 500)
        )

    response_content = matriz_response.get("answer", "No answer found.")
    prompt_tokens = len(query.split())
    completion_tokens = len(response_content.split())

    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message={"role": "assistant", "content": response_content},
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


async def stream_chat_completion(
    request: ChatCompletionRequest,
) -> AsyncGenerator[str, None]:
    """Stream chat completion chunks."""
    request_id = f"chatcmpl-{uuid.uuid4().hex}"
    created_time = int(time.time())

    try:
        async for chunk_text in matriz_engine.process_stream(request.messages):
            chunk = {
                "id": request_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": f" {chunk_text}"},
                        "finish_reason": None,
                    }
                ],
            }
            yield f"data: {json.dumps(chunk)}\n\n"

        final_chunk = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_chunk = OpenAIErrorHandler.format_error(e, 500)
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"


@router.get("/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": "lukhas-matriz-v1",
                "object": "model",
                "created": 1677610602,
                "owned_by": "lukhas-ai",
            },
            {
                "id": "lukhas-consciousness-v1",
                "object": "model",
                "created": 1677610602,
                "owned_by": "lukhas-ai",
            },
        ],
    }


@router.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """Generate embeddings for a given input."""
    inputs = (
        request.input if isinstance(request.input, list) else [request.input]
    )

    # Store memories and generate embeddings
    for text in inputs:
        memory_system.store_memory(
            content={"text": text},
            memory_type=MemoryType.EPISODIC,
        )

    # Retrieve memories to get embeddings (in a real scenario, this would be more direct)
    retrieved_memories = memory_system.retrieve_memories(
        MemoryQuery(query_text=",".join(inputs), memory_types=[MemoryType.EPISODIC])
    )

    embeddings = [_hash_to_vec(m.content.get("text", "")) for m in retrieved_memories]

    prompt_tokens = sum(len(text.split()) for text in inputs)

    return EmbeddingResponse(
        object="list",
        data=[
            Embedding(object="embedding", embedding=emb, index=i)
            for i, emb in enumerate(embeddings)
        ],
        model=request.model,
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=0,
            total_tokens=prompt_tokens,
        ),
    )
