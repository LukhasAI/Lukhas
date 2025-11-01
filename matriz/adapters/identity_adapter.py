import importlib

from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult

from core.trace import mk_crumb


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


# Added for test compatibility (matriz.adapters.identity_adapter.UidentityAdapter)
try:
    _candidate_module = importlib.import_module("candidate.matriz.adapters.identity_adapter")
    UidentityAdapter = getattr(_candidate_module, "UidentityAdapter")  # type: ignore[assignment]
except Exception:  # pragma: no cover - fallback for missing candidate module

    class UidentityAdapter:
        """Stub for UidentityAdapter when candidate lane is unavailable."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "UidentityAdapter" not in __all__:
    __all__.append("UidentityAdapter")
