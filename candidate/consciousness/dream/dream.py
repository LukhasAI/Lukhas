"""
Dream Module - Simplified entry point for LUKHAS dream system
Trinity Framework: ⚛️🧠🛡️

This module consolidates access to the complex dream system through a simple interface.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DreamSystem:
    """Unified interface to LUKHAS dream system"""

    def __init__(self):
        self.engine = None
        self.oneiric = None
        self.initialized = False

    def initialize(self):
        """Initialize dream components"""
        if self.initialized:
            return

        components = []

        # Try to load the main dream engine
        try:
            from .core.dream_engine import DreamEngine
            self.engine = DreamEngine()
            components.append("CoreEngine")
        except ImportError as e:
            logger.debug(f"Core dream engine not available: {e}")

        # Try to load the oneiric system
        try:
            from .oneiric.oneiric_core.engine.dream_engine_fastapi import (
                DreamEngineFastAPI,
            )
            self.oneiric = DreamEngineFastAPI()
            components.append("OneiricEngine")
        except ImportError as e:
            logger.debug(f"Oneiric engine not available: {e}")

        # Try the simple engine as fallback
        if not self.engine and not self.oneiric:
            try:
                from .engine.dream_engine import DreamEngine as SimpleDreamEngine
                self.engine = SimpleDreamEngine()
                components.append("SimpleEngine")
            except ImportError:
                pass

        self.initialized = True
        if components:
            logger.info(f"Dream system initialized with: {', '.join(components)}")
        else:
            logger.warning("No dream engines available")

    async def generate_dream(self, seed: Any = None) -> dict[str, Any]:
        """Generate a dream from a seed"""
        self.initialize()

        # Try the main engine first
        if self.engine and hasattr(self.engine, "generate_dream"):
            try:
                return await self.engine.generate_dream(seed)
            except Exception as e:
                logger.error(f"Core engine dream generation failed: {e}")

        # Try oneiric
        if self.oneiric and hasattr(self.oneiric, "generate"):
            try:
                return await self.oneiric.generate(seed)
            except Exception as e:
                logger.error(f"Oneiric dream generation failed: {e}")

        # Fallback
        return {
            "type": "fallback_dream",
            "content": f"Dream seed: {seed}",
            "engine": "none"
        }

    def get_status(self) -> dict[str, Any]:
        """Get dream system status"""
        self.initialize()
        return {
            "initialized": self.initialized,
            "core_engine": self.engine is not None,
            "oneiric_engine": self.oneiric is not None,
            "complexity": "high",  # Dreams are complex in LUKHAS
            "path": "consciousness/dream/dream.py"
        }


# Create a global instance for easy access
dream_system = DreamSystem()

# Export main functions
def initialize():
    """Initialize the dream system"""
    return dream_system.initialize()

async def generate_dream(seed: Any = None):
    """Generate a dream"""
    return await dream_system.generate_dream(seed)

def get_status():
    """Get dream system status"""
    return dream_system.get_status()

# For backward compatibility
DreamEngine = DreamSystem

__all__ = ["DreamSystem", "dream_system", "initialize", "generate_dream", "get_status", "DreamEngine"]
