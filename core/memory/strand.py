"""Memory strand types with double-helix structure."""
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class FactStrand:
    """Represents a factual/semantic memory strand."""

    content: str
    """The factual content or semantic information"""

    metadata: Dict[str, Any]
    """Additional metadata about the fact"""

    timestamp: float
    """When this fact was created/recorded"""

    def hash(self) -> str:
        """
        Compute hash of the fact strand.

        Returns:
            SHA256 hash of the strand content
        """
        data = {
            "content": self.content,
            "timestamp": self.timestamp
        }
        content_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def complement(self) -> str:
        """
        Get complement representation (stub for future implementation).

        In biological DNA, complement means the matching base pair.
        Here it's a placeholder for semantic/associative complement.

        Returns:
            Placeholder complement string
        """
        return f"complement_of_{self.hash()[:8]}"


@dataclass
class EmotionStrand:
    """Represents an emotional/affective memory strand."""

    valence: float
    """Emotional valence (-1.0 to 1.0, negative to positive)"""

    arousal: float
    """Emotional arousal (0.0 to 1.0, calm to intense)"""

    dominant_emotion: str
    """Primary emotion category"""

    intensity: float
    """Overall emotional intensity (0.0 to 1.0)"""

    timestamp: float
    """When this emotion was recorded"""

    def hash(self) -> str:
        """
        Compute hash of the emotion strand.

        Returns:
            SHA256 hash of the strand content
        """
        data = {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominant_emotion": self.dominant_emotion,
            "intensity": self.intensity,
            "timestamp": self.timestamp
        }
        content_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def complement(self) -> str:
        """
        Get complement representation (stub for future implementation).

        For emotions, complement could mean opposing emotion state.

        Returns:
            Placeholder complement string
        """
        # Invert valence for a simple emotional complement
        opposite_valence = -self.valence
        return f"complement_emotion_valence_{opposite_valence:.2f}"


@dataclass
class DoubleStrand:
    """
    Double-helix memory structure combining fact and emotion strands.

    Inspired by DNA's double helix, this pairs semantic/factual information
    with emotional/affective context to create richer memory representations.
    """

    fact: FactStrand
    """The factual/semantic strand"""

    emotion: EmotionStrand
    """The emotional/affective strand"""

    binding_strength: float = 1.0
    """How strongly the fact and emotion are bound (0.0 to 1.0)"""

    def hash(self) -> str:
        """
        Compute combined hash of both strands.

        Returns:
            SHA256 hash of the double-strand structure
        """
        data = {
            "fact_hash": self.fact.hash(),
            "emotion_hash": self.emotion.hash(),
            "binding_strength": self.binding_strength
        }
        content_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def complement(self) -> Dict[str, str]:
        """
        Get complement representation of both strands.

        Returns:
            Dictionary with complement of fact and emotion strands
        """
        return {
            "fact_complement": self.fact.complement(),
            "emotion_complement": self.emotion.complement(),
            "original_hash": self.hash()
        }

    def is_strongly_bound(self, threshold: float = 0.7) -> bool:
        """
        Check if the fact-emotion binding is strong.

        Args:
            threshold: Minimum binding strength to consider strong

        Returns:
            True if binding strength exceeds threshold
        """
        return self.binding_strength >= threshold

    def get_emotional_coloring(self) -> str:
        """
        Get a description of how emotion colors the fact.

        Returns:
            Human-readable description of the emotional context
        """
        if self.emotion.valence > 0.5:
            tone = "positive"
        elif self.emotion.valence < -0.5:
            tone = "negative"
        else:
            tone = "neutral"

        if self.emotion.arousal > 0.7:
            intensity = "intense"
        elif self.emotion.arousal > 0.3:
            intensity = "moderate"
        else:
            intensity = "mild"

        return f"{intensity} {tone} ({self.emotion.dominant_emotion})"


if __name__ == "__main__":
    # Demonstration
    import time
    print("=== Memory Double-Strand Demo ===\n")

    # Create a fact strand
    fact = FactStrand(
        content="The meeting was scheduled for 3pm",
        metadata={"source": "calendar", "confidence": 0.95},
        timestamp=time.time()
    )
    print(f"Fact: {fact.content}")
    print(f"Fact hash: {fact.hash()[:16]}...")
    print(f"Fact complement: {fact.complement()}\n")

    # Create an emotion strand
    emotion = EmotionStrand(
        valence=-0.6,  # Slightly negative
        arousal=0.7,   # Moderately high arousal
        dominant_emotion="anxiety",
        intensity=0.65,
        timestamp=time.time()
    )
    print(f"Emotion: {emotion.dominant_emotion}")
    print(f"  Valence: {emotion.valence}, Arousal: {emotion.arousal}")
    print(f"Emotion hash: {emotion.hash()[:16]}...")
    print(f"Emotion complement: {emotion.complement()}\n")

    # Create double strand
    double_strand = DoubleStrand(
        fact=fact,
        emotion=emotion,
        binding_strength=0.85
    )
    print("Double Strand:")
    print(f"  Combined hash: {double_strand.hash()[:16]}...")
    print(f"  Binding strength: {double_strand.binding_strength}")
    print(f"  Strongly bound: {double_strand.is_strongly_bound()}")
    print(f"  Emotional coloring: {double_strand.get_emotional_coloring()}\n")

    # Get complements
    complements = double_strand.complement()
    print("Complements:")
    for key, value in complements.items():
        print(f"  {key}: {value}")
