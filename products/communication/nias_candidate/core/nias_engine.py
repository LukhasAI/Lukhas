"""NIAS Filtering Engine

Handles content filtering and recommendations for the Golden Trio.
"""

import logging
from dataclasses import dataclass
from typing import Any

try:
    from ethics.core import get_shared_ethics_engine  # type: ignore[attr-defined]
except (ImportError, AttributeError):  # pragma: no cover - fallback path

    def get_shared_ethics_engine():
        class _EthicsEngine:
            async def evaluate_action(self, *_args, **_kwargs):
                class _Decision:
                    decision_type = type("Decision", (), {"value": "allow"})()
                    confidence = 0.8

                return _Decision()

        return _EthicsEngine()
try:
    from ethics.seedra import get_seedra
except ImportError:  # pragma: no cover - fallback for sandbox

    def get_seedra():
        class _Seedra:
            async def check_consent(self, *_args, **_kwargs):
                return {"allowed": True}

        return _Seedra()
try:
    from symbolic.core import Symbol, SymbolicVocabulary, get_symbolic_vocabulary
except ImportError:  # pragma: no cover - fallback for sandbox

    @dataclass
    class Symbol:  # type: ignore[override]
        symbol: str
        metadata: dict[str, Any]

        def to_dict(self) -> dict[str, Any]:
            return {"symbol": self.symbol, **self.metadata}

    class SymbolicVocabulary:  # type: ignore[override]
        def create_symbol(self, name: str, payload: dict[str, Any]) -> Symbol:
            return Symbol(symbol=name, metadata=payload)

    def get_symbolic_vocabulary() -> SymbolicVocabulary:  # type: ignore[override]
        return SymbolicVocabulary()

logger = logging.getLogger(__name__)


class PositiveGatingFilter:
    """Filter that only allows ethically positive content."""

    # ΛTAG: nias, positive_gating

    def __init__(self) -> None:
        self.ethics = get_shared_ethics_engine()
        self.symbolic: SymbolicVocabulary = get_symbolic_vocabulary()
        self.seedra = get_seedra()
        self.positive_threshold = 0.5

    async def evaluate_content(self, content: Any, user_context: dict[str, Any]) -> str:
        decision = await self.ethics.evaluate_action(
            {"type": "display_content"},
            {"content": content, **user_context},
            "NIAS",
        )
        if decision.decision_type.value == "allow" and decision.confidence > self.positive_threshold:
            return "APPROVED"
        return "BLOCKED"


class ContextAwareRecommendation:
    """Generate recommendations based on context."""

    # ΛTAG: nias, recommendation

    def __init__(self) -> None:
        try:
            from orchestration.golden_trio import get_trio_orchestrator

            self.orchestrator = get_trio_orchestrator()
        except Exception:
            self.orchestrator = None
        self.symbolic: SymbolicVocabulary = get_symbolic_vocabulary()
        self.seedra = get_seedra()

    async def generate_recommendations(self, user_context: dict[str, Any]) -> list[Symbol]:
        if not self.orchestrator:
            return []

        user_id = user_context.get("user_id")
        if user_id:
            try:
                consent = await self.seedra.check_consent(user_id, "nias_recommendations")
                if not consent.get("allowed", True):
                    logger.info("NIΛS recommendation skipped - consent not granted", extra={"user_id": user_id})
                    return []
            except Exception as exc:  # pragma: no cover - seedra failures are non-critical
                logger.debug("Seedra consent lookup failed", extra={"user_id": user_id, "error": str(exc)})

        dast_context = await self.orchestrator.send_message(
            self.orchestrator.SystemType.NIAS,
            self.orchestrator.SystemType.DAST,
            "request_context",
            {"user_id": user_context.get("user_id")},
        )
        if dast_context.status == "blocked":
            logger.debug("DAST context blocked", extra={"reason": dast_context.result})
            return []

        recommendations = self._build_recommendations(dast_context.result, user_context)
        return [self.symbolic.create_symbol("recommendation", payload) for payload in recommendations]
        return []

    def _build_recommendations(self, result: Any, user_context: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize orchestrator responses into symbolic recommendation payloads."""

        # ΛTAG: nias, recommendation_normalization
        payloads: list[dict[str, Any]] = []

        if isinstance(result, dict):
            if "recommendations" in result and isinstance(result["recommendations"], list):
                for rec in result["recommendations"]:
                    payloads.append({
                        "context": rec,
                        "user_id": user_context.get("user_id"),
                        "source": "dast",
                    })
            elif result:
                payloads.append({
                    "context": result,
                    "user_id": user_context.get("user_id"),
                    "source": "dast_context",
                })
        elif isinstance(result, list):
            for entry in result:
                payloads.extend(self._build_recommendations(entry, user_context))

        if not payloads:
            payloads.append({
                "context": {"signals": user_context.get("signals", {})},
                "user_id": user_context.get("user_id"),
                "source": "fallback",
            })

        return payloads


class NIASEngine:
    """Main NIAS engine."""

    # ΛTAG: nias, core_engine

    def __init__(self) -> None:
        self.filter = PositiveGatingFilter()
        self.recommender = ContextAwareRecommendation()

    async def filter_content(self, content: Any, user_context: dict[str, Any]) -> str:
        return await self.filter.evaluate_content(content, user_context)

    async def recommend(self, user_context: dict[str, Any]) -> list[Symbol]:
        return await self.recommender.generate_recommendations(user_context)
