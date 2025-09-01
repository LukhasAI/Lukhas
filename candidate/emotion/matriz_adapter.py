"""
MATRIZ Adapter for Emotion Module
Emits MATRIZ-compliant nodes for emotional states and affect events
"""

import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional


class EmotionMatrizAdapter:
    """Adapter to emit MATRIZ nodes for emotion events"""

    SCHEMA_REF = "lukhas://schemas/matriz_node_v1.json"

    @staticmethod
    def create_node(
        node_type: str,
        state: dict[str, float],
        labels: Optional[list[str]] = None,
        provenance_extra: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Create a MATRIZ-compliant node for emotion events"""

        node = {
            "version": 1,
            "id": f"LT-EMO-{uuid.uuid4().hex[:8]}",
            "type": node_type,
            "state": {
                "confidence": state.get("confidence", 0.7),
                "salience": state.get("salience", 0.6),
                "urgency": state.get("urgency", 0.3),
                "novelty": state.get("novelty", 0.4),
                **state,
            },
            "timestamps": {"created_ts": int(time.time() * 1000)},
            "provenance": {
                "producer": "lukhas.emotion",
                "capabilities": ["emotion:detect", "emotion:regulate", "emotion:vad"],
                "tenant": "system",
                "trace_id": f"LT-EMO-{int(time.time())}",
                "consent_scopes": ["system:emotion"],
                **(provenance_extra or {}),
            },
        }

        if labels:
            node["labels"] = labels

        return node

    @staticmethod
    def emit_emotion_state(
        valence: float, arousal: float, dominance: float, emotion_label: Optional[str] = None
    ) -> dict[str, Any]:
        """Emit a VAD emotion state node"""

        labels = ["emotion:vad"]
        if emotion_label:
            labels.append(f"emotion:{emotion_label}")

        # Map VAD to salience/urgency
        salience = abs(arousal)  # High arousal = high salience
        urgency = max(0, -valence) * arousal  # Negative valence + high arousal = urgent

        return EmotionMatrizAdapter.create_node(
            node_type="EMOTION",
            state={
                "confidence": 0.8,
                "salience": salience,
                "urgency": urgency,
                "novelty": 0.3,
                "valence": valence,
                "arousal": arousal,
                "dominance": dominance,
            },
            labels=labels,
        )

    @staticmethod
    def emit_mood_drift(
        current_mood: dict[str, float], target_mood: dict[str, float], drift_score: float
    ) -> dict[str, Any]:
        """Emit a mood drift detection node"""

        return EmotionMatrizAdapter.create_node(
            node_type="EMOTION",
            state={
                "confidence": 0.9,
                "salience": min(1.0, drift_score),
                "urgency": drift_score * 0.5,
                "novelty": 0.2,
                "drift_score": drift_score,
                "current_valence": current_mood.get("valence", 0),
                "current_arousal": current_mood.get("arousal", 0),
                "target_valence": target_mood.get("valence", 0),
                "target_arousal": target_mood.get("arousal", 0),
            },
            labels=["emotion:mood_drift", f"drift:{drift_score:.2f}"],
        )

    @staticmethod
    def emit_emotion_intent(intent: str, confidence: float, context: Optional[dict] = None) -> dict[str, Any]:
        """Emit an emotion-intent mapping node"""

        return EmotionMatrizAdapter.create_node(
            node_type="INTENT",
            state={
                "confidence": confidence,
                "salience": 0.7,
                "urgency": 0.4,
                "novelty": 0.3,
                **(context or {}),
            },
            labels=[f"intent:{intent}", "emotion:intent_mapping"],
        )

    @staticmethod
    def emit_stagnation_detection(emotion: str, duration_ms: int, threshold_ms: int = 5000) -> dict[str, Any]:
        """Emit an affect stagnation detection node"""

        stagnation_ratio = duration_ms / threshold_ms

        return EmotionMatrizAdapter.create_node(
            node_type="EMOTION",
            state={
                "confidence": 0.95,
                "salience": min(1.0, stagnation_ratio),
                "urgency": min(1.0, stagnation_ratio * 0.7),
                "novelty": 0.1,
                "duration_ms": duration_ms,
                "threshold_ms": threshold_ms,
            },
            labels=[
                f"emotion:{emotion}",
                "emotion:stagnation",
                "alert:stagnation" if duration_ms > threshold_ms else "status:normal",
            ],
        )

    @staticmethod
    def validate_node(node: dict[str, Any]) -> bool:
        """Validate that a node meets MATRIZ requirements"""
        required_fields = ["version", "id", "type", "state", "timestamps", "provenance"]

        for field in required_fields:
            if field not in node:
                return False

        # Check required provenance fields
        required_prov = ["producer", "capabilities", "tenant", "trace_id", "consent_scopes"]
        return all(field in node.get("provenance", {}) for field in required_prov)

    @staticmethod
    def save_node(node: dict[str, Any], output_dir: Optional[Path] = None) -> Path:
        """Save a MATRIZ node to disk for audit"""
        if output_dir is None:
            output_dir = Path("memory/inbox/emotion")

        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{node['id']}_{int(time.time())}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(node, f, indent=2)

        return filepath


# Decorator functions for existing emotion code
def wrap_vad_detection(original_func):
    """Decorator to add MATRIZ emission to VAD detection"""

    def wrapper(*args, **kwargs):
        result = original_func(*args, **kwargs)

        if isinstance(result, dict) and all(k in result for k in ["valence", "arousal", "dominance"]):
            node = EmotionMatrizAdapter.emit_emotion_state(
                valence=result["valence"],
                arousal=result["arousal"],
                dominance=result["dominance"],
                emotion_label=result.get("emotion"),
            )
            EmotionMatrizAdapter.save_node(node)

        return result

    return wrapper
