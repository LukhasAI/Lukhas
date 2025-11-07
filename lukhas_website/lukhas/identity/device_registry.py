"""
I.6 Device Registry - Advanced device fingerprinting and trust management
Enhanced device registry with ML-based fingerprinting and behavioral analysis.
"""

import asyncio
import contextlib
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from identity.observability import IdentityObservability
from identity.session_manager import DeviceInfo, DeviceType

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Device risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DeviceFingerprint:
    """Enhanced device fingerprinting data"""
    primary_hash: str  # Basic fingerprint
    secondary_hash: str  # Enhanced fingerprint with more data
    canvas_hash: Optional[str] = None  # Canvas fingerprinting
    webgl_hash: Optional[str] = None   # WebGL fingerprinting
    audio_hash: Optional[str] = None   # Audio context fingerprinting
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    hardware_concurrency: Optional[int] = None
    memory: Optional[int] = None
    connection_type: Optional[str] = None


@dataclass
class DeviceBehavior:
    """Device behavioral patterns"""
    login_times: List[datetime] = field(default_factory=list)
    ip_addresses: Set[str] = field(default_factory=set)
    user_agents: List[str] = field(default_factory=list)
    session_durations: List[int] = field(default_factory=list)
    activity_patterns: Dict[str, int] = field(default_factory=dict)
    location_data: List[Dict[str, Any]] = field(default_factory=list)
    failed_attempts: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class DeviceRiskAssessment:
    """Device risk assessment results"""
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    factors: List[str]  # Risk contributing factors
    assessment_time: datetime
    confidence: float  # Assessment confidence 0.0 to 1.0
    recommendations: List[str]


class DeviceRegistry:
    """
    Advanced device registry with ML-based fingerprinting and behavioral analysis
    """

    def __init__(self,
                 observability: IdentityObservability,
                 trust_decay_rate: float = 0.001,  # Daily trust decay
                 risk_threshold_high: float = 0.7,
                 risk_threshold_critical: float = 0.9,
                 fingerprint_similarity_threshold: float = 0.8):
        self.observability = observability
        self.trust_decay_rate = trust_decay_rate
        self.risk_threshold_high = risk_threshold_high
        self.risk_threshold_critical = risk_threshold_critical
        self.fingerprint_similarity_threshold = fingerprint_similarity_threshold

        # Storage
        self.devices: Dict[str, DeviceInfo] = {}
        self.fingerprints: Dict[str, DeviceFingerprint] = {}
        self.behaviors: Dict[str, DeviceBehavior] = {}
        self.risk_assessments: Dict[str, DeviceRiskAssessment] = {}

        # Indexes
        self.fingerprint_index: Dict[str, Set[str]] = {}  # hash -> device_ids
        self.user_devices: Dict[str, Set[str]] = {}  # lambda_id -> device_ids
        self.compromised_devices: Set[str] = set()

        # Background tasks
        self._decay_task: Optional[asyncio.Task] = None
        self._risk_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background tasks"""
        if self._decay_task is None:
            self._decay_task = asyncio.create_task(self._trust_decay_loop())
        if self._risk_task is None:
            self._risk_task = asyncio.create_task(self._risk_assessment_loop())

    async def stop(self):
        """Stop background tasks"""
        for task in [self._decay_task, self._risk_task]:
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

    async def register_device(self,
                            lambda_id: str,
                            device_info: DeviceInfo,
                            fingerprint_data: Dict[str, Any]) -> DeviceInfo:
        """Register device with enhanced fingerprinting"""

        # Create enhanced fingerprint
        fingerprint = self._create_fingerprint(fingerprint_data)

        # Check for existing similar devices
        similar_devices = await self._find_similar_devices(fingerprint)
        if similar_devices:
            # Device might already be registered
            for device_id in similar_devices:
                if device_id in self.user_devices.get(lambda_id, set()):
                    logger.info(f"Device appears already registered: {device_id}")
                    return self.devices[device_id]

        # Initialize device behavior tracking
        behavior = DeviceBehavior(
            login_times=[datetime.now(timezone.utc)],
            ip_addresses={device_info.ip_address},
            user_agents=[device_info.user_agent],
            last_activity=datetime.now(timezone.utc)
        )

        # Store device data
        device_id = device_info.device_id
        self.devices[device_id] = device_info
        self.fingerprints[device_id] = fingerprint
        self.behaviors[device_id] = behavior

        # Update indexes
        if lambda_id not in self.user_devices:
            self.user_devices[lambda_id] = set()
        self.user_devices[lambda_id].add(device_id)

        self._index_fingerprint(device_id, fingerprint)

        # Initial risk assessment
        await self._assess_device_risk(device_id)

        # Record metrics
        await self.observability.record_device_registration(lambda_id, device_info.device_type.value)

        logger.info(f"Device registered with enhanced fingerprinting: {device_id}")
        return device_info

    async def update_device_activity(self,
                                   device_id: str,
                                   ip_address: str,
                                   user_agent: str,
                                   session_duration: Optional[int] = None,
                                   activity_type: str = "login"):
        """Update device behavioral data"""

        if device_id not in self.behaviors:
            return

        behavior = self.behaviors[device_id]
        now = datetime.now(timezone.utc)

        # Update activity data
        behavior.login_times.append(now)
        behavior.ip_addresses.add(ip_address)
        behavior.user_agents.append(user_agent)
        behavior.last_activity = now

        if session_duration:
            behavior.session_durations.append(session_duration)

        # Track activity patterns
        hour = now.hour
        behavior.activity_patterns[f"hour_{hour}"] = behavior.activity_patterns.get(f"hour_{hour}", 0) + 1

        # Limit stored data size
        self._trim_behavior_data(behavior)

        # Update device last seen
        if device_id in self.devices:
            self.devices[device_id].last_seen = now
            self.devices[device_id].ip_address = ip_address

        # Re-assess risk if significant changes
        await self._assess_device_risk(device_id)

    async def verify_device_fingerprint(self,
                                      device_id: str,
                                      fingerprint_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Verify device fingerprint against stored data"""

        if device_id not in self.fingerprints:
            return False, 0.0

        stored_fingerprint = self.fingerprints[device_id]
        current_fingerprint = self._create_fingerprint(fingerprint_data)

        similarity = self._calculate_fingerprint_similarity(stored_fingerprint, current_fingerprint)
        is_valid = similarity >= self.fingerprint_similarity_threshold

        if not is_valid:
            logger.warning(f"Device fingerprint mismatch: {device_id}, similarity: {similarity:.3f}")
            await self._handle_fingerprint_mismatch(device_id, similarity)

        return is_valid, similarity

    async def assess_device_risk(self, device_id: str) -> Optional[DeviceRiskAssessment]:
        """Get current device risk assessment"""
        return self.risk_assessments.get(device_id)

    async def mark_device_compromised(self, device_id: str, reason: str):
        """Mark device as compromised"""
        self.compromised_devices.add(device_id)

        if device_id in self.devices:
            self.devices[device_id].trust_level = 0.0
            self.devices[device_id].metadata["compromised"] = {
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Create critical risk assessment
        assessment = DeviceRiskAssessment(
            risk_level=RiskLevel.CRITICAL,
            risk_score=1.0,
            factors=[f"manually_marked_compromised: {reason}"],
            assessment_time=datetime.now(timezone.utc),
            confidence=1.0,
            recommendations=["revoke_all_sessions", "require_reregistration"]
        )
        self.risk_assessments[device_id] = assessment

        logger.warning(f"Device marked as compromised: {device_id}, reason: {reason}")

    async def get_device_statistics(self, lambda_id: str) -> Dict[str, Any]:
        """Get device statistics for a user"""
        user_device_ids = self.user_devices.get(lambda_id, set())
        devices = [self.devices[did] for did in user_device_ids if did in self.devices]

        if not devices:
            return {}

        now = datetime.now(timezone.utc)
        trusted_devices = sum(1 for d in devices if d.trust_level >= 0.7)
        recent_activity = sum(1 for d in devices if d.last_seen > now - timedelta(days=7))

        risk_levels = {}
        for device_id in user_device_ids:
            assessment = self.risk_assessments.get(device_id)
            if assessment:
                risk_levels[assessment.risk_level.value] = risk_levels.get(assessment.risk_level.value, 0) + 1

        return {
            "total_devices": len(devices),
            "trusted_devices": trusted_devices,
            "recent_activity": recent_activity,
            "device_types": {
                dtype.value: sum(1 for d in devices if d.device_type == dtype)
                for dtype in DeviceType
            },
            "risk_levels": risk_levels,
            "compromised_devices": len([did for did in user_device_ids if did in self.compromised_devices])
        }

    def _create_fingerprint(self, fingerprint_data: Dict[str, Any]) -> DeviceFingerprint:
        """Create device fingerprint from raw data"""

        # Primary fingerprint (basic data)
        primary_data = {
            "user_agent": fingerprint_data.get("user_agent", ""),
            "screen_resolution": fingerprint_data.get("screen_resolution", ""),
            "timezone": fingerprint_data.get("timezone", ""),
            "language": fingerprint_data.get("language", "")
        }
        primary_hash = hashlib.sha256(json.dumps(primary_data, sort_keys=True).encode()).hexdigest()

        # Secondary fingerprint (enhanced data)
        secondary_data = {**primary_data}
        secondary_data.update({
            "platform": fingerprint_data.get("platform", ""),
            "hardware_concurrency": fingerprint_data.get("hardware_concurrency", 0),
            "memory": fingerprint_data.get("memory", 0),
            "connection_type": fingerprint_data.get("connection_type", "")
        })
        secondary_hash = hashlib.sha256(json.dumps(secondary_data, sort_keys=True).encode()).hexdigest()

        return DeviceFingerprint(
            primary_hash=primary_hash,
            secondary_hash=secondary_hash,
            canvas_hash=fingerprint_data.get("canvas_hash"),
            webgl_hash=fingerprint_data.get("webgl_hash"),
            audio_hash=fingerprint_data.get("audio_hash"),
            screen_resolution=fingerprint_data.get("screen_resolution"),
            timezone=fingerprint_data.get("timezone"),
            language=fingerprint_data.get("language"),
            platform=fingerprint_data.get("platform"),
            hardware_concurrency=fingerprint_data.get("hardware_concurrency"),
            memory=fingerprint_data.get("memory"),
            connection_type=fingerprint_data.get("connection_type")
        )

    def _index_fingerprint(self, device_id: str, fingerprint: DeviceFingerprint):
        """Index fingerprint for similarity searches"""
        for hash_value in [fingerprint.primary_hash, fingerprint.secondary_hash]:
            if hash_value not in self.fingerprint_index:
                self.fingerprint_index[hash_value] = set()
            self.fingerprint_index[hash_value].add(device_id)

    async def _find_similar_devices(self, fingerprint: DeviceFingerprint) -> Set[str]:
        """Find devices with similar fingerprints"""
        similar_devices = set()

        # Check exact matches first
        for hash_value in [fingerprint.primary_hash, fingerprint.secondary_hash]:
            similar_devices.update(self.fingerprint_index.get(hash_value, set()))

        # Check partial matches
        for device_id, stored_fingerprint in self.fingerprints.items():
            similarity = self._calculate_fingerprint_similarity(fingerprint, stored_fingerprint)
            if similarity >= self.fingerprint_similarity_threshold:
                similar_devices.add(device_id)

        return similar_devices

    def _calculate_fingerprint_similarity(self,
                                        fp1: DeviceFingerprint,
                                        fp2: DeviceFingerprint) -> float:
        """Calculate similarity between two fingerprints"""

        # Primary hash exact match
        if fp1.primary_hash == fp2.primary_hash:
            return 1.0

        # Partial similarity calculation
        similarity_factors = []

        # Screen resolution
        if fp1.screen_resolution and fp2.screen_resolution:
            similarity_factors.append(1.0 if fp1.screen_resolution == fp2.screen_resolution else 0.0)

        # Timezone
        if fp1.timezone and fp2.timezone:
            similarity_factors.append(1.0 if fp1.timezone == fp2.timezone else 0.0)

        # Language
        if fp1.language and fp2.language:
            similarity_factors.append(1.0 if fp1.language == fp2.language else 0.0)

        # Platform
        if fp1.platform and fp2.platform:
            similarity_factors.append(1.0 if fp1.platform == fp2.platform else 0.0)

        # Hardware features
        if fp1.hardware_concurrency and fp2.hardware_concurrency:
            similarity_factors.append(1.0 if fp1.hardware_concurrency == fp2.hardware_concurrency else 0.5)

        # Canvas/WebGL hashes
        for attr in ["canvas_hash", "webgl_hash", "audio_hash"]:
            val1 = getattr(fp1, attr)
            val2 = getattr(fp2, attr)
            if val1 and val2:
                similarity_factors.append(1.0 if val1 == val2 else 0.0)

        return sum(similarity_factors) / len(similarity_factors) if similarity_factors else 0.0

    async def _assess_device_risk(self, device_id: str):
        """Assess device risk based on behavior and fingerprint"""

        if device_id not in self.devices or device_id not in self.behaviors:
            return

        device = self.devices[device_id]
        behavior = self.behaviors[device_id]
        risk_factors = []
        risk_score = 0.0

        # Check for compromised status
        if device_id in self.compromised_devices:
            risk_score = 1.0
            risk_factors.append("device_marked_compromised")
        else:
            # Analyze behavioral patterns
            risk_score, risk_factors = self._analyze_behavioral_risk(behavior)

            # Factor in device trust level
            trust_factor = 1.0 - device.trust_level
            risk_score = min(1.0, risk_score + (trust_factor * 0.3))

            # Check for fingerprint anomalies
            if device.metadata.get("fingerprint_mismatch_count", 0) > 0:
                risk_score += 0.2
                risk_factors.append("fingerprint_inconsistency")

        # Determine risk level
        if risk_score >= self.risk_threshold_critical:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= self.risk_threshold_high:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_level, risk_factors)

        # Store assessment
        assessment = DeviceRiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            factors=risk_factors,
            assessment_time=datetime.now(timezone.utc),
            confidence=0.8,  # Base confidence
            recommendations=recommendations
        )
        self.risk_assessments[device_id] = assessment

        # Record metrics
        await self.observability.record_device_risk_assessment(device_id, risk_level.value, risk_score)

    def _analyze_behavioral_risk(self, behavior: DeviceBehavior) -> Tuple[float, List[str]]:
        """Analyze behavioral patterns for risk indicators"""
        risk_score = 0.0
        risk_factors = []

        # Check for excessive failed attempts
        if behavior.failed_attempts > 5:
            risk_score += 0.3
            risk_factors.append(f"excessive_failed_attempts_{behavior.failed_attempts}")

        # Check for unusual IP address patterns
        if len(behavior.ip_addresses) > 10:
            risk_score += 0.2
            risk_factors.append("multiple_ip_addresses")

        # Check for user agent inconsistencies
        unique_user_agents = set(behavior.user_agents[-10:])  # Last 10 logins
        if len(unique_user_agents) > 3:
            risk_score += 0.15
            risk_factors.append("inconsistent_user_agents")

        # Check for unusual activity patterns
        if behavior.activity_patterns:
            activity_hours = list(behavior.activity_patterns.keys())
            if len(activity_hours) > 18:  # Active across too many hours
                risk_score += 0.1
                risk_factors.append("unusual_activity_pattern")

        # Check for very short or very long sessions
        if behavior.session_durations:
            avg_duration = sum(behavior.session_durations) / len(behavior.session_durations)
            if avg_duration < 60 or avg_duration > 14400:  # < 1min or > 4hrs
                risk_score += 0.1
                risk_factors.append("unusual_session_duration")

        return min(1.0, risk_score), risk_factors

    def _generate_risk_recommendations(self, risk_level: RiskLevel, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "immediately_revoke_all_sessions",
                "require_device_reregistration",
                "enable_enhanced_monitoring",
                "consider_account_suspension"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "require_additional_authentication",
                "limit_session_duration",
                "enable_enhanced_monitoring",
                "consider_device_quarantine"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "increase_authentication_frequency",
                "monitor_device_activity",
                "limit_high_privilege_operations"
            ])

        # Factor-specific recommendations
        if "fingerprint_inconsistency" in risk_factors:
            recommendations.append("verify_device_fingerprint")

        if "multiple_ip_addresses" in risk_factors:
            recommendations.append("verify_geographic_location")

        return list(set(recommendations))  # Remove duplicates

    def _trim_behavior_data(self, behavior: DeviceBehavior):
        """Trim behavioral data to prevent unlimited growth"""
        # Keep last 100 login times
        if len(behavior.login_times) > 100:
            behavior.login_times = behavior.login_times[-100:]

        # Keep last 50 user agents
        if len(behavior.user_agents) > 50:
            behavior.user_agents = behavior.user_agents[-50:]

        # Keep last 100 session durations
        if len(behavior.session_durations) > 100:
            behavior.session_durations = behavior.session_durations[-100:]

        # Keep last 20 IP addresses
        if len(behavior.ip_addresses) > 20:
            behavior.ip_addresses = set(list(behavior.ip_addresses)[-20:])

    async def _handle_fingerprint_mismatch(self, device_id: str, similarity: float):
        """Handle fingerprint mismatch events"""
        if device_id in self.devices:
            mismatch_count = self.devices[device_id].metadata.get("fingerprint_mismatch_count", 0)
            self.devices[device_id].metadata["fingerprint_mismatch_count"] = mismatch_count + 1
            self.devices[device_id].metadata[f"fingerprint_mismatch_{int(time.time())}"] = {
                "similarity": similarity,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Decrease trust level
        if device_id in self.devices:
            trust_penalty = 0.1 + (0.1 * (1.0 - similarity))
            old_trust = self.devices[device_id].trust_level
            self.devices[device_id].trust_level = max(0.0, old_trust - trust_penalty)

    async def _trust_decay_loop(self):
        """Background task for trust decay"""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                await self._apply_trust_decay()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Trust decay error: {e}")

    async def _apply_trust_decay(self):
        """Apply daily trust decay to all devices"""
        for device in self.devices.values():
            if device.trust_level > 0.1:  # Don't decay below minimum
                device.trust_level = max(0.1, device.trust_level - self.trust_decay_rate)

    async def _risk_assessment_loop(self):
        """Background risk assessment updates"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run hourly
                for device_id in list(self.devices.keys()):
                    await self._assess_device_risk(device_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Risk assessment error: {e}")
