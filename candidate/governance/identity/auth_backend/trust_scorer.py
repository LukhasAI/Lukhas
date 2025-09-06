"""
LUKHAS Trust Scorer - Enhanced Authentication Intelligence
Integrates behavioral analysis and risk assessment with existing LUKHAS security standards
"""

import time
from datetime import datetime, timedelta
from typing import Any

from candidate.core.common import get_logger


class LukhasTrustScorer:
    """
    Enhanced trust scoring system that integrates with LUKHAS authentication flow.
    Provides multi-factor trust assessment while maintaining cryptographic security.
    """

    def __init__(self, entropy_validator, session_manager, audit_logger, timezone):
        self.entropy_validator = entropy_validator
        self.session_manager = session_manager
        self.audit_logger = audit_logger

        # Scoring parameters
        self.base_score = 50.0
        self.max_score = 100.0
        self.min_score = 0.0

        # Component weights (total = 100%)
        self.weights = {
            "entropy": 0.30,  # 30% - Entropy quality and level
            "behavioral": 0.25,  # 25% - User behavior patterns
            "device": 0.25,  # 25% - Device security characteristics
            "contextual": 0.20,  # 20% - Context and environmental factors
        }

        # Storage for behavioral patterns (in production, use persistent storage)
        self.behavioral_patterns = {}
        self.risk_factors = {}

        # Trust thresholds
        self.thresholds = {
            "high_security": 85.0,
            "medium_security": 70.0,
            "low_security": 50.0,
            "suspicious": 30.0,
        }

        self.logger = get_logger(__name__)

    def validate_entropy_data(self, entropy_data: dict[str, Any]) -> bool:
        """
        Validate entropy data using LUKHAS standards.
        Wrapper for entropy_validator interface compatibility.

        Args:
            entropy_data: Dictionary containing entropy information

        Returns:
            True if entropy data is valid, False otherwise
        """
        try:
            # Basic validation
            if not isinstance(entropy_data, dict):
                return False

            level = entropy_data.get("level", 0)
            if not isinstance(level, (int, float)) or level < 0 or level > 100:
                return False

            quality = entropy_data.get("quality", "low")
            if quality not in ["high", "medium", "low", "poor"]:
                return False

            # If we have access to the actual entropy validator, use it
            if hasattr(self.entropy_validator, "validate_entropy_data"):
                return self.entropy_validator.validate_entropy_data(entropy_data)
            elif hasattr(self.entropy_validator, "validate"):
                return self.entropy_validator.validate(level)

            # Fallback validation
            return level > 10  # Minimum entropy threshold

        except Exception as e:
            self.logger.warning(f"Entropy validation failed: {e}")
            return False

    def calculate_entropy_score(self, entropy_data: dict[str, Any]) -> float:
        """
        Calculate trust score based on entropy quality and LUKHAS validation.

        Args:
            entropy_data: Dict containing entropy level, quality, and metadata

        Returns:
            Float score (0-30 points)
        """
        # LUKHAS validation first - security cannot be compromised
        if not self.validate_entropy_data(entropy_data):
            self.audit_logger.log_security_event(
                "entropy_validation_failed",
                {"reason": "Invalid entropy data in trust calculation"},
            )
            return 0.0

        entropy_level = entropy_data.get("level", 0)
        entropy_quality = entropy_data.get("quality", "low")
        entropy_source = entropy_data.get("source", "unknown")
        entropy_age = entropy_data.get("age_seconds", 0)

        # Base score from entropy level (0-100 -> 0-15 points)
        level_score = (entropy_level / 100) * 15

        # Quality multiplier
        quality_multipliers = {"high": 1.0, "medium": 0.8, "low": 0.5, "poor": 0.2}
        quality_multiplier = quality_multipliers.get(entropy_quality, 0.2)

        # Source reliability bonus/penalty
        source_modifiers = {
            "hardware": 5.0,  # Hardware RNG bonus
            "system": 2.0,  # System entropy bonus
            "user": 0.0,  # User interaction (neutral)
            "network": -2.0,  # Network-based (slight penalty)
            "unknown": -5.0,  # Unknown source penalty
        }
        source_modifier = source_modifiers.get(entropy_source, -5.0)

        # Freshness factor (entropy should be recent)
        if entropy_age > 300:  # 5 minutes
            freshness_penalty = -3.0
        elif entropy_age > 60:  # 1 minute
            freshness_penalty = -1.0
        else:
            freshness_penalty = 0.0

        entropy_score = (level_score * quality_multiplier) + source_modifier + freshness_penalty

        # Ensure within bounds
        entropy_score = max(0, min(30, entropy_score))

        self.logger.debug(
            f"Entropy score calculated: {entropy_score} "
            f"(level: {entropy_level}, quality: {entropy_quality}, "
            f"source: {entropy_source}, age: {entropy_age}s)"
        )

        return entropy_score

    def calculate_behavioral_score(self, user_id: str, behavioral_data: dict[str, Any]) -> float:
        """
        Calculate trust score based on behavioral patterns and anomaly detection.

        Args:
            user_id: Unique user identifier
            behavioral_data: Dict containing current behavior metrics

        Returns:
            Float score (0-25 points)
        """
        if user_id not in self.behavioral_patterns:
            self.behavioral_patterns[user_id] = {
                "login_times": [],
                "device_patterns": [],
                "interaction_patterns": [],
                "geolocation_patterns": [],
                "session_durations": [],
                "anomaly_count": 0,
                "first_seen": datetime.now(timezone.utc),
                "last_update": datetime.now(timezone.utc),
            }

        patterns = self.behavioral_patterns[user_id]
        patterns["last_update"] = datetime.now(timezone.utc)

        score = 25.0  # Base behavioral score
        current_time = datetime.now(timezone.utc)

        # 1. Temporal pattern analysis
        current_hour = current_time.hour
        patterns["login_times"].append(current_hour)
        patterns["login_times"] = patterns["login_times"][-50:]  # Keep last 50 logins

        if len(patterns["login_times"]) > 10:
            # Calculate usual login time patterns
            avg_hour = sum(patterns["login_times"]) / len(patterns["login_times"])
            time_deviation = abs(current_hour - avg_hour)

            # Significant deviation from normal pattern
            if time_deviation > 8:
                score -= 4.0
                patterns["anomaly_count"] += 1
                self.logger.info(f"Temporal anomaly detected for {user_id}: current={current_hour}, avg={avg_hour:.1f}")
            elif time_deviation > 4:
                score -= 2.0

        # 2. Device consistency analysis
        device_id = behavioral_data.get("device_id", "unknown")
        device_fingerprint = behavioral_data.get("device_fingerprint", "")

        patterns["device_patterns"].append(
            {
                "id": device_id,
                "fingerprint": device_fingerprint,
                "timestamp": current_time,
            }
        )
        patterns["device_patterns"] = patterns["device_patterns"][-20:]  # Keep last 20

        # Analyze device diversity
        recent_devices = [d["id"] for d in patterns["device_patterns"][-10:]]
        unique_devices = len(set(recent_devices))

        if unique_devices > 5:  # Too many different devices recently
            score -= 5.0
            patterns["anomaly_count"] += 1
        elif unique_devices > 3:
            score -= 2.0

        # 3. Interaction speed and patterns
        interaction_speed = behavioral_data.get("interaction_speed", 1.0)
        typing_rhythm = behavioral_data.get("typing_rhythm", [])
        mouse_movement = behavioral_data.get("mouse_movement_pattern", {})

        patterns["interaction_patterns"].append(
            {
                "speed": interaction_speed,
                "typing": typing_rhythm,
                "mouse": mouse_movement,
                "timestamp": current_time,
            }
        )
        patterns["interaction_patterns"] = patterns["interaction_patterns"][-20:]

        if len(patterns["interaction_patterns"]) > 5:
            recent_speeds = [p["speed"] for p in patterns["interaction_patterns"][-10:]]
            avg_speed = sum(recent_speeds) / len(recent_speeds)

            # Detect unusual interaction speed
            speed_deviation = abs(interaction_speed - avg_speed)
            if speed_deviation > 1.0:  # Significantly different speed
                score -= 3.0
                patterns["anomaly_count"] += 1
            elif speed_deviation > 0.5:
                score -= 1.0

        # 4. Geographic consistency
        location = behavioral_data.get("location", {})
        if location:
            patterns["geolocation_patterns"].append(
                {
                    "lat": location.get("latitude"),
                    "lon": location.get("longitude"),
                    "country": location.get("country"),
                    "city": location.get("city"),
                    "timestamp": current_time,
                }
            )
            patterns["geolocation_patterns"] = patterns["geolocation_patterns"][-30:]

            # Check for impossible travel
            if len(patterns["geolocation_patterns"]) > 1:
                last_location = patterns["geolocation_patterns"][-2]
                time_diff = (current_time - last_location["timestamp"]).total_seconds() / 3600  # hours

                # Simplified distance check (in production, use proper geolocation)
                if (
                    last_location["country"] != location.get("country") and time_diff < 2
                ):  # Different country within 2 hours
                    score -= 8.0
                    patterns["anomaly_count"] += 1
                    self.logger.warning(f"Impossible travel detected for {user_id}")

        # 5. Session duration patterns
        session_duration = behavioral_data.get("current_session_duration", 0)
        if session_duration > 0:
            patterns["session_durations"].append(session_duration)
            patterns["session_durations"] = patterns["session_durations"][-20:]

            if len(patterns["session_durations"]) > 5:
                avg_duration = sum(patterns["session_durations"]) / len(patterns["session_durations"])
                if session_duration > avg_duration * 3:  # Unusually long session
                    score -= 2.0

        # 6. Account age factor
        account_age = (current_time - patterns["first_seen"]).days
        if account_age > 90:  # Established account bonus
            score += 2.0
        elif account_age < 1:  # New account penalty
            score -= 3.0

        # 7. Cumulative anomaly penalty
        if patterns["anomaly_count"] > 10:
            score -= 8.0
        elif patterns["anomaly_count"] > 5:
            score -= 4.0
        elif patterns["anomaly_count"] > 2:
            score -= 2.0

        behavioral_score = max(0, score)

        self.logger.debug(
            f"Behavioral score for {user_id}: {behavioral_score} (anomalies: {patterns['anomaly_count']})"
        )

        return behavioral_score

    def calculate_device_score(self, device_data: dict[str, Any]) -> float:
        """
        Calculate trust score based on device security characteristics.

        Args:
            device_data: Dict containing device security information

        Returns:
            Float score (0-25 points)
        """
        score = 20.0  # Base device score

        # Device age and establishment
        device_age = device_data.get("age_days", 0)
        if device_age > 90:
            score += 3.0  # Well-established device
        elif device_age > 30:
            score += 1.0  # Somewhat established
        elif device_age < 1:
            score -= 4.0  # Brand new device

        # Security features
        has_biometric = device_data.get("has_biometric", False)
        has_secure_enclave = device_data.get("has_secure_enclave", False)
        has_tpm = device_data.get("has_tpm", False)
        is_jailbroken = device_data.get("is_jailbroken", False)
        is_rooted = device_data.get("is_rooted", False)

        if has_biometric:
            score += 2.0
        if has_secure_enclave:
            score += 2.0
        if has_tpm:
            score += 1.0
        if is_jailbroken or is_rooted:
            score -= 8.0  # Significant security concern

        # Operating system and updates
        os_version = device_data.get("os_version", "")
        os_patch_level = device_data.get("patch_level", 0)

        # Simplified OS version checking (extend as needed)
        if "windows" in os_version.lower():
            if "11" in os_version or "10" in os_version:
                score += 1.0
            else:
                score -= 2.0  # Older Windows version
        elif "ios" in os_version.lower():
            if os_patch_level > 0:  # Recent patches
                score += 1.0
        elif "android" in os_version.lower():
            if os_patch_level > 0:
                score += 1.0
            else:
                score -= 1.0  # Android without recent patches

        # Network security
        network_type = device_data.get("network_type", "unknown")
        network_security = device_data.get("network_security", "unknown")

        if network_type == "cellular":
            score += 2.0  # Cellular generally more secure than WiFi
        elif network_type == "wifi":
            if network_security == "wpa3":
                score += 1.0
            elif network_security == "wpa2":
                score += 0.0  # Neutral
            elif network_security in ["wep", "open"]:
                score -= 4.0  # Insecure network
        elif network_type == "public_wifi":
            score -= 3.0  # Public WiFi risk

        # Device reputation (based on known device characteristics)
        device_brand = device_data.get("brand", "").lower()
        device_data.get("model", "").lower()

        # Simplified device reputation (extend based on security research)
        trusted_brands = ["apple", "samsung", "google", "microsoft"]
        if any(brand in device_brand for brand in trusted_brands):
            score += 1.0

        device_score = max(0, min(25, score))

        self.logger.debug(
            f"Device score calculated: {device_score} "
            f"(age: {device_age}, biometric: {has_biometric}, "
            f"jailbroken: {is_jailbroken})"
        )

        return device_score

    def calculate_contextual_score(self, context_data: dict[str, Any], user_id: str) -> float:
        """
        Calculate trust score based on contextual factors and environmental data.

        Args:
            context_data: Dict containing contextual information
            user_id: User identifier for session context

        Returns:
            Float score (0-20 points)
        """
        score = 15.0  # Base contextual score
        current_time = datetime.now(timezone.utc)

        # Time-based risk assessment
        hour = current_time.hour
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday

        # Business hours generally lower risk
        if 9 <= hour <= 17 and day_of_week < 5:  # Business hours, weekday
            score += 2.0
        elif hour >= 22 or hour <= 6:  # Late night/early morning
            score -= 2.0
        elif day_of_week >= 5:  # Weekend
            score -= 1.0

        # Authentication frequency analysis
        auth_frequency = context_data.get("recent_auth_count", 0)
        auth_timespan = context_data.get("auth_timespan_hours", 24)

        if auth_frequency > 20 and auth_timespan < 1:  # Too many recent authentications
            score -= 6.0
        elif auth_frequency > 10 and auth_timespan < 2:
            score -= 3.0
        elif auth_frequency > 5 and auth_timespan < 1:
            score -= 1.0

        # Session context
        session_data = self.session_manager.get_session_info(user_id)
        if session_data:
            concurrent_sessions = session_data.get("concurrent_count", 0)
            if concurrent_sessions > 3:  # Multiple concurrent sessions
                score -= 4.0
            elif concurrent_sessions > 1:
                score -= 1.0

        # Location-based risk assessment
        location = context_data.get("location", {})
        if location:
            country = location.get("country", "").lower()
            is_vpn = location.get("is_vpn", False)
            is_tor = location.get("is_tor", False)

            # High-risk countries (simplified list - extend based on threat
            # intelligence)
            high_risk_countries = ["unknown", "proxy"]
            if country in high_risk_countries:
                score -= 5.0

            if is_vpn:
                score -= 2.0  # VPN usage (could be legitimate or evasive)
            if is_tor:
                score -= 8.0  # Tor usage (high anonymity, high risk)

        # Request pattern analysis
        request_pattern = context_data.get("request_pattern", {})
        if request_pattern:
            burst_count = request_pattern.get("burst_requests", 0)
            if burst_count > 10:  # Burst of requests
                score -= 3.0

            failed_attempts = request_pattern.get("recent_failures", 0)
            if failed_attempts > 3:  # Recent authentication failures
                score -= 4.0

        contextual_score = max(0, score)

        self.logger.debug(
            f"Contextual score calculated: {contextual_score} (hour: {hour}, auth_freq: {auth_frequency})"
        )

        return contextual_score

    def calculate_trust_score(
        self,
        user_id: str,
        entropy_data: dict[str, Any],
        behavioral_data: dict[str, Any],
        device_data: dict[str, Any],
        context_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Calculate comprehensive trust score from all components.

        Args:
            user_id: Unique user identifier
            entropy_data: Entropy quality and metadata
            behavioral_data: User behavior patterns
            device_data: Device security characteristics
            context_data: Environmental and contextual factors

        Returns:
            Dict containing trust score and component breakdown
        """
        start_time = time.time()

        try:
            # Calculate component scores
            entropy_score = self.calculate_entropy_score(entropy_data)
            behavioral_score = self.calculate_behavioral_score(user_id, behavioral_data)
            device_score = self.calculate_device_score(device_data)
            contextual_score = self.calculate_contextual_score(context_data, user_id)

            # Apply component weights
            weighted_scores = {
                "entropy": entropy_score * self.weights["entropy"],
                "behavioral": behavioral_score * self.weights["behavioral"],
                "device": device_score * self.weights["device"],
                "contextual": contextual_score * self.weights["contextual"],
            }

            # Calculate total score
            total_score = sum(weighted_scores.values())

            # Apply risk factors if present
            risk_multiplier = 1.0
            if user_id in self.risk_factors:
                risk_level = self.risk_factors[user_id].get("level", "low")
                risk_multipliers = {
                    "low": 1.0,
                    "medium": 0.85,
                    "high": 0.6,
                    "critical": 0.3,
                }
                risk_multiplier = risk_multipliers.get(risk_level, 1.0)

                if risk_multiplier < 1.0:
                    self.audit_logger.log_security_event(
                        "risk_factor_applied",
                        {
                            "user_id": user_id,
                            "risk_level": risk_level,
                            "multiplier": risk_multiplier,
                        },
                    )

            final_score = min(self.max_score, total_score * risk_multiplier)

            # Determine trust level
            if final_score >= self.thresholds["high_security"]:
                trust_level = "high"
            elif final_score >= self.thresholds["medium_security"]:
                trust_level = "medium"
            elif final_score >= self.thresholds["low_security"]:
                trust_level = "low"
            else:
                trust_level = "suspicious"

            calculation_time = time.time() - start_time

            result = {
                "total_score": round(final_score, 2),
                "trust_level": trust_level,
                "components": {
                    "entropy": round(entropy_score, 2),
                    "behavioral": round(behavioral_score, 2),
                    "device": round(device_score, 2),
                    "contextual": round(contextual_score, 2),
                },
                "weighted_components": {
                    "entropy": round(weighted_scores["entropy"], 2),
                    "behavioral": round(weighted_scores["behavioral"], 2),
                    "device": round(weighted_scores["device"], 2),
                    "contextual": round(weighted_scores["contextual"], 2),
                },
                "risk_multiplier": risk_multiplier,
                "thresholds": self.thresholds,
                "calculation_time_ms": round(calculation_time * 1000, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Log trust calculation for audit trail
            self.audit_logger.log_trust_calculation(user_id, result)

            return result

        except Exception as e:
            self.logger.error(f"Trust score calculation failed for {user_id}: {e!s}")
            self.audit_logger.log_security_event("trust_calculation_error", {"user_id": user_id, "error": str(e)})

            # Return safe default score on error
            return {
                "total_score": 0.0,
                "trust_level": "error",
                "components": {
                    "entropy": 0,
                    "behavioral": 0,
                    "device": 0,
                    "contextual": 0,
                },
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def update_risk_factors(self, user_id: str, risk_level: str, reason: str, expiry_hours: int = 24):
        """
        Update risk factors for a user (e.g., after suspicious activity).

        Args:
            user_id: User identifier
            risk_level: 'low', 'medium', 'high', or 'critical'
            reason: Reason for risk factor
            expiry_hours: Hours until risk factor expires
        """
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)

        self.risk_factors[user_id] = {
            "level": risk_level,
            "reason": reason,
            "created": datetime.now(timezone.utc),
            "expires": expiry_time,
        }

        self.audit_logger.log_security_event(
            "risk_factor_updated",
            {
                "user_id": user_id,
                "risk_level": risk_level,
                "reason": reason,
                "expires": expiry_time.isoformat(),
            },
        )

        self.logger.info(f"Risk factor updated for {user_id}: {risk_level} - {reason}")

    def get_trust_threshold(self, operation_type: str = "standard") -> float:
        """
        Get appropriate trust threshold for different operation types.

        Args:
            operation_type: Type of operation requiring authentication

        Returns:
            Minimum trust score required
        """
        operation_thresholds = {
            "standard": self.thresholds["low_security"],
            "sensitive": self.thresholds["medium_security"],
            "admin": self.thresholds["high_security"],
            "critical": self.thresholds["high_security"],
        }

        return operation_thresholds.get(operation_type, self.thresholds["medium_security"])

    def cleanup_expired_data(self):
        """Remove expired risk factors and old behavioral data."""
        current_time = datetime.now(timezone.utc)

        # Clean expired risk factors
        expired_users = []
        for user_id, risk_data in self.risk_factors.items():
            if current_time > risk_data.get("expires", current_time):
                expired_users.append(user_id)

        for user_id in expired_users:
            del self.risk_factors[user_id]
            self.logger.debug(f"Expired risk factor removed for {user_id}")

        # Clean old behavioral patterns (keep only recent data)
        for user_id, patterns in self.behavioral_patterns.items():
            if current_time - patterns.get("last_update", current_time) > timedelta(days=30):
                # Keep only essential data for inactive users
                patterns["login_times"] = patterns["login_times"][-10:]
                patterns["device_patterns"] = patterns["device_patterns"][-5:]
                patterns["interaction_patterns"] = patterns["interaction_patterns"][-5:]
