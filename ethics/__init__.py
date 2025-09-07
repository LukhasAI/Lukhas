"""
Ethics Module
Provides ethical evaluation, safety monitoring, and constraint validation
"""

import warnings

# Import real implementations from governance
try:
    from lukhas.governance.bridge.meg_bridge import MegBridge, MEGPolicyBridge
    from lukhas.governance.ethics.core import create_meg_bridge, ethics_engine, safety_checks
    from lukhas.governance.ethics.ethics_engine import EthicsEngine
    from lukhas.governance.ethics.safety_checker import SafetyChecker
    from lukhas.governance.policy.base import Decision, RiskLevel
    from lukhas.governance.policy_engines import PolicyEngines
except ImportError as e:
    warnings.warn(f"Could not import lukhas.governance ethics components: {e}", stacklevel=2)

    # Fallback stub classes
    class EthicsEngine:
        pass

    class Decision:
        pass

    class RiskLevel:
        pass

    class SafetyChecker:
        pass

    class MEGPolicyBridge:
        pass

    class MegBridge:
        pass

    class PolicyEngines:
        pass

    def create_meg_bridge():
        return MegBridge()

    def ethics_engine():
        return EthicsEngine()

    def safety_checks():
        return SafetyChecker()

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
