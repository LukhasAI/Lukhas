import logging
import streamlit as st
logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Tiered Authentication System: Consciousness-Aware Authentication
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: AUTHENTICATION_ENGINE
║ CONSCIOUSNESS_ROLE: Multi-tier consciousness authentication validation
║ EVOLUTIONARY_STAGE: Advanced - Consciousness biometric integration
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Advanced multi-tier identity authentication
║ 🧠 CONSCIOUSNESS: Consciousness-aware biometric validation
║ 🛡️ GUARDIAN: Security validation and anti-spoofing protection
╚══════════════════════════════════════════════════════════════
"""

import base64
import logging as std_logging
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Optional

# Import MΛTRIZ consciousness components
try:
    from ..matriz_consciousness_signals import ConsciousnessSignal
    from .matriz_consciousness_identity_signals import (
        AuthenticationTier,
        IdentityBiometricData,
        consciousness_identity_signal_emitter,
    )
except ImportError as e:
    std_logging.error(f"Failed to import consciousness signal components: {e}")
    AuthenticationTier = None
    IdentityBiometricData = None
    consciousness_identity_signal_emitter = None

# Import existing identity components
try:
    from .lambda_id_core import LukhasIdentityService, WebAuthnPasskeyManager, ΛIDError
except ImportError as e:
    std_logging.warning(f"Legacy identity components not available: {e}")
    WebAuthnPasskeyManager = None
    LukhasIdentityService = None
    ΛIDError = Exception

logger = std_logging.getLogger(__name__)


class BiometricPattern(Enum):
    """Types of consciousness-enhanced biometric patterns"""

    BRAINWAVE_PATTERN = "brainwave_pattern"
    BEHAVIORAL_COHERENCE = "behavioral_coherence"
    CONSCIOUSNESS_SIGNATURE = "consciousness_signature"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    QUANTUM_ENTROPY = "quantum_entropy"
    REFLECTION_DEPTH = "reflection_depth"
    AWARENESS_RESONANCE = "awareness_resonance"


class AuthenticationMethod(Enum):
    """Authentication methods for different tiers"""

    PASSWORD = "password"
    EMOJI_PASSWORD = "emoji_password"
    WEBAUTHN_PASSKEY = "webauthn_passkey"
    BIOMETRIC_PATTERN = "biometric_pattern"
    CONSCIOUSNESS_SIGNATURE = "consciousness_signature"
    BRAINWAVE_AUTH = "brainwave_auth"
    QUANTUM_SIGNATURE = "quantum_signature"
    TRANSCENDENT_VERIFICATION = "transcendent_verification"


@dataclass
class AuthenticationCredential:
    """Structured authentication credential data"""

    method: AuthenticationMethod
    credential_data: dict[str, Any]
    confidence_level: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Biometric enhancement
    biometric_patterns: dict[BiometricPattern, float] = field(default_factory=dict)
    consciousness_coherence: float = 0.0
    anti_spoofing_score: float = 0.0
    liveness_verified: bool = False

    # Security validation
    device_fingerprint: Optional[str] = None
    location_context: Optional[dict[str, Any]] = None
    behavioral_context: Optional[dict[str, Any]] = None


@dataclass
class TierValidationResult:
    """Result of tier-specific authentication validation"""

    tier: str
    success: bool
    confidence_score: float
    validation_details: dict[str, Any] = field(default_factory=dict)
    biometric_scores: dict[str, float] = field(default_factory=dict)
    security_scores: dict[str, float] = field(default_factory=dict)
    consciousness_metrics: dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    validation_duration_ms: float = 0.0


class ConsciousnessWebAuthnManager:
    """Enhanced WebAuthn manager with consciousness biometric integration"""

    def __init__(self):
        self.base_webauthn_manager = WebAuthnPasskeyManager() if WebAuthnPasskeyManager else None

        # Consciousness-enhanced challenge storage
        self.consciousness_challenges: dict[str, dict[str, Any]] = {}
        self.biometric_patterns: dict[str, list[dict[str, Any]]] = {}

        # Advanced security features
        self.anti_spoofing_models: dict[str, Callable] = {}
        self.behavioral_analysis_enabled = True
        self.quantum_entropy_validation = True

        logger.info("🔐 Consciousness-enhanced WebAuthn manager initialized")

    async def initiate_consciousness_registration(
        self, identity_id: str, user_email: str, consciousness_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Initiate WebAuthn registration with consciousness enhancement"""

        try:
            # Generate base WebAuthn registration if available
            base_options = {}
            if self.base_webauthn_manager:
                base_options = self.base_webauthn_manager.initiate_registration(identity_id, user_email)

            # Generate consciousness-enhanced challenge
            consciousness_challenge = self._generate_consciousness_challenge(identity_id, consciousness_context)

            # Combine challenges
            enhanced_options = {
                "webauthn": base_options,
                "consciousness_challenge": consciousness_challenge,
                "biometric_requirements": {
                    "brainwave_patterns": consciousness_context.get("brainwave_enabled", False),
                    "behavioral_coherence": consciousness_context.get("behavioral_analysis", True),
                    "consciousness_signature": consciousness_context.get("consciousness_signature", False),
                    "quantum_entropy": consciousness_context.get("quantum_validation", False),
                },
                "session_id": consciousness_challenge["session_id"],
                "expires_at": consciousness_challenge["expires_at"],
            }

            logger.info(f"🧬 Initiated consciousness-enhanced WebAuthn registration for {identity_id}")
            return enhanced_options

        except Exception as e:
            logger.error(f"❌ Failed to initiate consciousness registration: {e}")
            raise ΛIDError(f"Consciousness registration failed: {e}")

    async def complete_consciousness_registration(
        self, identity_id: str, webauthn_credential: dict[str, Any], consciousness_data: dict[str, Any]
    ) -> bool:
        """Complete WebAuthn registration with consciousness validation"""

        try:
            # Validate consciousness challenge
            session_id = consciousness_data.get("session_id")
            if not session_id or session_id not in self.consciousness_challenges:
                logger.error(f"❌ Invalid consciousness session: {session_id}")
                return False

            challenge_data = self.consciousness_challenges[session_id]

            # Validate challenge expiration
            if datetime.now(timezone.utc) > datetime.fromisoformat(challenge_data["expires_at"]):
                logger.error(f"❌ Consciousness challenge expired for {identity_id}")
                del self.consciousness_challenges[session_id]
                return False

            # Complete base WebAuthn registration
            base_success = True
            if self.base_webauthn_manager:
                base_success = self.base_webauthn_manager.complete_registration(identity_id, webauthn_credential)

            if not base_success:
                logger.error(f"❌ Base WebAuthn registration failed for {identity_id}")
                return False

            # Process consciousness biometric data
            biometric_success = await self._process_consciousness_biometrics(
                identity_id, consciousness_data, "registration"
            )

            if biometric_success:
                # Clean up challenge
                del self.consciousness_challenges[session_id]
                logger.info(f"✅ Consciousness-enhanced WebAuthn registration completed for {identity_id}")
                return True
            else:
                logger.error(f"❌ Consciousness biometric validation failed for {identity_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Consciousness registration completion failed: {e}")
            return False

    async def initiate_consciousness_authentication(
        self, identity_id: str, authentication_tier: Optional[object] = None
    ) -> dict[str, Any]:
        """Initiate WebAuthn authentication with consciousness requirements"""

        try:
            # Generate base WebAuthn authentication if available
            base_options = {}
            if self.base_webauthn_manager:
                base_options = self.base_webauthn_manager.initiate_authentication(identity_id)

            # Determine consciousness requirements based on tier
            consciousness_requirements = self._get_tier_consciousness_requirements(authentication_tier)

            # Generate consciousness challenge
            consciousness_challenge = self._generate_consciousness_challenge(identity_id, consciousness_requirements)

            enhanced_options = {
                "webauthn": base_options,
                "consciousness_challenge": consciousness_challenge,
                "tier_requirements": consciousness_requirements,
                "session_id": consciousness_challenge["session_id"],
                "expires_at": consciousness_challenge["expires_at"],
            }

            logger.info(
                f"🔐 Initiated consciousness-enhanced authentication for {identity_id} (tier: {authentication_tier.value if authentication_tier else 'unknown'})"
            )
            return enhanced_options

        except Exception as e:
            logger.error(f"❌ Failed to initiate consciousness authentication: {e}")
            raise ΛIDError(f"Consciousness authentication initiation failed: {e}")

    async def verify_consciousness_authentication(
        self, identity_id: str, webauthn_assertion: dict[str, Any], consciousness_data: dict[str, Any]
    ) -> TierValidationResult:
        """Verify WebAuthn authentication with consciousness validation"""

        start_time = time.perf_counter()

        try:
            # Validate consciousness session
            session_id = consciousness_data.get("session_id")
            if not session_id or session_id not in self.consciousness_challenges:
                return TierValidationResult(
                    tier="unknown",
                    success=False,
                    confidence_score=0.0,
                    error_message="Invalid consciousness session",
                    validation_duration_ms=(time.perf_counter() - start_time) * 1000,
                )

            challenge_data = self.consciousness_challenges[session_id]

            # Verify base WebAuthn authentication
            base_success = True
            if self.base_webauthn_manager:
                base_success = self.base_webauthn_manager.verify_authentication(identity_id, webauthn_assertion)

            if not base_success:
                return TierValidationResult(
                    tier="T1_BASIC",
                    success=False,
                    confidence_score=0.0,
                    error_message="WebAuthn verification failed",
                    validation_duration_ms=(time.perf_counter() - start_time) * 1000,
                )

            # Process consciousness biometric validation
            biometric_result = await self._validate_consciousness_biometrics(
                identity_id, consciousness_data, challenge_data
            )

            # Determine authentication tier based on biometric results
            achieved_tier = self._determine_achieved_tier(biometric_result)

            # Calculate overall confidence
            base_confidence = 0.8  # WebAuthn base confidence
            consciousness_confidence = biometric_result.get("overall_confidence", 0.0)
            overall_confidence = (base_confidence * 0.4) + (consciousness_confidence * 0.6)

            # Clean up successful authentication
            if biometric_result.get("success", False):
                del self.consciousness_challenges[session_id]

            return TierValidationResult(
                tier=achieved_tier,
                success=biometric_result.get("success", False),
                confidence_score=overall_confidence,
                validation_details={"webauthn_success": base_success, "consciousness_validation": biometric_result},
                biometric_scores=biometric_result.get("biometric_scores", {}),
                security_scores={
                    "anti_spoofing": biometric_result.get("anti_spoofing_score", 0.0),
                    "liveness_detection": biometric_result.get("liveness_score", 0.0),
                },
                consciousness_metrics=biometric_result.get("consciousness_metrics", {}),
                validation_duration_ms=(time.perf_counter() - start_time) * 1000,
            )

        except Exception as e:
            logger.error(f"❌ Consciousness authentication verification failed: {e}")
            return TierValidationResult(
                tier="unknown",
                success=False,
                confidence_score=0.0,
                error_message=str(e),
                validation_duration_ms=(time.perf_counter() - start_time) * 1000,
            )

    def _generate_consciousness_challenge(self, identity_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """Generate consciousness-enhanced authentication challenge"""

        session_id = f"cs_{uuid.uuid4().hex[:16]}"
        challenge_bytes = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge_bytes).decode()

        # Generate consciousness-specific challenge components
        consciousness_challenge = {
            "session_id": session_id,
            "base_challenge": challenge_b64,
            "consciousness_seed": secrets.token_hex(16),
            "biometric_requirements": self._extract_biometric_requirements(context),
            "temporal_window_ms": 300000,  # 5 minute window
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        }

        # Add tier-specific requirements
        if context.get("authentication_tier"):
            tier_requirements = self._get_tier_consciousness_requirements(context["authentication_tier"])
            consciousness_challenge.update(tier_requirements)

        # Store challenge
        self.consciousness_challenges[session_id] = {
            "identity_id": identity_id,
            "challenge": consciousness_challenge,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": consciousness_challenge["expires_at"],
            "context": context,
        }

        return consciousness_challenge

    def _get_tier_consciousness_requirements(self, tier: Optional[object]) -> dict[str, Any]:
        """Get consciousness requirements for authentication tier"""

        if not tier or not AuthenticationTier:
            return {"minimum_consciousness_coherence": 0.5}

        tier_requirements = {
            "T1_BASIC": {
                "minimum_consciousness_coherence": 0.3,
                "required_biometric_patterns": [],
                "brainwave_validation": False,
                "quantum_entropy_required": False,
            },
            "T2_ENHANCED": {
                "minimum_consciousness_coherence": 0.5,
                "required_biometric_patterns": ["behavioral_coherence"],
                "brainwave_validation": False,
                "quantum_entropy_required": False,
            },
            "T3_CONSCIOUSNESS": {
                "minimum_consciousness_coherence": 0.7,
                "required_biometric_patterns": ["behavioral_coherence", "consciousness_signature"],
                "brainwave_validation": True,
                "minimum_brainwave_frequency": 30.0,
                "quantum_entropy_required": False,
            },
            "T4_QUANTUM": {
                "minimum_consciousness_coherence": 0.8,
                "required_biometric_patterns": ["behavioral_coherence", "consciousness_signature", "quantum_entropy"],
                "brainwave_validation": True,
                "minimum_brainwave_frequency": 40.0,
                "quantum_entropy_required": True,
                "minimum_quantum_entropy": 0.8,
            },
            "T5_TRANSCENDENT": {
                "minimum_consciousness_coherence": 0.9,
                "required_biometric_patterns": [
                    "behavioral_coherence",
                    "consciousness_signature",
                    "quantum_entropy",
                    "reflection_depth",
                ],
                "brainwave_validation": True,
                "minimum_brainwave_frequency": 60.0,
                "quantum_entropy_required": True,
                "minimum_quantum_entropy": 0.9,
                "transcendent_verification": True,
                "minimum_reflection_depth": 3,
            },
        }

        return tier_requirements.get(tier.value, tier_requirements["T1_BASIC"])

    def _extract_biometric_requirements(self, context: dict[str, Any]) -> list[str]:
        """Extract biometric requirements from context"""

        requirements = []

        if context.get("brainwave_enabled", False):
            requirements.append("brainwave_pattern")

        if context.get("behavioral_analysis", True):
            requirements.append("behavioral_coherence")

        if context.get("consciousness_signature", False):
            requirements.append("consciousness_signature")

        if context.get("quantum_validation", False):
            requirements.append("quantum_entropy")

        return requirements

    async def _process_consciousness_biometrics(
        self, identity_id: str, consciousness_data: dict[str, Any], operation: str
    ) -> bool:
        """Process and store consciousness biometric patterns"""

        try:
            # Extract biometric patterns
            biometric_patterns = {}

            if "brainwave_pattern" in consciousness_data:
                brainwave_data = consciousness_data["brainwave_pattern"]
                biometric_patterns["brainwave"] = self._process_brainwave_pattern(brainwave_data)

            if "behavioral_data" in consciousness_data:
                behavioral_data = consciousness_data["behavioral_data"]
                biometric_patterns["behavioral"] = self._process_behavioral_coherence(behavioral_data)

            if "consciousness_signature" in consciousness_data:
                consciousness_sig = consciousness_data["consciousness_signature"]
                biometric_patterns["consciousness"] = self._process_consciousness_signature(consciousness_sig)

            # Store patterns for identity
            if identity_id not in self.biometric_patterns:
                self.biometric_patterns[identity_id] = []

            pattern_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation,
                "patterns": biometric_patterns,
                "confidence_scores": {k: v.get("confidence", 0.0) for k, v in biometric_patterns.items()},
            }

            self.biometric_patterns[identity_id].append(pattern_entry)

            # Keep only last 10 patterns
            if len(self.biometric_patterns[identity_id]) > 10:
                self.biometric_patterns[identity_id] = self.biometric_patterns[identity_id][-10:]

            logger.debug(f"🧬 Processed consciousness biometrics for {identity_id}: {list(biometric_patterns.keys()}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process consciousness biometrics: {e}")
            return False

    async def _validate_consciousness_biometrics(
        self, identity_id: str, consciousness_data: dict[str, Any], challenge_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate consciousness biometric data against stored patterns and requirements"""

        try:
            validation_result = {
                "success": False,
                "overall_confidence": 0.0,
                "biometric_scores": {},
                "consciousness_metrics": {},
                "anti_spoofing_score": 0.0,
                "liveness_score": 0.0,
            }

            challenge_data.get("challenge", {}).get("biometric_requirements", [])
            tier_requirements = challenge_data.get("context", {}).get("tier_requirements", {})

            biometric_scores = []

            # Validate brainwave patterns
            if "brainwave_pattern" in consciousness_data:
                brainwave_score = self._validate_brainwave_pattern(
                    identity_id, consciousness_data["brainwave_pattern"], tier_requirements
                )
                validation_result["biometric_scores"]["brainwave"] = brainwave_score
                biometric_scores.append(brainwave_score)

            # Validate behavioral coherence
            if "behavioral_data" in consciousness_data:
                behavioral_score = self._validate_behavioral_coherence(
                    identity_id, consciousness_data["behavioral_data"], tier_requirements
                )
                validation_result["biometric_scores"]["behavioral"] = behavioral_score
                biometric_scores.append(behavioral_score)

            # Validate consciousness signature
            if "consciousness_signature" in consciousness_data:
                consciousness_score = self._validate_consciousness_signature(
                    identity_id, consciousness_data["consciousness_signature"], tier_requirements
                )
                validation_result["biometric_scores"]["consciousness"] = consciousness_score
                biometric_scores.append(consciousness_score)

            # Validate quantum entropy
            if "quantum_data" in consciousness_data:
                quantum_score = self._validate_quantum_entropy(consciousness_data["quantum_data"], tier_requirements)
                validation_result["biometric_scores"]["quantum"] = quantum_score
                biometric_scores.append(quantum_score)

            # Anti-spoofing validation
            validation_result["anti_spoofing_score"] = self._calculate_anti_spoofing_score(consciousness_data)

            # Liveness detection
            validation_result["liveness_score"] = self._calculate_liveness_score(consciousness_data)

            # Calculate overall confidence
            if biometric_scores:
                base_confidence = sum(biometric_scores) / len(biometric_scores)
                security_bonus = (
                    (validation_result["anti_spoofing_score"] + validation_result["liveness_score"]) / 2 * 0.1
                )
                validation_result["overall_confidence"] = min(1.0, base_confidence + security_bonus)

            # Determine success based on minimum requirements
            minimum_confidence = tier_requirements.get("minimum_consciousness_coherence", 0.5)
            validation_result["success"] = validation_result["overall_confidence"] >= minimum_confidence

            # Add consciousness metrics
            validation_result["consciousness_metrics"] = {
                "consciousness_coherence": validation_result["overall_confidence"],
                "biometric_pattern_count": len(biometric_scores),
                "security_validation_passed": validation_result["anti_spoofing_score"] > 0.7,
                "liveness_validated": validation_result["liveness_score"] > 0.8,
            }

            return validation_result

        except Exception as e:
            logger.error(f"❌ Consciousness biometric validation failed: {e}")
            return {"success": False, "error": str(e), "overall_confidence": 0.0}

    def _process_brainwave_pattern(self, brainwave_data: dict[str, Any]) -> dict[str, Any]:
        """Process and analyze brainwave patterns"""

        # Extract frequency bands
        delta = brainwave_data.get("delta", 0.0)  # 0.5-4 Hz
        theta = brainwave_data.get("theta", 0.0)  # 4-8 Hz
        alpha = brainwave_data.get("alpha", 0.0)  # 8-12 Hz
        beta = brainwave_data.get("beta", 0.0)  # 12-30 Hz
        gamma = brainwave_data.get("gamma", 0.0)  # 30+ Hz

        # Calculate consciousness indicators
        consciousness_frequency = alpha * 0.2 + beta * 0.3 + gamma * 0.5
        awareness_level = min(1.0, (alpha + beta + gamma) / 3.0)
        attention_focus = beta / max(1.0, alpha + theta + delta)  # Beta dominance indicates focus

        return {
            "frequency_bands": {"delta": delta, "theta": theta, "alpha": alpha, "beta": beta, "gamma": gamma},
            "consciousness_frequency": consciousness_frequency,
            "awareness_level": awareness_level,
            "attention_focus": attention_focus,
            "confidence": min(1.0, (consciousness_frequency + awareness_level) / 2),
        }

    def _process_behavioral_coherence(self, behavioral_data: dict[str, Any]) -> dict[str, Any]:
        """Process and analyze behavioral coherence patterns"""

        typing_rhythm = behavioral_data.get("typing_rhythm", {})
        mouse_patterns = behavioral_data.get("mouse_patterns", {})
        temporal_consistency = behavioral_data.get("temporal_consistency", 0.5)

        # Analyze typing rhythm
        typing_coherence = 0.5
        if typing_rhythm:
            keystroke_intervals = typing_rhythm.get("intervals", [])
            if keystroke_intervals:
                # Calculate rhythm consistency (lower std dev = higher coherence)
                import statistics

                if len(keystroke_intervals) > 1:
                    std_dev = statistics.stdev(keystroke_intervals)
                    mean_interval = statistics.mean(keystroke_intervals)
                    typing_coherence = max(0.0, 1.0 - (std_dev / max(mean_interval, 0.001)))

        # Analyze mouse patterns
        mouse_coherence = 0.5
        if mouse_patterns:
            movement_velocity = mouse_patterns.get("velocity_consistency", 0.5)
            click_patterns = mouse_patterns.get("click_rhythm", 0.5)
            mouse_coherence = (movement_velocity + click_patterns) / 2

        overall_coherence = (typing_coherence + mouse_coherence + temporal_consistency) / 3

        return {
            "typing_coherence": typing_coherence,
            "mouse_coherence": mouse_coherence,
            "temporal_consistency": temporal_consistency,
            "overall_coherence": overall_coherence,
            "confidence": overall_coherence,
        }

    def _process_consciousness_signature(self, consciousness_data: dict[str, Any]) -> dict[str, Any]:
        """Process consciousness signature patterns"""

        reflection_depth = consciousness_data.get("reflection_depth", 0)
        metacognition_level = consciousness_data.get("metacognition_level", 0.0)
        self_awareness_score = consciousness_data.get("self_awareness", 0.0)
        introspective_coherence = consciousness_data.get("introspective_coherence", 0.0)

        # Calculate consciousness signature strength
        signature_strength = (
            min(1.0, reflection_depth / 5.0) * 0.3
            + metacognition_level * 0.3
            + self_awareness_score * 0.2
            + introspective_coherence * 0.2
        )

        return {
            "reflection_depth": reflection_depth,
            "metacognition_level": metacognition_level,
            "self_awareness_score": self_awareness_score,
            "introspective_coherence": introspective_coherence,
            "signature_strength": signature_strength,
            "confidence": signature_strength,
        }

    def _validate_brainwave_pattern(
        self, identity_id: str, current_brainwave: dict[str, Any], requirements: dict[str, Any]
    ) -> float:
        """Validate brainwave patterns against stored patterns and requirements"""

        try:
            processed_brainwave = self._process_brainwave_pattern(current_brainwave)

            # Check minimum frequency requirements
            min_frequency = requirements.get("minimum_brainwave_frequency", 0.0)
            if processed_brainwave["consciousness_frequency"] < min_frequency:
                return 0.0

            # Compare with stored patterns if available
            stored_patterns = self.biometric_patterns.get(identity_id, [])
            if stored_patterns:
                # Find most recent brainwave patterns
                recent_brainwave_patterns = []
                for pattern_entry in stored_patterns:
                    if "brainwave" in pattern_entry["patterns"]:
                        recent_brainwave_patterns.append(pattern_entry["patterns"]["brainwave"])

                if recent_brainwave_patterns:
                    # Calculate similarity to stored patterns
                    similarities = []
                    for stored_pattern in recent_brainwave_patterns[-3:]:  # Last 3 patterns
                        similarity = self._calculate_brainwave_similarity(processed_brainwave, stored_pattern)
                        similarities.append(similarity)

                    pattern_match_score = sum(similarities) / len(similarities)
                    return min(1.0, processed_brainwave["confidence"] * 0.6 + pattern_match_score * 0.4)

            # No stored patterns - return base confidence
            return processed_brainwave["confidence"]

        except Exception as e:
            logger.error(f"❌ Brainwave pattern validation failed: {e}")
            return 0.0

    def _calculate_brainwave_similarity(self, current: dict[str, Any], stored: dict[str, Any]) -> float:
        """Calculate similarity between brainwave patterns"""

        try:
            current_bands = current["frequency_bands"]
            stored_bands = stored["frequency_bands"]

            # Calculate band similarities
            band_similarities = []
            for band in ["delta", "theta", "alpha", "beta", "gamma"]:
                current_val = current_bands.get(band, 0.0)
                stored_val = stored_bands.get(band, 0.0)

                # Calculate normalized difference
                max_val = max(current_val, stored_val, 0.001)
                similarity = 1.0 - abs(current_val - stored_val) / max_val
                band_similarities.append(similarity)

            # Weight gamma and beta more heavily (consciousness indicators)
            weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # delta, theta, alpha, beta, gamma
            weighted_similarity = sum(sim * weight for sim, weight in zip(band_similarities, weights))

            return max(0.0, weighted_similarity)

        except Exception as e:
            logger.error(f"❌ Brainwave similarity calculation failed: {e}")
            return 0.0

    def _validate_behavioral_coherence(
        self, identity_id: str, behavioral_data: dict[str, Any], requirements: dict[str, Any]
    ) -> float:
        """Validate behavioral coherence patterns"""

        try:
            processed_behavioral = self._process_behavioral_coherence(behavioral_data)

            # Check stored patterns for comparison
            stored_patterns = self.biometric_patterns.get(identity_id, [])
            if stored_patterns:
                recent_behavioral_patterns = []
                for pattern_entry in stored_patterns:
                    if "behavioral" in pattern_entry["patterns"]:
                        recent_behavioral_patterns.append(pattern_entry["patterns"]["behavioral"])

                if recent_behavioral_patterns:
                    # Calculate consistency with stored patterns
                    consistency_scores = []
                    for stored_pattern in recent_behavioral_patterns[-5:]:  # Last 5 patterns
                        consistency = self._calculate_behavioral_consistency(processed_behavioral, stored_pattern)
                        consistency_scores.append(consistency)

                    pattern_consistency = sum(consistency_scores) / len(consistency_scores)
                    return min(1.0, processed_behavioral["confidence"] * 0.5 + pattern_consistency * 0.5)

            return processed_behavioral["confidence"]

        except Exception as e:
            logger.error(f"❌ Behavioral coherence validation failed: {e}")
            return 0.0

    def _calculate_behavioral_consistency(self, current: dict[str, Any], stored: dict[str, Any]) -> float:
        """Calculate consistency between behavioral patterns"""

        try:
            # Compare coherence metrics
            current_coherence = current["overall_coherence"]
            stored_coherence = stored["overall_coherence"]

            coherence_similarity = 1.0 - abs(current_coherence - stored_coherence)

            # Compare specific patterns
            typing_consistency = 1.0 - abs(current["typing_coherence"] - stored["typing_coherence"])
            mouse_consistency = 1.0 - abs(current["mouse_coherence"] - stored["mouse_coherence"])
            temporal_consistency = 1.0 - abs(current["temporal_consistency"] - stored["temporal_consistency"])

            overall_consistency = (
                coherence_similarity * 0.4
                + typing_consistency * 0.3
                + mouse_consistency * 0.2
                + temporal_consistency * 0.1
            )

            return max(0.0, overall_consistency)

        except Exception as e:
            logger.error(f"❌ Behavioral consistency calculation failed: {e}")
            return 0.0

    def _validate_consciousness_signature(
        self, identity_id: str, consciousness_data: dict[str, Any], requirements: dict[str, Any]
    ) -> float:
        """Validate consciousness signature patterns"""

        try:
            processed_consciousness = self._process_consciousness_signature(consciousness_data)

            # Check minimum reflection depth requirement
            min_reflection_depth = requirements.get("minimum_reflection_depth", 0)
            if processed_consciousness["reflection_depth"] < min_reflection_depth:
                return 0.0

            return processed_consciousness["confidence"]

        except Exception as e:
            logger.error(f"❌ Consciousness signature validation failed: {e}")
            return 0.0

    def _validate_quantum_entropy(self, quantum_data: dict[str, Any], requirements: dict[str, Any]) -> float:
        """Validate quantum entropy patterns"""

        try:
            entropy_score = quantum_data.get("entropy_score", 0.0)
            quantum_signature = quantum_data.get("quantum_signature", "")
            coherence_measure = quantum_data.get("coherence", 0.0)

            # Check minimum entropy requirement
            min_entropy = requirements.get("minimum_quantum_entropy", 0.0)
            if entropy_score < min_entropy:
                return 0.0

            # Validate quantum signature format
            signature_valid = len(quantum_signature) >= 16 and all(c in "0123456789abcdef" for c in quantum_signature)

            if not signature_valid:
                return 0.0

            # Calculate quantum validation score
            quantum_score = entropy_score * 0.5 + coherence_measure * 0.5

            return quantum_score

        except Exception as e:
            logger.error(f"❌ Quantum entropy validation failed: {e}")
            return 0.0

    def _calculate_anti_spoofing_score(self, consciousness_data: dict[str, Any]) -> float:
        """Calculate anti-spoofing score based on consciousness data authenticity"""

        try:
            # Check for multiple data sources (harder to spoof)
            data_sources = 0
            if "brainwave_pattern" in consciousness_data:
                data_sources += 1
            if "behavioral_data" in consciousness_data:
                data_sources += 1
            if "consciousness_signature" in consciousness_data:
                data_sources += 1
            if "quantum_data" in consciousness_data:
                data_sources += 1

            diversity_score = min(1.0, data_sources / 4.0)

            # Check for temporal consistency indicators
            temporal_indicators = consciousness_data.get("temporal_consistency", 0.5)

            # Check for device fingerprint consistency
            device_consistency = consciousness_data.get("device_fingerprint_match", 0.8)

            # Combine anti-spoofing factors
            anti_spoofing_score = diversity_score * 0.4 + temporal_indicators * 0.3 + device_consistency * 0.3

            return anti_spoofing_score

        except Exception as e:
            logger.error(f"❌ Anti-spoofing score calculation failed: {e}")
            return 0.0

    def _calculate_liveness_score(self, consciousness_data: dict[str, Any]) -> float:
        """Calculate liveness detection score"""

        try:
            # Check for real-time consciousness indicators
            realtime_brainwave = consciousness_data.get("realtime_brainwave", False)
            active_behavioral_patterns = consciousness_data.get("active_behavioral", False)
            consciousness_variability = consciousness_data.get("consciousness_variability", 0.0)

            liveness_indicators = [
                1.0 if realtime_brainwave else 0.0,
                1.0 if active_behavioral_patterns else 0.0,
                min(1.0, consciousness_variability),  # Some variability indicates liveness
            ]

            liveness_score = sum(liveness_indicators) / len(liveness_indicators)

            return liveness_score

        except Exception as e:
            logger.error(f"❌ Liveness score calculation failed: {e}")
            return 0.0

    def _determine_achieved_tier(self, biometric_result: dict[str, Any]) -> str:
        """Determine achieved authentication tier based on biometric validation results"""

        overall_confidence = biometric_result.get("overall_confidence", 0.0)
        biometric_scores = biometric_result.get("biometric_scores", {})

        # T5 Transcendent - Requires all advanced patterns
        if overall_confidence >= 0.9 and len(biometric_scores) >= 3 and biometric_scores.get("quantum", 0.0) >= 0.9:
            return "T5_TRANSCENDENT"

        # T4 Quantum - Requires quantum validation
        elif overall_confidence >= 0.8 and biometric_scores.get("quantum", 0.0) >= 0.8:
            return "T4_QUANTUM"

        # T3 Consciousness - Requires consciousness signature
        elif overall_confidence >= 0.7 and (
            biometric_scores.get("consciousness", 0.0) >= 0.7 or biometric_scores.get("brainwave", 0.0) >= 0.7
        ):
            return "T3_CONSCIOUSNESS"

        # T2 Enhanced - Requires behavioral coherence
        elif overall_confidence >= 0.5 and biometric_scores.get("behavioral", 0.0) >= 0.5:
            return "T2_ENHANCED"

        # T1 Basic - Minimum authentication
        else:
            return "T1_BASIC"


class TieredAuthenticationEngine:
    """Main tiered authentication engine with consciousness integration"""

    def __init__(self):
        self.consciousness_webauthn = ConsciousnessWebAuthnManager()
        self.legacy_identity_service = LukhasIdentityService() if LukhasIdentityService else None

        # Authentication method handlers
        self.method_handlers = {
            AuthenticationMethod.WEBAUTHN_PASSKEY: self._handle_webauthn_authentication,
            AuthenticationMethod.CONSCIOUSNESS_SIGNATURE: self._handle_consciousness_authentication,
            AuthenticationMethod.BRAINWAVE_AUTH: self._handle_brainwave_authentication,
            AuthenticationMethod.QUANTUM_SIGNATURE: self._handle_quantum_authentication,
            AuthenticationMethod.TRANSCENDENT_VERIFICATION: self._handle_transcendent_authentication,
        }

        # Performance tracking
        self.authentication_metrics = {
            "total_authentications": 0,
            "successful_authentications": 0,
            "tier_distribution": {},
            "average_latency_ms": 0.0,
            "consciousness_validation_rate": 0.0,
        }

        logger.info("🎯 Tiered authentication engine initialized with consciousness integration")

    async def authenticate_with_tier(
        self,
        identity_id: str,
        authentication_credentials: list[AuthenticationCredential],
        target_tier: Optional[object] = None,
    ) -> TierValidationResult:
        """Authenticate user with specified tier requirements"""

        start_time = time.perf_counter()

        try:
            self.authentication_metrics["total_authentications"] += 1

            # Determine authentication methods available
            [cred.method for cred in authentication_credentials]

            # Process each authentication method
            validation_results = []

            for credential in authentication_credentials:
                if credential.method in self.method_handlers:
                    handler = self.method_handlers[credential.method]
                    result = await handler(identity_id, credential, target_tier)
                    validation_results.append(result)
                else:
                    logger.warning(f"⚠️ Unsupported authentication method: {credential.method}")

            # Combine validation results
            final_result = self._combine_validation_results(validation_results, target_tier)
            final_result.validation_duration_ms = (time.perf_counter() - start_time) * 1000

            # Update metrics
            if final_result.success:
                self.authentication_metrics["successful_authentications"] += 1

                # Update tier distribution
                tier = final_result.tier
                self.authentication_metrics["tier_distribution"][tier] = (
                    self.authentication_metrics["tier_distribution"].get(tier, 0) + 1
                )

            # Emit consciousness authentication signals if available
            if consciousness_identity_signal_emitter and final_result.success:
                await consciousness_identity_signal_emitter.emit_authentication_success_signal(
                    identity_id,
                    target_tier or (AuthenticationTier.T1_BASIC if AuthenticationTier else None),
                    final_result.confidence_score,
                    final_result.consciousness_metrics.get("consciousness_coherence", 0.0),
                    max(final_result.biometric_scores.values()) if final_result.biometric_scores else 0.0,
                )

            return final_result

        except Exception as e:
            logger.error(f"❌ Tiered authentication failed: {e}")
            return TierValidationResult(
                tier="unknown",
                success=False,
                confidence_score=0.0,
                error_message=str(e),
                validation_duration_ms=(time.perf_counter() - start_time) * 1000,
            )

    async def _handle_webauthn_authentication(
        self, identity_id: str, credential: AuthenticationCredential, target_tier: Optional[object]
    ) -> TierValidationResult:
        """Handle WebAuthn passkey authentication with consciousness enhancement"""

        try:
            # Extract WebAuthn assertion from credential
            webauthn_assertion = credential.credential_data.get("webauthn_assertion", {})
            consciousness_data = credential.credential_data.get("consciousness_data", {})

            # Perform consciousness-enhanced WebAuthn verification
            result = await self.consciousness_webauthn.verify_consciousness_authentication(
                identity_id, webauthn_assertion, consciousness_data
            )

            return result

        except Exception as e:
            logger.error(f"❌ WebAuthn authentication failed: {e}")
            return TierValidationResult(tier="T1_BASIC", success=False, confidence_score=0.0, error_message=str(e))

    async def _handle_consciousness_authentication(
        self, identity_id: str, credential: AuthenticationCredential, target_tier: Optional[object]
    ) -> TierValidationResult:
        """Handle pure consciousness signature authentication"""

        try:
            consciousness_signature = credential.credential_data.get("consciousness_signature", {})

            # Validate consciousness signature
            reflection_depth = consciousness_signature.get("reflection_depth", 0)
            metacognition_level = consciousness_signature.get("metacognition_level", 0.0)
            self_awareness = consciousness_signature.get("self_awareness", 0.0)

            # Calculate consciousness authentication score
            consciousness_score = (
                min(1.0, reflection_depth / 5.0) * 0.4 + metacognition_level * 0.3 + self_awareness * 0.3
            )

            success = consciousness_score >= 0.6  # Minimum threshold for consciousness auth

            return TierValidationResult(
                tier="T3_CONSCIOUSNESS" if success else "T1_BASIC",
                success=success,
                confidence_score=consciousness_score,
                consciousness_metrics={
                    "consciousness_coherence": consciousness_score,
                    "reflection_depth": reflection_depth,
                    "metacognition_level": metacognition_level,
                    "self_awareness": self_awareness,
                },
            )

        except Exception as e:
            logger.error(f"❌ Consciousness authentication failed: {e}")
            return TierValidationResult(tier="T1_BASIC", success=False, confidence_score=0.0, error_message=str(e))

    async def _handle_brainwave_authentication(
        self, identity_id: str, credential: AuthenticationCredential, target_tier: Optional[object]
    ) -> TierValidationResult:
        """Handle brainwave pattern authentication"""

        try:
            brainwave_data = credential.credential_data.get("brainwave_pattern", {})

            # Process brainwave patterns
            processed_brainwave = self.consciousness_webauthn._process_brainwave_pattern(brainwave_data)

            # Validate against stored patterns
            brainwave_score = self.consciousness_webauthn._validate_brainwave_pattern(
                identity_id, brainwave_data, {"minimum_brainwave_frequency": 30.0}
            )

            success = brainwave_score >= 0.7

            return TierValidationResult(
                tier="T3_CONSCIOUSNESS" if success else "T1_BASIC",
                success=success,
                confidence_score=brainwave_score,
                biometric_scores={"brainwave": brainwave_score},
                consciousness_metrics={
                    "consciousness_frequency": processed_brainwave["consciousness_frequency"],
                    "awareness_level": processed_brainwave["awareness_level"],
                    "attention_focus": processed_brainwave["attention_focus"],
                },
            )

        except Exception as e:
            logger.error(f"❌ Brainwave authentication failed: {e}")
            return TierValidationResult(tier="T1_BASIC", success=False, confidence_score=0.0, error_message=str(e))

    async def _handle_quantum_authentication(
        self, identity_id: str, credential: AuthenticationCredential, target_tier: Optional[object]
    ) -> TierValidationResult:
        """Handle quantum signature authentication"""

        try:
            quantum_data = credential.credential_data.get("quantum_signature", {})

            # Validate quantum signature
            quantum_score = self.consciousness_webauthn._validate_quantum_entropy(
                quantum_data, {"minimum_quantum_entropy": 0.8}
            )

            success = quantum_score >= 0.8

            return TierValidationResult(
                tier="T4_QUANTUM" if success else "T1_BASIC",
                success=success,
                confidence_score=quantum_score,
                biometric_scores={"quantum": quantum_score},
                consciousness_metrics={
                    "quantum_entropy": quantum_data.get("entropy_score", 0.0),
                    "quantum_coherence": quantum_data.get("coherence", 0.0),
                },
            )

        except Exception as e:
            logger.error(f"❌ Quantum authentication failed: {e}")
            return TierValidationResult(tier="T1_BASIC", success=False, confidence_score=0.0, error_message=str(e))

    async def _handle_transcendent_authentication(
        self, identity_id: str, credential: AuthenticationCredential, target_tier: Optional[object]
    ) -> TierValidationResult:
        """Handle transcendent consciousness verification"""

        try:
            transcendent_data = credential.credential_data

            # Require multiple consciousness factors for transcendent tier
            required_patterns = ["brainwave_pattern", "consciousness_signature", "quantum_signature"]
            available_patterns = [pattern for pattern in required_patterns if pattern in transcendent_data]

            if len(available_patterns) < 3:
                return TierValidationResult(
                    tier="T1_BASIC",
                    success=False,
                    confidence_score=0.0,
                    error_message="Insufficient consciousness patterns for transcendent verification",
                )

            # Validate all patterns with high thresholds
            pattern_scores = {}

            # Brainwave validation
            if "brainwave_pattern" in transcendent_data:
                pattern_scores["brainwave"] = self.consciousness_webauthn._validate_brainwave_pattern(
                    identity_id, transcendent_data["brainwave_pattern"], {"minimum_brainwave_frequency": 60.0}
                )

            # Consciousness signature validation
            if "consciousness_signature" in transcendent_data:
                consciousness_result = await self._handle_consciousness_authentication(
                    identity_id, credential, target_tier
                )
                pattern_scores["consciousness"] = consciousness_result.confidence_score

            # Quantum validation
            if "quantum_signature" in transcendent_data:
                pattern_scores["quantum"] = self.consciousness_webauthn._validate_quantum_entropy(
                    transcendent_data["quantum_signature"], {"minimum_quantum_entropy": 0.9}
                )

            # All patterns must meet transcendent thresholds
            transcendent_threshold = 0.9
            transcendent_success = all(score >= transcendent_threshold for score in pattern_scores.values())
            overall_confidence = sum(pattern_scores.values()) / len(pattern_scores) if pattern_scores else 0.0

            return TierValidationResult(
                tier="T5_TRANSCENDENT" if transcendent_success else "T3_CONSCIOUSNESS",
                success=transcendent_success,
                confidence_score=overall_confidence,
                biometric_scores=pattern_scores,
                consciousness_metrics={
                    "transcendent_patterns_validated": len(pattern_scores),
                    "transcendent_threshold_met": transcendent_success,
                    "consciousness_coherence": overall_confidence,
                },
            )

        except Exception as e:
            logger.error(f"❌ Transcendent authentication failed: {e}")
            return TierValidationResult(tier="T1_BASIC", success=False, confidence_score=0.0, error_message=str(e))

    def _combine_validation_results(
        self, results: list[TierValidationResult], target_tier: Optional[object]
    ) -> TierValidationResult:
        """Combine multiple validation results into final authentication result"""

        if not results:
            return TierValidationResult(
                tier="unknown", success=False, confidence_score=0.0, error_message="No validation results available"
            )

        # Filter successful results
        successful_results = [r for r in results if r.success]

        if not successful_results:
            # Return the best unsuccessful result
            best_result = max(results, key=lambda r: r.confidence_score)
            return best_result

        # Find highest tier achieved
        tier_hierarchy = ["T1_BASIC", "T2_ENHANCED", "T3_CONSCIOUSNESS", "T4_QUANTUM", "T5_TRANSCENDENT"]
        achieved_tiers = [r.tier for r in successful_results]

        highest_tier = "T1_BASIC"
        for tier in reversed(tier_hierarchy):
            if tier in achieved_tiers:
                highest_tier = tier
                break

        # Combine confidence scores (weighted by tier level)
        tier_weights = {"T1_BASIC": 1, "T2_ENHANCED": 2, "T3_CONSCIOUSNESS": 3, "T4_QUANTUM": 4, "T5_TRANSCENDENT": 5}

        weighted_confidence = 0.0
        total_weight = 0.0

        for result in successful_results:
            weight = tier_weights.get(result.tier, 1)
            weighted_confidence += result.confidence_score * weight
            total_weight += weight

        final_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0

        # Combine biometric and consciousness metrics
        combined_biometric_scores = {}
        combined_consciousness_metrics = {}

        for result in successful_results:
            combined_biometric_scores.update(result.biometric_scores)
            combined_consciousness_metrics.update(result.consciousness_metrics)

        return TierValidationResult(
            tier=highest_tier,
            success=True,
            confidence_score=final_confidence,
            biometric_scores=combined_biometric_scores,
            consciousness_metrics=combined_consciousness_metrics,
            validation_details={
                "successful_methods": len(successful_results),
                "total_methods": len(results),
                "achieved_tiers": achieved_tiers,
            },
        )

    async def get_authentication_metrics(self) -> dict[str, Any]:
        """Get comprehensive authentication metrics"""

        total_auths = self.authentication_metrics["total_authentications"]

        return {
            "total_authentications": total_auths,
            "successful_authentications": self.authentication_metrics["successful_authentications"],
            "success_rate": (self.authentication_metrics["successful_authentications"] / max(total_auths, 1)) * 100,
            "tier_distribution": self.authentication_metrics["tier_distribution"].copy(),
            "average_latency_ms": self.authentication_metrics["average_latency_ms"],
            "consciousness_validation_rate": self.authentication_metrics["consciousness_validation_rate"],
            "supported_authentication_methods": [method.value for method in AuthenticationMethod],
            "supported_tiers": [tier.value for tier in AuthenticationTier] if AuthenticationTier else [],
            "consciousness_webauthn_enabled": True,
            "legacy_identity_integration": self.legacy_identity_service is not None,
        }


# Global tiered authentication engine instance
tiered_authentication_engine = TieredAuthenticationEngine()


# Export key classes
__all__ = [
    "AuthenticationCredential",
    "AuthenticationMethod",
    "BiometricPattern",
    "ConsciousnessWebAuthnManager",
    "TierValidationResult",
    "TieredAuthenticationEngine",
    "tiered_authentication_engine",
]