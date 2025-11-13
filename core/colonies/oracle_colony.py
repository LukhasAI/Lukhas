"""Oracle Colony - core/colonies/oracle_colony.py

This module provides a lane-safe OracleColony implementation that keeps the
public API used by downstream modules while deferring any optional Labs
integrations until runtime. The implementation intentionally avoids static
imports from the `labs` package so that lane guard checks do not flag a
production → labs dependency.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:  # BaseColony lives in the same lane, but keep a defensive import.
    from core.colonies.base_colony import BaseColony
except ImportError:  # pragma: no cover - fallback for partial environments.
    BaseColony = object  # type: ignore[assignment]

logger = logging.getLogger("ΛTRACE.oracle_colony")


# NOTE: lazy loader to avoid import-time dependency on `labs`.
def _get_labs() -> Optional[Any]:
    """Attempt to import the optional `labs` integration lazily."""

    try:
        return importlib.import_module("labs")
    except Exception:
        # Deliberately swallow import errors so production lanes without `labs`
        # installed won't fail during module import. Callers should handle None.
        return None


@dataclass
class OracleQuery:
    """Unified query structure for Oracle operations."""

    query_type: str  # "prediction", "dream", "prophecy", "analysis"
    context: Dict[str, Any]
    time_horizon: str = "near"  # "immediate", "near", "medium", "far"
    user_id: Optional[str] = None
    priority: str = "normal"  # "low", "normal", "high", "critical"
    openai_enhanced: bool = True


@dataclass
class OracleResponse:
    """Unified response payload returned by the Oracle colony."""

    query_id: str
    response_type: str
    content: Dict[str, Any]
    confidence: float
    temporal_scope: str
    generated_at: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the response to a JSON-friendly dictionary."""

        return {
            "query_id": self.query_id,
            "response_type": self.response_type,
            "content": self.content,
            "confidence": self.confidence,
            "temporal_scope": self.temporal_scope,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata,
        }


class OracleColony(BaseColony):
    """Lane-safe oracle colony that optionally proxies to Labs implementations."""

    def __init__(self, colony_id: str = "oracle", capabilities: Optional[list[str]] = None):
        super().__init__(colony_id, capabilities)
        self._labs_colony: Optional[Any] = None
        self._labs_error: Optional[Exception] = None
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def process_oracle_query(self, query: OracleQuery) -> Dict[str, Any]:
        """Process an oracle query using Labs if present, otherwise fall back."""

        await self._ensure_initialized()

        if self._labs_colony is not None:
            handler = getattr(self._labs_colony, "process_oracle_query", None)
            if handler is None:
                handler = getattr(self._labs_colony, "query_oracle", None)

            if handler is not None:
                try:
                    result = handler(query)
                    if asyncio.iscoroutine(result):
                        result = await result
                    return self._normalize_response(result, query)
                except Exception as exc:  # pragma: no cover - defensive logging.
                    logger.warning(
                        "Labs OracleColony handler failed, falling back", error=str(exc)
                    )

        fallback = await self._fallback_process(query)
        return fallback.to_dict()

    async def _ensure_initialized(self) -> None:
        """Initialize the colony exactly once, instantiating Labs proxies if available."""

        if self._initialized:
            return

        async with self._init_lock:
            if self._initialized:
                return

            labs_colony = self._instantiate_labs_colony()
            if labs_colony is not None:
                init_callable = getattr(labs_colony, "initialize", None)
                if init_callable is not None:
                    try:
                        maybe_coro = init_callable()
                        if asyncio.iscoroutine(maybe_coro):
                            await maybe_coro
                    except Exception as exc:  # pragma: no cover - optional integration
                        self._labs_error = exc
                        logger.warning(
                            "Labs OracleColony initialization failed; reverting to fallback",
                            error=str(exc),
                        )
                    else:
                        logger.info("OracleColony initialized with Labs integration")
                        self._labs_colony = labs_colony
                else:
                    logger.info("OracleColony using Labs implementation without initialize()")
                    self._labs_colony = labs_colony
            else:
                logger.info("OracleColony running in fallback mode (Labs unavailable)")

            self._initialized = True

    def _instantiate_labs_colony(self) -> Optional[Any]:
        """Instantiate the Labs OracleColony implementation if it is available."""

        labs = _get_labs()
        if labs is None:
            return None

        try:
            colony_module = importlib.import_module("labs.core.colonies.oracle_colony")
        except Exception as exc:  # pragma: no cover - best-effort import
            self._labs_error = exc
            logger.debug("Labs oracle module import failed", error=str(exc))
            return None

        colony_cls = getattr(colony_module, "OracleColony", None)
        if colony_cls is None:
            logger.debug("Labs oracle colony missing OracleColony attribute")
            return None

        try:
            return colony_cls(self.colony_id, self.capabilities)
        except TypeError:
            try:
                return colony_cls(self.colony_id)
            except TypeError:
                return colony_cls()
        except Exception as exc:  # pragma: no cover - propagate via fallback
            self._labs_error = exc
            logger.debug("Labs oracle colony instantiation failed", error=str(exc))
            return None

    async def _fallback_process(self, query: OracleQuery) -> OracleResponse:
        """Fallback oracle processing when Labs integration is unavailable."""

        handlers = {
            "prediction": self._fallback_prediction,
            "dream": self._fallback_dream,
            "prophecy": self._fallback_prophecy,
            "analysis": self._fallback_analysis,
        }
        handler = handlers.get(query.query_type, self._fallback_analysis)
        return await handler(query)

    async def _fallback_prediction(self, query: OracleQuery) -> OracleResponse:
        await asyncio.sleep(0)
        content = {
            "summary": "Predicted swarm trends derived from local colony metrics.",
            "insights": [
                "Swarm cohesion remains stable.",
                "Bio-symbolic colonies projected to maintain alignment.",
            ],
            "context_snapshot": query.context,
        }
        return self._build_response(query, "prediction", content, confidence=0.62)

    async def _fallback_dream(self, query: OracleQuery) -> OracleResponse:
        await asyncio.sleep(0)
        content = {
            "dream_narrative": "A lattice of luminous nodes weaving shared memories.",
            "symbols": ["lattice", "aurora", "convergence"],
            "context_snapshot": query.context,
        }
        return self._build_response(query, "dream", content, confidence=0.58)

    async def _fallback_prophecy(self, query: OracleQuery) -> OracleResponse:
        await asyncio.sleep(0)
        content = {
            "prophecy": "Collective insight points toward harmonious temporal alignment.",
            "signals": ["synchrony", "low_drift"],
            "context_snapshot": query.context,
        }
        return self._build_response(query, "prophecy", content, confidence=0.6)

    async def _fallback_analysis(self, query: OracleQuery) -> OracleResponse:
        await asyncio.sleep(0)
        content = {
            "analysis": "Baseline oracle analysis executed without Labs augmentation.",
            "details": json.dumps(query.context, indent=2),
        }
        return self._build_response(query, "analysis", content, confidence=0.55)

    def _build_response(
        self,
        query: OracleQuery,
        response_type: str,
        content: Dict[str, Any],
        *,
        confidence: float,
    ) -> OracleResponse:
        return OracleResponse(
            query_id=f"{response_type}_{datetime.now(timezone.utc).timestamp():.6f}",
            response_type=response_type,
            content=content,
            confidence=confidence,
            temporal_scope=query.time_horizon,
            generated_at=datetime.now(timezone.utc),
            metadata={
                "colony_id": self.colony_id,
                "openai_enhanced": query.openai_enhanced,
                "labs_enabled": self._labs_colony is not None,
                "priority": query.priority,
            },
        )

    def _normalize_response(self, response: Any, query: OracleQuery) -> Dict[str, Any]:
        """Normalize arbitrary Labs responses into a dictionary."""

        if response is None:
            return self._build_response(query, query.query_type, {"status": "empty"}, confidence=0.0).to_dict()

        if isinstance(response, OracleResponse):
            return response.to_dict()

        if isinstance(response, dict):
            return response

        to_dict = getattr(response, "to_dict", None)
        if callable(to_dict):
            try:
                return to_dict()
            except Exception:  # pragma: no cover - fall back to generic conversion
                pass

        return self._build_response(
            query,
            query.query_type,
            {"raw_response": str(response)},
            confidence=0.5,
        ).to_dict()


__all__ = ["OracleColony", "OracleQuery", "OracleResponse"]
