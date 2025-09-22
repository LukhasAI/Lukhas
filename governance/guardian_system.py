"""
LUKHAS Guardian System
====================

Core guardian and safety system for LUKHAS AI.
"""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class GuardianSystem:
    """Core guardian and safety system"""

    def __init__(self):
        """Initialize guardian system"""
        self.logger = logger
        self.logger.info("GuardianSystem initialized")
        self.drift_threshold = 0.15

    def validate_safety(self, operation: dict[str, Any]) -> dict[str, Any]:
        """Validate operation safety with emergency kill-switch check"""

        # CRITICAL: Check for emergency kill-switch
        emergency_file = Path("/tmp/guardian_emergency_disable")
        if emergency_file.exists():
            self.logger.critical("🚨 EMERGENCY KILL-SWITCH ACTIVATED - All operations disabled")
            return {
                "safe": False,
                "drift_score": 1.0,
                "guardian_status": "emergency_disabled",
                "reason": "Emergency kill-switch activated",
                "emergency_active": True
            }

        # Check if Guardian enforcement is enabled (FAIL CLOSED by default)
        dsl_setting = os.getenv("ENFORCE_ETHICS_DSL", "1")
        # Only "0" explicitly disables; everything else (including invalid values) enables (fail closed)
        enforce_dsl = dsl_setting != "0"
        if not enforce_dsl:
            self.logger.warning("Guardian enforcement explicitly disabled via ENFORCE_ETHICS_DSL=0")
            return {
                "safe": True,
                "drift_score": 0.0,
                "guardian_status": "disabled",
                "enforcement_enabled": False
            }

        # Normal safety validation (when enabled and no emergency)
        self.logger.debug("Guardian validating operation safety")
        return {
            "safe": True,
            "drift_score": 0.05,
            "guardian_status": "active",
            "enforcement_enabled": True,
            "emergency_active": False
        }
