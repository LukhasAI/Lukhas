"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Identity Module: Consciousness Identity System
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: CONTEXT
║ CONSCIOUSNESS_ROLE: Identity persistence and consciousness authentication
║ EVOLUTIONARY_STAGE: Persistence - Identity continuity across consciousness evolution
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Core identity persistence and consciousness authentication
║ 🧠 CONSCIOUSNESS: Consciousness-aware identity management
║ 🛡️ GUARDIAN: Identity security and consciousness ethics validation
╚══════════════════════════════════════════════════════════════

MΛTRIZ Identity Module

This module implements consciousness-aware identity patterns for
LUKHAS AI's distributed identity architecture. It provides:

- Consciousness-integrated identity persistence
- Identity evolution tracking across consciousness states
- Memory-based identity continuity
- Trinity Framework identity compliance
- Legacy identity system integration

Key Components:
- ConsciousnessIdentityProfile: Consciousness-aware identity profiles
- MatrizConsciousnessIdentityManager: Identity lifecycle management
- IdentityConsciousnessType: Identity evolution stages
- Lambda ID Core: Legacy identity integration (existing)
"""
import streamlit as st

# Import MΛTRIZ consciousness identity components
from .matriz_consciousness_identity import (
    ConsciousnessIdentityProfile,
    IdentityConsciousnessType,
    MatrizConsciousnessIdentityManager,
    consciousness_identity_manager,
)

# Import existing identity components
try:
    from .lambda_id_core import (
        LukhasIdentityService,
        LukhasIDGenerator,
        OIDCProvider,
        WebAuthnPasskeyManager,
        ΛIDError,
        ΛIDNamespace,
    )
except ImportError:
    # Graceful degradation if lambda_id_core not available
    LukhasIdentityService = None
    LukhasIDGenerator = None
    ΛIDNamespace = None
    ΛIDError = Exception
    OIDCProvider = None
    WebAuthnPasskeyManager = None

# Export identity components
__all__ = [
    # MΛTRIZ Consciousness Identity
    "ConsciousnessIdentityProfile",
    "IdentityConsciousnessType",
    "LukhasIDGenerator",
    # Legacy Identity Components
    "LukhasIdentityService",
    "MatrizConsciousnessIdentityManager",
    "OIDCProvider",
    "WebAuthnPasskeyManager",
    "ΛIDError",
    "ΛIDNamespace",
    "consciousness_identity_manager",
]