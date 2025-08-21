"""
Glyph module shim for lukhas.accepted.core.glyph imports
Trinity Framework: ⚛️🧠🛡️
"""

# Import the actual glyph implementation
import os
import sys

# Add the project root to path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

# Import from the actual core.glyph module
try:
    from core.glyph.glyph_engine import GlyphEngine
    from core.glyph.glyphs import GLYPHS
except ImportError:
    # Fallback definitions for testing
    class GlyphEngine:
        """Mock GlyphEngine for testing"""

        def __init__(self):
            self.glyphs = {}

        def process(self, text):
            return text

    GLYPHS = {
        "IDENTITY": "⚛️",
        "CONSCIOUSNESS": "🧠",
        "GUARDIAN": "🛡️",
        "TRINITY": "⚛️🧠🛡️",
    }

__all__ = ["GlyphEngine", "GLYPHS"]
