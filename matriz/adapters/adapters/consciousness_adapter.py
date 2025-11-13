from core.trace import mk_crumb
from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult


class ConsciousnessAdapter(MatrizNode):
    name = "consciousness-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "awareness":
            out = {"level": payload.get("level", 1), "active": True}
        elif topic == "reflection":
            out = {"thoughts": payload.get("thoughts", []), "depth": 2}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"consciousness_enter": mk_crumb("consciousness_enter", msg.glyph, topic=topic)},
            guardian_log=[f"consciousness_processed_{topic}"],
        )
