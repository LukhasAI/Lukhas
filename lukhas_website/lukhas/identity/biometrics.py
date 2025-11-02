"""
LUKHAS Mock Biometric Authentication Service for T5
==================================================

Mock biometric authentication service for T5 tier authentication within the LUKHAS
tiered authentication system. Provides realistic biometric simulation with test keys,
confidence scoring, and comprehensive security monitoring.

Features:
- Mock biometric attestation with realistic confidence scoring
- Multiple biometric modalities (fingerprint, face, voice, iris)
- Anti-spoofing detection simulation
- Guardian system integration
- Performance monitoring (<50ms p95 latency)
- Comprehensive audit trails for compliance
- Test key management for development/testing

Note: This is a mock implementation for development and testing purposes.
Production deployments should integrate with real biometric authentication providers.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import structlog

# Import Guardian system for security validation
try:
    from ..governance.guardian_system import GuardianSystem
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False

logger = structlog.get_logger(__name__)


class BiometricModality(Enum):
    """Supported biometric authentication modalities."""

    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    IRIS = "iris"
    PALM = "palm"
    RETINA = "retina"


class BiometricQuality(Enum):
    """Biometric sample quality levels."""

    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


@dataclass
class BiometricTemplate:
    """Mock biometric template for user enrollment."""

    template_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    modality: BiometricModality = BiometricModality.FINGERPRINT
    template_data: str = ""  # Base64-encoded mock template
    quality_score: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None
    usage_count: int = 0

    # Security metadata
    enrollment_device: str = "unknown"
    encryption_key_id: str = ""
    anti_spoofing_verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            "template_id": self.template_id,
            "user_id": self.user_id,
            "modality": self.modality.value,
            "template_data": self.template_data,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "enrollment_device": self.enrollment_device,
            "encryption_key_id": self.encryption_key_id,
            "anti_spoofing_verified": self.anti_spoofing_verified
        }


@dataclass
class BiometricSample:
    """Biometric sample for authentication."""

    sample_id: str = field(default_factory=lambda: str(uuid4()))
    modality: BiometricModality = BiometricModality.FINGERPRINT
    sample_data: str = ""  # Base64-encoded mock sample
    quality_score: float = 0.0

    # Capture metadata
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    capture_device: str = "unknown"
    capture_environment: str = "unknown"

    # Anti-spoofing metadata
    liveness_score: float = 0.0
    anti_spoofing_passed: bool = False
    spoof_detection_methods: List[str] = field(default_factory=list)


@dataclass
class BiometricMatchResult:
    """Result of biometric template matching."""

    match_score: float = 0.0
    confidence: float = 0.0
    decision: str = "reject"  # accept, reject, inconclusive

    # Matching metadata
    template_id: str = ""
    sample_id: str = ""
    match_time_ms: float = 0.0

    # Quality factors
    template_quality: float = 0.0
    sample_quality: float = 0.0
    quality_degradation: float = 0.0

    # Security factors
    anti_spoofing_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class BiometricAttestation:
    """Biometric attestation for T5 authentication."""

    attestation_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    modality: BiometricModality = BiometricModality.FINGERPRINT

    # Authentication result
    authenticated: bool = False
    confidence: float = 0.0
    match_score: float = 0.0

    # Security attestation
    anti_spoofing_passed: bool = False
    liveness_verified: bool = False
    device_attestation: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    nonce: str = field(default_factory=lambda: secrets.token_hex(16))
    signature: str = ""

    # Performance data
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert attestation to dictionary representation."""
        return {
            "attestation_id": self.attestation_id,
            "user_id": self.user_id,
            "modality": self.modality.value,
            "authenticated": self.authenticated,
            "confidence": self.confidence,
            "match_score": self.match_score,
            "anti_spoofing_passed": self.anti_spoofing_passed,
            "liveness_verified": self.liveness_verified,
            "device_attestation": self.device_attestation,
            "created_at": self.created_at.isoformat(),
            "nonce": self.nonce,
            "signature": self.signature,
            "processing_time_ms": self.processing_time_ms
        }


class MockBiometricProvider:
    """
    Mock biometric authentication provider for T5 tier authentication.

    Simulates realistic biometric authentication with configurable success rates,
    quality scoring, and anti-spoofing detection for development and testing.
    """

    def __init__(
        self,
        provider_id: str = "lukhas_mock_biometric",
        base_success_rate: float = 0.95,
        quality_threshold: float = 0.7,
        confidence_threshold: float = 0.95,
        guardian_system: Optional[GuardianSystem] = None
    ):
        """Initialize mock biometric provider."""
        self.provider_id = provider_id
        self.base_success_rate = base_success_rate
        self.quality_threshold = quality_threshold
        self.confidence_threshold = confidence_threshold
        self.guardian = guardian_system

        self.logger = logger.bind(component="MockBiometricProvider")

        # Template storage (in production, use secure encrypted database)
        self._templates: Dict[str, BiometricTemplate] = {}
        self._user_templates: Dict[str, List[str]] = {}

        # Test keys and configuration
        self._test_keys = self._generate_test_keys()
        self._device_attestation_keys = self._generate_device_keys()

        # Performance tracking
        self._performance_metrics = {
            "enrollment_times": [],
            "authentication_times": [],
            "total_authentications": 0,
            "successful_authentications": 0
        }

        # Security state
        self._used_nonces: Set[str] = set()
        self._recent_authentications: Dict[str, List[datetime]] = {}

        self.logger.info("Mock biometric provider initialized",
                        provider_id=provider_id, success_rate=base_success_rate)

    def _generate_test_keys(self) -> Dict[str, str]:
        """Generate mock test keys for biometric operations."""
        return {
            "signing_key": secrets.token_hex(32),
            "encryption_key": secrets.token_hex(32),
            "template_key": secrets.token_hex(32),
            "attestation_key": secrets.token_hex(32)
        }

    def _generate_device_keys(self) -> Dict[str, Dict[str, str]]:
        """Generate mock device attestation keys."""
        return {
            "trusted_device_1": {
                "device_id": "dev_fingerprint_001",
                "attestation_key": secrets.token_hex(32),
                "certificate": "mock_cert_fingerprint_001"
            },
            "trusted_device_2": {
                "device_id": "dev_face_001",
                "attestation_key": secrets.token_hex(32),
                "certificate": "mock_cert_face_001"
            }
        }

    async def enroll_biometric(
        self,
        user_id: str,
        modality: BiometricModality,
        sample_data: str,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Enroll biometric template for user.

        Args:
            user_id: User identifier
            modality: Biometric modality (fingerprint, face, etc.)
            sample_data: Base64-encoded biometric sample
            device_info: Capture device information

        Returns:
            Tuple of (success, template_id or error_message)
        """
        start_time = time.perf_counter()

        try:
            # Guardian pre-validation
            if self.guardian:
                await self._guardian_validate("biometric_enrollment", {
                    "user_id": user_id,
                    "modality": modality.value,
                    "device_info": device_info
                })

            # Validate sample quality
            quality_score = await self._assess_sample_quality(sample_data, modality)
            if quality_score < self.quality_threshold:
                return False, f"Sample quality too low: {quality_score:.2f}"

            # Generate mock template
            template = BiometricTemplate(
                user_id=user_id,
                modality=modality,
                template_data=await self._generate_mock_template(sample_data, modality),
                quality_score=quality_score,
                enrollment_device=device_info.get("device_id", "unknown") if device_info else "unknown",
                encryption_key_id=self._test_keys["template_key"],
                anti_spoofing_verified=True  # Mock anti-spoofing always passes
            )

            # Store template
            self._templates[template.template_id] = template

            if user_id not in self._user_templates:
                self._user_templates[user_id] = []
            self._user_templates[user_id].append(template.template_id)

            # Performance tracking
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._performance_metrics["enrollment_times"].append(duration_ms)

            # Guardian post-monitoring
            if self.guardian:
                await self._guardian_monitor("biometric_enrolled", {
                    "user_id": user_id,
                    "template_id": template.template_id,
                    "modality": modality.value,
                    "quality_score": quality_score,
                    "duration_ms": duration_ms
                })

            self.logger.info("Biometric template enrolled",
                           user_id=user_id, template_id=template.template_id,
                           modality=modality.value, quality_score=quality_score)

            return True, template.template_id

        except Exception as e:
            self.logger.error("Biometric enrollment failed",
                            user_id=user_id, modality=modality.value, error=str(e))
            return False, f"Enrollment error: {e!s}"

    async def authenticate_biometric(
        self,
        user_id: str,
        sample_data: str,
        modality: BiometricModality,
        nonce: str,
        device_info: Optional[Dict[str, Any]] = None
    ) -> BiometricAttestation:
        """
        Authenticate user using biometric sample.

        Args:
            user_id: User identifier
            sample_data: Base64-encoded biometric sample
            modality: Biometric modality
            nonce: Anti-replay nonce
            device_info: Capture device information

        Returns:
            BiometricAttestation with authentication result
        """
        start_time = time.perf_counter()

        try:
            # Check nonce uniqueness (anti-replay protection)
            if nonce in self._used_nonces:
                return BiometricAttestation(
                    user_id=user_id,
                    modality=modality,
                    authenticated=False,
                    confidence=0.0,
                    processing_time_ms=(time.perf_counter() - start_time) * 1000
                )

            self._used_nonces.add(nonce)

            # Guardian pre-validation
            if self.guardian:
                await self._guardian_validate("biometric_authentication", {
                    "user_id": user_id,
                    "modality": modality.value,
                    "nonce": nonce
                })

            # Rate limiting check
            if await self._is_rate_limited(user_id):
                return BiometricAttestation(
                    user_id=user_id,
                    modality=modality,
                    authenticated=False,
                    confidence=0.0,
                    processing_time_ms=(time.perf_counter() - start_time) * 1000
                )

            # Check if user has enrolled templates
            user_template_ids = self._user_templates.get(user_id, [])
            if not user_template_ids:
                return BiometricAttestation(
                    user_id=user_id,
                    modality=modality,
                    authenticated=False,
                    confidence=0.0,
                    processing_time_ms=(time.perf_counter() - start_time) * 1000
                )

            # Create biometric sample
            sample = BiometricSample(
                modality=modality,
                sample_data=sample_data,
                quality_score=await self._assess_sample_quality(sample_data, modality),
                capture_device=device_info.get("device_id", "unknown") if device_info else "unknown"
            )

            # Anti-spoofing detection
            liveness_result = await self._detect_liveness(sample)
            sample.liveness_score = liveness_result["score"]
            sample.anti_spoofing_passed = liveness_result["passed"]
            sample.spoof_detection_methods = liveness_result["methods"]

            if not sample.anti_spoofing_passed:
                return BiometricAttestation(
                    user_id=user_id,
                    modality=modality,
                    authenticated=False,
                    confidence=0.0,
                    anti_spoofing_passed=False,
                    processing_time_ms=(time.perf_counter() - start_time) * 1000
                )

            # Find matching templates
            best_match = await self._find_best_match(sample, user_template_ids, modality)

            # Determine authentication result
            authenticated = (
                best_match.confidence >= self.confidence_threshold and
                best_match.decision == "accept" and
                sample.anti_spoofing_passed
            )

            # Generate device attestation
            device_attestation = await self._generate_device_attestation(device_info)

            # Create attestation
            attestation = BiometricAttestation(
                user_id=user_id,
                modality=modality,
                authenticated=authenticated,
                confidence=best_match.confidence,
                match_score=best_match.match_score,
                anti_spoofing_passed=sample.anti_spoofing_passed,
                liveness_verified=sample.liveness_score > 0.8,
                device_attestation=device_attestation,
                nonce=nonce,
                processing_time_ms=(time.perf_counter() - start_time) * 1000
            )

            # Sign attestation
            attestation.signature = await self._sign_attestation(attestation)

            # Update template usage
            if authenticated and best_match.template_id:
                await self._update_template_usage(best_match.template_id)

            # Record authentication attempt
            await self._record_authentication_attempt(user_id)

            # Performance tracking
            self._performance_metrics["authentication_times"].append(attestation.processing_time_ms)
            self._performance_metrics["total_authentications"] += 1
            if authenticated:
                self._performance_metrics["successful_authentications"] += 1

            # Guardian post-monitoring
            if self.guardian:
                await self._guardian_monitor("biometric_authentication_completed", {
                    "user_id": user_id,
                    "modality": modality.value,
                    "authenticated": authenticated,
                    "confidence": best_match.confidence,
                    "duration_ms": attestation.processing_time_ms
                })

            self.logger.info("Biometric authentication completed",
                           user_id=user_id, modality=modality.value,
                           authenticated=authenticated, confidence=best_match.confidence)

            return attestation

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.error("Biometric authentication failed",
                            user_id=user_id, modality=modality.value, error=str(e))

            return BiometricAttestation(
                user_id=user_id,
                modality=modality,
                authenticated=False,
                confidence=0.0,
                processing_time_ms=duration_ms
            )

    async def _assess_sample_quality(self, sample_data: str, modality: BiometricModality) -> float:
        """Assess biometric sample quality."""
        try:
            # Mock quality assessment based on data length and modality
            data_length = len(sample_data)

            base_quality = 0.7

            # Length-based quality adjustment
            if data_length > 1000:
                base_quality += 0.2
            elif data_length > 500:
                base_quality += 0.1

            # Modality-specific adjustments
            modality_multipliers = {
                BiometricModality.FINGERPRINT: 1.0,
                BiometricModality.FACE: 0.95,
                BiometricModality.IRIS: 1.1,
                BiometricModality.VOICE: 0.85,
                BiometricModality.PALM: 0.9
            }

            quality = base_quality * modality_multipliers.get(modality, 1.0)

            # Add some realistic variance
            import random
            quality += random.uniform(-0.1, 0.1)

            return max(0.0, min(1.0, quality))

        except Exception:
            return 0.5  # Fallback quality score

    async def _generate_mock_template(self, sample_data: str, modality: BiometricModality) -> str:
        """Generate mock biometric template from sample."""
        # Create deterministic template based on sample data
        template_hash = hashlib.sha256(
            f"{sample_data}_{modality.value}_{self._test_keys['template_key']}".encode()
        ).hexdigest()

        # Mock template structure
        template = {
            "version": "1.0",
            "modality": modality.value,
            "features": template_hash[:64],  # Mock feature vector
            "minutiae": template_hash[64:128] if len(template_hash) > 64 else template_hash,
            "encryption": "aes256"
        }

        return base64.b64encode(json.dumps(template).encode()).decode()

    async def _detect_liveness(self, sample: BiometricSample) -> Dict[str, Any]:
        """Mock liveness detection for anti-spoofing."""
        # Mock liveness detection with high success rate
        base_score = 0.9

        # Add some realistic variance
        import random
        variance = random.uniform(-0.1, 0.1)
        liveness_score = max(0.0, min(1.0, base_score + variance))

        # Mock detection methods
        methods = [
            "pulse_detection",
            "micro_movement_analysis",
            "texture_analysis",
            "depth_estimation"
        ]

        return {
            "score": liveness_score,
            "passed": liveness_score > 0.8,
            "methods": methods[:2] if sample.modality == BiometricModality.FINGERPRINT else methods
        }

    async def _find_best_match(
        self,
        sample: BiometricSample,
        template_ids: List[str],
        modality: BiometricModality
    ) -> BiometricMatchResult:
        """Find best matching template for the sample."""
        best_score = 0.0
        best_template_id = ""

        for template_id in template_ids:
            if template_id not in self._templates:
                continue

            template = self._templates[template_id]
            if template.modality != modality:
                continue

            # Mock matching algorithm
            match_score = await self._calculate_match_score(sample, template)

            if match_score > best_score:
                best_score = match_score
                best_template_id = template_id

        # Determine confidence and decision
        confidence = best_score * 0.95  # Slight confidence penalty
        decision = "accept" if confidence >= self.confidence_threshold else "reject"

        return BiometricMatchResult(
            match_score=best_score,
            confidence=confidence,
            decision=decision,
            template_id=best_template_id,
            sample_id=sample.sample_id,
            template_quality=self._templates[best_template_id].quality_score if best_template_id else 0.0,
            sample_quality=sample.quality_score,
            anti_spoofing_score=sample.liveness_score
        )

    async def _calculate_match_score(self, sample: BiometricSample, template: BiometricTemplate) -> float:
        """Calculate mock match score between sample and template."""
        try:
            # Create deterministic but realistic matching
            sample_hash = hashlib.sha256(sample.sample_data.encode()).hexdigest()
            template_hash = hashlib.sha256(template.template_data.encode()).hexdigest()

            # Mock matching algorithm based on hash similarity
            similarity = 0.0
            for i in range(min(len(sample_hash), len(template_hash))):
                if sample_hash[i] == template_hash[i]:
                    similarity += 1

            base_score = similarity / min(len(sample_hash), len(template_hash))

            # Apply quality adjustments
            quality_factor = (sample.quality_score + template.quality_score) / 2
            adjusted_score = base_score * quality_factor

            # Add some realistic variance
            import random
            adjusted_score += random.uniform(-0.05, 0.05)

            return max(0.0, min(1.0, adjusted_score))

        except Exception:
            return 0.0

    async def _generate_device_attestation(self, device_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock device attestation."""
        if not device_info:
            return {"status": "no_device_info"}

        device_id = device_info.get("device_id", "unknown")

        # Mock device verification
        trusted_device = device_id in [dev["device_id"] for dev in self._device_attestation_keys.values()]

        return {
            "device_id": device_id,
            "trusted": trusted_device,
            "certificate_valid": trusted_device,
            "attestation_time": datetime.now(timezone.utc).isoformat(),
            "signature": secrets.token_hex(32) if trusted_device else ""
        }

    async def _sign_attestation(self, attestation: BiometricAttestation) -> str:
        """Sign biometric attestation for integrity verification."""
        # Create signature payload
        payload = {
            "attestation_id": attestation.attestation_id,
            "user_id": attestation.user_id,
            "authenticated": attestation.authenticated,
            "confidence": attestation.confidence,
            "nonce": attestation.nonce,
            "timestamp": attestation.created_at.isoformat()
        }

        payload_json = json.dumps(payload, sort_keys=True)
        signing_key = self._test_keys["signing_key"]

        # Mock HMAC signature
        signature = hmac.new(
            signing_key.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def _update_template_usage(self, template_id: str) -> None:
        """Update template usage statistics."""
        if template_id in self._templates:
            template = self._templates[template_id]
            template.last_used = datetime.now(timezone.utc)
            template.usage_count += 1

    async def _record_authentication_attempt(self, user_id: str) -> None:
        """Record authentication attempt for rate limiting."""
        now = datetime.now(timezone.utc)

        if user_id not in self._recent_authentications:
            self._recent_authentications[user_id] = []

        self._recent_authentications[user_id].append(now)

        # Keep only last hour of attempts
        cutoff = now - timedelta(hours=1)
        self._recent_authentications[user_id] = [
            attempt for attempt in self._recent_authentications[user_id]
            if attempt > cutoff
        ]

    async def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited."""
        if user_id not in self._recent_authentications:
            return False

        # Allow max 10 attempts per hour
        return len(self._recent_authentications[user_id]) >= 10

    async def _guardian_validate(self, action: str, context: Dict[str, Any]) -> None:
        """Guardian pre-validation hook."""
        if self.guardian:
            try:
                await self.guardian.validate_action_async(action, context)
            except Exception as e:
                self.logger.warning("Guardian validation failed", action=action, error=str(e))

    async def _guardian_monitor(self, event: str, context: Dict[str, Any]) -> None:
        """Guardian post-monitoring hook."""
        if self.guardian:
            try:
                await self.guardian.monitor_behavior_async(event, context)
            except Exception as e:
                self.logger.warning("Guardian monitoring failed", event=event, error=str(e))

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        auth_times = self._performance_metrics["authentication_times"]
        enroll_times = self._performance_metrics["enrollment_times"]

        return {
            "enrollment": {
                "count": len(enroll_times),
                "avg_ms": sum(enroll_times) / len(enroll_times) if enroll_times else 0,
                "p95_ms": sorted(enroll_times)[int(len(enroll_times) * 0.95)] if enroll_times else 0
            },
            "authentication": {
                "count": len(auth_times),
                "avg_ms": sum(auth_times) / len(auth_times) if auth_times else 0,
                "p95_ms": sorted(auth_times)[int(len(auth_times) * 0.95)] if auth_times else 0
            },
            "success_rate": (
                self._performance_metrics["successful_authentications"] /
                max(1, self._performance_metrics["total_authentications"])
            ),
            "enrolled_users": len(self._user_templates),
            "total_templates": len(self._templates)
        }


# Factory function for dependency injection
def create_mock_biometric_provider(
    provider_id: str = "lukhas_mock_biometric",
    base_success_rate: float = 0.95,
    quality_threshold: float = 0.7,
    confidence_threshold: float = 0.95,
    guardian_system: Optional[GuardianSystem] = None
) -> MockBiometricProvider:
    """Create mock biometric provider with configuration."""
    return MockBiometricProvider(
        provider_id=provider_id,
        base_success_rate=base_success_rate,
        quality_threshold=quality_threshold,
        confidence_threshold=confidence_threshold,
        guardian_system=guardian_system
    )


# Test keys and sample data for development
DEVELOPMENT_TEST_DATA = {
    "test_users": {
        "alice": {
            "fingerprint_sample": base64.b64encode(b"mock_fingerprint_alice_sample").decode(),
            "face_sample": base64.b64encode(b"mock_face_alice_sample").decode(),
        },
        "bob": {
            "fingerprint_sample": base64.b64encode(b"mock_fingerprint_bob_sample").decode(),
            "iris_sample": base64.b64encode(b"mock_iris_bob_sample").decode(),
        }
    },
    "test_devices": {
        "dev_fingerprint_001": {
            "type": "fingerprint",
            "vendor": "Mock Biometrics Inc",
            "model": "FP-3000",
            "certificate": "mock_cert_fp_3000"
        },
        "dev_face_001": {
            "type": "face",
            "vendor": "Mock Vision Systems",
            "model": "FC-2000",
            "certificate": "mock_cert_fc_2000"
        }
    }
}
