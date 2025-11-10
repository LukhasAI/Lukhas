from typing import Any

from matriz.core.node_interface import CognitiveNode, NodeState


class IntentAnalyzer:
    def analyze(self, user_input: str) -> dict:
        """Create INTENT MATRIZ node from user input (schema-compliant)."""
        # Simple intent detection
        if any(op in user_input for op in ["+", "-", "*", "/", "="]):
            detected_intent = "mathematical"
        elif "?" in user_input.lower():
            detected_intent = "question"
        elif "dog" in user_input.lower() or "see" in user_input.lower():
            detected_intent = "perception"
        else:
            detected_intent = "general"

        state = NodeState(confidence=0.9, salience=1.0)

        # Create a temporary lightweight node producer to leverage helper
        class _IntentEmitter(CognitiveNode):  # type: ignore
            def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
                raise NotImplementedError

            def can_handle(self, intent: str) -> bool:
                raise NotImplementedError

            def validate_output(self, output: dict[str, Any]) -> bool:
                return True

        emitter = _IntentEmitter(
            node_name="matriz_orchestrator_intent",
            capabilities=["intent_analysis"],
        )

        node = emitter.create_matriz_node(
            node_type="INTENT",
            state=state,
            additional_data={
                "input_text": user_input,
                "intent": detected_intent,
            },
        )
        return node
