"""
Compatibility shim - DEPRECATED
This module has been moved to production.
Will be removed after 2025-11-01 (SHIM_CULL_DATE)
"""

import warnings

warnings.warn(
    "Import path deprecated. Use 'from lukhas.acceptance.accepted.governance.drift_governor import ...'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from lukhas.acceptance.accepted.governance.drift_governor import (
    EthicalConcern,
    EthicalDriftGovernor,
    EthicalSeverity,
    GovernanceRule,
    InterventionType,
)

__all__ = [
    "EthicalDriftGovernor",
    "EthicalSeverity",
    "InterventionType",
    "EthicalConcern",
    "GovernanceRule",
]
