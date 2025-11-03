import importlib

from core.trace import mk_crumb
from matriz.node_contract import MatrizMessage, MatrizNode, MatrizResult


class EmotionAdapter(MatrizNode):
    name = "emotion-adapter"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Deterministic, pure handling keyed by topic
        payload = msg.payload or {}
        topic = msg.topic

        if topic == "mood":
            out = {
                "emotion": payload.get("emotion", "neutral"),
                "intensity": payload.get("intensity", 0.5),
            }
        elif topic == "response":
            out = {"reaction": "processed", "valence": payload.get("valence", 0)}
        else:
            out = {"status": "unknown_topic", "topic": topic}

        return MatrizResult(
            ok=True,
            payload=out,
            trace={"emotion_enter": mk_crumb("emotion_enter", msg.glyph, topic=topic)},
            guardian_log=[f"emotion_processed_{topic}"],
        )


# Added for test compatibility (matriz.adapters.emotion_adapter.UemotionAdapter)
try:
    _candidate_module = importlib.import_module("candidate.matriz.adapters.emotion_adapter")
    UemotionAdapter = _candidate_module.UemotionAdapter  # type: ignore[assignment]
except Exception:  # pragma: no cover - fallback for missing candidate module

    class UemotionAdapter:
        """Stub for UemotionAdapter when candidate lane is unavailable."""

        def __init__(self, *args, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "UemotionAdapter" not in __all__:
    __all__.append("UemotionAdapter")
