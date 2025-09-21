from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from lukhas.core.trace import mk_crumb

class BioAdapter(MatrizNode):
    name = "bio-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "homeostasis":
            out = {"status": "ok", "delta": payload.get("delta", 0)}
        elif topic == "energy":
            out = {"joules": payload.get("joules", 0)}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"bio_enter": mk_crumb("bio_enter", msg.glyph, topic=topic)},
            guardian_log=[f"bio_processed_{topic}"],
        )