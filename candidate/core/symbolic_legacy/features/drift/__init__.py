"""
Symbolic Drift Detection Submodule
==================================

Critical consciousness stability monitoring through drift detection.
Tracks symbolic state changes and detects potentially dangerous drift patterns.

CLAUDE_EDIT_v0.1: Organized drift detection for direct symbolic state interface
LAMBDA_TAG: drift, detection, consciousness, stability
"""

import logging

# Initialize logger
log = logging.getLogger(__name__)
log.info(
    "core.symbolic.drift module initialized - consciousness stability monitoring active"
)

# Import drift detection components
try:
    from .drift_score import DriftScore, DriftScoreCalculator
    from .symbolic_drift_tracker import SymbolicDriftTracker
    from .trace_drift_tracker import TraceDriftMonitor
except ImportError as e:
    log.warning(f"Failed to import drift components: {e}")
    # Provide fallback imports
    SymbolicDriftTracker = None
    DriftScore = None
    DriftScoreCalculator = None
    TraceDriftMonitor = None

# CLAUDE_EDIT_v0.1: Export list for drift submodule
__all__ = [
    "SymbolicDriftTracker",
    "DriftScore",
    "DriftScoreCalculator",
    "TraceDriftMonitor",
    "get_drift_status",
    "calculate_drift_score",
]

# Drift detection thresholds
DRIFT_THRESHOLDS = {
    "safe": 0.2,
    "warning": 0.5,
    "critical": 0.8,
    "collapse_risk": 0.95,
}

# Drift monitoring configuration
DRIFT_CONFIG = {
    "enabled": True,
    "real_time_monitoring": True,
    "alert_on_critical": True,
    "auto_stabilization": False,  # Manual intervention required for safety
    "thresholds": DRIFT_THRESHOLDS,
}

log.info(f"Drift detection configuration: {DRIFT_CONFIG}")


def get_drift_status(drift_score: float) -> str:
    """
    Get drift status based on score.

    CLAUDE_EDIT_v0.1: Helper function for drift status assessment
    """
    if drift_score < DRIFT_THRESHOLDS["safe"]:
        return "SAFE"
    elif drift_score < DRIFT_THRESHOLDS["warning"]:
        return "WARNING"
    elif drift_score < DRIFT_THRESHOLDS["critical"]:
        return "CRITICAL"
    else:
        return "COLLAPSE_RISK"


def calculate_drift_score(current_state, previous_state) -> float:
    """
    Calculate drift score between states.

    CLAUDE_EDIT_v0.1: Wrapper function for backward compatibility
    """
    if DriftScoreCalculator:
        calculator = DriftScoreCalculator()
        return calculator.calculate(current_state, previous_state)
    else:
        # Simple fallback calculation
        return 0.0
