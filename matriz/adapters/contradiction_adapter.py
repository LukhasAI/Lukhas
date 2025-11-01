from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult

from core.trace import mk_crumb


class ContradictionAdapter(MatrizNode):
    name = "contradiction-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "detect":
            out = {"contradiction_found": False, "confidence": payload.get("confidence", 0.9)}
        elif topic == "resolve":
            out = {"resolution": payload.get("strategy", "default"), "success": True}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"contradiction_enter": mk_crumb("contradiction_enter", msg.glyph, topic=topic)},
            guardian_log=[f"contradiction_processed_{topic}"],
        )
