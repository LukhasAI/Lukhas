"""
LUKHAS AI MΛTRIZ Module
======================

Distributed consciousness architecture with cognitive DNA system.
Implements the MΛTRIZ cognitive framework for consciousness nodes.

Trinity Framework: ⚛️🧠🛡️
"""

import logging

logger = logging.getLogger(__name__)

# Import runtime components
try:
    from .runtime.supervisor import RuntimeSupervisor
    from .runtime.policy import PolicyEngine

    # Alias for backward compatibility
    MatrizNode = RuntimeSupervisor

except ImportError as e:
    logger.warning(f"Failed to import MΛTRIZ runtime components: {e}")
    RuntimeSupervisor = None
    PolicyEngine = None
    MatrizNode = None

__all__ = [
    "RuntimeSupervisor",
    "MatrizNode",  # Alias
    "PolicyEngine",
]

__version__ = "1.0.0"
