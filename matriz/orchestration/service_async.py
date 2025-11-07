"""Async orchestrator service seam for MATRIZ pipelines."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from threading import Lock
from typing import Any, Dict

from matriz.nodes.fact_node import FactNode
from matriz.nodes.math_node import MathNode
from matriz.nodes.validator_node import ValidatorNode

# ΛTAG: async_service_imports -- canonical orchestrator dependency wiring
from matriz.orchestration.async_orchestrator import AsyncCognitiveOrchestrator

logger = logging.getLogger(__name__)

# Ensure module-level logger inherits global configuration
logger.addHandler(logging.NullHandler())

# ΛTAG: async_service_singleton -- guarantee single orchestrator instantiation
_ORCHESTRATOR_INSTANCE: AsyncCognitiveOrchestrator | None = None
_ORCHESTRATOR_LOCK = Lock()


class _MathNodeAdapter(MathNode):
    """Adapter that maps generic queries to math node input."""

    # ΛTAG: adapter_math -- translate query payload to expression schema
    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        query = input_data.get("query", "")
        adapted = dict(input_data)
        adapted.setdefault("expression", query)
        return super().process(adapted)


class _FactNodeAdapter(FactNode):
    """Adapter that maps generic queries to fact node input."""

    # ΛTAG: adapter_fact -- translate query payload to question schema
    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        query = input_data.get("query", "")
        adapted = dict(input_data)
        adapted.setdefault("question", query)
        return super().process(adapted)


def _initialize_orchestrator() -> AsyncCognitiveOrchestrator:
    """Instantiate and configure the async orchestrator singleton."""

    orchestrator = AsyncCognitiveOrchestrator()
    orchestrator.register_node("math", _MathNodeAdapter())
    orchestrator.register_node("facts", _FactNodeAdapter())
    orchestrator.register_node("validator", ValidatorNode())

    logger.info("Async MATRIZ orchestrator initialized with math/facts/validator lanes")
    return orchestrator


def get_async_orchestrator() -> AsyncCognitiveOrchestrator:
    """Return a singleton instance of the async orchestrator."""

    global _ORCHESTRATOR_INSTANCE
    if _ORCHESTRATOR_INSTANCE is None:
        with _ORCHESTRATOR_LOCK:
            if _ORCHESTRATOR_INSTANCE is None:
                _ORCHESTRATOR_INSTANCE = _initialize_orchestrator()
    return _ORCHESTRATOR_INSTANCE


async def run_async_matriz(query: str) -> dict[str, Any]:
    """Execute the async MATRIZ pipeline for the provided query."""

    orchestrator = get_async_orchestrator()

    try:
        result = await orchestrator.process_query(query)
    except asyncio.TimeoutError:
        logger.warning("Async MATRIZ orchestrator timed out for query length=%s", len(query))
        metrics = asdict(orchestrator.metrics)
        return {
            "error": f"Pipeline timeout exceeded {orchestrator.total_timeout}s",
            "orchestrator_metrics": metrics,
        }
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Async MATRIZ orchestrator failed: %s", exc)
        metrics = asdict(orchestrator.metrics)
        return {"error": str(exc), "orchestrator_metrics": metrics}

    if "orchestrator_metrics" not in result:
        # ΛTAG: async_service_metrics -- propagate orchestrator telemetry upstream
        result["orchestrator_metrics"] = asdict(orchestrator.metrics)

    return result


def _reset_async_orchestrator_for_testing() -> None:
    """Reset singleton for deterministic unit testing."""

    global _ORCHESTRATOR_INSTANCE
    with _ORCHESTRATOR_LOCK:
        _ORCHESTRATOR_INSTANCE = None
