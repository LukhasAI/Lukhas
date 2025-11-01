#!/usr/bin/env python3
"""
Tests for LUKHAS I.4 WebAuthn/Passkeys - Production Implementation
Production Schema v1.0.0

Comprehensive test suite for WebAuthn/FIDO2 operations,
biometric authentication, and performance validation.
"""

import base64
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import importlib.util
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "lukhas_website" / "lukhas"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

MODULE_PATH = PACKAGE_ROOT / "identity" / "webauthn_production.py"
spec = importlib.util.spec_from_file_location(
    "lukhas_identity.webauthn_production", MODULE_PATH
)
webauthn_production = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = webauthn_production
spec.loader.exec_module(webauthn_production)

AuthenticatorTier = webauthn_production.AuthenticatorTier
AuthenticatorType = webauthn_production.AuthenticatorType
CredentialStatus = webauthn_production.CredentialStatus
WebAuthnChallenge = webauthn_production.WebAuthnChallenge
WebAuthnCredential = webauthn_production.WebAuthnCredential
WebAuthnCredentialStore = webauthn_production.WebAuthnCredentialStore
WebAuthnManager = webauthn_production.WebAuthnManager
get_webauthn_manager = webauthn_production.get_webauthn_manager


class TestWebAuthnCredential:
    """Test WebAuthnCredential data class functionality"""

    def test_credential_creation(self):
        """Test WebAuthn credential creation"""
        credential = WebAuthnCredential(
            credential_id="test_credential_123",
            public_key="mock_public_key",
            user_id="user_123",
            sign_count=0,
            authenticator_type=AuthenticatorType.PLATFORM,
            tier=AuthenticatorTier.T4_STRONG,
            device_name="Test Device"
        )

        assert credential.credential_id == "test_credential_123"
        assert credential.public_key == "mock_public_key"
        assert credential.user_id == "user_123"
        assert credential.sign_count == 0
        assert credential.authenticator_type == AuthenticatorType.PLATFORM
        assert credential.tier == AuthenticatorTier.T4_STRONG
        assert credential.status == CredentialStatus.ACTIVE
        assert credential.device_name == "Test Device"
        assert credential.biometric_enrolled is False

    def test_credential_to_dict(self):
        """Test credential serialization to dictionary"""
        credential = WebAuthnCredential(
            credential_id="test_credential",
            public_key="test_key",
            user_id="user_123",
            device_name="iPhone"
        )

        data = credential.to_dict()

        assert data["credential_id"] == "test_credential"
        assert data["public_key"] == "test_key"
        assert data["user_id"] == "user_123"
        assert data["device_name"] == "iPhone"
        assert data["authenticator_type"] == "platform"
        assert data["tier"] == "T4"
        assert data["status"] == "active"
        assert "created_at" in data

    def test_credential_from_dict(self):
        """Test credential deserialization from dictionary"""
        data = {
            "credential_id": "test_credential",
            "public_key": "test_key",
            "user_id": "user_123",
            "sign_count": 5,
            "authenticator_type": "roaming",
            "tier": "T5",
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "device_name": "YubiKey",
            "biometric_enrolled": True,
            "backup_eligible": False
        }

        credential = WebAuthnCredential.from_dict(data)

        assert credential.credential_id == "test_credential"
        assert credential.public_key == "test_key"
        assert credential.user_id == "user_123"
        assert credential.sign_count == 5
        assert credential.authenticator_type == AuthenticatorType.ROAMING
        assert credential.tier == AuthenticatorTier.T5_BIOMETRIC
        assert credential.device_name == "YubiKey"
        assert credential.biometric_enrolled is True


class TestWebAuthnChallenge:
    """Test WebAuthnChallenge functionality"""

    def test_challenge_creation(self):
        """Test challenge creation"""
        challenge = WebAuthnChallenge(
            challenge_id="challenge_123",
            challenge="base64_challenge",
            user_id="user_123",
            operation="registration",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            tier_required=AuthenticatorTier.T4_STRONG
        )

        assert challenge.challenge_id == "challenge_123"
        assert challenge.challenge == "base64_challenge"
        assert challenge.user_id == "user_123"
        assert challenge.operation == "registration"
        assert challenge.tier_required == AuthenticatorTier.T4_STRONG
        assert not challenge.is_expired()

    def test_challenge_expiration(self):
        """Test challenge expiration"""
        # Expired challenge
        expired_challenge = WebAuthnChallenge(
            challenge_id="expired",
            challenge="challenge",
            user_id="user",
            operation="registration",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)
        )

        assert expired_challenge.is_expired()

        # Valid challenge
        valid_challenge = WebAuthnChallenge(
            challenge_id="valid",
            challenge="challenge",
            user_id="user",
            operation="registration",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )

        assert not valid_challenge.is_expired()


class TestWebAuthnCredentialStore:
    """Test WebAuthnCredentialStore functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.store = WebAuthnCredentialStore()

    @pytest.mark.asyncio
    async def test_store_and_get_credential(self):
        """Test credential storage and retrieval"""
        credential = WebAuthnCredential(
            credential_id="test_cred",
            public_key="test_key",
            user_id="user_123"
        )

        await self.store.store_credential(credential)

        # Get all credentials for user
        credentials = await self.store.get_credentials("user_123")
        assert len(credentials) == 1
        assert credentials[0].credential_id == "test_cred"

        # Get specific credential
        retrieved = await self.store.get_credential("test_cred")
        assert retrieved is not None
        assert retrieved.credential_id == "test_cred"

    @pytest.mark.asyncio
    async def test_update_credential(self):
        """Test credential updates"""
        credential = WebAuthnCredential(
            credential_id="test_cred",
            public_key="test_key",
            user_id="user_123"
        )

        await self.store.store_credential(credential)

        # Update credential
        credential.sign_count = 5
        credential.last_used = datetime.now(timezone.utc)
        await self.store.update_credential(credential)

        # Verify update
        retrieved = await self.store.get_credential("test_cred")
        assert retrieved.sign_count == 5
        assert retrieved.last_used is not None

    @pytest.mark.asyncio
    async def test_delete_credential(self):
        """Test credential deletion"""
        credential = WebAuthnCredential(
            credential_id="test_cred",
            public_key="test_key",
            user_id="user_123"
        )

        await self.store.store_credential(credential)
        assert await self.store.get_credential("test_cred") is not None

        # Delete credential
        deleted = await self.store.delete_credential("test_cred")
        assert deleted is True

        # Verify deletion
        assert await self.store.get_credential("test_cred") is None

    @pytest.mark.asyncio
    async def test_challenge_storage(self):
        """Test challenge storage and retrieval"""
        challenge = WebAuthnChallenge(
            challenge_id="test_challenge",
            challenge="base64_challenge",
            user_id="user_123",
            operation="registration",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        )

        await self.store.store_challenge(challenge)

        # Retrieve challenge
        retrieved = await self.store.get_challenge("test_challenge")
        assert retrieved is not None
        assert retrieved.challenge_id == "test_challenge"

        # Delete challenge
        await self.store.delete_challenge("test_challenge")
        assert await self.store.get_challenge("test_challenge") is None

    @pytest.mark.asyncio
    async def test_expired_challenge_cleanup(self):
        """Test automatic cleanup of expired challenges"""
        expired_challenge = WebAuthnChallenge(
            challenge_id="expired",
            challenge="challenge",
            user_id="user",
            operation="registration",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1)
        )

        await self.store.store_challenge(expired_challenge)

        # Should return None for expired challenge
        retrieved = await self.store.get_challenge("expired")
        assert retrieved is None


class TestWebAuthnManager:
    """Test WebAuthnManager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = WebAuthnManager(
            rp_id="test.example.com",
            rp_name="Test App",
            origin="https://test.example.com"
        )

    @pytest.mark.asyncio
    async def test_begin_registration_mock(self):
        """Test WebAuthn registration initiation (mock implementation)"""
        options = await self.manager.begin_registration(
            user_id="user_123",
            username="testuser",
            display_name="Test User",
            tier=AuthenticatorTier.T4_STRONG
        )

        # Verify registration options structure
        assert "challenge" in options
        assert "rp" in options
        assert "user" in options
        assert "pubKeyCredParams" in options
        assert "authenticatorSelection" in options
        assert "_challenge_id" in options

        # Verify RP info
        assert options["rp"]["id"] == "test.example.com"
        assert options["rp"]["name"] == "Test App"

        # Verify user info
        user = options["user"]
        assert user["name"] == "testuser"
        assert user["displayName"] == "Test User"

        # Verify challenge is stored
        challenge_id = options["_challenge_id"]
        stored_challenge = await self.manager.credential_store.get_challenge(challenge_id)
        assert stored_challenge is not None
        assert stored_challenge.operation == "registration"

    @pytest.mark.asyncio
    async def test_finish_registration_mock(self):
        """Test WebAuthn registration completion (mock implementation)"""
        # Begin registration first
        options = await self.manager.begin_registration(
            user_id="user_123",
            username="testuser",
            display_name="Test User"
        )

        challenge_id = options["_challenge_id"]

        # Mock credential data
        mock_credential_data = {
            "id": "mock_credential_id",
            "rawId": "mock_raw_id",
            "type": "public-key",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }

        # Finish registration
        credential = await self.manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential_data,
            device_name="Test Device"
        )

        # Verify credential was created
        assert credential is not None
        assert credential.user_id == "user_123"
        assert credential.device_name == "Test Device"
        assert credential.tier == AuthenticatorTier.T4_STRONG
        assert credential.status == CredentialStatus.ACTIVE

        # Verify credential is stored
        stored_credentials = await self.manager.credential_store.get_credentials("user_123")
        assert len(stored_credentials) == 1

        # Verify challenge is consumed
        consumed_challenge = await self.manager.credential_store.get_challenge(challenge_id)
        assert consumed_challenge is None

    @pytest.mark.asyncio
    async def test_begin_authentication_mock(self):
        """Test WebAuthn authentication initiation (mock implementation)"""
        # Register a credential first
        await self.register_test_credential()

        # Begin authentication
        options = await self.manager.begin_authentication(
            user_id="user_123",
            tier=AuthenticatorTier.T4_STRONG
        )

        # Verify authentication options structure
        assert "challenge" in options
        assert "rpId" in options
        assert "allowCredentials" in options
        assert "userVerification" in options
        assert "_challenge_id" in options

        # Should include the registered credential
        assert len(options["allowCredentials"]) == 1

        # Verify challenge is stored
        challenge_id = options["_challenge_id"]
        stored_challenge = await self.manager.credential_store.get_challenge(challenge_id)
        assert stored_challenge is not None
        assert stored_challenge.operation == "authentication"

    @pytest.mark.asyncio
    async def test_finish_authentication_mock(self):
        """Test WebAuthn authentication completion (mock implementation)"""
        # Register a credential first
        credential = await self.register_test_credential()

        # Begin authentication
        auth_options = await self.manager.begin_authentication(user_id="user_123")
        challenge_id = auth_options["_challenge_id"]

        # Mock authentication data
        mock_auth_data = {
            "id": credential.credential_id,
            "rawId": credential.credential_id,
            "type": "public-key",
            "response": {
                "authenticatorData": "mock_auth_data",
                "clientDataJSON": "mock_client_data",
                "signature": "mock_signature"
            }
        }

        # Finish authentication
        auth_credential, verification_result = await self.manager.finish_authentication(
            challenge_id=challenge_id,
            credential_data=mock_auth_data
        )

        # Verify authentication result
        assert auth_credential is not None
        assert auth_credential.credential_id == credential.credential_id
        assert verification_result["verified"] is True
        assert auth_credential.sign_count > 0
        assert auth_credential.last_used is not None

    @pytest.mark.asyncio
    async def test_authentication_tiers(self):
        """Test different authentication tiers"""
        # Test T3 tier
        t3_options = await self.manager.begin_registration(
            user_id="user_t3",
            username="t3user",
            display_name="T3 User",
            tier=AuthenticatorTier.T3_MFA
        )

        assert t3_options["authenticatorSelection"]["userVerification"] == "preferred"

        # Test T5 biometric tier
        t5_options = await self.manager.begin_registration(
            user_id="user_t5",
            username="t5user",
            display_name="T5 User",
            tier=AuthenticatorTier.T5_BIOMETRIC
        )

        assert t5_options["authenticatorSelection"]["userVerification"] == "required"
        assert t5_options["attestation"] == "direct"

    @pytest.mark.asyncio
    async def test_authenticator_types(self):
        """Test different authenticator types"""
        # Platform authenticator
        platform_options = await self.manager.begin_registration(
            user_id="user_platform",
            username="platform_user",
            display_name="Platform User",
            authenticator_attachment="platform"
        )

        assert platform_options["authenticatorSelection"]["authenticatorAttachment"] == "platform"

        # Cross-platform authenticator
        roaming_options = await self.manager.begin_registration(
            user_id="user_roaming",
            username="roaming_user",
            display_name="Roaming User",
            authenticator_attachment="cross-platform"
        )

        assert roaming_options["authenticatorSelection"]["authenticatorAttachment"] == "cross-platform"

    @pytest.mark.asyncio
    async def test_list_user_credentials(self):
        """Test listing user credentials"""
        # Register multiple credentials
        await self.register_test_credential("user_multi", "cred1", "Device 1")
        await self.register_test_credential("user_multi", "cred2", "Device 2")

        # List credentials
        credentials_list = await self.manager.list_user_credentials("user_multi")

        assert len(credentials_list) == 2
        assert any(cred["device_name"] == "Device 1" for cred in credentials_list)
        assert any(cred["device_name"] == "Device 2" for cred in credentials_list)

        # Verify credential structure
        cred = credentials_list[0]
        assert "id" in cred
        assert "device_name" in cred
        assert "authenticator_type" in cred
        assert "tier" in cred
        assert "status" in cred
        assert "created_at" in cred

    @pytest.mark.asyncio
    async def test_revoke_credential(self):
        """Test credential revocation"""
        credential = await self.register_test_credential()

        # Revoke credential
        success = await self.manager.revoke_credential(credential.credential_id)
        assert success is True

        # Verify credential is revoked
        retrieved = await self.manager.credential_store.get_credential(credential.credential_id)
        assert retrieved.status == CredentialStatus.REVOKED

    @pytest.mark.asyncio
    async def test_usernameless_authentication(self):
        """Test usernameless (discoverable credential) authentication"""
        # Begin authentication without user ID
        options = await self.manager.begin_authentication(
            user_id=None,
            tier=AuthenticatorTier.T4_STRONG
        )

        # Should allow empty credential list for discoverable credentials
        assert "allowCredentials" in options
        assert isinstance(options["allowCredentials"], list)

    def test_decode_credential_id_round_trip(self):
        """Credential IDs should round-trip through encoding helpers."""
        original = b"credential-bytes"
        encoded = base64.urlsafe_b64encode(original).decode().rstrip("=")

        decoded = self.manager._decode_credential_id(encoded)

        assert decoded == original

    def test_build_descriptor_without_webauthn(self, monkeypatch):
        """Fallback descriptor should be dict when WebAuthn is unavailable."""
        monkeypatch.setattr(webauthn_production, "WEBAUTHN_AVAILABLE", False)
        monkeypatch.setattr(webauthn_production, "PublicKeyCredentialDescriptor", None)

        descriptor = self.manager._build_credential_descriptor("plain-id")

        assert descriptor == {"id": "plain-id", "type": "public-key"}

    def test_build_descriptor_with_webauthn(self, monkeypatch):
        """Descriptor should use WebAuthn struct when available."""

        class DummyDescriptor:
            def __init__(self, *, id: bytes, type: str = "public-key", transports=None):
                self.id = id
                self.type = type
                self.transports = transports

        original = b"binary-data"
        encoded = base64.urlsafe_b64encode(original).decode().rstrip("=")

        monkeypatch.setattr(webauthn_production, "WEBAUTHN_AVAILABLE", True)
        monkeypatch.setattr(webauthn_production, "PublicKeyCredentialDescriptor", DummyDescriptor)

        descriptor = self.manager._build_credential_descriptor(encoded)

        assert isinstance(descriptor, DummyDescriptor)
        assert descriptor.id == original
        assert descriptor.type == "public-key"

    def test_build_descriptor_invalid_id_falls_back(self, monkeypatch):
        """Invalid credential IDs should fall back to dict descriptors."""

        class DummyDescriptor:
            def __init__(self, *, id: bytes, type: str = "public-key", transports=None):
                self.id = id
                self.type = type
                self.transports = transports

        monkeypatch.setattr(webauthn_production, "WEBAUTHN_AVAILABLE", True)
        monkeypatch.setattr(webauthn_production, "PublicKeyCredentialDescriptor", DummyDescriptor)

        descriptor = self.manager._build_credential_descriptor("not-base64@@@")

        assert descriptor == {"id": "not-base64@@@", "type": "public-key"}

    async def register_test_credential(self,
                                     user_id: str = "user_123",
                                     credential_id: str = "test_credential",
                                     device_name: str = "Test Device") -> WebAuthnCredential:
        """Helper method to register a test credential"""
        # Begin registration
        options = await self.manager.begin_registration(
            user_id=user_id,
            username="testuser",
            display_name="Test User"
        )

        challenge_id = options["_challenge_id"]

        # Mock credential data
        mock_credential_data = {
            "id": credential_id,
            "rawId": credential_id,
            "type": "public-key",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }

        # Finish registration
        return await self.manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential_data,
            device_name=device_name
        )


class TestWebAuthnPerformanceRequirements:
    """Test performance requirements for I.4 WebAuthn"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = get_webauthn_manager()

    @pytest.mark.asyncio
    async def test_registration_latency_p95(self):
        """Test that registration latency meets p95 < 100ms requirement"""
        import os
        from datetime import datetime

        latencies = []

        # Run multiple registration operations
        for i in range(20):
            start_time = time.time()

            try:
                options = await self.manager.begin_registration(
                    user_id=f"perf_user_{i}",
                    username=f"perfuser{i}",
                    display_name=f"Perf User {i}"
                )

                latency = time.time() - start_time
                latencies.append(latency)

                # Verify options were generated
                assert "challenge" in options
                assert "_challenge_id" in options

            except Exception as e:
                print(f"Registration failed: {e}")
                latencies.append(float('inf'))

        # Calculate percentiles
        valid_latencies = [l for l in latencies if l != float('inf')]
        valid_latencies.sort()
        p95_index = int(0.95 * len(valid_latencies)) if valid_latencies else 0
        p50_index = int(0.50 * len(valid_latencies)) if valid_latencies else 0
        p99_index = min(int(0.99 * len(valid_latencies)), len(valid_latencies) - 1) if valid_latencies else 0

        p95_latency = valid_latencies[p95_index] if valid_latencies else float('inf')
        p50_latency = valid_latencies[p50_index] if valid_latencies else float('inf')
        p99_latency = valid_latencies[p99_index] if valid_latencies else float('inf')

        print(f"P95 registration latency: {p95_latency:.3f}s")

        # Generate performance artifact
        perf_data = {
            "test": "webauthn_registration_latency",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "p50_ms": p50_latency * 1000 if p50_latency != float('inf') else None,
                "p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "p99_ms": p99_latency * 1000 if p99_latency != float('inf') else None,
                "samples": len(valid_latencies),
                "failed_samples": len(latencies) - len(valid_latencies),
                "target_p95_ms": 100,
                "actual_p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "passed": p95_latency < 0.1
            },
            "latencies_ms": [l * 1000 for l in valid_latencies[:10]]  # First 10 samples
        }

        # Save artifact
        os.makedirs("artifacts", exist_ok=True)
        artifact_path = f"artifacts/perf_webauthn_registration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(artifact_path, "w") as f:
            json.dump(perf_data, f, indent=2)

        print(f"📊 Performance artifact saved: {artifact_path}")

        # Should meet p95 < 100ms requirement
        assert p95_latency < 0.1, f"P95 registration latency {p95_latency:.3f}s exceeds 100ms requirement"

    @pytest.mark.asyncio
    async def test_authentication_latency_p95(self):
        """Test that authentication latency meets p95 < 100ms requirement"""
        import os
        from datetime import datetime

        latencies = []

        # Run multiple authentication operations
        for i in range(20):
            start_time = time.time()

            try:
                options = await self.manager.begin_authentication(
                    user_id=f"auth_user_{i}",
                    tier=AuthenticatorTier.T4_STRONG
                )

                latency = time.time() - start_time
                latencies.append(latency)

                # Verify options were generated
                assert "challenge" in options
                assert "_challenge_id" in options

            except Exception as e:
                print(f"Authentication failed: {e}")
                latencies.append(float('inf'))

        # Calculate percentiles
        valid_latencies = [l for l in latencies if l != float('inf')]
        valid_latencies.sort()
        p95_index = int(0.95 * len(valid_latencies)) if valid_latencies else 0
        p50_index = int(0.50 * len(valid_latencies)) if valid_latencies else 0
        p99_index = min(int(0.99 * len(valid_latencies)), len(valid_latencies) - 1) if valid_latencies else 0

        p95_latency = valid_latencies[p95_index] if valid_latencies else float('inf')
        p50_latency = valid_latencies[p50_index] if valid_latencies else float('inf')
        p99_latency = valid_latencies[p99_index] if valid_latencies else float('inf')

        print(f"P95 authentication latency: {p95_latency:.3f}s")

        # Generate performance artifact
        perf_data = {
            "test": "webauthn_authentication_latency",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "p50_ms": p50_latency * 1000 if p50_latency != float('inf') else None,
                "p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "p99_ms": p99_latency * 1000 if p99_latency != float('inf') else None,
                "samples": len(valid_latencies),
                "failed_samples": len(latencies) - len(valid_latencies),
                "target_p95_ms": 100,
                "actual_p95_ms": p95_latency * 1000 if p95_latency != float('inf') else None,
                "passed": p95_latency < 0.1
            },
            "latencies_ms": [l * 1000 for l in valid_latencies[:10]]  # First 10 samples
        }

        # Save artifact
        os.makedirs("artifacts", exist_ok=True)
        artifact_path = f"artifacts/perf_webauthn_authentication_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(artifact_path, "w") as f:
            json.dump(perf_data, f, indent=2)

        print(f"📊 Performance artifact saved: {artifact_path}")

        # Should meet p95 < 100ms requirement
        assert p95_latency < 0.1, f"P95 authentication latency {p95_latency:.3f}s exceeds 100ms requirement"

    @pytest.mark.asyncio
    async def test_credential_lookup_performance(self):
        """Test credential lookup performance"""
        # Register multiple credentials
        user_id = "perf_lookup_user"
        for i in range(10):
            await self.register_test_credential(
                user_id, f"cred_{i}", f"Device {i}"
            )

        # Measure lookup performance
        start_time = time.time()
        credentials = await self.manager.credential_store.get_credentials(user_id)
        lookup_time = time.time() - start_time

        print(f"Credential lookup time for 10 credentials: {lookup_time:.3f}s")

        assert len(credentials) == 10
        assert lookup_time < 0.01  # Should be very fast

    async def register_test_credential(self,
                                     user_id: str,
                                     credential_id: str,
                                     device_name: str) -> WebAuthnCredential:
        """Helper method to register a test credential"""
        options = await self.manager.begin_registration(
            user_id=user_id,
            username="testuser",
            display_name="Test User"
        )

        challenge_id = options["_challenge_id"]

        mock_credential_data = {
            "id": credential_id,
            "rawId": credential_id,
            "type": "public-key",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }

        return await self.manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential_data,
            device_name=device_name
        )


@pytest.mark.integration
class TestWebAuthnIntegration:
    """Integration tests for WebAuthn system"""

    @pytest.mark.asyncio
    async def test_complete_registration_flow(self):
        """Test complete registration flow end-to-end"""
        manager = get_webauthn_manager()

        # 1. Begin registration
        reg_options = await manager.begin_registration(
            user_id="integration_user",
            username="intuser",
            display_name="Integration User",
            tier=AuthenticatorTier.T5_BIOMETRIC,
            authenticator_attachment="platform",
            device_name="Integration Device"
        )

        assert reg_options is not None
        challenge_id = reg_options["_challenge_id"]

        # 2. Mock client-side WebAuthn response
        mock_credential = {
            "id": "integration_credential_id",
            "rawId": "integration_credential_id",
            "type": "public-key",
            "response": {
                "attestationObject": base64.b64encode(b"mock_attestation").decode(),
                "clientDataJSON": base64.b64encode(b"mock_client_data").decode()
            }
        }

        # 3. Complete registration
        credential = await manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential,
            device_name="Integration Device"
        )

        assert credential.user_id == "integration_user"
        assert credential.tier == AuthenticatorTier.T5_BIOMETRIC
        assert credential.device_name == "Integration Device"

        # 4. Begin authentication
        auth_options = await manager.begin_authentication(
            user_id="integration_user",
            tier=AuthenticatorTier.T5_BIOMETRIC
        )

        assert len(auth_options["allowCredentials"]) == 1
        auth_challenge_id = auth_options["_challenge_id"]

        # 5. Mock authentication response
        mock_assertion = {
            "id": credential.credential_id,
            "rawId": credential.credential_id,
            "type": "public-key",
            "response": {
                "authenticatorData": base64.b64encode(b"mock_auth_data").decode(),
                "clientDataJSON": base64.b64encode(b"mock_client_data").decode(),
                "signature": base64.b64encode(b"mock_signature").decode()
            }
        }

        # 6. Complete authentication
        auth_cred, verification = await manager.finish_authentication(
            challenge_id=auth_challenge_id,
            credential_data=mock_assertion
        )

        assert verification["verified"] is True
        assert auth_cred.credential_id == credential.credential_id
        assert auth_cred.sign_count > 0

    def test_global_manager_configuration(self):
        """Test global WebAuthn manager configuration"""
        manager1 = get_webauthn_manager()
        manager2 = get_webauthn_manager()

        # Should return same instance
        assert manager1 is manager2

        # Should have correct default configuration
        assert manager1.rp_id == "ai"
        assert manager1.rp_name == "LUKHAS AI"
        assert manager1.origin == "https://ai"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
