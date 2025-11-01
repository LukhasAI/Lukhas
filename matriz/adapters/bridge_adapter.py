from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult

from core.trace import mk_crumb


class BridgeAdapter(MatrizNode):
    name = "bridge-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "connect":
            out = {"connected": True, "target": payload.get("target", "default")}
        elif topic == "transfer":
            out = {"transferred": payload.get("data", ""), "bytes": len(str(payload.get("data", "")))}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"bridge_enter": mk_crumb("bridge_enter", msg.glyph, topic=topic)},
            guardian_log=[f"bridge_processed_{topic}"],
        )
