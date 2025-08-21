"""NIAS Filtering Engine

Handles content filtering and recommendations for the Golden Trio.
"""

import logging
from typing import Any

from ethics.core import get_shared_ethics_engine
from ethics.seedra import get_seedra
from symbolic.core import Symbol, SymbolicVocabulary, get_symbolic_vocabulary

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
        if (
            decision.decision_type.value == "allow"
            and decision.confidence > self.positive_threshold
        ):
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

    async def generate_recommendations(
        self, user_context: dict[str, Any]
    ) -> list[Symbol]:
        if not self.orchestrator:
            return []

        dast_context = await self.orchestrator.send_message(
            self.orchestrator.SystemType.NIAS,
            self.orchestrator.SystemType.DAST,
            "request_context",
            {"user_id": user_context.get("user_id")},
        )
        if dast_context.status != "blocked":
            return [self.symbolic.create_symbol("rec", {"context": "TODO"})]
        return []


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
