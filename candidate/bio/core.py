"""
LUKHAS AI Bio Module - Core Engine
Central bio processing engine
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
from typing import Any

import streamlit as st

from .awareness import BioAwareness
from .oscillator import get_orchestrator
from .symbolic import get_symbolic_processor

__module__ = "bio.core"
__trinity__ = "⚛️🧠🛡️"


class BioEngine:
    """Main bio processing engine"""

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.symbolic = get_symbolic_processor()
        self.awareness = BioAwareness()
        self.active = True
        self.cycles = 0

    def process(self, input_data: Any = None) -> dict[str, Any]:
        """Main processing cycle"""
        if not self.active:
            return {"status": "inactive"}

        self.cycles += 1

        # Step oscillators
        oscillations = self.orchestrator.step()

        # Process symbolic
        symbolic_result = self.symbolic.process(input_data)

        # Update awareness
        awareness_result = self.awareness.sense(input_data)

        return {
            "cycle": self.cycles,
            "oscillations": oscillations,
            "symbolic": symbolic_result,
            "awareness": awareness_result,
            "trinity": "aligned",
        }

    def reset(self):
        """Reset bio engine"""
        self.orchestrator.reset_all()
        self.cycles = 0
        self.awareness = BioAwareness()

    def shutdown(self):
        """Shutdown bio engine"""
        self.active = False


# Singleton instance
_engine = None


def get_bio_engine() -> BioEngine:
    """Get or create bio engine singleton"""
    global _engine
    if _engine is None:
        _engine = BioEngine()
    return _engine
