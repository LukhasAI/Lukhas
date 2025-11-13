"""
DEPRECATED: Legacy Module Location
===================================

This module has been relocated in Phase 3 consolidation.

**Deprecation Notice**: This import path is deprecated as of 2025-11-12.

The implementation has been moved to the canonical location:
    from lukhas_website.lukhas.governance.guardian.policies import GuardianPoliciesEngine

Or use the convenience bridge:
    from governance.guardian.policies import GuardianPoliciesEngine

Migration Path:
    OLD: from governance.guardian_policies import GuardianPolicies
    NEW: from lukhas_website.lukhas.governance.guardian.policies import GuardianPoliciesEngine

This legacy bridge will be removed in Phase 4 (2025-Q1).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "governance.guardian_policies is deprecated and has been relocated. "
    "Use lukhas_website.lukhas.governance.guardian.policies instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from new canonical location
from lukhas_website.lukhas.governance.guardian.policies import (
    ActionType,
    DecisionType,
    DriftThresholdPolicy,
    EmergencyStopPolicy,
    GuardianPoliciesEngine,
    GuardianResponse,
    PolicyAction,
    PolicyContext,
    PolicyReason,
    PolicyRule,
    RateLimitPolicy,
    SeverityLevel,
    TierAccessPolicy,
    get_guardian_policies_engine,
)

# Legacy aliases for backward compatibility
GuardianPolicies = GuardianPoliciesEngine
PolicyEngine = GuardianPoliciesEngine
PolicyCondition = PolicyContext
PolicyResult = GuardianResponse
PolicySeverity = SeverityLevel

__all__ = [
    "ActionType",
    # Enums
    "DecisionType",
    # Built-in policies
    "DriftThresholdPolicy",
    "EmergencyStopPolicy",
    # Legacy aliases
    "GuardianPolicies",
    # Main classes
    "GuardianPoliciesEngine",
    "GuardianResponse",
    "PolicyAction",
    "PolicyCondition",
    "PolicyContext",
    "PolicyEngine",
    "PolicyReason",
    "PolicyResult",
    "PolicyRule",
    "PolicySeverity",
    "RateLimitPolicy",
    "SeverityLevel",
    "TierAccessPolicy",
    # Functions
    "get_guardian_policies_engine",
]
