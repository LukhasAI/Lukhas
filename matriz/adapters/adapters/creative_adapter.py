from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult

from core.trace import mk_crumb


class CreativeAdapter(MatrizNode):
    name = "creative-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "generate":
            out = {"output": payload.get("prompt", "default") + "_generated", "tokens": 100}
        elif topic == "inspire":
            out = {"inspiration": True, "source": payload.get("source", "creativity")}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"creative_enter": mk_crumb("creative_enter", msg.glyph, topic=topic)},
            guardian_log=[f"creative_processed_{topic}"],
        )
