"""
LUKHAS Accepted Bio Components
Links to verified bio-inspired consciousness modules

⚛️🧠🛡️ Trinity Framework: Identity-Consciousness-Guardian
"""

# Import from existing bio modules
try:
    from bio.awareness import *

    # Also import utilities
    from bio.bio_utilities import *
    from bio.core import *
    from bio.symbolic import *

except ImportError as e:
    # Log the import issue but provide fallbacks
    import logging

    logger = logging.getLogger(__name__)
    logger.debug(f"Some bio components not available: {e}")

    # Minimal fallback classes
    class BioEngine:
        def __init__(self):
            self.status = "fallback"

    class BioAwareness:
        def __init__(self):
            self.level = 0.5


# Export main components
__all__ = ["BioEngine", "BioAwareness"]
