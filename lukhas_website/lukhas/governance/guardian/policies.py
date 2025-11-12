"""
Guardian Policies Bridge Module
================================

Bridge to Guardian policies implementation until full consolidation in Phase 3.

This module provides access to GuardianPolicies from the root governance location
while we transition to the canonical lukhas_website location structure.

**Usage**:
    from lukhas_website.lukhas.governance.guardian.policies import GuardianPolicies

**Note**: The actual implementation is currently in governance.guardian_policies
and will be relocated to this location in Phase 3.
"""
from __future__ import annotations

# Bridge to current implementation location
# TODO(Phase 3): Move actual implementation here from governance/guardian_policies.py
from governance.guardian_policies import (
    GuardianPolicies,
    PolicyAction,
    PolicyCondition,
    PolicyEngine,
    PolicyResult,
    PolicyRule,
    PolicySeverity,
)

__all__ = [
    "GuardianPolicies",
    "PolicyAction",
    "PolicyCondition",
    "PolicyEngine",
    "PolicyResult",
    "PolicyRule",
    "PolicySeverity",
]
