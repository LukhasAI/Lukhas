"""
LUKHAS AI Bio Module
Unified bio-inspired processing system
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

__version__ = "1.0.0"
__trinity__ = "⚛️🧠🛡️"

# Core components
from . import adapters, awareness, oscillator, symbolic

# Optional quantum features (feature-flagged)
try:
    from . import qi
except ImportError:
    quantum = None

# Optional voice features
try:
    from . import voice
except ImportError:
    voice = None

__all__ = ["oscillator", "symbolic", "awareness", "adapters", "quantum", "voice"]

# Bio engine singleton
_engine = None


def get_bio_engine():
    """Get or create bio engine instance"""
    from .core import get_bio_engine as _get_engine

    return _get_engine()


# Trinity integration
def trinity_sync():
    """Synchronize with Trinity Framework"""
    return {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "status": "synchronized",
    }
