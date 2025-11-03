"""
══════════════════════════════════════════════════════════════════════════════════
║ 🫀 LUKHAS AI - BIO MODULE SYMBOLIC VOCABULARY
║ Symbolic vocabulary for biometric monitoring and health tracking operations
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: bio_vocabulary.py
║ Path: lukhas/symbolic/vocabularies/bio_vocabulary.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Bio Team | Claude Code (vocabulary extraction)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The Bio Vocabulary module provides symbolic representations for all biometric
║ and health-related operations within the LUKHAS AGI system. It enables clear
║ communication of physiological states and authentication statuses.
║
║ Key Features:
║ • Biometric authentication symbols
║ • Health monitoring status indicators
║ • Device connectivity representations
║ • Physiological metric symbols
║ • Privacy compliance indicators
║
║ Vocabulary Categories:
║ • Authentication: Face, Voice, Fingerprint, EEG, DNA
║ • Health States: Excellent, Good, Warning, Critical
║ • Metrics: Heart Rate, Stress, Temperature, Activity
║
║ Part of the LUKHAS Symbolic System - Unified Grammar v1.0.0
║ Symbolic Tags: {ΛBIO}, {ΛHEALTH}, {ΛAUTH}
╚══════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations


# Bio status symbols
BIO_SYMBOLS = {
    "🫀": "bio_active",
    "💓": "heartbeat_detected",
    "🧬": "dna_analysis",
    "🔐": "biometric_auth",
    "⚡": "signal_strong",
    "📱": "device_connected",
    "🏥": "health_monitoring",
    "😌": "calm_state",
    "🚨": "stress_detected",
    "💊": "health_alert",
    "🔋": "device_battery",
    "📊": "health_analytics",
    "🎯": "calibration",
    "🔬": "bio_analysis",
    "⏰": "monitoring_cycle",
}

# Emotional state symbols
EMOTION_SYMBOLS = {
    "😌": "calm",
    "😄": "happy",
    "😰": "stressed",
    "😴": "tired",
    "🎯": "focused",
    "😤": "frustrated",
    "😊": "excited",
    "😟": "anxious",
    "🧘": "meditative",
    "💪": "energized",
}

# Device type symbols
DEVICE_SYMBOLS = {
    "⌚": "apple_watch",
    "💍": "oura_ring",
    "📱": "smartphone",
    "🎧": "eeg_headset",
    "👁️": "eye_tracker",
    "🖐️": "gesture_sensor",
    "🩺": "medical_device",
    "🏃": "fitness_tracker",
    "💤": "sleep_monitor",
    "🧠": "brain_monitor",
}

# Biometric type symbols
BIOMETRIC_SYMBOLS = {
    "👤": "face_recognition",
    "🗣️": "voice_pattern",
    "👆": "fingerprint",
    "🧠": "brainwave",
    "⚡": "skin_response",
    "💓": "heart_rhythm",
    "👁️": "eye_gaze",
    "🖐️": "hand_gesture",
    "⌨️": "typing_pattern",
    "👣": "gait_pattern",
}

# Health metric symbols
HEALTH_SYMBOLS = {
    "💓": "heart_rate",
    "🩸": "blood_pressure",
    "😰": "stress_level",
    "💤": "sleep_quality",
    "🏃": "activity_level",
    "🌡️": "temperature",
    "🫁": "oxygen_level",
    "💨": "breathing_rate",
    "🧘": "hrv_score",
    "⚖️": "body_weight",
}

# Authentication status symbols
AUTH_SYMBOLS = {
    "✅": "auth_success",
    "❌": "auth_failed",
    "🔐": "auth_required",
    "⏰": "auth_timeout",
    "🚫": "auth_locked",
    "🔄": "auth_retry",
    "👤": "user_verified",
    "🔓": "access_granted",
    "🛡️": "security_check",
    "📋": "consent_given",
}

# Data privacy symbols
PRIVACY_SYMBOLS = {
    "🔒": "data_encrypted",
    "🛡️": "privacy_protected",
    "📜": "gdpr_compliant",
    "🗑️": "data_deleted",
    "⏰": "retention_expired",
    "📋": "consent_required",
    "🔐": "access_controlled",
    "🏥": "medical_privacy",
    "🔄": "data_anonymized",
    "📊": "usage_analytics",
}

# Alert and notification symbols
ALERT_SYMBOLS = {
    "🚨": "critical_alert",
    "⚠️": "warning",
    "ℹ️": "info_notice",
    "💊": "health_reminder",
    "🏃": "activity_goal",
    "😴": "sleep_reminder",
    "💧": "hydration_alert",
    "🧘": "stress_break",
    "🩺": "checkup_due",
    "📈": "trend_alert",
}

# Complete symbolic vocabulary for Bio module
BIO_VOCABULARY = {
    **BIO_SYMBOLS,
    **EMOTION_SYMBOLS,
    **DEVICE_SYMBOLS,
    **BIOMETRIC_SYMBOLS,
    **HEALTH_SYMBOLS,
    **AUTH_SYMBOLS,
    **PRIVACY_SYMBOLS,
    **ALERT_SYMBOLS,
}

# Bio operation messages
BIO_MESSAGES = {
    "startup": "🫀 Bio module awakening - monitoring life signs",
    "shutdown": "🫀 Bio module resting - health data secured",
    "device_connected": "📱 Wearable device synced with bio stream",
    "auth_success": "🔐 Biometric identity confirmed - access granted",
    "auth_failed": "❌ Biometric pattern unrecognized - please retry",
    "health_alert": "🚨 Vital signs require attention - health alert triggered",
    "stress_detected": "😰 Elevated stress patterns detected - recommend relaxation",
    "calibration": "🎯 Biometric sensors calibrating for optimal accuracy",
    "privacy_mode": "🛡️ GDPR privacy mode active - data protection enabled",
    "emotion_calm": "😌 Emotional state: calm and balanced",
    "emotion_stressed": "😰 Emotional state: stress detected - monitoring closely",
    "data_encrypted": "🔒 Biometric data encrypted and secured",
    "monitoring_active": "🏥 Continuous health monitoring active",
    "entropy_calculated": "🧬 Symbolic entropy extracted from bio signals",
}


def get_bio_symbol(key: str) -> str:
    """Get bio symbol for a given key."""
    return BIO_VOCABULARY.get(key, "🫀")


def get_bio_message(key: str) -> str:
    """Get bio message for a given key."""
    return BIO_MESSAGES.get(key, f"🫀 Bio operation: {key}")


def format_bio_log(operation: str, details: str = "") -> str:
    """Format a bio module log message."""
    symbol = get_bio_symbol(operation)
    base_msg = get_bio_message(operation)
    if details:
        return f"{symbol} {base_msg} - {details}"
    return f"{symbol} {base_msg}"


"""
╔══════════════════════════════════════════════════════════════════════════════════
║ REFERENCES:
║   - Docs: docs/symbolic/vocabularies/bio_vocabulary.md
║   - Issues: github.com/lukhas-ai/core/issues?label=bio-vocabulary
║   - Wiki: internal.ai/wiki/bio-symbolic-system
║
║ VOCABULARY STATUS:
║   - Total Symbols: 40+ bio-related symbols
║   - Coverage: Complete for bio module operations
║   - Integration: Fully integrated with Unified Grammar v1.0.0
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This vocabulary is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚══════════════════════════════════════════════════════════════════════════════════
"""