"""
Bridge module for governance.guardian.guardian_wrapper
======================================================

Provides access to Guardian wrapper functions from lukhas_website.lukhas.governance.guardian.guardian_wrapper
with fallback to labs implementation if needed.

This bridge enables imports like:
    from governance.guardian.guardian_wrapper import detect_drift, evaluate_ethics

Wrapper Functions:
- detect_drift: Detect ethical drift in system behavior
- evaluate_ethics: Evaluate ethical implications of an action
- check_safety: Perform safety validation on content
- get_guardian_status: Get Guardian system status and metrics
"""

from __future__ import annotations

try:
    # Primary: lukhas_website production lane
    from lukhas_website.lukhas.governance.guardian.guardian_wrapper import (
        check_safety,
        detect_drift,
        evaluate_ethics,
        get_guardian_status,
    )
except ImportError:
    try:
        # Fallback: labs development lane
        from labs.governance.guardian.guardian_wrapper import (
            check_safety,
            detect_drift,
            evaluate_ethics,
            get_guardian_status,
        )
    except ImportError:
        # Final fallback: raise informative error
        raise ImportError(
            "Guardian wrapper not found. "
            "Expected location: lukhas_website.lukhas.governance.guardian.guardian_wrapper "
            "or labs.governance.guardian.guardian_wrapper"
        )

__all__ = [
    "check_safety",
    "detect_drift",
    "evaluate_ethics",
    "get_guardian_status",
]
