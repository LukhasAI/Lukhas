"""Dream generation with regret signature emission."""
from datetime import datetime
from typing import Any, Dict, Optional


class DreamRegretSignature:
    """Event representing a dream's regret signature for post-hoc continuity analysis."""

    def __init__(self, valence: float, arousal: float, cause_tag: str, timestamp: Optional[datetime] = None):
        """
        Initialize a dream regret signature.

        Args:
            valence: Emotional valence score (-1.0 to 1.0, negative=unpleasant, positive=pleasant)
            arousal: Emotional arousal level (0.0 to 1.0, low=calm, high=intense)
            cause_tag: Tag identifying the cause or theme of the regret
            timestamp: When the signature was generated (defaults to now)
        """
        self.valence = max(-1.0, min(1.0, valence))
        self.arousal = max(0.0, min(1.0, arousal))
        self.cause_tag = cause_tag
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert signature to dictionary format."""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "cause_tag": self.cause_tag,
            "timestamp": self.timestamp.isoformat()
        }


class DreamGenerator:
    """Generates dreams and computes regret signatures."""

    def __init__(self, event_bus: Optional[Any] = None):
        """
        Initialize the dream generator.

        Args:
            event_bus: Event bus for emitting signatures (optional)
        """
        self.event_bus = event_bus
        self.last_dream = None
        self.last_signature = None

    def synthesize_dream(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize a dream from the given context.

        Args:
            context: Dream synthesis context containing memory, emotions, etc.

        Returns:
            Generated dream data
        """
        # Placeholder dream synthesis logic
        dream = {
            "id": f"dream_{datetime.utcnow().timestamp()}",
            "content": context.get("seed_content", "A dream unfolds..."),
            "themes": context.get("themes", []),
            "intensity": context.get("intensity", 0.5),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.last_dream = dream

        # Compute and emit regret signature after synthesis
        signature = self._compute_regret_signature(dream, context)
        self._emit_regret_signature(signature)

        return dream

    def _compute_regret_signature(self, dream: Dict[str, Any], context: Dict[str, Any]) -> DreamRegretSignature:
        """
        Compute regret signature for a synthesized dream.

        Args:
            dream: The generated dream
            context: Original context used for synthesis

        Returns:
            DreamRegretSignature containing emotional metrics
        """
        # Extract or compute emotional dimensions
        intensity = dream.get("intensity", 0.5)
        themes = dream.get("themes", [])

        # Simple heuristic: negative themes indicate negative valence
        negative_themes = {"loss", "fear", "anxiety", "regret", "sadness"}
        has_negative = any(theme in negative_themes for theme in themes)

        valence = -0.6 if has_negative else 0.4
        arousal = min(1.0, intensity * 1.2)  # Scale intensity to arousal

        # Determine cause tag from themes or default
        cause_tag = themes[0] if themes else "unspecified"

        signature = DreamRegretSignature(
            valence=valence,
            arousal=arousal,
            cause_tag=cause_tag
        )

        self.last_signature = signature
        return signature

    def _emit_regret_signature(self, signature: DreamRegretSignature) -> None:
        """
        Emit regret signature to event bus.

        Args:
            signature: The signature to emit
        """
        if self.event_bus:
            try:
                self.event_bus.emit("DreamRegretSignature", signature.to_dict())
            except Exception as e:
                # Log but don't fail dream generation
                print(f"Warning: Failed to emit regret signature: {e}")

    def get_last_signature(self) -> Optional[Dict[str, Any]]:
        """Get the last computed regret signature."""
        return self.last_signature.to_dict() if self.last_signature else None


# Example usage and event bus stub
class SimpleEventBus:
    """Simple event bus for demonstration."""

    def __init__(self):
        self.events = []

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit an event."""
        self.events.append({"event": event_name, "data": data, "timestamp": datetime.utcnow()})


if __name__ == "__main__":
    # Demonstration
    bus = SimpleEventBus()
    generator = DreamGenerator(event_bus=bus)

    dream = generator.synthesize_dream({
        "seed_content": "Walking through a misty forest",
        "themes": ["mystery", "exploration"],
        "intensity": 0.7
    })

    print("Generated dream:", dream)
    print("Regret signature:", generator.get_last_signature())
    print("Events emitted:", len(bus.events))
