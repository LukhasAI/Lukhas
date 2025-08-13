"""
LUKHAS AI - Main Package
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

Complete namespace migration from lukhas_pwm → lukhas
Acceptance system available at lukhas.acceptance
"""

__version__ = "3.0.0"
__trinity__ = "⚛️🧠🛡️"

# Main package exports (from old lukhas_pwm)
from . import api
from . import audit
from . import branding
from . import colony
from . import dna
from . import feedback
from . import flags
from . import metrics
from . import migration
from . import modulation
from . import openai
from . import tools

# Legacy client for backwards compatibility
try:
    from .client import LukhasPWM
    # Alias for new namespace
    LukhasAI = LukhasPWM
except ImportError:
    pass

# Acceptance system (kept separate)
from . import acceptance

# Convenient access to common functions
try:
    from .flags import get_flags, require_feature, when_enabled
    from .metrics import get_metrics_collector
except ImportError:
    pass


def get_trinity_status():
    """Get Trinity Framework status: ⚛️🧠🛡️"""
    return {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "version": __version__,
        "status": "🚀 Namespace migration complete"
    }


__all__ = [
    # Core modules
    'flags', 'api', 'audit', 'branding', 'colony', 'dna',
    'feedback', 'metrics', 'migration', 'modulation', 'openai', 'tools',
    # Acceptance system
    'acceptance',
    # Common functions
    'get_flags', 'require_feature', 'when_enabled', 'get_metrics_collector',
    # Trinity helpers
    'get_trinity_status',
    # Legacy compatibility
    'LukhasPWM', 'LukhasAI'
]
