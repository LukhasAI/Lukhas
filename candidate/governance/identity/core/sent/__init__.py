"""
ΛSENT - Symbolic Consent Engine
==============================

Advanced consent management system for LUKHAS ecosystem.
Handles granular permissions, consent tracking, and revocation.

Features:
- Tier-aware consent boundaries (Tier 0-5)
- Symbolic consent representation with Unicode symbols
- Immutable consent trails with hash-chain verification
- ΛTRACE integration for audit logging
- Zero-knowledge proof support for privacy-preserving consent
- Compliance monitoring (GDPR, EU AI Act, CCPA)

Components:
- ConsentManager: Core consent lifecycle management
- SymbolicScopesManager: Symbolic representation and scope management
- ConsentHistoryManager: Immutable trail and hash-chain verification
- PolicyEngine: Policy management and compliance validation

Symbolic Ecosystem Integration:
- ΛiD# → Identity management
- ΛTRACE → Activity audit trails
- ΛTIER → Access control boundaries
- ΛSING → SSO token management
- ΛSENT → Consent and permission control

Usage:
    from governance.identity.core.sent import LambdaConsentManager

    consent_mgr = LambdaConsentManager(config, trace_logger, tier_manager)
    result = consent_mgr.collect_consent(user_id, "memory", metadata)
    status = consent_mgr.get_consent_status(user_id)
"""

from .consent_history import ConsentHistoryManager
from .consent_manager import LambdaConsentManager
from .policy_engine import ComprehensiveEthicsPolicyEngine
from .symbolic_scopes import SymbolicScopesManager

# Create alias for compatibility with interface.py
ConsentManager = LambdaConsentManager

__all__ = [
    "ComprehensiveEthicsPolicyEngine",
    "ConsentHistoryManager",
    "ConsentManager",
    "LambdaConsentManager",
    "SymbolicScopesManager",
]

# Symbolic consent system version
__version__ = "2.0.0"
__symbolic_name__ = "ΛSENT"
