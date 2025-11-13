"""
LUKHAS QI (Quantum Intelligence) System
Bio-quantum consciousness integration and processing
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import Any

# Version info
__version__ = "1.0.0"
__author__ = "LUKHAS AI Team"

# Core QI system status
QI_AVAILABLE = True

# Try to import core QI components
try:
    # Import coordination components
    from .coordination import coordinator

    QI_COORDINATION_AVAILABLE = True
except ImportError:
    coordinator = None
    QI_COORDINATION_AVAILABLE = False

try:
    # Import awareness systems
    from .awareness_system import core_awareness

    QI_AWARENESS_AVAILABLE = True
except ImportError:
    core_awareness = None
    QI_AWARENESS_AVAILABLE = False

try:
    # Import processing systems
    from .processing import qi_coordinator

    QI_PROCESSING_AVAILABLE = True
except ImportError:
    qi_coordinator = None
    QI_PROCESSING_AVAILABLE = False

try:
    # Import bio integration
    from .bio import bio_integration

    QI_BIO_AVAILABLE = True
except ImportError:
    bio_integration = None
    QI_BIO_AVAILABLE = False

try:
    # Import entanglement system
    from . import qi_entanglement

    QI_ENTANGLEMENT_AVAILABLE = True
except ImportError:
    qi_entanglement = None
    QI_ENTANGLEMENT_AVAILABLE = False


def get_qi_status() -> dict[str, Any]:
    """Get overall QI system status"""
    return {
        "qi_available": QI_AVAILABLE,
        "coordination": QI_COORDINATION_AVAILABLE,
        "awareness": QI_AWARENESS_AVAILABLE,
        "processing": QI_PROCESSING_AVAILABLE,
        "bio_integration": QI_BIO_AVAILABLE,
        "entanglement": QI_ENTANGLEMENT_AVAILABLE,
        "version": __version__,
    }


__all__ = [
    "QI_AVAILABLE",
    "QI_AWARENESS_AVAILABLE",
    "QI_BIO_AVAILABLE",
    "QI_COORDINATION_AVAILABLE",
    "QI_ENTANGLEMENT_AVAILABLE",
    "QI_PROCESSING_AVAILABLE",
    "bio_integration",
    "coordinator",
    "core_awareness",
    "get_qi_status",
    "qi_coordinator",
    "qi_entanglement",
]

# Import compliance, ops, and security modules
try:
    from . import compliance
    QI_COMPLIANCE_AVAILABLE = True
except ImportError:
    compliance = None
    QI_COMPLIANCE_AVAILABLE = False

try:
    from . import ops
    QI_OPS_AVAILABLE = True
except ImportError:
    ops = None
    QI_OPS_AVAILABLE = False

try:
    from . import security
    QI_SECURITY_AVAILABLE = True
except ImportError:
    security = None
    QI_SECURITY_AVAILABLE = False
