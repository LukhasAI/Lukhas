# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: emotion/affect_stagnation_detector.py
# MODULE: emotion.affect_stagnation_detector
# DESCRIPTION: Monitors for emotional stagnation and triggers recovery mechanisms.
# DEPENDENCIES: EmotionalMemory
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - DO NOT DISTRIBUTE
# ═══════════════════════════════════════════════════════════════════════════
# {AIM}{emotion}
# {ΛDRIFT}
# {ΛTRACE}

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import streamlit as st

from identity.interface import IdentityClient, check_consent, verify_access
from lukhas.memory.emotional import EmotionalMemory

log = logging.getLogger(__name__)


class AffectStagnationDetector:
    """
    Monitors for emotional stagnation and triggers recovery mechanisms.
    """

    def __init__(self, emotional_memory: EmotionalMemory, config: Optional[dict[str, Any]] = None):
        self.emotional_memory = emotional_memory
        self.config = config or {}
        self.stagnation_threshold = self.config.get("stagnation_threshold_hours", 24)
        self.last_affect_change_ts = datetime.now(timezone.utc).timestamp()
        self.identity_client = IdentityClient()

    # LUKHAS_TAG: stagnation_alert
    # LUKHAS_TAG: emotion_freeze
    # LUKHAS_TAG: recovery_trigger
    def check_for_stagnation(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Checks for emotional stagnation with tier-based access control.

        Args:
            user_id (str): User requesting stagnation check

        Returns:
            Optional[Dict[str, Any]]: A symbolic prompt if stagnation is detected.
        """
        # Verify user has appropriate tier for emotion monitoring
        if not verify_access(user_id, "LAMBDA_TIER_2"):
            log.warning(f"Access denied for stagnation check: {user_id} lacks LAMBDA_TIER_2")
            raise PermissionError(f"User {user_id} lacks required tier for emotion monitoring")

        # Check consent for emotional processing
        if not check_consent(user_id, "emotion_stagnation_monitoring"):
            log.info(f"Consent denied for emotion stagnation monitoring: {user_id}")
            return None
        now_ts = datetime.now(timezone.utc).timestamp()

        if (
            self.emotional_memory.affect_vector_velocity(depth=2) is not None
            and self.emotional_memory.affect_vector_velocity(depth=2) > 0.001
        ):
            self.last_affect_change_ts = now_ts

        time_since_last_change = now_ts - self.last_affect_change_ts

        # Log the monitoring activity
        self.identity_client.log_activity(
            "emotion_stagnation_check",
            user_id,
            {
                "time_since_last_change_hours": time_since_last_change / 3600,
                "threshold_hours": self.stagnation_threshold,
                "stagnation_detected": time_since_last_change > self.stagnation_threshold * 3600,
            },
        )

        if time_since_last_change > self.stagnation_threshold * 3600:
            log.warning(
                f"Emotional stagnation detected for user {user_id}. No significant affect change for {time_since_last_change / 3600:.2f} hours."
            )

            # Log stagnation detection as security event
            self.identity_client.log_security_event(
                "emotion_stagnation_detected",
                user_id,
                {
                    "duration_hours": time_since_last_change / 3600,
                    "threshold_exceeded": True,
                    "recovery_triggered": True,
                },
            )

            return {
                "stagnation": True,
                "symbol": "🧊",
                "trigger": f"No significant affect change for over {self.stagnation_threshold} hours.",
                "recovery_needed": True,
                "user_id": user_id,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }

        return None
