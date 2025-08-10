#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Core Symbolic Glyphs Package

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Core GLYPH subsystem package for symbolic identity, memory tagging, and
action logic processing throughout the LUKHAS AGI system.

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: Core symbolic glyphs package initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 14 - GLYPH Engine Integration

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

from .glyph import (
    CausalLink,
    EmotionVector,
    Glyph,
    GlyphFactory,
    GlyphPriority,
    GlyphType,
    TemporalStamp,
)
from .glyph_engine import GlyphEngine
from .glyph_sentinel import DecayState, GlyphSentinel, PersistencePolicy
from .symbolic_foundry import SymbolicFoundry

# GLYPH_MAP for backward compatibility with tests
# This provides the central glyph mapping that was previously in glyphs.py
GLYPH_MAP = {
    "☯": "Bifurcation Point / Duality / Choice",
    "🪞": "Symbolic Self-Reflection / Introspection",
    "🌪️": "Collapse Risk / High Instability / Chaotic State",
    "🔁": "Dream Echo Loop / Recursive Feedback / Iterative Refinement",
    "💡": "Insight / Revelation / Novel Idea",
    "🔗": "Symbolic Link / Connection / Dependency",
    "🛡️": "Safety Constraint / Ethical Boundary / Protection",
    "🌱": "Emergent Property / Growth / New Potential",
    "❓": "Ambiguity / Uncertainty / Query Point",
    "👁️": "Observation / Monitoring / Awareness State",
    "🧭": "Path Tracking / Logic Navigation / Trace Route",
    "🌊": "Entropic Divergence / Gradual Instability / Drift Point",
    "⚠️": "Caution / Potential Risk / Audit Needed",
    "📝": "Developer Note / Insight / Anchor Comment",
    "✨": "Emergent Logic / Inferred Pattern / Novel Synthesis",
    "✅": "Confirmation / Verification Passed / Logical True / Integrity OK",
    "☣️": (
        "Data Corruption / Symbolic Contamination / Invalid State / "
        "Integrity Compromised"
    ),
    "🔱": (
        "Irrecoverable Divergence / Major System Fork / Entropic Split / "
        "Path No Return"
    ),
}

GLYPH_MAP_VERSION = "1.2.0"


def get_glyph_meaning(glyph_char):
    """Get the meaning of a glyph character from the GLYPH_MAP."""
    return GLYPH_MAP.get(glyph_char, "Unknown Glyph")


__all__ = [
    "Glyph",
    "GlyphType",
    "GlyphPriority",
    "EmotionVector",
    "TemporalStamp",
    "CausalLink",
    "GlyphFactory",
    "SymbolicFoundry",
    "GlyphSentinel",
    "DecayState",
    "PersistencePolicy",
    "GlyphEngine",
    "GLYPH_MAP",
    "GLYPH_MAP_VERSION",
    "get_glyph_meaning",
]
