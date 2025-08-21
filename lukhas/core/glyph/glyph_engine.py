#!/usr/bin/env python3

"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

LUKHAS Glyph Engine - Simple wrapper for the GLYPH system
Provides high-level interface for concept encoding and glyph operations
"""

import hashlib
import json
from typing import Optional

from .glyph import EmotionVector, Glyph, GlyphFactory, GlyphType

# Import LUKHAS AI branding system for Trinity Framework glyphs
try:
    from lukhas.branding_bridge import (
        get_trinity_context, IDENTITY_SYMBOL, CONSCIOUSNESS_SYMBOL, 
        GUARDIAN_SYMBOL, TRINITY_FRAMEWORK
    )
    BRANDING_AVAILABLE = True
except ImportError:
    BRANDING_AVAILABLE = False
    # Fallback Trinity symbols
    IDENTITY_SYMBOL = "⚛️"
    CONSCIOUSNESS_SYMBOL = "🧠"
    GUARDIAN_SYMBOL = "🛡️"
    TRINITY_FRAMEWORK = "⚛️🧠🛡️"


class GlyphEngine:
    """
    High-level interface for LUKHAS GLYPH system operations.
    Simplifies creation and management of glyphs for AI consciousness encoding.
    """

    def __init__(self):
        """Initialize the GLYPH engine."""
        self.factory = GlyphFactory()
        self._glyph_cache = {}

    def encode_concept(
        self, concept: str, emotion: Optional[dict[str, float]] = None
    ) -> str:
        """
        Encode a concept into a GLYPH representation.

        Args:
            concept: The concept to encode
            emotion: Optional emotional context

        Returns:
            String representation of the encoded GLYPH
        """
        # Create emotion vector if provided
        emotion_vector = None
        if emotion:
            emotion_vector = EmotionVector(**emotion)

        # Create appropriate glyph based on concept type
        if any(word in concept.lower() for word in ["remember", "memory", "recall"]):
            glyph = self.factory.create_memory_glyph(concept, emotion_vector)
        elif any(word in concept.lower() for word in ["feel", "emotion", "mood"]):
            glyph = self.factory.create_emotion_glyph(
                emotion_vector or EmotionVector(intensity=0.5)
            )
        elif any(
            word in concept.lower() for word in ["think", "consciousness", "aware"]
        ):
            # Create a consciousness/thought glyph
            glyph = Glyph(
                glyph_type=GlyphType.CAUSAL,
                symbol="🧠",
                emotion_vector=emotion_vector or EmotionVector(),
                semantic_tags={concept},
            )
        else:
            # Default to action glyph
            glyph = self.factory.create_action_glyph(
                action_type=concept, parameters={}, required_tier=1
            )

        # Generate symbolic hash
        glyph_data = {
            "id": glyph.id,
            "type": glyph.glyph_type.value,
            "symbol": glyph.symbol,
            "concept": concept,
        }

        # Create a readable GLYPH representation
        glyph_hash = hashlib.sha256(
            json.dumps(glyph_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        glyph_repr = f"GLYPH[{glyph.symbol}:{glyph_hash}]"

        # Cache the glyph
        self._glyph_cache[glyph_repr] = glyph

        return glyph_repr

    def decode_glyph(self, glyph_repr: str) -> Optional[Glyph]:
        """
        Decode a GLYPH representation back to a Glyph object.

        Args:
            glyph_repr: String representation of the GLYPH

        Returns:
            The decoded Glyph object or None if not found
        """
        return self._glyph_cache.get(glyph_repr)

    def create_memory_glyph(
        self, memory_content: str, emotion: Optional[dict[str, float]] = None
    ) -> Glyph:
        """Create a memory-specific glyph."""
        emotion_vector = EmotionVector(**emotion) if emotion else None
        return self.factory.create_memory_glyph(memory_content, emotion_vector)

    def create_emotion_glyph(self, emotion: dict[str, float]) -> Glyph:
        """Create an emotion-specific glyph."""
        emotion_vector = EmotionVector(**emotion)
        return self.factory.create_emotion_glyph(emotion_vector)
    
    def get_trinity_glyphs(self) -> dict[str, str]:
        """
        Get Trinity Framework glyphs for LUKHAS AI system integration.
        
        Returns:
            Dictionary mapping Trinity aspects to their symbols
        """
        return {
            "identity": IDENTITY_SYMBOL,
            "consciousness": CONSCIOUSNESS_SYMBOL,
            "guardian": GUARDIAN_SYMBOL,
            "framework": TRINITY_FRAMEWORK
        }
    
    def create_trinity_glyph(self, emphasis: str = "balanced") -> Glyph:
        """
        Create a Trinity Framework glyph for LUKHAS AI operations.
        
        Args:
            emphasis: Which Trinity aspect to emphasize (identity, consciousness, guardian, balanced)
            
        Returns:
            Trinity Framework glyph
        """
        if BRANDING_AVAILABLE:
            trinity_context = get_trinity_context(emphasis)
            symbol = trinity_context.get("framework", TRINITY_FRAMEWORK)
        else:
            symbol = TRINITY_FRAMEWORK
            
        return self.factory.create_concept_glyph(
            f"Trinity Framework ({emphasis})",
            symbol=symbol
        )


# Export the GlyphEngine as the main interface
__all__ = ["GlyphEngine"]
