"""
LUKHAS AI Candidate Module Package

This package contains all candidate implementations and modules for the
LUKHAS AI consciousness development system.

⚛️🧠🛡️ Trinity Framework Integration
- Identity: Candidate consciousness modules
- Consciousness: Core processing implementations
- Guardian: Safety and compliance validation

Modules:
- core/: Core consciousness and processing systems
- governance/: Governance and policy implementations
- tools/: Tool execution and management systems
- orchestration/: High-level coordination systems
- memory/: Memory management and persistence
- emotion/: Emotional intelligence systems
- consciousness/: Consciousness development modules
- vivox/: VIVOX consciousness system components
- bridge/: Integration and bridge systems
- monitoring/: System monitoring and analytics
- compliance/: Compliance and regulatory systems
- bio/: Bio-inspired processing systems
- qi/: Quantum-inspired processing modules
- voice/: Voice and communication systems
"""

# from consciousness.qi import qi  # Temporarily disabled due to import cascade
try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None
    # Optional UI dependency; core runtime must not require it.

# Version information
__version__ = "1.0.0-dev"
__author__ = "LUKHAS AI Agent Army"
__description__ = "LUKHAS AI Candidate Module Package - Trinity Framework Implementation"

# Trinity Framework symbols
TRINITY_SYMBOLS = "⚛️🧠🛡️"

# Package metadata
PACKAGE_INFO = {
    "name": "lukhas-candidate",
    "version": __version__,
    "description": __description__,
    "trinity_framework": True,
    "consciousness_aware": True,
    "agent_army_compatible": True,
}
