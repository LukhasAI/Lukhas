"""MATRIZ MemoryNode implementation."""

from typing import Any, Dict, List

from matriz.core.node_interface import NodeState

from .base import BaseMatrixNode


class MemoryNode(BaseMatrixNode):
    """Recall recent memories with lightweight semantic scoring."""

    def __init__(self, tenant: str = "default", top_k: int = 5) -> None:
        super().__init__(
            node_name="matriz_memory_node",
            capabilities=["memory_recall", "semantic_search", "governed_trace"],
            tenant=tenant,
        )
        self.top_k = top_k
        # ✅ TODO: integrate with production memory backend once available

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[override]
        start = self._start_timer()
        query = str(input_data.get("query", "")).lower()
        memory_entries = input_data.get("memory_context") or input_data.get("memories") or []
        if not isinstance(memory_entries, list):
            memory_entries = []

        scored: List[tuple[float, Dict[str, Any]]] = []
        for entry in memory_entries:
            if not isinstance(entry, dict):
                continue
            text = str(entry.get("content") or entry.get("text") or "")
            if not text:
                continue
            score = self._score_entry(query, text, entry)
            if score <= 0:
                continue
            scored.append((score, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        top_matches = [entry for _, entry in scored[: self.top_k]]
        confidence = min(1.0, sum(score for score, _ in scored[: self.top_k]) / max(1, len(top_matches)))

        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.4 + 0.1 * len(top_matches)),
            novelty=max(0.05, 1.0 - confidence),
            utility=min(1.0, 0.5 + confidence / 2),
            valence=0.1,
            arousal=min(1.0, 0.2 + 0.15 * len(top_matches)),
        )

        trigger = self._build_trigger("memory_recall", "retrieved_memory")
        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            triggers=[trigger],
            additional_data={
                "query": query,
                "matches": top_matches,
                "total_candidates": len(memory_entries),
                "driftScore": input_data.get("drift_score", 0.0),
            },
        )

        self.logger.info("ΛTAG:memory_recall", extra={"matches": len(top_matches), "query": query[:32]})

        result = self._finish(
            started_at=start,
            answer={"matches": top_matches},
            confidence=confidence,
            matriz_node=matriz_node,
        )
        result["recall_matches"] = top_matches
        result["driftScore"] = input_data.get("drift_score", 0.0)
        return result

    def _score_entry(self, query: str, text: str, entry: Dict[str, Any]) -> float:
        if not query:
            base = 0.25
        else:
            query_terms = {token for token in query.split() if token}
            text_terms = {token for token in text.lower().split() if token}
            overlap = query_terms & text_terms
            base = len(overlap) / max(1, len(query_terms))
        importance = float(entry.get("importance", 0.5))
        recency = float(entry.get("recency", 0.5))
        score = base * 0.6 + importance * 0.3 + recency * 0.1
        return max(0.0, min(1.0, score))
