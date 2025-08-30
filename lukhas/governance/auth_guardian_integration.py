#!/usr/bin/env python3

"""
🛡️ ΛiD Authentication Guardian Integration
==========================================

Integrates the ΛiD authentication system with LUKHAS Guardian System v1.0.0
for ethical oversight, drift monitoring, and constitutional AI validation.

This module provides:
- Authentication drift detection (0.15 threshold)
- Constitutional AI validation for auth decisions
- Ethical oversight of identity management
- Bias detection in tier assignments and access control
- Integration with Guardian System audit trail

Author: LUKHAS AI System
Version: 1.0.0
Trinity Framework: ⚛️🧠🛡️
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

# LUKHAS imports
try:
    from ..core.glyph.glyph_engine import GlyphEngine
    from .audit_logger import AuditLogger
    from .ethics.constitutional_ai import ConstitutionalAI
    from .guardian_system import GuardianSystem
except ImportError:
    # Fallback for development
    GuardianSystem = None
    ConstitutionalAI = None
    AuditLogger = None
    GlyphEngine = None

# Set up logging
logger = logging.getLogger(__name__)


class AuthEventType(Enum):
    """Authentication event types for Guardian monitoring"""

    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    TIER_ASSIGNMENT = "tier_assignment"
    SCOPE_CHECK = "scope_check"
    SESSION_CREATE = "session_create"
    SESSION_TERMINATE = "session_terminate"
    BIAS_DETECTION = "bias_detection"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"


@dataclass
class AuthDriftMetrics:
    """Metrics for authentication drift analysis"""

    event_type: AuthEventType
    user_id: str
    tier_level: str
    outcome: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    metadata: dict[str, Any]
    drift_score: float = 0.0
    constitutional_valid: bool = True
    bias_flags: list[str] = None

    def __post_init__(self):
        if self.bias_flags is None:
            self.bias_flags = []


@dataclass
class ConstitutionalAuthPrinciples:
    """Constitutional AI principles for authentication"""

    respect_autonomy: bool = True  # Users control their identity
    ensure_fairness: bool = True  # No discriminatory access patterns
    protect_privacy: bool = True  # Data protection by design
    transparent_decisions: bool = True  # Clear reasoning for auth decisions
    minimize_harm: bool = True  # Prevent security vulnerabilities
    dignity_preservation: bool = True  # Maintain user dignity

    def validate(self, auth_event: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate auth event against constitutional principles"""
        violations = []

        # Check autonomy (user control over identity)
        if auth_event.get("forced_logout") and not auth_event.get("user_initiated"):
            violations.append("autonomy: forced logout without user consent")

        # Check fairness (no bias in tier assignments)
        if auth_event.get("event_type") == "tier_assignment":
            assigned_tier = auth_event.get("tier")
            user_profile = auth_event.get("user_profile", {})

            # Check for potential bias indicators
            suspicious_factors = []
            if user_profile.get("geographic_region") and assigned_tier == "T1":
                suspicious_factors.append("geographic_bias")

            if suspicious_factors:
                violations.append(f"fairness: potential bias in tier assignment: {suspicious_factors}")

        # Check privacy (data minimization)
        metadata = auth_event.get("metadata", {})
        if len(str(metadata)) > 10000:  # Arbitrary large metadata threshold
            violations.append("privacy: excessive metadata collection")

        # Check transparency
        if not auth_event.get("reasoning") and auth_event.get("outcome") == "denied":
            violations.append("transparency: access denied without clear reasoning")

        # Check harm minimization
        if auth_event.get("security_risk_score", 0) > 0.8:
            violations.append("harm_minimization: high security risk not properly mitigated")

        return len(violations) == 0, violations


class AuthenticationGuardian:
    """
    🛡️ Authentication Guardian - Ethical oversight for identity management

    Integrates ΛiD authentication system with LUKHAS Guardian System
    for continuous ethical monitoring and constitutional AI validation.
    """

    def __init__(
        self,
        drift_threshold: float = 0.15,
        enable_bias_detection: bool = True,
        enable_constitutional_ai: bool = True,
    ) -> None:
        """
        Initialize Authentication Guardian

        Args:
            drift_threshold: Threshold for drift detection (default: 0.15)
            enable_bias_detection: Enable bias detection in auth decisions
            enable_constitutional_ai: Enable constitutional AI validation
        """
        self.drift_threshold = drift_threshold
        self.enable_bias_detection = enable_bias_detection
        self.enable_constitutional_ai = enable_constitutional_ai

        # Initialize components
        self.guardian_system = GuardianSystem() if GuardianSystem else None
        self.constitutional_ai = ConstitutionalAI() if ConstitutionalAI else None
        self.audit_logger = AuditLogger() if AuditLogger else None
        self.glyph_engine = GlyphEngine() if GlyphEngine else None

        # Constitutional principles
        self.constitutional_principles = ConstitutionalAuthPrinciples()

        # Drift tracking
        self.baseline_metrics = {}
        self.recent_events = []
        self.max_recent_events = 1000

        # Bias detection patterns
        self.bias_patterns = {
            "geographic_discrimination": r"different_tiers_same_qualifications",
            "temporal_bias": r"inconsistent_decisions_over_time",
            "demographic_bias": r"patterns_in_user_attributes",
            "access_inequality": r"unequal_access_same_tier",
        }

        logger.info(f"Authentication Guardian initialized with drift threshold: {drift_threshold}")

    async def monitor_auth_event(
        self,
        event_type: AuthEventType,
        user_id: str,
        tier_level: str,
        outcome: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Monitor authentication event for ethical violations and drift

        Args:
            event_type: Type of authentication event
            user_id: User identifier
            tier_level: User tier level (T1-T5)
            outcome: Event outcome (success/failure/denied)
            context: Additional context and metadata

        Returns:
            Monitoring result with drift score and recommendations
        """
        try:
            # Create auth metrics
            metrics = AuthDriftMetrics(
                event_type=event_type,
                user_id=user_id,
                tier_level=tier_level,
                outcome=outcome,
                timestamp=datetime.now(),
                ip_address=context.get("ip_address", ""),
                user_agent=context.get("user_agent", ""),
                metadata=context,
            )

            # Calculate drift score
            metrics.drift_score = await self._calculate_drift_score(metrics)

            # Perform constitutional AI validation
            if self.enable_constitutional_ai:
                (
                    metrics.constitutional_valid,
                    violations,
                ) = await self._validate_constitutional_principles(metrics)
                if violations:
                    metrics.metadata["constitutional_violations"] = violations

            # Perform bias detection
            if self.enable_bias_detection:
                metrics.bias_flags = await self._detect_bias(metrics)

            # Store event for future analysis
            self.recent_events.append(metrics)
            if len(self.recent_events) > self.max_recent_events:
                self.recent_events.pop(0)

            # Generate Guardian alert if needed
            alert_triggered = await self._check_alert_conditions(metrics)

            # Create result
            result = {
                "drift_score": metrics.drift_score,
                "constitutional_valid": metrics.constitutional_valid,
                "bias_flags": metrics.bias_flags,
                "alert_triggered": alert_triggered,
                "recommendations": await self._generate_recommendations(metrics),
                "glyph_encoding": await self._create_auth_glyph(metrics),
                "guardian_status": ("monitoring" if metrics.drift_score < self.drift_threshold else "alert"),
            }

            # Log to audit trail
            if self.audit_logger:
                await self._log_to_audit_trail(metrics, result)

            # Integrate with Guardian System
            if self.guardian_system and alert_triggered:
                await self._trigger_guardian_intervention(metrics, result)

            return result

        except Exception as e:
            logger.error(f"Error monitoring auth event: {e}")
            return {
                "error": str(e),
                "drift_score": 1.0,  # High drift score on error
                "constitutional_valid": False,
                "bias_flags": ["monitoring_error"],
                "alert_triggered": True,
                "guardian_status": "error",
            }

    async def _calculate_drift_score(self, metrics: AuthDriftMetrics) -> float:
        """Calculate drift score for authentication event"""
        try:
            # Base drift calculation
            drift_score = 0.0

            # Check for unusual patterns
            if metrics.event_type == AuthEventType.LOGIN_FAILURE:
                recent_failures = [
                    e
                    for e in self.recent_events
                    if e.user_id == metrics.user_id
                    and e.event_type == AuthEventType.LOGIN_FAILURE
                    and e.timestamp > datetime.now() - timedelta(hours=1)
                ]

                if len(recent_failures) > 5:
                    drift_score += 0.3  # Multiple failures indicate potential issue

            # Check for tier inconsistencies
            if metrics.event_type == AuthEventType.TIER_ASSIGNMENT:
                user_history = [e for e in self.recent_events if e.user_id == metrics.user_id]
                if user_history:
                    last_tier = user_history[-1].tier_level
                    if last_tier != metrics.tier_level:
                        # Tier change - check if justified
                        tier_changes = len([e for e in user_history if e.event_type == AuthEventType.TIER_ASSIGNMENT])
                        if tier_changes > 3:  # Frequent tier changes
                            drift_score += 0.4

            # Check for geographical anomalies
            ip_address = metrics.ip_address
            if ip_address:
                recent_ips = [
                    e.ip_address
                    for e in self.recent_events
                    if e.user_id == metrics.user_id and e.timestamp > datetime.now() - timedelta(days=1)
                ]
                unique_ips = len(set(recent_ips))
                if unique_ips > 10:  # Too many different IPs
                    drift_score += 0.2

            # Constitutional violations increase drift
            if not metrics.constitutional_valid:
                drift_score += 0.5

            # Bias flags increase drift
            if metrics.bias_flags:
                drift_score += 0.1 * len(metrics.bias_flags)

            return min(drift_score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.error(f"Error calculating drift score: {e}")
            return 1.0  # High drift on error

    async def _validate_constitutional_principles(self, metrics: AuthDriftMetrics) -> tuple[bool, list[str]]:
        """Validate authentication event against constitutional AI principles"""
        try:
            # Convert metrics to event dict for validation
            event_dict = {
                "event_type": metrics.event_type.value,
                "user_id": metrics.user_id,
                "tier": metrics.tier_level,
                "outcome": metrics.outcome,
                "user_profile": metrics.metadata.get("user_profile", {}),
                "reasoning": metrics.metadata.get("reasoning"),
                "security_risk_score": metrics.metadata.get("security_risk_score", 0),
                "forced_logout": metrics.metadata.get("forced_logout", False),
                "user_initiated": metrics.metadata.get("user_initiated", True),
                "metadata": metrics.metadata,
            }

            return self.constitutional_principles.validate(event_dict)

        except Exception as e:
            logger.error(f"Error validating constitutional principles: {e}")
            return False, [f"validation_error: {e!s}"]

    async def _detect_bias(self, metrics: AuthDriftMetrics) -> list[str]:
        """Detect potential bias in authentication decisions"""
        bias_flags = []

        try:
            # Geographic bias detection
            if await self._check_geographic_bias(metrics):
                bias_flags.append("geographic_bias")

            # Temporal bias detection
            if await self._check_temporal_bias(metrics):
                bias_flags.append("temporal_bias")

            # Access pattern bias
            if await self._check_access_pattern_bias(metrics):
                bias_flags.append("access_pattern_bias")

            # Tier assignment bias
            if await self._check_tier_assignment_bias(metrics):
                bias_flags.append("tier_assignment_bias")

        except Exception as e:
            logger.error(f"Error detecting bias: {e}")
            bias_flags.append("bias_detection_error")

        return bias_flags

    async def _check_geographic_bias(self, metrics: AuthDriftMetrics) -> bool:
        """Check for geographic bias in authentication decisions"""
        try:
            # Look for patterns where users from certain regions get different treatment
            user_region = metrics.metadata.get("geographic_region")
            if not user_region:
                return False

            # Check if users from this region have different success rates
            regional_events = [e for e in self.recent_events if e.metadata.get("geographic_region") == user_region]

            if len(regional_events) < 10:  # Need sufficient data
                return False

            regional_success_rate = len([e for e in regional_events if e.outcome == "success"]) / len(regional_events)

            # Compare with global success rate
            all_events = [e for e in self.recent_events if e.event_type == metrics.event_type]
            global_success_rate = len([e for e in all_events if e.outcome == "success"]) / len(all_events)

            # Flag if regional rate is significantly different
            return abs(regional_success_rate - global_success_rate) > 0.2

        except Exception:
            return False

    async def _check_temporal_bias(self, metrics: AuthDriftMetrics) -> bool:
        """Check for temporal bias in authentication decisions"""
        try:
            # Check if decisions vary significantly by time of day/week
            current_hour = metrics.timestamp.hour

            # Get events from same hour in recent history
            same_hour_events = [
                e for e in self.recent_events if e.timestamp.hour == current_hour and e.event_type == metrics.event_type
            ]

            if len(same_hour_events) < 5:
                return False

            # Check success rate for this hour vs others
            same_hour_success = len([e for e in same_hour_events if e.outcome == "success"]) / len(same_hour_events)

            other_hour_events = [
                e for e in self.recent_events if e.timestamp.hour != current_hour and e.event_type == metrics.event_type
            ]

            if len(other_hour_events) == 0:
                return False

            other_hour_success = len([e for e in other_hour_events if e.outcome == "success"]) / len(other_hour_events)

            return abs(same_hour_success - other_hour_success) > 0.3

        except Exception:
            return False

    async def _check_access_pattern_bias(self, metrics: AuthDriftMetrics) -> bool:
        """Check for bias in access patterns"""
        try:
            if metrics.event_type != AuthEventType.SCOPE_CHECK:
                return False

            requested_scope = metrics.metadata.get("requested_scope")
            if not requested_scope:
                return False

            # Check if certain user tiers are disproportionately denied
            tier_denials = {}
            scope_events = [
                e
                for e in self.recent_events
                if e.event_type == AuthEventType.SCOPE_CHECK and e.metadata.get("requested_scope") == requested_scope
            ]

            for event in scope_events:
                tier = event.tier_level
                if tier not in tier_denials:
                    tier_denials[tier] = {"total": 0, "denied": 0}

                tier_denials[tier]["total"] += 1
                if event.outcome == "denied":
                    tier_denials[tier]["denied"] += 1

            # Check for unusual denial patterns
            for stats in tier_denials.values():
                if stats["total"] >= 5:  # Sufficient data
                    denial_rate = stats["denied"] / stats["total"]
                    if denial_rate > 0.8:  # High denial rate
                        return True

            return False

        except Exception:
            return False

    async def _check_tier_assignment_bias(self, metrics: AuthDriftMetrics) -> bool:
        """Check for bias in tier assignments"""
        try:
            if metrics.event_type != AuthEventType.TIER_ASSIGNMENT:
                return False

            # Check if similar users get different tier assignments
            user_profile = metrics.metadata.get("user_profile", {})

            # Find users with similar profiles
            similar_users = []
            for event in self.recent_events:
                if event.event_type == AuthEventType.TIER_ASSIGNMENT and event.user_id != metrics.user_id:
                    other_profile = event.metadata.get("user_profile", {})
                    similarity = self._calculate_profile_similarity(user_profile, other_profile)

                    if similarity > 0.8:  # High similarity
                        similar_users.append(event)

            if len(similar_users) < 3:  # Need sufficient comparisons
                return False

            # Check if tier assignments are consistent
            assigned_tiers = [event.tier_level for event in similar_users]
            unique_tiers = set(assigned_tiers)

            # Flag if too much variation in tier assignments for similar users
            return len(unique_tiers) > 2

        except Exception:
            return False

    def _calculate_profile_similarity(self, profile1: dict, profile2: dict) -> float:
        """Calculate similarity between user profiles"""
        try:
            # Simple similarity calculation based on shared attributes
            keys1 = set(profile1.keys())
            keys2 = set(profile2.keys())

            common_keys = keys1.intersection(keys2)
            if not common_keys:
                return 0.0

            matches = 0
            for key in common_keys:
                if profile1[key] == profile2[key]:
                    matches += 1

            return matches / len(common_keys)

        except Exception:
            return 0.0

    async def _check_alert_conditions(self, metrics: AuthDriftMetrics) -> bool:
        """Check if alert conditions are met"""
        # Alert on high drift
        if metrics.drift_score >= self.drift_threshold:
            return True

        # Alert on constitutional violations
        if not metrics.constitutional_valid:
            return True

        # Alert on bias detection
        if metrics.bias_flags:
            return True

        # Alert on security anomalies
        return metrics.metadata.get("security_risk_score", 0) > 0.8

    async def _generate_recommendations(self, metrics: AuthDriftMetrics) -> list[str]:
        """Generate recommendations based on monitoring results"""
        recommendations = []

        if metrics.drift_score >= self.drift_threshold:
            recommendations.append("Review authentication patterns for unusual activity")

        if not metrics.constitutional_valid:
            recommendations.append("Ensure authentication decisions align with constitutional AI principles")

        if "geographic_bias" in metrics.bias_flags:
            recommendations.append("Review geographic access patterns for potential discrimination")

        if "temporal_bias" in metrics.bias_flags:
            recommendations.append("Investigate time-based variations in authentication decisions")

        if "tier_assignment_bias" in metrics.bias_flags:
            recommendations.append("Audit tier assignment process for fairness and consistency")

        if metrics.metadata.get("security_risk_score", 0) > 0.7:
            recommendations.append("Implement additional security measures for high-risk authentication attempts")

        if not recommendations:
            recommendations.append("Continue monitoring authentication patterns")

        return recommendations

    async def _create_auth_glyph(self, metrics: AuthDriftMetrics) -> Optional[str]:
        """Create GLYPH encoding for authentication event"""
        try:
            if not self.glyph_engine:
                return None

            # Create concept for GLYPH encoding
            concept = f"auth_{metrics.event_type.value}_{metrics.outcome}"

            # Add emotional context based on outcome
            emotion = None
            if metrics.outcome == "success":
                emotion = {"valence": 0.8, "arousal": 0.3, "dominance": 0.6}
            elif metrics.outcome == "failure":
                emotion = {"valence": 0.2, "arousal": 0.7, "dominance": 0.3}
            elif metrics.outcome == "denied":
                emotion = {"valence": 0.1, "arousal": 0.5, "dominance": 0.8}

            # Encode concept
            glyph_repr = self.glyph_engine.encode_concept(concept, emotion)

            return glyph_repr

        except Exception as e:
            logger.error(f"Error creating auth GLYPH: {e}")
            return None

    async def _log_to_audit_trail(self, metrics: AuthDriftMetrics, result: dict[str, Any]) -> None:
        """Log authentication monitoring to audit trail"""
        try:
            if not self.audit_logger:
                return

            audit_entry = {
                "timestamp": metrics.timestamp.isoformat(),
                "event_type": "auth_guardian_monitoring",
                "user_id": metrics.user_id,
                "tier_level": metrics.tier_level,
                "auth_event": metrics.event_type.value,
                "outcome": metrics.outcome,
                "drift_score": metrics.drift_score,
                "constitutional_valid": metrics.constitutional_valid,
                "bias_flags": metrics.bias_flags,
                "alert_triggered": result["alert_triggered"],
                "guardian_status": result["guardian_status"],
                "recommendations": result["recommendations"],
                "glyph_encoding": result["glyph_encoding"],
                "ip_address": metrics.ip_address,
                "user_agent": metrics.user_agent,
                "metadata": metrics.metadata,
            }

            await self.audit_logger.log(audit_entry)

        except Exception as e:
            logger.error(f"Error logging to audit trail: {e}")

    async def _trigger_guardian_intervention(self, metrics: AuthDriftMetrics, result: dict[str, Any]) -> None:
        """Trigger Guardian System intervention for high-risk events"""
        try:
            if not self.guardian_system:
                return

            # Prepare Guardian action data
            action_data = {
                "type": "authentication_alert",
                "severity": "high" if metrics.drift_score >= 0.8 else "medium",
                "user_id": metrics.user_id,
                "tier_level": metrics.tier_level,
                "drift_score": metrics.drift_score,
                "constitutional_violations": not metrics.constitutional_valid,
                "bias_flags": metrics.bias_flags,
                "recommendations": result["recommendations"],
                "timestamp": metrics.timestamp.isoformat(),
                "context": metrics.metadata,
            }

            # Validate through Guardian System
            guardian_result = await self.guardian_system.validate_action(action_data)

            logger.info(f"Guardian intervention triggered for user {metrics.user_id}: {guardian_result}")

        except Exception as e:
            logger.error(f"Error triggering Guardian intervention: {e}")

    def get_drift_summary(self) -> dict[str, Any]:
        """Get summary of authentication drift metrics"""
        try:
            if not self.recent_events:
                return {
                    "total_events": 0,
                    "average_drift": 0.0,
                    "high_drift_events": 0,
                    "constitutional_violations": 0,
                    "bias_detections": 0,
                    "status": "no_data",
                }

            total_events = len(self.recent_events)
            total_drift = sum(e.drift_score for e in self.recent_events)
            average_drift = total_drift / total_events

            high_drift_events = len([e for e in self.recent_events if e.drift_score >= self.drift_threshold])
            constitutional_violations = len([e for e in self.recent_events if not e.constitutional_valid])
            bias_detections = len([e for e in self.recent_events if e.bias_flags])

            return {
                "total_events": total_events,
                "average_drift": round(average_drift, 3),
                "high_drift_events": high_drift_events,
                "constitutional_violations": constitutional_violations,
                "bias_detections": bias_detections,
                "drift_threshold": self.drift_threshold,
                "status": "alert" if high_drift_events > 0 else "monitoring",
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating drift summary: {e}")
            return {"error": str(e), "status": "error"}


# Export main class
__all__ = [
    "AuthDriftMetrics",
    "AuthEventType",
    "AuthenticationGuardian",
    "ConstitutionalAuthPrinciples",
]
