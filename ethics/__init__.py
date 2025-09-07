"""
Ethics Module
Provides ethical evaluation, safety monitoring, and constraint validation
"""

import warnings

# Import real implementations from governance
try:
    from lukhas.governance.ethics.ethics_engine import EthicsEngine
    from lukhas.governance.policy.base import Decision, RiskLevel
except ImportError as e:
    warnings.warn(f"Could not import lukhas.governance ethics components: {e}", stacklevel=2)()

# Create aliases for backward compatibility
meg_bridge = MegBridge
policy_engines = PolicyEngines

__all__ = [
    # Core classes
    "Decision",
    "EthicsEngine",
    "MEGPolicyBridge",
    # Namespaces for compatibility
    "MegBridge",
    "PolicyEngines",
    "RiskLevel",
    "SafetyChecker",
    "create_meg_bridge",
    "ethics_engine",
    "meg_bridge",  # Backward compatibility
    "policy_engines",  # Backward compatibility
    "safety_checks",
]
