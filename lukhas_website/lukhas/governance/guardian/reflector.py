"""
Guardian Reflector Bridge Module
=================================

Bridge to Guardian reflector implementation until full consolidation in Phase 3.

This module provides access to GuardianReflector from the root governance location
while we transition to the canonical lukhas_website location structure.

**Usage**:
    from lukhas_website.lukhas.governance.guardian.reflector import GuardianReflector

**Note**: The actual implementation is currently in governance.guardian_reflector
and will be relocated to this location in Phase 3.
"""
from __future__ import annotations

# Bridge to current implementation location
# TODO(Phase 3): Move actual implementation here from governance/guardian_reflector.py
from governance.guardian_reflector import (
    DriftDimension,
    DriftMetrics,
    DriftSeverity,
    GuardianReflector,
    RemediationAction,
    RemediationPlan,
    RemediationStrategy,
)

__all__ = [
    "DriftDimension",
    "DriftMetrics",
    "DriftSeverity",
    "GuardianReflector",
    "RemediationAction",
    "RemediationPlan",
    "RemediationStrategy",
]
