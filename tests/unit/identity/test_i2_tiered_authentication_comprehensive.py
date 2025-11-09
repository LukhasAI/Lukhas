"""
Comprehensive Test Suite for I.2 Tiered Authentication System
============================================================

T4/0.01% excellence compliant test suite for the LUKHAS tiered authentication system.
Provides comprehensive coverage with property-based testing, performance validation,
and security verification.

Test Coverage:
- All authentication tiers (T1-T5)
- Security hardening features
- WebAuthn enhanced service
- Biometric authentication
- Guardian system integration
- Performance benchmarks
- Error handling and edge cases
- Property-based testing with Hypothesis
"""

import asyncio
import base64
import json
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from importlib.util import find_spec

import pytest

HYPOTHESIS_AVAILABLE = find_spec("hypothesis") is not None
if HYPOTHESIS_AVAILABLE:
    from hypothesis import HealthCheck, given, settings, strategies as st
    from hypothesis.strategies import text

# Import the components under test
COMPONENTS_AVAILABLE = all(
    find_spec(module) is not None
    for module in [
        "governance.guardian_system",
        "identity.biometrics",
        "identity.security_hardening",
        "identity.tiers",
        "identity.webauthn_enhanced",
    ]
)

if COMPONENTS_AVAILABLE:
    from governance.guardian_system import GuardianSystem
    from identity.biometrics import BiometricAttestation, BiometricModality, MockBiometricProvider
    from identity.security_hardening import SecurityHardeningManager
    from identity.tiers import (
        AuthContext,
        AuthResult,
        SecurityPolicy,
        Tier,
        TieredAuthenticator,
        create_tiered_authenticator,
    )
    from identity.webauthn_enhanced import (
        EnhancedWebAuthnService,
        WebAuthnChallenge,
        WebAuthnCredentialMetadata,
    )


@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
class TestTieredAuthenticationEngine:
    """Test suite for the core tiered authentication engine."""

    @pytest.fixture
    async def authenticator(self):
        """Create test authenticator instance."""
        mock_guardian = AsyncMock(spec=GuardianSystem)
        security_policy = SecurityPolicy(
            max_attempts=3,
            lockout_duration_minutes=5,
            argon2_time_cost=1,  # Faster for testing
            argon2_memory_cost=1024,  # Smaller for testing
        )
        return create_tiered_authenticator(security_policy, mock_guardian)

    @pytest.fixture
    def auth_context(self):
        """Create basic authentication context."""
        return AuthContext(
            ip_address="127.0.0.1",
            user_agent="test-agent/1.0",
            username="test_user",
            password="test_password",
        )

    @pytest.mark.asyncio
    async def test_t1_public_authentication_success(self, authenticator, auth_context):
        """Test T1 public authentication always succeeds."""
        # Arrange
        start_time = time.perf_counter()

        # Act
        result = await authenticator.authenticate_T1(auth_context)

        # Assert
        assert result.ok is True
        assert result.tier == "T1"
        assert result.reason == "public_access_granted"
        assert result.session_id == auth_context.correlation_id
        assert result.jwt_token is not None
        assert result.expires_at is not None
        assert result.guardian_validated is True
        assert result.duration_ms is not None
        assert result.duration_ms < 100  # Performance requirement

        # Verify performance requirement
        duration = (time.perf_counter() - start_time) * 1000
        assert duration < 100  # Sub-100ms requirement

    @pytest.mark.asyncio
    async def test_t2_password_authentication_mock_success(self, authenticator, auth_context):
        """Test T2 password authentication with mock verification."""
        # Arrange - Mock password verification to pass
        with patch.object(authenticator, "_verify_password", return_value=True):
            # Act
            result = await authenticator.authenticate_T2(auth_context)

            # Assert
            assert result.ok is True
            assert result.tier == "T2"
            assert result.reason == "password_authenticated"
            assert result.user_id == auth_context.username
            assert result.jwt_token is not None
            assert result.duration_ms < 200  # Performance requirement

    @pytest.mark.asyncio
    async def test_t2_password_authentication_failure(self, authenticator, auth_context):
        """Test T2 password authentication failure."""
        # Arrange - Mock password verification to fail
        with patch.object(authenticator, "_verify_password", return_value=False):
            # Act
            result = await authenticator.authenticate_T2(auth_context)

            # Assert
            assert result.ok is False
            assert result.tier == "T2"
            assert result.reason == "invalid_credentials"
            assert result.user_id is None

    @pytest.mark.asyncio
    async def test_t3_mfa_authentication_success(self, authenticator, auth_context):
        """Test T3 multi-factor authentication success."""
        # Arrange
        auth_context.existing_tier = "T2"
        auth_context.totp_token = "123456"

        with patch.object(authenticator, "_verify_totp", return_value=True):
            # Act
            result = await authenticator.authenticate_T3(auth_context)

            # Assert
            assert result.ok is True
            assert result.tier == "T3"
            assert result.reason == "mfa_authenticated"
            assert result.tier_elevation_path == "T1→T2→T3"

    @pytest.mark.asyncio
    async def test_t3_requires_t2_prerequisite(self, authenticator, auth_context):
        """Test T3 authentication requires T2 prerequisite."""
        # Arrange - No existing tier
        auth_context.totp_token = "123456"

        # Act
        result = await authenticator.authenticate_T3(auth_context)

        # Assert
        assert result.ok is False
        assert result.reason == "requires_t2_authentication"

    @pytest.mark.asyncio
    async def test_t4_webauthn_authentication_success(self, authenticator, auth_context):
        """Test T4 WebAuthn authentication success."""
        # Arrange
        auth_context.existing_tier = "T3"

        assert authenticator.webauthn is not None

        credential_id = "cred-test"
        await authenticator.webauthn.register_credential(
            user_id=auth_context.username,
            credential_data={"id": credential_id, "public_key": "test-public-key", "device_type": "security_key"},
        )

        challenge_payload = await authenticator.generate_webauthn_challenge(
            username=auth_context.username,
            correlation_id=auth_context.correlation_id,
            ip_address=auth_context.ip_address,
            user_agent=auth_context.user_agent,
        )

        challenge_id = challenge_payload["challenge_id"]
        challenge_b64 = challenge_payload["options"]["challenge"]

        client_data = {
            "type": "webauthn.get",
            "challenge": challenge_b64,
            "origin": "https://ai",
        }
        client_data_json = base64.urlsafe_b64encode(json.dumps(client_data).encode()).decode().rstrip("=")

        authenticator_data_bytes = bytearray(37)
        authenticator_data_bytes[32] = 0x05  # user present + verified
        authenticator_data = base64.urlsafe_b64encode(bytes(authenticator_data_bytes)).decode().rstrip("=")

        signature = base64.urlsafe_b64encode(b"x01" * 64).decode().rstrip("=")

        auth_context.challenge_data = {"challenge_id": challenge_id}
        auth_context.webauthn_response = {
            "id": credential_id,
            "response": {
                "clientDataJSON": client_data_json,
                "authenticatorData": authenticator_data,
                "signature": signature,
            },
        }

        # Act
        result = await authenticator.authenticate_T4(auth_context)

        # Assert
        assert result.ok is True
        assert result.tier == "T4"
        assert result.reason == "hardware_key_authenticated"
        assert result.tier_elevation_path == "T1→T2→T3→T4"
        assert result.user_id == auth_context.username
        assert result.session_id == auth_context.correlation_id

    @pytest.mark.asyncio
    async def test_t5_biometric_authentication_success(self, authenticator, auth_context):
        """Test T5 biometric authentication success."""
        # Arrange
        auth_context.existing_tier = "T4"
        auth_context.biometric_attestation = {"confidence": 0.98, "signature": "test"}

        with patch.object(authenticator, "_verify_biometric", return_value=True):
            # Act
            result = await authenticator.authenticate_T5(auth_context)

            # Assert
            assert result.ok is True
            assert result.tier == "T5"
        assert result.reason == "biometric_authenticated"
        assert result.tier_elevation_path == "T1→T2→T3→T4→T5"

    @pytest.mark.asyncio
    async def test_generate_webauthn_challenge_metadata(self, authenticator, auth_context):
        """Challenge generation stores metadata for verification."""

        assert authenticator.webauthn is not None

        await authenticator.webauthn.register_credential(
            user_id=auth_context.username,
            credential_data={"id": "cred-meta", "public_key": "pk"},
        )

        challenge_payload = await authenticator.generate_webauthn_challenge(
            username=auth_context.username,
            correlation_id=auth_context.correlation_id,
            ip_address=auth_context.ip_address,
            user_agent=auth_context.user_agent,
        )

        challenge_id = challenge_payload["challenge_id"]
        assert challenge_id in authenticator._active_challenges
        metadata = authenticator._active_challenges[challenge_id]
        assert metadata["username"] == auth_context.username
        assert metadata["correlation_id"] == auth_context.correlation_id

    @pytest.mark.asyncio
    async def test_t4_webauthn_requires_challenge(self, authenticator, auth_context):
        """Authentication fails when WebAuthn challenge metadata is missing."""

        auth_context.existing_tier = "T3"
        auth_context.webauthn_response = {
            "id": "missing",
            "response": {
                "clientDataJSON": "",
                "authenticatorData": "",
                "signature": "",
            },
        }

        result = await authenticator.authenticate_T4(auth_context)

        assert result.ok is False
        assert result.reason == "MISSING_CHALLENGE_ID"

    @pytest.mark.asyncio
    async def test_missing_credentials_validation(self, authenticator):
        """Test validation of missing credentials for each tier."""
        # T2 without username/password
        ctx = AuthContext(ip_address="127.0.0.1")
        result = await authenticator.authenticate_T2(ctx)
        assert result.ok is False
        assert result.reason == "missing_credentials"

        # T3 without TOTP token
        ctx.existing_tier = "T2"
        result = await authenticator.authenticate_T3(ctx)
        assert result.ok is False
        assert result.reason == "missing_totp_token"

    @pytest.mark.asyncio
    async def test_account_lockout_mechanism(self, authenticator, auth_context):
        """Test account lockout after failed attempts."""
        # Arrange - Mock password verification to fail
        with patch.object(authenticator, "_verify_password", return_value=False):
            # Act - Exceed max attempts
            for _ in range(5):  # Default max_attempts is 5
                await authenticator.authenticate_T2(auth_context)

            # Check if account is locked
            is_locked = await authenticator._is_account_locked(auth_context.username)

            # Assert
            assert is_locked is True

    @pytest.mark.asyncio
    async def test_guardian_integration(self, authenticator, auth_context):
        """Test Guardian system integration."""
        # Act
        result = await authenticator.authenticate_T1(auth_context)

        # Assert Guardian methods were called
        authenticator.guardian.validate_action_async.assert_called_once()
        authenticator.guardian.monitor_behavior_async.assert_called_once()
        assert result.guardian_validated is True

    @pytest.mark.asyncio
    async def test_performance_requirements(self, authenticator, auth_context):
        """Test performance requirements for all tiers."""
        # Performance requirements (in milliseconds)
        tier_limits = {
            "T1": 50,  # Public access should be fastest
            "T2": 200,  # Password hashing adds overhead
            "T3": 150,  # TOTP verification
            "T4": 300,  # WebAuthn processing
            "T5": 400,  # Biometric processing
        }

        # Mock all verification methods to pass
        with patch.object(authenticator, "_verify_password", return_value=True), patch.object(
            authenticator, "_verify_totp", return_value=True
        ), patch.object(authenticator, "_verify_webauthn", return_value=True), patch.object(
            authenticator, "_verify_biometric", return_value=True
        ):
            # Test T1
            start = time.perf_counter()
            result = await authenticator.authenticate_T1(auth_context)
            duration = (time.perf_counter() - start) * 1000
            assert result.ok is True
            assert duration < tier_limits["T1"]

            # Test T2
            start = time.perf_counter()
            result = await authenticator.authenticate_T2(auth_context)
            duration = (time.perf_counter() - start) * 1000
            assert result.ok is True
            assert duration < tier_limits["T2"]

    if HYPOTHESIS_AVAILABLE:

        @given(
            ip_address=st.ip_addresses().map(str),
            username=text(min_size=1, max_size=50),
            correlation_id=text(min_size=10, max_size=50),
        )
        @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
        async def test_property_based_authentication_contexts(
            self, authenticator, ip_address, username, correlation_id
        ):
            """Property-based test for authentication contexts."""
            # Arrange
            ctx = AuthContext(ip_address=ip_address, username=username, correlation_id=correlation_id)

            # Act
            result = await authenticator.authenticate_T1(ctx)

            # Assert properties that should always hold
            assert result is not None
            assert isinstance(result, AuthResult)
            assert result.tier == "T1"
            assert result.correlation_id == correlation_id

    else:

        @pytest.mark.skip(reason="Hypothesis not installed")
        async def test_property_based_authentication_contexts(self):
            """Skipped when Hypothesis is unavailable."""
            raise pytest.SkipTest("Hypothesis dependency is required")


@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
class TestWebAuthnEnhancedService:
    """Test suite for enhanced WebAuthn service."""

    @pytest.fixture
    async def webauthn_service(self):
        """Create test WebAuthn service."""
        mock_guardian = AsyncMock(spec=GuardianSystem)
        return EnhancedWebAuthnService(guardian_system=mock_guardian)

    @pytest.mark.asyncio
    async def test_challenge_generation(self, webauthn_service):
        """Test WebAuthn challenge generation."""
        # Act
        challenge_data = await webauthn_service.generate_authentication_challenge(
            user_id="test_user", correlation_id="test_corr", ip_address="127.0.0.1"
        )

        # Assert
        assert "challenge_id" in challenge_data
        assert "options" in challenge_data
        assert "expires_at" in challenge_data
        assert challenge_data["options"]["challenge"] is not None
        assert challenge_data["options"]["userVerification"] == "required"

    @pytest.mark.asyncio
    async def test_challenge_uniqueness(self, webauthn_service):
        """Test that challenges are unique."""
        # Act - Generate multiple challenges
        challenges = []
        for i in range(10):
            challenge_data = await webauthn_service.generate_authentication_challenge(
                user_id=f"user_{i}", correlation_id=f"corr_{i}", ip_address="127.0.0.1"
            )
            challenges.append(challenge_data["options"]["challenge"])

        # Assert - All challenges should be unique
        assert len(set(challenges)) == 10

    @pytest.mark.asyncio
    async def test_challenge_expiration(self, webauthn_service):
        """Test challenge expiration handling."""
        # Arrange
        challenge_data = await webauthn_service.generate_authentication_challenge(
            user_id="test_user", correlation_id="test_corr", ip_address="127.0.0.1"
        )

        challenge_id = challenge_data["challenge_id"]

        # Manually expire the challenge
        challenge = webauthn_service._active_challenges[challenge_id]
        challenge.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

        # Act
        result = await webauthn_service.verify_authentication_response(
            challenge_id=challenge_id,
            webauthn_response={"id": "test", "response": {}},
            correlation_id="test_corr",
            ip_address="127.0.0.1",
        )

        # Assert
        assert result.success is False
        assert result.error_code == "CHALLENGE_INVALID"

    @pytest.mark.asyncio
    async def test_anti_replay_protection(self, webauthn_service):
        """Test anti-replay protection for challenges."""
        # Arrange
        challenge_data = await webauthn_service.generate_authentication_challenge(
            user_id="test_user", correlation_id="test_corr", ip_address="127.0.0.1"
        )

        challenge_id = challenge_data["challenge_id"]
        webauthn_response = {
            "id": "test_credential",
            "response": {
                "authenticatorData": "dGVzdA==",
                "clientDataJSON": "eyJjaGFsbGVuZ2UiOiJ0ZXN0IiwidHlwZSI6IndlYmF1dGhuLmdldCIsIm9yaWdpbiI6Imh0dHBzOi8vbHVraGFzLmFpIn0=",
                "signature": "dGVzdF9zaWduYXR1cmU=",
            },
        }

        # Register a test credential
        await webauthn_service.register_credential(
            user_id="test_user", credential_data={"id": "test_credential", "public_key": "test_key"}
        )

        # Act - First verification attempt
        result1 = await webauthn_service.verify_authentication_response(
            challenge_id=challenge_id,
            webauthn_response=webauthn_response,
            correlation_id="test_corr",
            ip_address="127.0.0.1",
        )

        # Act - Second verification attempt (should fail due to replay)
        result2 = await webauthn_service.verify_authentication_response(
            challenge_id=challenge_id,
            webauthn_response=webauthn_response,
            correlation_id="test_corr",
            ip_address="127.0.0.1",
        )

        # Assert
        assert result1.success is True  # First attempt succeeds
        assert result2.success is False  # Second attempt fails (replay)

    @pytest.mark.asyncio
    async def test_performance_requirements(self, webauthn_service):
        """Test WebAuthn performance requirements."""
        # Performance requirement: <100ms p95 for challenge generation
        times = []

        for _ in range(100):
            start = time.perf_counter()
            await webauthn_service.generate_authentication_challenge(
                user_id="test_user", correlation_id="test_corr", ip_address="127.0.0.1"
            )
            duration = (time.perf_counter() - start) * 1000
            times.append(duration)

        # Calculate p95
        times.sort()
        p95_time = times[94]  # 95th percentile (0-indexed)

        assert p95_time < 100  # Sub-100ms p95 requirement


@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
class TestBiometricProvider:
    """Test suite for mock biometric provider."""

    @pytest.fixture
    async def biometric_provider(self):
        """Create test biometric provider."""
        mock_guardian = AsyncMock(spec=GuardianSystem)
        return MockBiometricProvider(guardian_system=mock_guardian)

    @pytest.mark.asyncio
    async def test_biometric_enrollment(self, biometric_provider):
        """Test biometric template enrollment."""
        # Act
        success, result = await biometric_provider.enroll_biometric(
            user_id="test_user",
            modality=BiometricModality.FINGERPRINT,
            sample_data="dGVzdF9maW5nZXJwcmludA==",  # base64 encoded
        )

        # Assert
        assert success is True
        assert result is not None  # template_id
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_biometric_authentication(self, biometric_provider):
        """Test biometric authentication."""
        # Arrange - Enroll a template first
        await biometric_provider.enroll_biometric(
            user_id="test_user", modality=BiometricModality.FINGERPRINT, sample_data="dGVzdF9maW5nZXJwcmludA=="
        )

        # Act
        attestation = await biometric_provider.authenticate_biometric(
            user_id="test_user",
            sample_data="dGVzdF9maW5nZXJwcmludA==",
            modality=BiometricModality.FINGERPRINT,
            nonce="test_nonce_123",
        )

        # Assert
        assert isinstance(attestation, BiometricAttestation)
        assert attestation.user_id == "test_user"
        assert attestation.modality == BiometricModality.FINGERPRINT
        assert attestation.nonce == "test_nonce_123"
        assert attestation.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_anti_spoofing_detection(self, biometric_provider):
        """Test anti-spoofing detection."""
        # Arrange - Enroll a template
        await biometric_provider.enroll_biometric(
            user_id="test_user", modality=BiometricModality.FINGERPRINT, sample_data="dGVzdF9maW5nZXJwcmludA=="
        )

        # Act
        attestation = await biometric_provider.authenticate_biometric(
            user_id="test_user",
            sample_data="dGVzdF9maW5nZXJwcmludA==",
            modality=BiometricModality.FINGERPRINT,
            nonce="test_nonce_456",
        )

        # Assert
        assert attestation.anti_spoofing_passed is not None
        assert attestation.liveness_verified is not None

    @pytest.mark.asyncio
    async def test_nonce_replay_protection(self, biometric_provider):
        """Test nonce replay protection."""
        # Arrange - Enroll a template
        await biometric_provider.enroll_biometric(
            user_id="test_user", modality=BiometricModality.FINGERPRINT, sample_data="dGVzdF9maW5nZXJwcmludA=="
        )

        nonce = "test_nonce_replay"

        # Act - First authentication
        attestation1 = await biometric_provider.authenticate_biometric(
            user_id="test_user",
            sample_data="dGVzdF9maW5nZXJwcmludA==",
            modality=BiometricModality.FINGERPRINT,
            nonce=nonce,
        )

        # Act - Second authentication with same nonce (should fail)
        attestation2 = await biometric_provider.authenticate_biometric(
            user_id="test_user",
            sample_data="dGVzdF9maW5nZXJwcmludA==",
            modality=BiometricModality.FINGERPRINT,
            nonce=nonce,
        )

        # Assert
        assert attestation1.authenticated is True  # First attempt should succeed
        assert attestation2.authenticated is False  # Second attempt should fail (replay)

    @pytest.mark.asyncio
    async def test_performance_requirements(self, biometric_provider):
        """Test biometric authentication performance requirements."""
        # Arrange - Enroll template
        await biometric_provider.enroll_biometric(
            user_id="test_user", modality=BiometricModality.FINGERPRINT, sample_data="dGVzdF9maW5nZXJwcmludA=="
        )

        # Performance requirement: <50ms p95 for authentication
        times = []

        for i in range(100):
            start = time.perf_counter()
            await biometric_provider.authenticate_biometric(
                user_id="test_user",
                sample_data="dGVzdF9maW5nZXJwcmludA==",
                modality=BiometricModality.FINGERPRINT,
                nonce=f"test_nonce_{i}",
            )
            duration = (time.perf_counter() - start) * 1000
            times.append(duration)

        # Calculate p95
        times.sort()
        p95_time = times[94]  # 95th percentile

        assert p95_time < 50  # Sub-50ms p95 requirement


@pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
class TestSecurityHardening:
    """Test suite for security hardening features."""

    @pytest.fixture
    async def security_manager(self):
        """Create test security hardening manager."""
        mock_guardian = AsyncMock(spec=GuardianSystem)
        return SecurityHardeningManager(mock_guardian)

    @pytest.mark.asyncio
    async def test_nonce_generation_and_validation(self, security_manager):
        """Test nonce generation and validation."""
        # Act - Generate nonce
        nonce = await security_manager.generate_nonce("test_user", "test_endpoint")

        # Assert nonce properties
        assert nonce is not None
        assert len(nonce) > 20  # Should be sufficiently long
        assert nonce.startswith("nonce_")

        # Act - Validate nonce
        is_valid, reason = await security_manager.validate_nonce(nonce, "test_user", "test_endpoint")

        # Assert validation
        assert is_valid is True
        assert reason == "valid"

        # Act - Try to reuse nonce (should fail)
        is_valid_replay, reason_replay = await security_manager.validate_nonce(
            nonce, "test_user", "test_endpoint"
        )

        # Assert replay protection
        assert is_valid_replay is False
        assert reason_replay == "nonce_not_found"

    @pytest.mark.asyncio
    async def test_rate_limiting(self, security_manager):
        """Test rate limiting functionality."""
        identifier = "127.0.0.1"

        # Act - Send requests within limit
        for _i in range(5):
            action, reason = await security_manager.check_rate_limit(identifier, "authentication")
            assert action.value in ["allow", "throttle"]

        # Act - Exceed rate limit
        for _i in range(10):
            action, reason = await security_manager.check_rate_limit(identifier, "authentication")

        # Assert - Should be blocked or throttled
        assert action.value in ["block", "throttle"]
        assert "rate_limit_exceeded" in reason

    @pytest.mark.asyncio
    async def test_request_analysis(self, security_manager):
        """Test request analysis for threat detection."""
        # Act - Analyze normal request
        threat_level, _indicators = await security_manager.analyze_request(
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            headers={"Host": "ai", "Accept": "text/html"},
        )

        # Assert - Should be low threat
        assert threat_level.value == "low"

        # Act - Analyze suspicious request
        threat_level_sus, indicators_sus = await security_manager.analyze_request(
            ip_address="127.0.0.1",
            user_agent="sqlmap/1.0",  # Suspicious user agent
            headers={"X-Scanner": "test", "Host": "ai"},  # Suspicious header
        )

        # Assert - Should be higher threat
        assert threat_level_sus.value in ["medium", "high", "critical"]
        assert len(indicators_sus) > 0

    @pytest.mark.asyncio
    async def test_comprehensive_security_check(self, security_manager):
        """Test comprehensive security check integration."""
        # Act
        action, report = await security_manager.comprehensive_security_check(
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0 (legitimate browser)",
            headers={"Host": "ai"},
            user_id="test_user",
            endpoint="/identity/authenticate",
        )

        # Assert
        assert action is not None
        assert "checks_performed" in report
        assert "rate_limiting" in report["checks_performed"]
        assert "request_analysis" in report["checks_performed"]
        assert "final_action" in report


class TestIntegrationScenarios:
    """Integration test scenarios for complete authentication flows."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
    async def test_complete_t1_to_t5_elevation_flow(self):
        """Test complete tier elevation from T1 to T5."""
        # Arrange
        authenticator = create_tiered_authenticator()

        # Mock all verification methods
        with patch.object(authenticator, "_verify_password", return_value=True), patch.object(
            authenticator, "_verify_totp", return_value=True
        ), patch.object(authenticator, "_verify_webauthn", return_value=True), patch.object(
            authenticator, "_verify_biometric", return_value=True
        ):
            # Act & Assert - T1
            ctx = AuthContext(ip_address="127.0.0.1", username="test_user")
            result_t1 = await authenticator.authenticate_T1(ctx)
            assert result_t1.ok is True
            assert result_t1.tier == "T1"

            # Act & Assert - T2
            ctx.password = "test_password"
            result_t2 = await authenticator.authenticate_T2(ctx)
            assert result_t2.ok is True
            assert result_t2.tier == "T2"

            # Act & Assert - T3
            ctx.existing_tier = "T2"
            ctx.totp_token = "123456"
            result_t3 = await authenticator.authenticate_T3(ctx)
            assert result_t3.ok is True
            assert result_t3.tier == "T3"

            # Act & Assert - T4
            ctx.existing_tier = "T3"
            ctx.webauthn_response = {"challenge": "test", "signature": "test"}
            result_t4 = await authenticator.authenticate_T4(ctx)
            assert result_t4.ok is True
            assert result_t4.tier == "T4"

            # Act & Assert - T5
            ctx.existing_tier = "T4"
            ctx.biometric_attestation = {"confidence": 0.98, "signature": "test"}
            result_t5 = await authenticator.authenticate_T5(ctx)
            assert result_t5.ok is True
            assert result_t5.tier == "T5"
            assert result_t5.tier_elevation_path == "T1→T2→T3→T4→T5"


class TestPerformanceBenchmarks:
    """Performance benchmark tests for T4/0.01% excellence validation."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
    async def test_authentication_performance_sla(self):
        """Test authentication performance meets SLA requirements."""
        # SLA Requirements:
        # - T1: <50ms p95
        # - T2: <200ms p95
        # - T3: <150ms p95
        # - T4: <300ms p95 (includes WebAuthn)
        # - T5: <400ms p95 (includes biometric)

        authenticator = create_tiered_authenticator()

        # Mock all verification methods to be fast
        with patch.object(authenticator, "_verify_password", return_value=True), patch.object(
            authenticator, "_verify_totp", return_value=True
        ), patch.object(authenticator, "_verify_webauthn", return_value=True), patch.object(
            authenticator, "_verify_biometric", return_value=True
        ):
            # Test T1 performance (100 samples for statistical significance)
            t1_times = []
            for i in range(100):
                ctx = AuthContext(ip_address="127.0.0.1", correlation_id=f"test_{i}")
                start = time.perf_counter()
                result = await authenticator.authenticate_T1(ctx)
                duration = (time.perf_counter() - start) * 1000
                t1_times.append(duration)
                assert result.ok is True

            # Calculate p95 latency
            t1_times.sort()
            t1_p95 = t1_times[94]  # 95th percentile (0-indexed)

            # Assert SLA compliance
            assert t1_p95 < 50, f"T1 p95 latency {t1_p95}ms exceeds 50ms SLA"

            # Test T2 performance
            t2_times = []
            for i in range(100):
                ctx = AuthContext(
                    ip_address="127.0.0.1",
                    username="test_user",
                    password="test_password",
                    correlation_id=f"test_t2_{i}",
                )
                start = time.perf_counter()
                result = await authenticator.authenticate_T2(ctx)
                duration = (time.perf_counter() - start) * 1000
                t2_times.append(duration)
                assert result.ok is True

            t2_times.sort()
            t2_p95 = t2_times[94]
            assert t2_p95 < 200, f"T2 p95 latency {t2_p95}ms exceeds 200ms SLA"

    @pytest.mark.asyncio
    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="Identity components not available")
    async def test_concurrent_authentication_load(self):
        """Test system performance under concurrent load."""
        authenticator = create_tiered_authenticator()

        with patch.object(authenticator, "_verify_password", return_value=True):
            # Simulate 50 concurrent T2 authentications
            async def auth_task(user_id: int):
                ctx = AuthContext(
                    ip_address="127.0.0.1", username=f"user_{user_id}", password="test_password"
                )
                start = time.perf_counter()
                result = await authenticator.authenticate_T2(ctx)
                duration = (time.perf_counter() - start) * 1000
                return result.ok, duration

            # Execute concurrent tasks
            tasks = [auth_task(i) for i in range(50)]
            results = await asyncio.gather(*tasks)

            # Analyze results
            success_count = sum(1 for success, _ in results if success)
            durations = [duration for _, duration in results]
            max_duration = max(durations)
            avg_duration = sum(durations) / len(durations)

            # Assert performance under load
            assert success_count == 50, "All concurrent authentications should succeed"
            assert max_duration < 500, f"Max duration {max_duration}ms too high under load"
            assert avg_duration < 250, f"Average duration {avg_duration}ms too high under load"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
