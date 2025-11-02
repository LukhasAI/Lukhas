"""Shared utilities for MATRIZ cognitive nodes."""

import logging
import time
from typing import Any, Dict

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class BaseMatrixNode(CognitiveNode):
    """Base class providing common helpers for MATRIZ nodes."""

    def __init__(self, node_name: str, capabilities: list[str], tenant: str = "default") -> None:
        super().__init__(node_name=node_name, capabilities=capabilities, tenant=tenant)
        self.logger = logging.getLogger(f"candidate.core.matrix.nodes.{node_name}")

    def validate_output(self, output: dict[str, Any]) -> bool:  # type: ignore[override]
        if not isinstance(output, dict):
            return False
        required = {"answer", "confidence", "matriz_node"}
        if not required.issubset(output.keys()):
            return False
        try:
            confidence = float(output["confidence"])
        except (TypeError, ValueError):
            return False
        return 0.0 <= confidence <= 1.0

    def _start_timer(self) -> float:
        return time.perf_counter()

    def _finish(
        self,
        *,
        started_at: float,
        answer: Any,
        confidence: float,
        matriz_node: Dict[str, Any],
    ) -> Dict[str, Any]:
        duration = time.perf_counter() - started_at
        self.processing_history.append(matriz_node)
        result = {
            "answer": answer,
            "confidence": max(0.0, min(1.0, float(confidence))),
            "matriz_node": matriz_node,
            "processing_time": duration,
        }
        return result

    def _build_trigger(self, event_type: str, effect: str) -> NodeTrigger:
        return NodeTrigger(
            event_type=event_type,
            timestamp=int(time.time() * 1000),
            effect=effect,
        )

    def _default_state(self, *, confidence: float, salience: float = 0.5, **kwargs: Any) -> NodeState:
        return NodeState(
            confidence=max(0.0, min(1.0, confidence)),
            salience=max(0.0, min(1.0, salience)),
            **kwargs,
        )
