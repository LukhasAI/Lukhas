"""
LUKHAS Python SDK
OpenAI-compatible client with type safety and async support
"""

import os
import time
from typing import Optional, Dict, Any, List, AsyncIterator

import httpx
from pydantic import BaseModel, Field


# ==================== Request/Response Models ====================

class ResponseRequest(BaseModel):
    """Request model for /v1/responses endpoint"""
    prompt: str
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Request model for /v1/chat/completions endpoint"""
    model: str = "lukhas-consciousness-v1"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None


class SearchRequest(BaseModel):
    """Request model for /v1/indexes/search endpoint"""
    query: str
    index_name: Optional[str] = "default"
    top_k: Optional[int] = 10
    threshold: Optional[float] = 0.0
    filter: Optional[Dict[str, Any]] = None


class DreamRequest(BaseModel):
    """Request model for /v1/dreams endpoint"""
    scenario: str
    num_paths: Optional[int] = 3
    depth: Optional[int] = 5
    temperature: Optional[float] = 0.8
    guidance: Optional[List[str]] = None


# ==================== LUKHAS Client ====================

class LukhasClient:
    """
    Synchronous LUKHAS API client
    
    Example:
        ```python
        client = LukhasClient(api_key="sk-lukhas-...")
        response = client.create_response(ResponseRequest(prompt="Hello"))
        print(response["choices"][0]["text"])
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("LUKHAS_API_KEY")
        if not self.api_key:
            raise ValueError("api_key must be provided or set via LUKHAS_API_KEY env var")

        self.base_url = base_url or os.getenv("LUKHAS_BASE_URL", "https://api.ai")

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and extract trace headers"""
        # Add idempotency key for POST requests
        if method.upper() == "POST" and "headers" not in kwargs:
            kwargs["headers"] = {}
        if method.upper() == "POST":
            kwargs["headers"]["Idempotency-Key"] = f"req-{int(time.time())}-{id(kwargs)}"

        response = self.client.request(method, endpoint, **kwargs)

        # Extract trace ID
        trace_id = response.headers.get("X-Trace-Id")
        if trace_id:
            print(f"[LUKHAS] Trace ID: {trace_id}")

        response.raise_for_status()
        return response.json()

    def create_response(self, request: ResponseRequest) -> Dict[str, Any]:
        """Create a text completion"""
        return self._make_request("POST", "/v1/responses", json=request.dict(exclude_none=True))

    def create_chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Create a chat completion"""
        return self._make_request("POST", "/v1/chat/completions", json=request.dict(exclude_none=True))

    def search_index(self, request: SearchRequest) -> Dict[str, Any]:
        """Search an index"""
        return self._make_request("POST", "/v1/indexes/search", json=request.dict(exclude_none=True))

    def create_dream(self, request: DreamRequest) -> Dict[str, Any]:
        """Create a dream scenario"""
        return self._make_request("POST", "/v1/dreams", json=request.dict(exclude_none=True))

    def health(self) -> Dict[str, Any]:
        """Health check"""
        return self._make_request("GET", "/health")

    def close(self):
        """Close the client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncLukhasClient:
    """
    Asynchronous LUKHAS API client
    
    Example:
        ```python
        async with AsyncLukhasClient(api_key="sk-lukhas-...") as client:
            response = await client.create_response(ResponseRequest(prompt="Hello"))
            print(response["choices"][0]["text"])
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("LUKHAS_API_KEY")
        if not self.api_key:
            raise ValueError("api_key must be provided or set via LUKHAS_API_KEY env var")

        self.base_url = base_url or os.getenv("LUKHAS_BASE_URL", "https://api.ai")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make async HTTP request and extract trace headers"""
        # Add idempotency key for POST requests
        if method.upper() == "POST" and "headers" not in kwargs:
            kwargs["headers"] = {}
        if method.upper() == "POST":
            kwargs["headers"]["Idempotency-Key"] = f"req-{int(time.time())}-{id(kwargs)}"

        response = await self.client.request(method, endpoint, **kwargs)

        # Extract trace ID
        trace_id = response.headers.get("X-Trace-Id")
        if trace_id:
            print(f"[LUKHAS] Trace ID: {trace_id}")

        response.raise_for_status()
        return response.json()

    async def create_response(self, request: ResponseRequest) -> Dict[str, Any]:
        """Create a text completion"""
        return await self._make_request("POST", "/v1/responses", json=request.dict(exclude_none=True))

    async def create_chat_completion(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Create a chat completion"""
        return await self._make_request("POST", "/v1/chat/completions", json=request.dict(exclude_none=True))

    async def search_index(self, request: SearchRequest) -> Dict[str, Any]:
        """Search an index"""
        return await self._make_request("POST", "/v1/indexes/search", json=request.dict(exclude_none=True))

    async def create_dream(self, request: DreamRequest) -> Dict[str, Any]:
        """Create a dream scenario"""
        return await self._make_request("POST", "/v1/dreams", json=request.dict(exclude_none=True))

    async def stream_response(self, request: ResponseRequest) -> AsyncIterator[Dict[str, Any]]:
        """Stream a response with SSE"""
        request.stream = True
        idempotency_key = f"stream-{int(time.time())}-{id(request)}"

        async with self.client.stream(
            "POST",
            "/v1/responses",
            json=request.dict(exclude_none=True),
            headers={"Idempotency-Key": idempotency_key},
        ) as response:
            response.raise_for_status()

            # Extract trace ID from headers
            trace_id = response.headers.get("X-Trace-Id")
            if trace_id:
                print(f"[LUKHAS] Trace ID: {trace_id}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                    try:
                        yield eval(data)  # Parse JSON
                    except Exception:
                        continue

    async def health(self) -> Dict[str, Any]:
        """Health check"""
        return await self._make_request("GET", "/health")

    async def close(self):
        """Close the client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
