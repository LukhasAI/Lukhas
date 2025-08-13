"""
LUKHAS AI - Main Package
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

Complete namespace: lukhas
Acceptance system available at lukhas.acceptance
"""

__version__ = "1.0.0"
__trinity__ = "⚛️🧠🛡️"

# Main package exports
from . import (
    api,
    audit,
    branding,
    colony,
    dna,
    feedback,
    flags,
    metrics,
    migration,
    modulation,
    openai,
    tools,
)

# Legacy client for backwards compatibility
try:
    from .client import LukhasAI

    # Legacy alias for backwards compatibility
    Lukhas = LukhasAI
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
        "status": "🚀 Active",
    }


__all__ = [
    # Core modules
    "flags",
    "api",
    "audit",
    "branding",
    "colony",
    "dna",
    "feedback",
    "metrics",
    "migration",
    "modulation",
    "openai",
    "tools",
    # Acceptance system
    "acceptance",
    # Common functions
    "get_flags",
    "require_feature",
    "when_enabled",
    "get_metrics_collector",
    # Trinity helpers
    "get_trinity_status",
    # Main client
    "LukhasAI",
    "Lukhas",  # Legacy alias
    "LukhasAI",
]
