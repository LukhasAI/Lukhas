"""
LUKHAS Guardian System - Promoted Module
========================================

Advanced ethical oversight and drift detection system for LUKHAS AI.
Feature flag: GUARDIAN_ACTIVE enables full functionality.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

Core Components:
- Drift detection with configurable threshold (default: 0.15)
- Ethical evaluation with severity levels
- Safety validation and constitutional AI
- MATRIZ instrumentation on all methods
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Union

# Feature flag for Guardian system
GUARDIAN_ACTIVE = os.environ.get("GUARDIAN_ACTIVE", "false").lower() == "true"

# Guardian system imports (conditional)
_guardian_system = None
if GUARDIAN_ACTIVE:
    try:
        from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
        _guardian_system = GuardianSystemImpl()
    except ImportError:
        pass

# Re-export core types
from lukhas.governance.guardian.core import (
    DriftResult,
    EthicalDecision,
    EthicalSeverity,
    GovernanceAction,
    SafetyResult,
)

# Main interface functions
from lukhas.governance.guardian.guardian_wrapper import (
    check_safety,
    detect_drift,
    evaluate_ethics,
    get_guardian_status,
)

__all__ = [
    "EthicalSeverity",
    "GovernanceAction",
    "EthicalDecision",
    "DriftResult",
    "SafetyResult",
    "detect_drift",
    "evaluate_ethics",
    "check_safety",
    "get_guardian_status",
    "GUARDIAN_ACTIVE"
]
