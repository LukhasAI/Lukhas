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
    warnings.warn(f"Could not import lukhas.governance ethics components: {e}")
    # Fall back to stubs if needed
    from .stubs import Decision, EthicsEngine, RiskLevel

# Import or create MEGPolicyBridge
try:
    from lukhas.governance.policy.meg_bridge import MEGPolicyBridge, create_meg_bridge
except ImportError:
    # MEGPolicyBridge doesn't exist in governance, use stub
    from .stubs import MEGPolicyBridge, create_meg_bridge

# Import or create SafetyChecker
try:
    from lukhas.governance.ethics.safety_checks import SafetyChecker
except ImportError:
    # SafetyChecker doesn't exist, use stub
    from .stubs import SafetyChecker

# Create namespaces for compatibility with imports like:
# from ethics.meg_bridge import MEGPolicyBridge
# from ethics.policy_engines.base import Decision, RiskLevel
class MegBridge:
    """Namespace for MEG bridge components"""
    MEGPolicyBridge = MEGPolicyBridge
    create_meg_bridge = create_meg_bridge

class PolicyEngines:
    """Namespace for policy engine components"""
    class Base:
        Decision = Decision
        RiskLevel = RiskLevel

# Create module-style attributes for imports like:
# from ethics.ethics_engine import EthicsEngine
# from ethics.safety_checks import SafetyChecker
ethics_engine = type("Module", (), {"EthicsEngine": EthicsEngine})()
safety_checks = type("Module", (), {"SafetyChecker": SafetyChecker})()

# Create aliases for backward compatibility
meg_bridge = MegBridge
policy_engines = PolicyEngines

__all__ = [
    # Core classes
    "Decision",
    "RiskLevel",
    "EthicsEngine",
    "SafetyChecker",
    "MEGPolicyBridge",
    "create_meg_bridge",
    # Namespaces for compatibility
    "MegBridge",
    "PolicyEngines",
    "meg_bridge",  # Backward compatibility
    "policy_engines",  # Backward compatibility
    "ethics_engine",
    "safety_checks"
]
