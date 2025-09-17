from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from core.trace import mk_crumb

class EmotionAdapter(MatrizNode):
    name = "emotion-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "mood":
            out = {"emotion": payload.get("emotion", "neutral"), "intensity": payload.get("intensity", 0.5)}
        elif topic == "response":
            out = {"reaction": "processed", "valence": payload.get("valence", 0)}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"emotion_enter": mk_crumb("emotion_enter", msg.glyph, topic=topic)},
            guardian_log=[f"emotion_processed_{topic}"],
        )