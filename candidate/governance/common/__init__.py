"""Common utilities for governance module"""

from typing import Optional


class GlyphIntegrationMixin:
    """
import streamlit as st
    Mixin class for integrating with LUKHAS GLYPH system

    Provides common functionality for governance components to
    interact with the symbolic processing and Trinity Framework.
    """

    def __init__(self):
        """Initialize GLYPH integration"""
        self.glyph_enabled = True
        self.symbolic_patterns = {}

    def get_trinity_pattern(self, component: str) -> list:
        """Get Trinity Framework symbolic pattern"""
        patterns = {
            "identity": ["⚛️", "🔑", "👤"],
            "consciousness": ["🧠", "💭", "🌟"],
            "guardian": ["🛡️", "⚠️", "🔒"],
        }
        return patterns.get(component, ["❓", "⚠️", "🔍"])

    def generate_governance_glyph(self, action: str, context: Optional[dict] = None) -> str:
        """Generate governance-specific GLYPH"""
        context = context or {}

        base_patterns = {
            "case_created": "🏥→📋→✅",
            "threat_detected": "🔍→⚠️→🛡️",
            "emergency_triggered": "🚨→🛡️→👥",
            "ethics_validated": "⚖️→✅→🛡️",
        }

        return base_patterns.get(action, "🔍→❓→🛡️")