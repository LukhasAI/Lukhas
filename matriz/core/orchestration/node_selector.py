import time
from typing import Any

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


class NodeSelector:
    def select_node(self, intent_node: dict) -> str:
        """Select appropriate node based on intent"""
        intent = intent_node["state"].get("intent", "general")

        return {
            "mathematical": "math",
            "question": "facts",
            "perception": "vision",  # Would handle "boy sees dog"
        }.get(
            intent, "facts"
        )  # Default

    def create_decision_node(self, decision: str, trigger_id: str) -> dict:
        """Create DECISION MATRIZ node (schema-compliant)."""

        class _DecisionEmitter(CognitiveNode):  # type: ignore
            def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
                raise NotImplementedError

            def can_handle(self, intent: str) -> bool:
                raise NotImplementedError

            def validate_output(self, output: dict[str, Any]) -> bool:
                return True

        emitter = _DecisionEmitter(
            node_name="matriz_orchestrator_decision",
            capabilities=["node_selection"],
        )

        trigger = NodeTrigger(
            event_type="node_selection",
            timestamp=int(time.time() * 1000),
            trigger_node_id=trigger_id,
            effect="selected_processing_node",
        )

        node = emitter.create_matriz_node(
            node_type="DECISION",
            state=NodeState(confidence=0.85, salience=0.9),
            triggers=[trigger],
            additional_data={"decision": decision},
        )
        return node
