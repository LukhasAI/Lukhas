"""MATRIZ DecisionNode implementation."""
from typing import Any, Dict, List

from matriz.core.node_interface import NodeState

from .base import BaseMatrixNode


class DecisionNode(BaseMatrixNode):
    """Select downstream action based on synthesized thought and context."""

    def __init__(self, tenant: str = "default", default_action: str = "memory_follow_up") -> None:
        super().__init__(
            node_name="matriz_decision_node",
            capabilities=["action_selection", "risk_balancing", "governance_trace"],
            tenant=tenant,
        )
        self.default_action = default_action

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[override]
        start = self._start_timer()
        candidate_actions = input_data.get("candidate_actions") or []
        if not isinstance(candidate_actions, list):
            candidate_actions = []

        selected = self._choose_action(candidate_actions, input_data)
        confidence = selected.get("confidence", 0.5)
        risk_score = selected.get("risk", 0.2)

        state = NodeState(
            confidence=max(0.0, min(1.0, confidence)),
            salience=min(1.0, 0.6 + confidence * 0.2),
            risk=max(0.0, min(1.0, risk_score)),
            utility=min(1.0, 0.5 + confidence / 2),
            urgency=min(1.0, float(input_data.get("urgency", 0.3))),
        )

        trigger = self._build_trigger("decision_request", "selected_action")
        matriz_node = self.create_matriz_node(
            node_type="DECISION",
            state=state,
            triggers=[trigger],
            additional_data={
                "selected_action": selected,
                "candidate_actions": candidate_actions,
                "rationale": selected.get("rationale", "heuristic_selection"),
            },
        )

        self.logger.info(
            "ΛTAG:decision_selection",
            extra={"action": selected.get("name"), "confidence": confidence},
        )

        result = self._finish(
            started_at=start,
            answer=selected,
            confidence=confidence,
            matriz_node=matriz_node,
        )
        return result

    def _choose_action(self, actions: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        if not actions:
            return {
                "name": self.default_action,
                "confidence": 0.4,
                "risk": 0.2,
                "rationale": "fallback_no_candidates",
            }

        sorted_actions = sorted(
            actions,
            key=lambda item: (
                float(item.get("score", item.get("confidence", 0.0))),
                -float(item.get("risk", 0.0)),
            ),
            reverse=True,
        )
        best = dict(sorted_actions[0])
        best.setdefault("rationale", "score_weighted_selection")
        return best
