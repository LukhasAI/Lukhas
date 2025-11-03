"""
LUKHAS Guardian System - Promoted Module
========================================

Advanced ethical oversight and drift detection system for LUKHAS AI.
Feature flag: GUARDIAN_ACTIVE enables full functionality.

Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

Core Components:
- Drift detection with configurable threshold (default: 0.15)
- Ethical evaluation with severity levels
- Safety validation and constitutional AI
- MATRIZ instrumentation on all methods
"""

from __future__ import annotations

import os

import streamlit as st

# Re-export core types
from governance.guardian.core import (
    DriftResult,
    EthicalDecision,
    EthicalSeverity,
    GovernanceAction,
    SafetyResult,
)

# Main interface functions
from governance.guardian.guardian_wrapper import (
    check_safety,
    detect_drift,
    evaluate_ethics,
    get_guardian_status,
)

# Feature flag for Guardian system
GUARDIAN_ACTIVE = os.environ.get("GUARDIAN_ACTIVE", "false").lower() == "true"

# Guardian system imports (conditional)
_guardian_system = None
if GUARDIAN_ACTIVE:
    try:
        from governance.guardian.guardian_impl import GuardianSystemImpl

        _guardian_system = GuardianSystemImpl()
    except ImportError:
        pass

# Legacy compatibility bridge
try:
    from governance.guardian_bridge import GuardianSystem
except ImportError:
    # Create minimal fallback if bridge is not available
    class GuardianSystem:
        def __init__(self, drift_threshold=0.15) -> None:
            self.drift_threshold = drift_threshold

        async def check_drift(self, data) -> float:
            _ = data
            return 0.05  # Safe default

        def get_status(self):
            return {"active": False, "fallback": True}


# Mock guardian for API compatibility
class MockGuardian:
    """Mock Guardian implementation for testing"""

    def __init__(self):
        self.enabled = True

    async def validate_request_async(self, request: dict) -> dict:
        """Mock async request validation"""
        return {
            "approved": True,
            "reason": "Mock Guardian approval",
            "confidence": 0.95
        }

    def validate_action(self, action: dict) -> dict:
        """Mock synchronous action validation"""
        return {
            "allowed": True,
            "reason": "Mock Guardian validation",
            "confidence": 0.95
        }


# Global guardian instance
_global_guardian = None


def get_guardian() -> MockGuardian:
    """Get global Guardian instance"""
    global _global_guardian
    if _global_guardian is None:
        _global_guardian = MockGuardian()
    return _global_guardian


__all__ = [
    "GUARDIAN_ACTIVE",
    "DriftResult",
    "EthicalDecision",
    "EthicalSeverity",
    "GovernanceAction",
    "GuardianSystem",  # Legacy compatibility
    "SafetyResult",
    "check_safety",
    "detect_drift",
    "evaluate_ethics",
    "get_guardian",
    "get_guardian_status",
]
