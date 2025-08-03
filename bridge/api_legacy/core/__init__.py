"""

# Import the integration hub to connect all systems
from orchestration.integration_hub import get_integration_hub

# Initialize the hub to ensure all systems are connected
integration_hub = get_integration_hub()

LUKHAS AI API Module
====================

FastAPI endpoints for accessing LUKHAS AI functionality.

This module provides RESTful API access to:
- Memory System (creation, recall, enhanced recall)
- Dream Processing (logging, consolidation, pattern analysis)
- Emotional Analysis (landscape mapping, clustering, neighborhoods)
- Consciousness Synthesis (state integration, synthesis generation)

All endpoints require proper authentication and respect tier-based access controls.
"""

from . import memory, dream, emotion, consciousness, glyph_exchange

__all__ = ["memory", "dream", "emotion", "consciousness", "glyph_exchange"]
