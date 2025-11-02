"""MATRIZ ThoughtNode implementation."""

from typing import Any, Dict, List

from matriz.core.node_interface import NodeState

from .base import BaseMatrixNode


class ThoughtNode(BaseMatrixNode):
    """Synthesize intermediate reasoning from recalled memories."""

    def __init__(self, tenant: str = "default") -> None:
        super().__init__(
            node_name="matriz_thought_node",
            capabilities=["hypothesis_generation", "context_integration", "affect_tracking"],
            tenant=tenant,
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[override]
        start = self._start_timer()
        query = str(input_data.get("query", "")).strip()
        memory_signals: List[Dict[str, Any]] = input_data.get("recall_matches") or input_data.get("memory_recall") or []
        if not isinstance(memory_signals, list):
            memory_signals = []

        synthesis = self._compose_thought(query, memory_signals)
        supporting_ids = [m.get("id") for m in memory_signals if isinstance(m, dict) and m.get("id")]
        confidence = min(1.0, 0.55 + 0.1 * len(memory_signals))
        affect_delta = 0.05 * len(memory_signals)

        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.5 + 0.1 * len(memory_signals)),
            valence=0.25,
            arousal=min(1.0, 0.3 + 0.1 * len(memory_signals)),
        )

        trigger = self._build_trigger("thought_generation", "synthesized_hypothesis")
        matriz_node = self.create_matriz_node(
            node_type="HYPOTHESIS",
            state=state,
            triggers=[trigger],
            additional_data={
                "query": query,
                "summary": synthesis,
                "supporting_memory_ids": supporting_ids,
                "memory_signal_count": len(memory_signals),
                "affect_delta": affect_delta,
            },
        )

        self.logger.info(
            "ΛTAG:thought_synthesis",
            extra={"memory_matches": len(memory_signals), "summary_len": len(synthesis)},
        )

        result = self._finish(
            started_at=start,
            answer={"summary": synthesis, "support": memory_signals},
            confidence=confidence,
            matriz_node=matriz_node,
        )
        result["affect_delta"] = affect_delta
        return result

    def _compose_thought(self, query: str, memories: List[Dict[str, Any]]) -> str:
        if not memories:
            return f"Reflecting on '{query or 'input'}' with no direct memory matches."

        highlights = []
        for memory in memories[:3]:
            snippet = str(memory.get("content") or memory.get("text") or "").strip()
            if not snippet:
                continue
            highlights.append(snippet[:80])

        highlights_text = "; ".join(highlights)
        if query:
            return f"Synthesized insight for '{query}': {highlights_text}."
        return f"Synthesized insight: {highlights_text}."
