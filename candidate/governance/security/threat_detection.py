import logging
from datetime import timezone
import streamlit as st
logger = logging.getLogger(__name__)
"""
Advanced Threat Detection System for LUKHAS AI

This module provides comprehensive threat detection and response
capabilities including behavioral analysis, anomaly detection,
pattern recognition, and automated threat response integrated
with Constellation Framework and Guardian System.

Features:
- Real-time behavioral threat detection
- Machine learning-based anomaly detection
- Pattern recognition for attack identification
- Automated threat response and mitigation
- Integration with Constellation Framework (⚛️🧠🛡️)
- Constitutional AI threat assessment
- Multi-vector threat analysis
- Forensic data collection and analysis
- Threat intelligence integration

#TAG:governance
#TAG:security
#TAG:threat_detection
#TAG:anomaly_detection
#TAG:constellation
#TAG:guardian
"""

import asyncio
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from lukhas.core.common import get_logger

logger = get_logger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ThreatType(Enum):
    """Types of security threats"""

    # Authentication threats
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_STUFFING = "credential_stuffing"
    ACCOUNT_TAKEOVER = "account_takeover"

    # Access threats
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ACCESS_PATTERN_ANOMALY = "access_pattern_anomaly"

    # Data threats
    DATA_EXFILTRATION = "data_exfiltration"
    DATA_MANIPULATION = "data_manipulation"
    PRIVACY_VIOLATION = "privacy_violation"

    # System threats
    SYSTEM_ABUSE = "system_abuse"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    MALICIOUS_CODE = "malicious_code"

    # AI/ML specific threats
    AI_MANIPULATION = "ai_manipulation"
    MODEL_POISONING = "model_poisoning"
    PROMPT_INJECTION = "prompt_injection"
    ADVERSARIAL_ATTACK = "adversarial_attack"

    # Constitutional threats
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    ETHICAL_BYPASS = "ethical_bypass"
    GUARDRAIL_EVASION = "guardrail_evasion"

    # Constellation Framework threats
    IDENTITY_SPOOFING = "identity_spoofing"
    CONSCIOUSNESS_MANIPULATION = "consciousness_manipulation"
    GUARDIAN_BYPASS = "guardian_bypass"

    # Behavioral threats
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    INSIDER_THREAT = "insider_threat"
    SOCIAL_ENGINEERING = "social_engineering"


class ThreatStatus(Enum):
    """Status of threat incidents"""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class ResponseAction(Enum):
    """Automated response actions"""

    MONITOR = "monitor"
    ALERT = "alert"
    BLOCK_IP = "block_ip"
    SUSPEND_USER = "suspend_user"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"
    TERMINATE_SESSION = "terminate_session"
    INCREASE_MONITORING = "increase_monitoring"
    REQUEST_ADDITIONAL_AUTH = "request_additional_auth"
    EMERGENCY_LOCKDOWN = "emergency_lockdown"


@dataclass
class ThreatIndicator:
    """Represents a threat indicator"""

    indicator_id: str
    indicator_type: str
    value: str
    confidence: float  # 0.0 to 1.0
    severity: ThreatLevel
    source: str
    description: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    count: int = 1
    tags: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatEvent:
    """Represents a detected threat event"""

    event_id: str
    timestamp: datetime
    threat_type: ThreatType
    threat_level: ThreatLevel
    confidence: float

    # Event details
    title: str
    description: str
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    target_resource: Optional[str] = None

    # Technical details
    indicators: list[ThreatIndicator] = field(default_factory=list)
    attack_vector: Optional[str] = None
    affected_systems: list[str] = field(default_factory=list)

    # Context
    user_agent: Optional[str] = None
    geo_location: Optional[str] = None
    behavioral_profile: dict[str, Any] = field(default_factory=dict)

    # Constellation Framework context
    identity_context: dict[str, Any] = field(default_factory=dict)  # ⚛️
    consciousness_context: dict[str, Any] = field(default_factory=dict)  # 🧠
    guardian_context: dict[str, Any] = field(default_factory=dict)  # 🛡️

    # Response
    status: ThreatStatus = ThreatStatus.DETECTED
    automated_actions: list[ResponseAction] = field(default_factory=list)
    manual_actions: list[str] = field(default_factory=list)

    # Forensics
    evidence: list[dict[str, Any]] = field(default_factory=list)
    forensic_data: dict[str, Any] = field(default_factory=dict)

    # Resolution
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    false_positive: bool = False


@dataclass
class UserBehaviorProfile:
    """Behavioral profile for anomaly detection"""

    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Authentication patterns
    typical_login_hours: list[int] = field(default_factory=list)
    typical_login_locations: set[str] = field(default_factory=set)
    average_session_duration: float = 0.0
    typical_user_agents: set[str] = field(default_factory=set)

    # Access patterns
    typical_resources: set[str] = field(default_factory=set)
    access_frequency: dict[str, float] = field(default_factory=dict)
    permission_usage: dict[str, int] = field(default_factory=dict)

    # Behavioral metrics
    typing_pattern: Optional[dict[str, float]] = None
    navigation_pattern: list[str] = field(default_factory=list)
    error_rate: float = 0.0

    # Statistical baselines
    baseline_metrics: dict[str, float] = field(default_factory=dict)
    anomaly_threshold: float = 2.0  # Standard deviations

    # Constellation Framework profile
    identity_confidence: float = 1.0  # ⚛️
    consciousness_interaction: float = 0.5  # 🧠
    guardian_trust_score: float = 1.0  # 🛡️


class BehavioralAnalyzer:
    """Analyzes user behavior for anomaly detection"""

    def __init__(self):
        self.user_profiles: dict[str, UserBehaviorProfile] = {}
        self.learning_period = timedelta(days=30)
        self.min_observations = 10

        logger.info("🔍 Behavioral Analyzer initialized")

    async def analyze_user_activity(self, user_id: str, activity_data: dict[str, Any]) -> tuple[float, list[str]]:
        """
        Analyze user activity for behavioral anomalies

        Returns:
            (anomaly_score, anomaly_details)
        """

        # Get or create user profile
        profile = self.user_profiles.get(user_id)
        if not profile:
            profile = UserBehaviorProfile(user_id=user_id)
            self.user_profiles[user_id] = profile

        anomaly_score = 0.0
        anomaly_details = []

        # Analyze different aspects of behavior
        temporal_score, temporal_details = await self._analyze_temporal_patterns(profile, activity_data)
        anomaly_score += temporal_score
        anomaly_details.extend(temporal_details)

        access_score, access_details = await self._analyze_access_patterns(profile, activity_data)
        anomaly_score += access_score
        anomaly_details.extend(access_details)

        technical_score, technical_details = await self._analyze_technical_patterns(profile, activity_data)
        anomaly_score += technical_score
        anomaly_details.extend(technical_details)

        # Constellation Framework behavioral analysis
        constellation_score, constellation_details = await self._analyze_trinity_behavior(profile, activity_data)
        anomaly_score += constellation_score
        anomaly_details.extend(constellation_details)

        # Update profile with new data
        await self._update_user_profile(profile, activity_data)

        # Normalize anomaly score (0.0 to 1.0)
        normalized_score = min(1.0, anomaly_score / 4.0)  # Divided by number of analysis types

        return normalized_score, anomaly_details

    async def _analyze_temporal_patterns(
        self, profile: UserBehaviorProfile, activity_data: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Analyze temporal behavioral patterns"""

        score = 0.0
        details = []

        # Check login time anomaly
        current_hour = datetime.now(timezone.utc).hour
        if profile.typical_login_hours and current_hour not in profile.typical_login_hours:
            # Calculate how far from typical hours
            min_distance = min(abs(current_hour - h) for h in profile.typical_login_hours)
            if min_distance > 3:  # More than 3 hours from typical
                score += 0.3
                details.append(f"Login at unusual hour: {current_hour}")

        # Check session duration
        session_duration = activity_data.get("session_duration", 0)
        if profile.average_session_duration > 0 and session_duration > 0:
            duration_ratio = session_duration / profile.average_session_duration
            if duration_ratio > 3.0 or duration_ratio < 0.3:  # 3x longer or 3x shorter
                score += 0.2
                details.append(
                    f"Unusual session duration: {session_duration:.1f}s vs avg {profile.average_session_duration:.1f}s"
                )

        return score, details

    async def _analyze_access_patterns(
        self, profile: UserBehaviorProfile, activity_data: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Analyze resource access patterns"""

        score = 0.0
        details = []

        accessed_resources = set(activity_data.get("accessed_resources", []))

        if profile.typical_resources and accessed_resources:
            # Check for access to unusual resources
            unusual_resources = accessed_resources - profile.typical_resources
            if unusual_resources:
                score += 0.4 * min(1.0, len(unusual_resources) / 3)
                details.append(f"Access to unusual resources: {', '.join(list(unusual_resources}[:3])}")  # noqa: invalid-syntax  # TODO: Expected ,, found }

            # Check for bulk access (potential data exfiltration)
            if len(accessed_resources) > len(profile.typical_resources) * 2:
                score += 0.3
                details.append(f"Unusual volume of resource access: {len(accessed_resources)}")

        return score, details

    async def _analyze_technical_patterns(
        self, profile: UserBehaviorProfile, activity_data: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Analyze technical behavioral patterns"""

        score = 0.0
        details = []

        # Check user agent anomaly
        current_user_agent = activity_data.get("user_agent")
        if current_user_agent and profile.typical_user_agents:
            if current_user_agent not in profile.typical_user_agents:
                score += 0.2
                details.append("New user agent detected")

        # Check location anomaly (simplified)
        current_location = activity_data.get("geo_location")
        if current_location and profile.typical_login_locations:
            if current_location not in profile.typical_login_locations:
                score += 0.3
                details.append(f"Login from new location: {current_location}")

        # Check error rate anomaly
        current_error_rate = activity_data.get("error_rate", 0.0)
        if profile.error_rate > 0 and current_error_rate > profile.error_rate * 3:
            score += 0.2
            details.append(f"High error rate: {current_error_rate:.2f}")

        return score, details

    async def _analyze_trinity_behavior(
        self, profile: UserBehaviorProfile, activity_data: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Analyze Constellation Framework behavioral patterns"""

        score = 0.0
        details = []

        # ⚛️ Identity behavioral analysis
        identity_confidence = activity_data.get("identity_confidence", 1.0)
        if identity_confidence < profile.identity_confidence * 0.7:
            score += 0.3
            details.append(f"Identity confidence drop: {identity_confidence:.2f}")

        # 🧠 Consciousness interaction analysis
        consciousness_level = activity_data.get("consciousness_interaction", 0.5)
        baseline = profile.consciousness_interaction
        if abs(consciousness_level - baseline) > 0.3:
            score += 0.2
            details.append(f"Unusual consciousness interaction pattern: {consciousness_level:.2f}")

        # 🛡️ Guardian trust score analysis
        guardian_score = activity_data.get("guardian_trust_score", 1.0)
        if guardian_score < profile.guardian_trust_score * 0.8:
            score += 0.4
            details.append(f"Guardian trust score decline: {guardian_score:.2f}")

        return score, details

    async def _update_user_profile(self, profile: UserBehaviorProfile, activity_data: dict[str, Any]):
        """Update user behavioral profile with new activity data"""

        # Update temporal patterns
        current_hour = datetime.now(timezone.utc).hour
        if current_hour not in profile.typical_login_hours:
            profile.typical_login_hours.append(current_hour)
            # Keep only recent patterns (last 50 logins)
            if len(profile.typical_login_hours) > 50:
                profile.typical_login_hours = profile.typical_login_hours[-50:]

        # Update location patterns
        current_location = activity_data.get("geo_location")
        if current_location:
            profile.typical_login_locations.add(current_location)

        # Update user agent patterns
        user_agent = activity_data.get("user_agent")
        if user_agent:
            profile.typical_user_agents.add(user_agent)

        # Update session duration average
        session_duration = activity_data.get("session_duration", 0)
        if session_duration > 0:
            if profile.average_session_duration == 0:
                profile.average_session_duration = session_duration
            else:
                # Exponential moving average
                alpha = 0.1
                profile.average_session_duration = (
                    alpha * session_duration + (1 - alpha) * profile.average_session_duration
                )

        # Update resource access patterns
        accessed_resources = activity_data.get("accessed_resources", [])
        for resource in accessed_resources:
            profile.typical_resources.add(resource)
            profile.access_frequency[resource] = profile.access_frequency.get(resource, 0) + 1

        # Update Constellation Framework profiles
        if "identity_confidence" in activity_data:
            profile.identity_confidence = 0.9 * profile.identity_confidence + 0.1 * activity_data["identity_confidence"]

        if "consciousness_interaction" in activity_data:
            profile.consciousness_interaction = (
                0.9 * profile.consciousness_interaction + 0.1 * activity_data["consciousness_interaction"]
            )

        if "guardian_trust_score" in activity_data:
            profile.guardian_trust_score = (
                0.9 * profile.guardian_trust_score + 0.1 * activity_data["guardian_trust_score"]
            )

        profile.updated_at = datetime.now(timezone.utc)


class PatternRecognizer:
    """Recognizes attack patterns and threat signatures"""

    def __init__(self):
        self.attack_patterns = self._initialize_attack_patterns()
        self.event_history = deque(maxlen=10000)
        self.pattern_cache = {}

        logger.info("🎯 Pattern Recognizer initialized")

    def _initialize_attack_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize known attack patterns"""

        return {
            "brute_force": {
                "name": "Brute Force Attack",
                "description": "Multiple failed authentication attempts",
                "indicators": [
                    {"type": "failed_login_count", "threshold": 5, "window": 300},
                    {"type": "multiple_ips", "threshold": 3, "window": 600},
                ],
                "threat_type": ThreatType.BRUTE_FORCE,
                "confidence_threshold": 0.8,
            },
            "credential_stuffing": {
                "name": "Credential Stuffing",
                "description": "Automated login attempts with known credentials",
                "indicators": [
                    {"type": "rapid_login_attempts", "threshold": 10, "window": 60},
                    {"type": "diverse_user_agents", "threshold": 5, "window": 300},
                    {"type": "success_failure_ratio", "min_ratio": 0.1, "window": 300},
                ],
                "threat_type": ThreatType.CREDENTIAL_STUFFING,
                "confidence_threshold": 0.7,
            },
            "data_exfiltration": {
                "name": "Data Exfiltration",
                "description": "Unusual data access and download patterns",
                "indicators": [
                    {"type": "bulk_data_access", "threshold": 100, "window": 3600},
                    {"type": "off_hours_access", "unusual_hours": [0, 1, 2, 3, 4, 5]},
                    {
                        "type": "download_volume",
                        "threshold": 10485760,
                        "window": 1800,
                    },  # 10MB
                ],
                "threat_type": ThreatType.DATA_EXFILTRATION,
                "confidence_threshold": 0.75,
            },
            "privilege_escalation": {
                "name": "Privilege Escalation",
                "description": "Attempts to gain higher privileges",
                "indicators": [
                    {"type": "admin_access_attempts", "threshold": 3, "window": 300},
                    {"type": "permission_changes", "threshold": 2, "window": 600},
                    {"type": "system_config_access", "threshold": 1, "window": 300},
                ],
                "threat_type": ThreatType.PRIVILEGE_ESCALATION,
                "confidence_threshold": 0.85,
            },
            "ai_manipulation": {
                "name": "AI System Manipulation",
                "description": "Attempts to manipulate AI behavior",
                "indicators": [
                    {
                        "type": "prompt_injection_attempts",
                        "threshold": 3,
                        "window": 300,
                    },
                    {
                        "type": "constitutional_violations",
                        "threshold": 2,
                        "window": 600,
                    },
                    {
                        "type": "guardrail_bypass_attempts",
                        "threshold": 1,
                        "window": 300,
                    },
                ],
                "threat_type": ThreatType.AI_MANIPULATION,
                "confidence_threshold": 0.9,
            },
            "insider_threat": {
                "name": "Insider Threat",
                "description": "Suspicious behavior from legitimate users",
                "indicators": [
                    {"type": "after_hours_activity", "threshold": 5, "window": 86400},
                    {
                        "type": "unusual_resource_access",
                        "threshold": 10,
                        "window": 3600,
                    },
                    {"type": "data_hoarding", "threshold": 50, "window": 86400},
                ],
                "threat_type": ThreatType.INSIDER_THREAT,
                "confidence_threshold": 0.7,
            },
        }

    async def analyze_events(self, events: list[dict[str, Any]]) -> list[ThreatEvent]:
        """Analyze events for threat patterns"""

        detected_threats = []

        # Add events to history
        for event in events:
            self.event_history.append(event)

        # Check each pattern
        for pattern_id, pattern in self.attack_patterns.items():
            threat_events = await self._check_pattern(pattern_id, pattern, events)
            detected_threats.extend(threat_events)

        return detected_threats

    async def _check_pattern(
        self,
        pattern_id: str,
        pattern: dict[str, Any],
        recent_events: list[dict[str, Any]],
    ) -> list[ThreatEvent]:
        """Check if events match a specific attack pattern"""

        threats = []

        # Aggregate events by time windows and analyze indicators
        pattern_matches = 0
        total_indicators = len(pattern["indicators"])
        evidence = []

        for indicator in pattern["indicators"]:
            match_result = await self._check_indicator(indicator, recent_events)
            if match_result["matched"]:
                pattern_matches += 1
                evidence.append(match_result)

        # Calculate confidence based on matching indicators
        confidence = pattern_matches / total_indicators

        if confidence >= pattern["confidence_threshold"]:
            # Create threat event
            threat_event = ThreatEvent(
                event_id=f"threat_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                threat_type=pattern["threat_type"],
                threat_level=self._calculate_threat_level(confidence),
                confidence=confidence,
                title=pattern["name"],
                description=pattern["description"],
                evidence=evidence,
            )

            # Add pattern-specific context
            threat_event.attack_vector = pattern_id

            threats.append(threat_event)

            logger.warning(f"⚠️ Threat pattern detected: {pattern['name']} (confidence: {confidence:.2f})")

        return threats

    async def _check_indicator(self, indicator: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
        """Check if events match a specific indicator"""

        indicator_type = indicator["type"]

        if indicator_type == "failed_login_count":
            return await self._check_failed_login_indicator(indicator, events)
        elif indicator_type == "rapid_login_attempts":
            return await self._check_rapid_login_indicator(indicator, events)
        elif indicator_type == "bulk_data_access":
            return await self._check_bulk_access_indicator(indicator, events)
        elif indicator_type == "privilege_escalation_attempts":
            return await self._check_privilege_escalation_indicator(indicator, events)
        elif indicator_type == "prompt_injection_attempts":
            return await self._check_prompt_injection_indicator(indicator, events)
        else:
            # Generic threshold-based check
            return await self._check_generic_threshold(indicator, events)

    async def _check_failed_login_indicator(
        self, indicator: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check for failed login patterns"""

        threshold = indicator["threshold"]
        window = indicator["window"]
        current_time = time.time()

        # Count failed logins in time window
        failed_count = 0
        source_ips = set()

        for event in events:
            event_time = event.get("timestamp", current_time)
            if isinstance(event_time, str):
                # Parse timestamp if string
                event_time = datetime.fromisoformat(event_time).timestamp()

            if current_time - event_time <= window and event.get("event_type") == "login_failure":
                failed_count += 1
                if event.get("source_ip"):
                    source_ips.add(event["source_ip"])

        matched = failed_count >= threshold

        return {
            "matched": matched,
            "indicator_type": "failed_login_count",
            "value": failed_count,
            "threshold": threshold,
            "details": f"{failed_count} failed logins from {len(source_ips)} IPs in {window}s",
        }

    async def _check_rapid_login_indicator(
        self, indicator: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check for rapid login attempt patterns"""

        threshold = indicator["threshold"]
        window = indicator["window"]
        current_time = time.time()

        login_attempts = 0
        for event in events:
            event_time = event.get("timestamp", current_time)
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time).timestamp()

            if current_time - event_time <= window:
                if event.get("event_type") in ["login_success", "login_failure"]:
                    login_attempts += 1

        matched = login_attempts >= threshold

        return {
            "matched": matched,
            "indicator_type": "rapid_login_attempts",
            "value": login_attempts,
            "threshold": threshold,
            "details": f"{login_attempts} login attempts in {window}s",
        }

    async def _check_bulk_access_indicator(
        self, indicator: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check for bulk data access patterns"""

        threshold = indicator["threshold"]
        window = indicator["window"]
        current_time = time.time()

        access_count = 0
        resources = set()

        for event in events:
            event_time = event.get("timestamp", current_time)
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time).timestamp()

            if current_time - event_time <= window and event.get("event_type") == "data_access":
                access_count += 1
                if event.get("resource"):
                    resources.add(event["resource"])

        matched = access_count >= threshold

        return {
            "matched": matched,
            "indicator_type": "bulk_data_access",
            "value": access_count,
            "threshold": threshold,
            "details": f"{access_count} data accesses to {len(resources)} resources in {window}s",
        }

    async def _check_prompt_injection_indicator(
        self, indicator: dict[str, Any], events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Check for prompt injection attempt patterns"""

        threshold = indicator["threshold"]
        window = indicator["window"]
        current_time = time.time()

        injection_attempts = 0

        # Keywords that might indicate prompt injection
        injection_keywords = [
            "ignore",
            "system",
            "override",
            "bypass",
            "jailbreak",
            "forget",
            "pretend",
            "role",
            "instruction",
            "command",
        ]

        for event in events:
            event_time = event.get("timestamp", current_time)
            if isinstance(event_time, str):
                event_time = datetime.fromisoformat(event_time).timestamp()

            if current_time - event_time <= window and event.get("event_type") == "ai_interaction":
                content = event.get("content", "").lower()
                if any(keyword in content for keyword in injection_keywords):
                    injection_attempts += 1

        matched = injection_attempts >= threshold

        return {
            "matched": matched,
            "indicator_type": "prompt_injection_attempts",
            "value": injection_attempts,
            "threshold": threshold,
            "details": f"{injection_attempts} potential prompt injection attempts in {window}s",
        }

    async def _check_generic_threshold(self, indicator: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
        """Generic threshold-based indicator check"""

        return {
            "matched": False,
            "indicator_type": indicator["type"],
            "value": 0,
            "threshold": indicator.get("threshold", 0),
            "details": "Generic threshold check - not implemented",
        }

    def _calculate_threat_level(self, confidence: float) -> ThreatLevel:
        """Calculate threat level based on confidence"""

        if confidence >= 0.95:
            return ThreatLevel.EMERGENCY
        elif confidence >= 0.85:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.7:
            return ThreatLevel.HIGH
        elif confidence >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW


class ThreatResponseEngine:
    """Handles automated threat response and mitigation"""

    def __init__(self):
        self.response_rules = self._initialize_response_rules()
        self.active_responses = {}

        logger.info("🛡️ Threat Response Engine initialized")

    def _initialize_response_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize automated response rules"""

        return {
            "brute_force_response": {
                "triggers": [ThreatType.BRUTE_FORCE],
                "conditions": {"min_confidence": 0.8, "min_level": ThreatLevel.HIGH},
                "actions": [
                    ResponseAction.BLOCK_IP,
                    ResponseAction.ALERT,
                    ResponseAction.INCREASE_MONITORING,
                ],
                "cooldown": 3600,  # 1 hour
            },
            "data_exfiltration_response": {
                "triggers": [ThreatType.DATA_EXFILTRATION],
                "conditions": {"min_confidence": 0.75, "min_level": ThreatLevel.HIGH},
                "actions": [
                    ResponseAction.SUSPEND_USER,
                    ResponseAction.ALERT,
                    ResponseAction.ESCALATE,
                    ResponseAction.QUARANTINE,
                ],
                "cooldown": 7200,  # 2 hours
            },
            "privilege_escalation_response": {
                "triggers": [ThreatType.PRIVILEGE_ESCALATION],
                "conditions": {"min_confidence": 0.85, "min_level": ThreatLevel.HIGH},
                "actions": [
                    ResponseAction.TERMINATE_SESSION,
                    ResponseAction.ALERT,
                    ResponseAction.ESCALATE,
                    ResponseAction.INCREASE_MONITORING,
                ],
                "cooldown": 1800,  # 30 minutes
            },
            "ai_manipulation_response": {
                "triggers": [ThreatType.AI_MANIPULATION, ThreatType.PROMPT_INJECTION],
                "conditions": {
                    "min_confidence": 0.9,
                    "min_level": ThreatLevel.CRITICAL,
                },
                "actions": [
                    ResponseAction.QUARANTINE,
                    ResponseAction.ALERT,
                    ResponseAction.ESCALATE,
                    ResponseAction.REQUEST_ADDITIONAL_AUTH,
                ],
                "cooldown": 1800,
            },
            "constitutional_violation_response": {
                "triggers": [
                    ThreatType.CONSTITUTIONAL_VIOLATION,
                    ThreatType.ETHICAL_BYPASS,
                ],
                "conditions": {
                    "min_confidence": 0.95,
                    "min_level": ThreatLevel.EMERGENCY,
                },
                "actions": [
                    ResponseAction.EMERGENCY_LOCKDOWN,
                    ResponseAction.ALERT,
                    ResponseAction.ESCALATE,
                ],
                "cooldown": 0,  # No cooldown for constitutional violations
            },
            "constellation_threat_response": {
                "triggers": [
                    ThreatType.IDENTITY_SPOOFING,
                    ThreatType.CONSCIOUSNESS_MANIPULATION,
                    ThreatType.GUARDIAN_BYPASS,
                ],
                "conditions": {"min_confidence": 0.8, "min_level": ThreatLevel.HIGH},
                "actions": [
                    ResponseAction.SUSPEND_USER,
                    ResponseAction.ALERT,
                    ResponseAction.ESCALATE,
                    ResponseAction.INCREASE_MONITORING,
                ],
                "cooldown": 3600,
            },
        }

    async def respond_to_threat(self, threat_event: ThreatEvent) -> list[str]:
        """Execute automated response to threat"""

        executed_actions = []

        # Find applicable response rules
        for rule_id, rule in self.response_rules.items():
            if await self._should_apply_rule(rule, threat_event):
                actions = await self._execute_response_rule(rule, threat_event)
                executed_actions.extend(actions)

                # Track active response
                self.active_responses[threat_event.event_id] = {
                    "rule_id": rule_id,
                    "timestamp": datetime.now(timezone.utc),
                    "actions": actions,
                }

        # Update threat event with actions
        threat_event.automated_actions = [
            ResponseAction(action) for action in executed_actions if action in [a.value for a in ResponseAction]
        ]

        return executed_actions

    async def _should_apply_rule(self, rule: dict[str, Any], threat_event: ThreatEvent) -> bool:
        """Check if response rule should be applied"""

        # Check if threat type matches
        if threat_event.threat_type not in rule["triggers"]:
            return False

        conditions = rule["conditions"]

        # Check confidence threshold
        if threat_event.confidence < conditions.get("min_confidence", 0.0):
            return False

        # Check threat level
        min_level = conditions.get("min_level", ThreatLevel.LOW)
        level_order = {
            ThreatLevel.LOW: 0,
            ThreatLevel.MEDIUM: 1,
            ThreatLevel.HIGH: 2,
            ThreatLevel.CRITICAL: 3,
            ThreatLevel.EMERGENCY: 4,
        }

        if level_order[threat_event.threat_level] < level_order[min_level]:
            return False

        # Check cooldown period
        cooldown = rule.get("cooldown", 0)
        if cooldown > 0:
            # Check if similar response was recently executed
            recent_responses = [
                r
                for r in self.active_responses.values()
                if (datetime.now(timezone.utc) - r["timestamp"]).total_seconds() < cooldown
            ]
            if recent_responses:
                return False

        return True

    async def _execute_response_rule(self, rule: dict[str, Any], threat_event: ThreatEvent) -> list[str]:
        """Execute actions from response rule"""

        executed_actions = []

        for action in rule["actions"]:
            try:
                result = await self._execute_response_action(action, threat_event)
                if result:
                    executed_actions.append(action.value)
                    logger.info(f"✅ Executed response action: {action.value} for threat {threat_event.event_id}")

            except Exception as e:
                logger.error(f"❌ Failed to execute response action {action.value}: {e}")

        return executed_actions

    async def _execute_response_action(self, action: ResponseAction, threat_event: ThreatEvent) -> bool:
        """Execute a specific response action"""

        if action == ResponseAction.ALERT:
            return await self._send_alert(threat_event)

        elif action == ResponseAction.BLOCK_IP:
            return await self._block_ip(threat_event.source_ip)

        elif action == ResponseAction.SUSPEND_USER:
            return await self._suspend_user(threat_event.user_id)

        elif action == ResponseAction.TERMINATE_SESSION:
            return await self._terminate_session(threat_event.session_id)

        elif action == ResponseAction.ESCALATE:
            return await self._escalate_threat(threat_event)

        elif action == ResponseAction.QUARANTINE:
            return await self._quarantine_threat(threat_event)

        elif action == ResponseAction.INCREASE_MONITORING:
            return await self._increase_monitoring(threat_event)

        elif action == ResponseAction.REQUEST_ADDITIONAL_AUTH:
            return await self._request_additional_auth(threat_event)

        elif action == ResponseAction.EMERGENCY_LOCKDOWN:
            return await self._emergency_lockdown(threat_event)

        else:
            logger.warning(f"Unknown response action: {action}")
            return False

    async def _send_alert(self, threat_event: ThreatEvent) -> bool:
        """Send security alert"""
        logger.critical(f"🚨 SECURITY ALERT: {threat_event.title} (ID: {threat_event.event_id})")
        # In production: send to SIEM, security team, etc.
        return True

    async def _block_ip(self, ip_address: Optional[str]) -> bool:
        """Block IP address"""
        if not ip_address:
            return False

        logger.warning(f"🚫 Blocking IP address: {ip_address}")
        # In production: integrate with firewall/WAF
        return True

    async def _suspend_user(self, user_id: Optional[str]) -> bool:
        """Suspend user account"""
        if not user_id:
            return False

        logger.warning(f"🔒 Suspending user: {user_id}")
        # In production: integrate with user management system
        return True

    async def _terminate_session(self, session_id: Optional[str]) -> bool:
        """Terminate user session"""
        if not session_id:
            return False

        logger.warning(f"🔐 Terminating session: {session_id}")
        # In production: integrate with session manager
        return True

    async def _escalate_threat(self, threat_event: ThreatEvent) -> bool:
        """Escalate threat to security team"""
        logger.critical(f"🚨 ESCALATING THREAT: {threat_event.title}")
        # In production: create incident ticket, notify security team
        return True

    async def _quarantine_threat(self, threat_event: ThreatEvent) -> bool:
        """Quarantine threat for analysis"""
        logger.warning(f"🔬 QUARANTINING THREAT: {threat_event.event_id}")
        # In production: isolate affected systems/data
        return True

    async def _increase_monitoring(self, threat_event: ThreatEvent) -> bool:
        """Increase monitoring for affected entities"""
        logger.info(f"👁️ INCREASING MONITORING for threat: {threat_event.event_id}")
        # In production: adjust monitoring rules, increase logging
        return True

    async def _request_additional_auth(self, threat_event: ThreatEvent) -> bool:
        """Request additional authentication"""
        logger.info(f"🔐 REQUESTING ADDITIONAL AUTH for threat: {threat_event.event_id}")
        # In production: trigger MFA challenge, additional verification
        return True

    async def _emergency_lockdown(self, threat_event: ThreatEvent) -> bool:
        """Execute emergency system lockdown"""
        logger.critical(f"🚨 EMERGENCY LOCKDOWN triggered by threat: {threat_event.event_id}")
        # In production: emergency shutdown procedures
        return True


class ComprehensiveThreatDetection:
    """
    Main comprehensive threat detection system for LUKHAS AI

    Integrates behavioral analysis, pattern recognition, and automated
    response with Constellation Framework and constitutional AI principles
    for complete threat protection.
    """

    def __init__(self):
        self.behavioral_analyzer = BehavioralAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.response_engine = ThreatResponseEngine()

        # Threat tracking
        self.active_threats: dict[str, ThreatEvent] = {}
        self.threat_history: list[ThreatEvent] = []

        # System metrics
        self.metrics = {
            "threats_detected": 0,
            "threats_mitigated": 0,
            "false_positives": 0,
            "active_threats": 0,
            "response_actions": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # Start monitoring
        asyncio.create_task(self._continuous_monitoring())

        logger.info("🛡️ Comprehensive Threat Detection System initialized")

    async def analyze_activity(
        self,
        user_id: str,
        activity_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Analyze user activity for threats

        Returns:
            Analysis result with threat assessment
        """

        analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
        context = context or {}

        try:
            # Behavioral analysis
            (
                behavioral_score,
                behavioral_anomalies,
            ) = await self.behavioral_analyzer.analyze_user_activity(user_id, activity_data)

            # Pattern recognition
            events = [activity_data]  # Convert to event format
            pattern_threats = await self.pattern_recognizer.analyze_events(events)

            # Constellation Framework threat assessment
            constellation_assessment = await self._assess_trinity_threats(user_id, activity_data, context)

            # Combine threat indicators
            overall_threat_score = max(
                behavioral_score,
                max([t.confidence for t in pattern_threats], default=0.0),
                constellation_assessment.get("threat_score", 0.0),
            )

            # Create comprehensive result
            result = {
                "analysis_id": analysis_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "overall_threat_score": overall_threat_score,
                "threat_level": self._score_to_level(overall_threat_score).value,
                "behavioral_analysis": {
                    "anomaly_score": behavioral_score,
                    "anomalies": behavioral_anomalies,
                },
                "pattern_analysis": {
                    "threats_detected": len(pattern_threats),
                    "threat_types": [t.threat_type.value for t in pattern_threats],
                },
                "constellation_assessment": constellation_assessment,
                "recommendations": await self._generate_recommendations(
                    overall_threat_score, behavioral_anomalies, pattern_threats
                ),
            }

            # Execute automated response if needed
            if overall_threat_score > 0.7:  # High threat threshold
                for threat in pattern_threats:
                    if threat.confidence > 0.7:
                        await self._handle_threat_event(threat)

            # Update metrics
            self.metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

            return result

        except Exception as e:
            logger.error(f"❌ Activity analysis failed: {e}")
            return {
                "analysis_id": analysis_id,
                "error": str(e),
                "overall_threat_score": 0.5,  # Conservative score on error
                "threat_level": ThreatLevel.MEDIUM.value,
            }

    async def _assess_trinity_threats(
        self, user_id: str, activity_data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess threats specific to Constellation Framework"""

        threat_score = 0.0
        threats = []

        # ⚛️ Identity threats
        identity_confidence = activity_data.get("identity_confidence", 1.0)
        if identity_confidence < 0.7:
            threat_score = max(threat_score, 0.6)
            threats.append("Identity verification failure")

        # 🧠 Consciousness threats
        consciousness_drift = context.get("consciousness_drift", 0.0)
        if consciousness_drift > 0.15:  # Drift threshold
            threat_score = max(threat_score, 0.8)
            threats.append("Consciousness drift detected")

        # 🛡️ Guardian threats
        guardian_violations = context.get("guardian_violations", [])
        if guardian_violations:
            threat_score = max(threat_score, 0.9)
            threats.extend([f"Guardian violation: {v}" for v in guardian_violations])

        # Constitutional AI threats
        constitutional_score = context.get("constitutional_score", 1.0)
        if constitutional_score < 0.8:
            threat_score = max(threat_score, 0.85)
            threats.append("Constitutional compliance violation")

        return {
            "threat_score": threat_score,
            "threats": threats,
            "identity_status": ("verified" if identity_confidence >= 0.8 else "suspicious"),
            "consciousness_drift": consciousness_drift,
            "guardian_status": "clear" if not guardian_violations else "alert",
            "constitutional_compliance": constitutional_score >= 0.8,
        }

    def _score_to_level(self, score: float) -> ThreatLevel:
        """Convert threat score to threat level"""

        if score >= 0.9:
            return ThreatLevel.EMERGENCY
        elif score >= 0.8:
            return ThreatLevel.CRITICAL
        elif score >= 0.6:
            return ThreatLevel.HIGH
        elif score >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    async def _generate_recommendations(
        self,
        threat_score: float,
        behavioral_anomalies: list[str],
        pattern_threats: list[ThreatEvent],
    ) -> list[str]:
        """Generate security recommendations"""

        recommendations = []

        if threat_score > 0.8:
            recommendations.append("Immediate security review required")
            recommendations.append("Consider temporary access restriction")

        if behavioral_anomalies:
            recommendations.append("Investigate behavioral anomalies")
            recommendations.append("Increase user monitoring")

        if pattern_threats:
            for threat in pattern_threats:
                if threat.threat_type == ThreatType.BRUTE_FORCE:
                    recommendations.append("Implement additional authentication measures")
                elif threat.threat_type == ThreatType.DATA_EXFILTRATION:
                    recommendations.append("Review data access permissions")
                elif threat.threat_type == ThreatType.AI_MANIPULATION:
                    recommendations.append("Enhance AI input validation")

        return recommendations

    async def _handle_threat_event(self, threat_event: ThreatEvent):
        """Handle detected threat event"""

        # Add to active threats
        self.active_threats[threat_event.event_id] = threat_event
        self.threat_history.append(threat_event)

        # Execute automated response
        response_actions = await self.response_engine.respond_to_threat(threat_event)

        # Update metrics
        self.metrics["threats_detected"] += 1
        self.metrics["active_threats"] = len(self.active_threats)
        self.metrics["response_actions"] += len(response_actions)

        logger.warning(f"🚨 Threat handled: {threat_event.title} (Actions: {len(response_actions)})")

    async def _continuous_monitoring(self):
        """Background monitoring task"""

        while True:
            try:
                # Clean up resolved threats
                current_time = datetime.now(timezone.utc)
                expired_threats = []

                for threat_id, threat in self.active_threats.items():
                    # Auto-resolve old threats (24 hours)
                    if (current_time - threat.timestamp).total_seconds() > 86400:
                        expired_threats.append(threat_id)

                for threat_id in expired_threats:
                    threat = self.active_threats.pop(threat_id)
                    threat.status = ThreatStatus.RESOLVED
                    threat.resolved_at = current_time
                    threat.resolution_notes = "Auto-resolved after 24 hours"

                # Update metrics
                self.metrics["active_threats"] = len(self.active_threats)

                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Monitoring task error: {e}")
                await asyncio.sleep(60)

    async def get_threat_status(self) -> dict[str, Any]:
        """Get current threat detection status"""

        return {
            "system_status": "operational",
            "active_threats": len(self.active_threats),
            "threat_distribution": {
                level.value: len([t for t in self.active_threats.values() if t.threat_level == level])
                for level in ThreatLevel
            },
            "recent_threats": [
                {
                    "event_id": t.event_id,
                    "type": t.threat_type.value,
                    "level": t.threat_level.value,
                    "confidence": t.confidence,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in list(self.active_threats.values())[-10:]  # Last 10 threats
            ],
            "metrics": self.metrics,
        }


# Export main classes and functions
__all__ = [
    "BehavioralAnalyzer",
    "ComprehensiveThreatDetection",
    "PatternRecognizer",
    "ResponseAction",
    "ThreatEvent",
    "ThreatIndicator",
    "ThreatLevel",
    "ThreatResponseEngine",
    "ThreatStatus",
    "ThreatType",
    "UserBehaviorProfile",
]
