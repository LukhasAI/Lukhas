from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from core.trace import mk_crumb

class MemoryAdapter(MatrizNode):
    name = "memory-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "store":
            out = {"stored": True, "key": payload.get("key", "default")}
        elif topic == "retrieve":
            out = {"data": payload.get("data", "cached_value")}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"memory_enter": mk_crumb("memory_enter", msg.glyph, topic=topic)},
            guardian_log=[f"memory_processed_{topic}"],
        )