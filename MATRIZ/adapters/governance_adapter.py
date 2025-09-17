from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult
from core.trace import mk_crumb

class GovernanceAdapter(MatrizNode):
    name = "governance-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "policy":
            out = {"policy_active": True, "rule": payload.get("rule", "default_rule")}
        elif topic == "audit":
            out = {"audit_result": "passed", "score": payload.get("score", 100)}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"governance_enter": mk_crumb("governance_enter", msg.glyph, topic=topic)},
            guardian_log=[f"governance_processed_{topic}"],
        )