"""
DEPRECATED: Legacy Module Location
===================================

This module has been relocated in Phase 3 consolidation.

**Deprecation Notice**: This import path is deprecated as of 2025-11-12.

The implementation has been moved to the canonical location:
    from lukhas_website.lukhas.governance.guardian.reflector import GuardianReflector

Or use the convenience bridge:
    from governance.guardian.reflector import GuardianReflector

Migration Path:
    OLD: from governance.guardian_reflector import GuardianReflector
    NEW: from lukhas_website.lukhas.governance.guardian.reflector import GuardianReflector

This legacy bridge will be removed in Phase 4 (2025-Q1).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "governance.guardian_reflector is deprecated and has been relocated. "
    "Use lukhas_website.lukhas.governance.guardian.reflector instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import from new canonical location
from lukhas_website.lukhas.governance.guardian.reflector import (
    DriftAnalysis,
    DriftIndicator,
    DriftPredictor,
    DriftSeverity,
    DriftType,
    GuardianReflector,
    RemediationEngine,
    RemediationPlan,
    TrendAnalyzer,
)

# Legacy aliases for backward compatibility
DriftMetrics = DriftAnalysis
RemediationAction = dict
RemediationStrategy = RemediationPlan
DriftDimension = DriftType

__all__ = [
    "DriftAnalysis",
    "DriftDimension",
    "DriftIndicator",
    # Legacy aliases
    "DriftMetrics",
    "DriftPredictor",
    # Enums
    "DriftSeverity",
    "DriftType",
    # Main classes
    "GuardianReflector",
    "RemediationAction",
    "RemediationEngine",
    "RemediationPlan",
    "RemediationStrategy",
    # Supporting classes
    "TrendAnalyzer",
]
