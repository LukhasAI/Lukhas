"""Unit tests for the orchestration OpenAI service wrapper."""
from __future__ import annotations

import asyncio
from collections import deque
from typing import Any, AsyncIterator

import pytest
from labs.orchestration.openai_modulated_service import (
    OpenAIOrchestrationService,
    OrchestratedOpenAIRequest,
)


class _StubBridgeService:
    """Lightweight stub that mimics the bridge OpenAI service."""

    def __init__(self) -> None:
        self.calls: deque[dict[str, Any]] = deque()
        self.concurrent = 0
        self.max_concurrent = 0

    async def generate(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(dict(kwargs))
        return {
            "content": f"echo:{kwargs['prompt']}",
            "metadata": {"request_id": "req-123"},
            "modulation": {"style": "balanced"},
            "tool_analytics": {"tools_used": []},
        }

    async def generate_stream(self, **kwargs: Any) -> AsyncIterator[str]:
        async def _gen() -> AsyncIterator[str]:
            yield "chunk-1"
            yield "chunk-2"

        return _gen()


class _SlowStubBridgeService(_StubBridgeService):
    async def generate(self, **kwargs: Any) -> dict[str, Any]:
        self.concurrent += 1
        self.max_concurrent = max(self.max_concurrent, self.concurrent)
        try:
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            return await super().generate(**kwargs)
        finally:
            self.concurrent -= 1


class _TimeoutStubBridgeService(_StubBridgeService):
    async def generate(self, **kwargs: Any) -> dict[str, Any]:
        await asyncio.sleep(0.05)
        return await super().generate(**kwargs)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.tier2
@pytest.mark.no_external_calls
async def test_run_normalizes_bridge_response() -> None:
    service = OpenAIOrchestrationService(service=_StubBridgeService())
    request = OrchestratedOpenAIRequest(
        prompt="hello",
        task="demo",
        metadata={"priority": "high"},
    )

    response = await service.run(request)

    assert response.content == "echo:hello"
    assert response.metadata["orchestration"]["task"] == "demo"
    assert response.metadata["orchestration"]["priority"] == "high"
    assert service.get_metrics()["requests"] == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.tier2
@pytest.mark.no_external_calls
async def test_run_many_respects_concurrency_limit() -> None:
    stub = _SlowStubBridgeService()
    service = OpenAIOrchestrationService(service=stub)

    requests = [OrchestratedOpenAIRequest(prompt=f"p-{idx}") for idx in range(4)]

    responses = await service.run_many(requests, concurrency=2)

    assert {resp.content for resp in responses} == {"echo:p-0", "echo:p-1", "echo:p-2", "echo:p-3"}
    assert stub.max_concurrent <= 2


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.tier2
@pytest.mark.no_external_calls
async def test_run_records_timeout_metric() -> None:
    service = OpenAIOrchestrationService(service=_TimeoutStubBridgeService())
    request = OrchestratedOpenAIRequest(prompt="slow")

    with pytest.raises(asyncio.TimeoutError):
        await service.run(request, timeout=0.01)

    metrics = service.get_metrics()
    assert metrics["timeouts"] == 1
    assert metrics["requests"] == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.tier2
@pytest.mark.no_external_calls
async def test_run_stream_proxies_chunks() -> None:
    service = OpenAIOrchestrationService(service=_StubBridgeService())
    request = OrchestratedOpenAIRequest(prompt="stream")

    stream = await service.run_stream(request)
    chunks = [chunk async for chunk in stream]

    assert chunks == ["chunk-1", "chunk-2"]
    assert service.get_metrics()["streams"] == 1
