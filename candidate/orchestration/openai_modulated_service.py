"""OpenAI orchestration service integration layer."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass, field
from typing import Any, Callable

# Optional imports with graceful degradation to maintain deterministic execution
try:  # pragma: no cover - import guard
    from candidate.bridge.llm_wrappers.openai_modulated_service import (
        OpenAIModulatedService as _BridgeOpenAIModulatedService,
    )
except Exception:  # pragma: no cover - fallback path
    _BridgeOpenAIModulatedService = None  # type: ignore[assignment]

try:  # pragma: no cover - import guard
    from candidate.orchestration.signals.homeostasis import ModulationParams
except Exception:  # pragma: no cover - fallback
    ModulationParams = Any  # type: ignore[assignment]

try:  # pragma: no cover - import guard
    from candidate.orchestration.signals.signal_bus import Signal
except Exception:  # pragma: no cover - fallback
    Signal = Any  # type: ignore[assignment]

logger = logging.getLogger("ΛTRACE.orchestration.openai_modulated_service")


class ServiceUnavailableError(RuntimeError):
    """Raised when the bridge OpenAI service cannot be constructed."""


@dataclass(slots=True)
class OrchestratedOpenAIRequest:
    """Structured orchestration request payload."""

    prompt: str
    context: dict[str, Any] | None = None
    signals: list[Signal] | None = None
    params: ModulationParams | None = None
    task: str | None = None
    stream: bool = False
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class OrchestratedOpenAIResponse:
    """Normalized orchestration response payload."""

    content: str
    raw: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    modulation: dict[str, Any] | None = None
    tool_analytics: dict[str, Any] | None = None


# ΛTAG: orchestration_bridge
class OpenAIOrchestrationService:
    """Coordinates the signal-modulated OpenAI bridge for orchestration flows."""

    def __init__(
        self,
        *,
        service: Any | None = None,
        service_factory: Callable[[], Any] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._service = service
        self._service_factory = service_factory
        self._loop = loop
        # ΛTAG: orchestration_metrics
        self._metrics: dict[str, int] = {
            "requests": 0,
            "streams": 0,
            "timeouts": 0,
            "errors": 0,
        }
        # Track inflight tasks for cancellation during shutdown
        self._inflight: set[asyncio.Task[Any]] = set()

    def _default_factory(self) -> Any:
        if _BridgeOpenAIModulatedService is None:
            raise ServiceUnavailableError(
                "candidate.bridge.llm_wrappers.OpenAIModulatedService is unavailable",
            )
        return _BridgeOpenAIModulatedService()

    def _get_service(self) -> Any:
        if self._service is None:
            factory = self._service_factory or self._default_factory
            self._service = factory()
        return self._service

    def _register_task(self, task: asyncio.Task[Any]) -> asyncio.Task[Any]:
        self._inflight.add(task)
        task.add_done_callback(self._inflight.discard)
        return task

    async def run(
        self,
        request: OrchestratedOpenAIRequest,
        *,
        timeout: float | None = None,
    ) -> OrchestratedOpenAIResponse:
        """Execute a single modulated OpenAI request."""

        service = self._get_service()
        # ΛTAG: audit_chain
        orchestration_meta = {
            "task": request.task or "general",
            "stream": request.stream,
        }

        async def _execute() -> dict[str, Any]:
            return await service.generate(
                prompt=request.prompt,
                context=request.context,
                signals=request.signals,
                params=request.params,
                task=request.task,
                stream=request.stream,
            )

        self._metrics["requests"] += 1

        try:
            if timeout is not None:
                raw_response = await asyncio.wait_for(_execute(), timeout)
            else:
                raw_response = await _execute()
        except asyncio.TimeoutError:
            self._metrics["timeouts"] += 1
            logger.warning("OpenAI orchestration request timed out", extra=orchestration_meta)
            raise
        except Exception:
            self._metrics["errors"] += 1
            logger.exception("OpenAI orchestration request failed", extra=orchestration_meta)
            raise

        if request.metadata:
            orchestration_meta.update(request.metadata)

        return self._normalize_response(raw_response, orchestration_meta)

    async def run_many(
        self,
        requests: Iterable[OrchestratedOpenAIRequest],
        *,
        concurrency: int = 3,
        timeout: float | None = None,
    ) -> list[OrchestratedOpenAIResponse]:
        """Execute multiple requests with bounded concurrency."""

        semaphore = asyncio.Semaphore(max(1, concurrency))

        async def _runner(req: OrchestratedOpenAIRequest) -> OrchestratedOpenAIResponse:
            async with semaphore:
                return await self.run(req, timeout=timeout)

        tasks = [
            self._register_task(asyncio.create_task(_runner(req)))
            for req in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses: list[OrchestratedOpenAIResponse] = []
        for result in results:
            if isinstance(result, Exception):
                raise result
            responses.append(result)
        return responses

    async def run_stream(
        self,
        request: OrchestratedOpenAIRequest,
        *,
        chunk_timeout: float | None = None,
    ) -> AsyncIterator[str]:
        """Proxy streaming responses from the bridge service."""

        service = self._get_service()
        self._metrics["streams"] += 1

        stream_iter = await service.generate_stream(
            prompt=request.prompt,
            context=request.context,
            signals=request.signals,
            params=request.params,
            task=request.task,
        )

        async def _iterate() -> AsyncIterator[str]:
            iterator = stream_iter.__aiter__()
            while True:
                try:
                    if chunk_timeout is None:
                        chunk = await iterator.__anext__()
                    else:
                        chunk = await asyncio.wait_for(iterator.__anext__(), chunk_timeout)
                except StopAsyncIteration:
                    break
                yield str(chunk)

        return _iterate()

    def _normalize_response(
        self,
        raw_response: dict[str, Any],
        orchestration_meta: dict[str, Any],
    ) -> OrchestratedOpenAIResponse:
        content = str(raw_response.get("content", ""))
        metadata = dict(raw_response.get("metadata", {}))
        modulation = raw_response.get("modulation")
        tool_analytics = raw_response.get("tool_analytics")

        orchestration = metadata.get("orchestration", {})
        orchestration.update(orchestration_meta)
        metadata["orchestration"] = orchestration

        return OrchestratedOpenAIResponse(
            content=content,
            raw=raw_response,
            metadata=metadata,
            modulation=modulation,
            tool_analytics=tool_analytics,
        )

    def get_metrics(self) -> dict[str, int]:
        """Return collected orchestration metrics."""

        return dict(self._metrics)

    async def shutdown(self) -> None:
        """Cancel inflight tasks to ensure deterministic teardown."""

        if not self._inflight:
            return
        for task in list(self._inflight):
            task.cancel()
        await asyncio.gather(*self._inflight, return_exceptions=True)
        self._inflight.clear()


def create_orchestration_service(
    *,
    service_factory: Callable[[], Any] | None = None,
) -> OpenAIOrchestrationService:
    """Factory helper that respects optional dependency fallbacks."""

    return OpenAIOrchestrationService(service_factory=service_factory)


__all__ = [
    "OpenAIOrchestrationService",
    "OrchestratedOpenAIRequest",
    "OrchestratedOpenAIResponse",
    "ServiceUnavailableError",
    "create_orchestration_service",
]
