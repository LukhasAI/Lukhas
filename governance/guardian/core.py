"""
Bridge module for governance.guardian.core
==========================================

Provides access to Guardian core types from lukhas_website.lukhas.governance.guardian.core
with fallback to labs implementation if needed.

This bridge enables imports like:
    from governance.guardian.core import DriftResult, EthicalDecision

Core Types:
- DriftResult: Drift detection analysis result
- EthicalDecision: Ethical evaluation decision
- EthicalSeverity: Severity level enum (LOW, MEDIUM, HIGH, CRITICAL)
- GovernanceAction: Action requiring governance oversight
- SafetyResult: Safety validation result
"""

from __future__ import annotations

try:
    # Primary: lukhas_website production lane
    from lukhas_website.lukhas.governance.guardian.core import (
        DriftResult,
        EthicalDecision,
        EthicalSeverity,
        GovernanceAction,
        SafetyResult,
    )
except ImportError:
    try:
        # Fallback: labs development lane
        from labs.governance.guardian.core import (
            DriftResult,
            EthicalDecision,
            EthicalSeverity,
            GovernanceAction,
            SafetyResult,
        )
    except ImportError:
        # Final fallback: raise informative error
        raise ImportError(
            "Guardian core types not found. "
            "Expected location: lukhas_website.lukhas.governance.guardian.core "
            "or labs.governance.guardian.core"
        )

__all__ = [
    "DriftResult",
    "EthicalDecision",
    "EthicalSeverity",
    "GovernanceAction",
    "SafetyResult",
]
