import streamlit as st
import time
# 📦 MODULE      : lukhas_awareness_protocol.py
# 🧾 DESCRIPTION : Context-aware tier fallback + symbolic awareness for post-recovery access
# 🧩 TYPE        : Security Middleware        🔧 VERSION: v0.1.0


class LUKHASAwarenessProtocol:
    def __init__(self, user_id, session_data, symbolic_trace_engine, memory_context):
        self.user_id = user_id
        self.session_data = session_data
        self.symbolic_trace = symbolic_trace_engine
        self.memory = memory_context
        self.confidence_score = 0.0
        self.access_tier = "restricted"
        self.recovery_mode = True

    def assess_awareness(self):
        context_vector = self._generate_context_vector()
        self.confidence_score = self._calculate_confidence(context_vector)
        self.access_tier = self._determine_tier()

        self.symbolic_trace.log_awareness_trace(
            {
                "user_id": self.user_id,
                "confidence_score": self.confidence_score,
                "tier_granted": self.access_tier,
                "recovery_mode": True,
                "timestamp": self.session_data["timestamp"],
            }
        )

        return self.access_tier

    def _generate_context_vector(self):
        return {
            "location_trusted": self.memory.last_known_location_match(),
            "device_fingerprint_match": self.memory.device_fingerprint_check(),
            "voice_resonance": self.memory.voice_match_score(),
            "gesture_pattern": self.memory.lidar_hand_match(),
            "recent_activity": self.memory.recent_activity_baseline_match(),
        }

    def _calculate_confidence(self, context_vector):
        score = (
            0.3 * context_vector["location_trusted"]
            + 0.3 * context_vector["voice_resonance"]
            + 0.2 * context_vector["device_fingerprint_match"]
            + 0.1 * context_vector["gesture_pattern"]
            + 0.1 * context_vector["recent_activity"]
        )
        return round(score, 2)

    def _determine_tier(self):
        if self.confidence_score >= 0.9:
            return "full"
        elif self.confidence_score >= 0.7:
            return "medium"
        elif self.confidence_score >= 0.5:
            return "light"
        else:
            return "restricted"
