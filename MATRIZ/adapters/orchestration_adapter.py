from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from core.trace import mk_crumb

class OrchestrationAdapter(MatrizNode):
    name = "orchestration-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "coordinate":
            out = {"coordinated": True, "tasks": payload.get("tasks", [])}
        elif topic == "schedule":
            out = {"scheduled": True, "time": payload.get("time", "now")}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"orchestration_enter": mk_crumb("orchestration_enter", msg.glyph, topic=topic)},
            guardian_log=[f"orchestration_processed_{topic}"],
        )