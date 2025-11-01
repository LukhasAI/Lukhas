from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult

from core.trace import mk_crumb


class ComplianceAdapter(MatrizNode):
    name = "compliance-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "check":
            out = {"compliant": True, "standard": payload.get("standard", "default")}
        elif topic == "report":
            out = {"report_id": payload.get("id", "R001"), "status": "generated"}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"compliance_enter": mk_crumb("compliance_enter", msg.glyph, topic=topic)},
            guardian_log=[f"compliance_processed_{topic}"],
        )
