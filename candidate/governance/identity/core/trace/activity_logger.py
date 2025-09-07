"""
ΛTRACE Activity Logger
=====================

Core symbolic activity logging engine for LUKHAS ecosystem.
Captures user interactions in symbolic format for pattern analysis.

Logged Events:
- 🆔 ID creation and validation
- 🔐 Session start/end events
- ⬆️ Tier changes and progressions
- 📋 Consent trail modifications
- 🌍 Geo-symbolic traces (with consent)
- 📊 Entropy drift over time
- 🔗 Cross-system interactions
"""

import json
import time
from datetime import datetime
from typing import Any


class LambdaTraceLogger:
    """Symbolic activity logger for LUKHAS ecosystem with enterprise forensic support"""

    def __init__(self, config, consent_manager=None):
        self.config = config
        self.consent_manager = consent_manager
        self.trace_buffer = []
        self.symbolic_map = {
            "id_creation": "🆔",
            "session_start": "🔐",
            "session_end": "🔓",
            "tier_change": "⬆️",
            "consent_grant": "✅",
            "consent_revoke": "❌",
            "geo_event": "🌍",
            "entropy_drift": "📊",
            "cross_system": "🔗",
            "error": "⚠️",
            "security_event": "🛡️",
        }
        self.enterprise_mode = config.get("enterprise_forensic_enabled", False)

    def log_activity(self, user_id: str, activity_type: str, symbolic_data: dict[str, Any]) -> str:
        """Log a symbolic activity event with enterprise forensic capabilities"""

        # Check consent for activity logging
        if self.consent_manager and not self._check_logging_consent(user_id, activity_type):
            return None

        timestamp = datetime.now(timezone.utc).isoformat()
        event_symbol = self.symbolic_map.get(activity_type, "❓")

        # Create comprehensive trace record
        trace_record = {
            "trace_id": self._generate_trace_id(user_id, timestamp),
            "user_id": user_id,
            "activity_type": activity_type,
            "symbol": event_symbol,
            "timestamp": timestamp,
            "symbolic_data": symbolic_data,
            "session_id": symbolic_data.get("session_id"),
            "device_fingerprint": symbolic_data.get("device_fingerprint"),
            "ip_address": (symbolic_data.get("ip_address") if self._geo_consent_granted(user_id) else None),
            "user_agent": symbolic_data.get("user_agent"),
            "trace_context": self._build_trace_context(user_id, activity_type),
        }

        # Add enterprise forensic data if enabled
        if self.enterprise_mode:
            trace_record["forensic_data"] = self._build_forensic_context(trace_record)

        # Store in buffer and persistent storage
        self.trace_buffer.append(trace_record)
        self._persist_trace_record(trace_record)

        return trace_record["trace_id"]

    def log_id_creation(self, user_id: str, lambda_id: str, tier: int, entropy_score: float):
        """Specialized logging for ΛiD creation events"""
        symbolic_data = {
            "lambda_id": lambda_id,
            "tier": tier,
            "entropy_score": entropy_score,
            "creation_method": "symbolic_generation",
            "symbol_representation": f"🆔 {lambda_id}",
        }
        return self.log_activity(user_id, "id_creation", symbolic_data)

    def log_session_event(self, user_id: str, event_type: str, session_data: dict):
        """Log session start/end with symbolic representation"""
        symbolic_data = {
            "session_id": session_data.get("session_id"),
            "device_type": session_data.get("device_type"),
            "login_method": session_data.get("login_method"),
            "symbolic_auth": session_data.get("symbolic_auth_used", False),
        }
        return self.log_activity(user_id, event_type, symbolic_data)

    def log_tier_change(self, user_id: str, old_tier: int, new_tier: int, change_reason: str):
        """Log tier progression with symbolic representation"""
        symbolic_data = {
            "old_tier": old_tier,
            "new_tier": new_tier,
            "change_reason": change_reason,
            "progression_symbol": f"T{old_tier}→T{new_tier}",
            "timestamp_change": datetime.now(timezone.utc).isoformat(),
        }
        return self.log_activity(user_id, "tier_change", symbolic_data)

    def log_consent_trail(self, user_id: str, consent_action: str, scope: str, consent_hash: str):
        """Log consent modifications for audit trail"""
        symbolic_data = {
            "consent_action": consent_action,  # 'grant', 'revoke', 'update'
            "consent_scope": scope,
            "consent_hash": consent_hash,
            "trail_symbol": "✅" if consent_action == "grant" else "❌",
        }
        activity_type = "consent_grant" if consent_action == "grant" else "consent_revoke"
        return self.log_activity(user_id, activity_type, symbolic_data)

    def log_geo_symbolic_trace(self, user_id: str, location_data: dict):
        """Log geo-symbolic events (requires explicit consent)"""
        if not self._geo_consent_granted(user_id):
            return None

        symbolic_data = {
            "location_symbol": location_data.get("location_symbol", "🌍"),
            "region_code": location_data.get("region_code"),
            "symbolic_region": location_data.get("symbolic_region"),
            "precision_level": location_data.get("precision_level", "city"),
        }
        return self.log_activity(user_id, "geo_event", symbolic_data)

    def log_entropy_drift(self, user_id: str, entropy_data: dict):
        """Log entropy changes over time for security monitoring"""
        symbolic_data = {
            "current_entropy": entropy_data.get("current_entropy"),
            "baseline_entropy": entropy_data.get("baseline_entropy"),
            "drift_percentage": entropy_data.get("drift_percentage"),
            "risk_level": entropy_data.get("risk_level", "normal"),
        }
        return self.log_activity(user_id, "entropy_drift", symbolic_data)

    def generate_trace_pattern(self, user_id: str, time_range: dict) -> dict:
        """Generate activity patterns for analysis with symbolic representation"""
        user_traces = [t for t in self.trace_buffer if t["user_id"] == user_id]

        # Filter by time range if provided
        if time_range:
            start_time = time_range.get("start")
            end_time = time_range.get("end")
            user_traces = [t for t in user_traces if start_time <= t["timestamp"] <= end_time]

        # Generate symbolic pattern
        activity_sequence = "".join([t["symbol"] for t in user_traces])

        pattern_analysis = {
            "user_id": user_id,
            "total_events": len(user_traces),
            "symbolic_sequence": activity_sequence,
            "activity_breakdown": self._analyze_activity_breakdown(user_traces),
            "risk_indicators": self._identify_risk_patterns(user_traces),
            "enterprise_summary": (self._generate_enterprise_summary(user_traces) if self.enterprise_mode else None),
        }

        return pattern_analysis

    def _check_logging_consent(self, user_id: str, activity_type: str) -> bool:
        """Check if user has consented to activity logging"""
        if not self.consent_manager:
            return True  # Default to allow if no consent manager

        # Different activities require different consent levels
        consent_requirements = {
            "id_creation": "essential_functions",
            "session_start": "essential_functions",
            "session_end": "essential_functions",
            "tier_change": "trace",
            "consent_grant": "essential_functions",
            "consent_revoke": "essential_functions",
            "geo_event": "location",
            "entropy_drift": "trace",
            "cross_system": "trace",
        }

        required_consent = consent_requirements.get(activity_type, "trace")
        return self.consent_manager.validate_consent(user_id, required_consent)

    def _geo_consent_granted(self, user_id: str) -> bool:
        """Check if user has granted geo-location consent"""
        if not self.consent_manager:
            return False
        return self.consent_manager.validate_consent(user_id, "location")

    def _generate_trace_id(self, user_id: str, timestamp: str) -> str:
        """Generate unique trace ID"""
        import hashlib

        data = f"{user_id}|{timestamp}|{time.time()}"
        return f"TR_{hashlib.sha256(data.encode()).hexdigest()[:8]}"

    def _build_trace_context(self, user_id: str, activity_type: str) -> dict:
        """Build contextual information for trace"""
        return {
            "user_tier": self._get_user_tier(user_id),
            "recent_activity_count": len([t for t in self.trace_buffer[-10:] if t["user_id"] == user_id]),
            "activity_frequency": self._calculate_activity_frequency(user_id),
            "symbolic_pattern_hash": self._generate_pattern_hash(user_id),
        }

    def _build_forensic_context(self, trace_record: dict) -> dict:
        """Build enterprise forensic context"""
        return {
            "forensic_timestamp": time.time(),
            "trace_integrity_hash": self._calculate_integrity_hash(trace_record),
            "audit_chain_link": self._link_to_audit_chain(trace_record),
            "compliance_tags": self._generate_compliance_tags(trace_record),
        }

    def _persist_trace_record(self, trace_record: dict):
        """Persist trace record to storage"""
        # TODO: Implement persistent storage logic

    def _get_user_tier(self, user_id: str) -> int:
        """Get current user tier"""
        # TODO: Integration with ΛTIER system
        return 1  # Placeholder

    def _analyze_activity_breakdown(self, traces: list[dict]) -> dict:
        """Analyze breakdown of activity types"""
        breakdown = {}
        for trace in traces:
            activity = trace["activity_type"]
            breakdown[activity] = breakdown.get(activity, 0) + 1
        return breakdown

    def _identify_risk_patterns(self, traces: list[dict]) -> list[str]:
        """Identify potential risk patterns in activity"""
        risks = []

        # Check for unusual activity frequency
        if len(traces) > 100:  # Threshold for high activity
            risks.append("high_activity_frequency")

        # Check for geo-location anomalies
        geo_events = [t for t in traces if t["activity_type"] == "geo_event"]
        if len({g["symbolic_data"].get("region_code") for g in geo_events}) > 5:
            risks.append("multiple_geographic_regions")

        return risks

    def _generate_enterprise_summary(self, traces: list[dict]) -> dict:
        """Generate enterprise-grade summary for forensic analysis"""
        return {
            "total_trace_events": len(traces),
            "security_events": len([t for t in traces if t["activity_type"] == "security_event"]),
            "consent_modifications": len([t for t in traces if "consent" in t["activity_type"]]),
            "cross_system_interactions": len([t for t in traces if t["activity_type"] == "cross_system"]),
            "forensic_confidence": "high" if len(traces) > 10 else "medium",
        }

    def _calculate_activity_frequency(self, user_id: str) -> str:
        """Calculate user activity frequency"""
        user_traces = [t for t in self.trace_buffer if t["user_id"] == user_id]
        count = len(user_traces)

        if count > 50:
            return "high"
        elif count > 10:
            return "medium"
        else:
            return "low"

    def _generate_pattern_hash(self, user_id: str) -> str:
        """Generate hash of user's activity pattern"""
        user_traces = [t for t in self.trace_buffer if t["user_id"] == user_id]
        pattern = "".join([t["symbol"] for t in user_traces[-20:]])  # Last 20 events
        import hashlib

        return hashlib.sha256(pattern.encode()).hexdigest()[:8]

    def _calculate_integrity_hash(self, trace_record: dict) -> str:
        """Calculate integrity hash for forensic verification"""
        import hashlib

        record_string = json.dumps(trace_record, sort_keys=True)
        return hashlib.sha256(record_string.encode()).hexdigest()

    def _link_to_audit_chain(self, trace_record: dict) -> str:
        """Link trace to audit chain for enterprise compliance"""
        # TODO: Implement audit chain linking
        return f"AUDIT_{trace_record['trace_id']}"

    def _generate_compliance_tags(self, trace_record: dict) -> list[str]:
        """Generate compliance tags for regulatory requirements"""
        tags = ["gdpr_compliant"]

        if trace_record["activity_type"] in ["consent_grant", "consent_revoke"]:
            tags.append("consent_audit_trail")

        if trace_record.get("ip_address"):
            tags.append("geo_data_processed")

        return tags
