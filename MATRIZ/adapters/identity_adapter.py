from core.trace import mk_crumb
from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult


class IdentityAdapter(MatrizNode):
    name = "identity-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "authenticate":
            out = {"authenticated": True, "user_id": payload.get("user_id", "default_user")}
        elif topic == "authorize":
            out = {"authorized": True, "permissions": payload.get("permissions", [])}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"identity_enter": mk_crumb("identity_enter", msg.glyph, topic=topic)},
            guardian_log=[f"identity_processed_{topic}"],
        )
