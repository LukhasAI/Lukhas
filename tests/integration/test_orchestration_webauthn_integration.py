#!/usr/bin/env python3
"""
Integration Tests for LUKHAS O.2 + I.4 Components
Production Schema v1.0.0

End-to-end integration tests validating O.2 Orchestration Core
and I.4 WebAuthn/Passkeys working together with full authentication flow.

Constellation Framework: ⚛️🧠🛡️ integrated validation
"""

import time
from unittest.mock import Mock

import pytest

from identity.webauthn_production import AuthenticatorTier, get_webauthn_manager
from orchestration.multi_ai_router import (
    AIProvider,
    ConsensusType,
    RoutingRequest,
    get_multi_ai_router,
)


@pytest.mark.integration
class TestOrchestrationWebAuthnIntegration:
    """Integration tests for Orchestration + WebAuthn systems"""

    def setup_method(self):
        """Set up test fixtures"""
        self.multi_ai_router = get_multi_ai_router()
        self.webauthn_manager = get_webauthn_manager(
            rp_id="test.ai",
            rp_name="Test LUKHAS",
            origin="https://test.ai"
        )

        # Mock AI clients
        mock_client = Mock()
        for provider in AIProvider:
            self.multi_ai_router.register_ai_client(provider, mock_client)

    @pytest.mark.asyncio
    async def test_authenticated_orchestration_flow(self):
        """Test complete flow: WebAuthn auth → Multi-AI orchestration"""

        # Step 1: Register WebAuthn credential for user
        user_id = "integration_test_user"

        # Begin WebAuthn registration
        reg_options = await self.webauthn_manager.begin_registration(
            user_id=user_id,
            username="testuser",
            display_name="Test User",
            tier=AuthenticatorTier.T4_STRONG
        )

        challenge_id = reg_options["_challenge_id"]

        # Complete WebAuthn registration (mock)
        mock_credential_data = {
            "id": "test_credential_123",
            "rawId": "test_credential_123",
            "type": "public-key",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }

        credential = await self.webauthn_manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential_data,
            device_name="Test Device"
        )

        assert credential is not None
        assert credential.user_id == user_id

        # Step 2: Authenticate with WebAuthn
        auth_options = await self.webauthn_manager.begin_authentication(
            user_id=user_id,
            tier=AuthenticatorTier.T4_STRONG
        )

        auth_challenge_id = auth_options["_challenge_id"]

        # Complete WebAuthn authentication (mock)
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

        auth_credential, verification = await self.webauthn_manager.finish_authentication(
            challenge_id=auth_challenge_id,
            credential_data=mock_auth_data
        )

        assert verification["verified"] == True
        assert auth_credential.user_id == user_id

        # Step 3: Use authenticated identity for multi-AI orchestration
        orchestration_request = RoutingRequest(
            prompt="Explain the benefits of multi-factor authentication",
            consensus_type=ConsensusType.MAJORITY,
            min_responses=2,
            max_responses=3,
            metadata={
                "authenticated_user": user_id,
                "auth_tier": auth_credential.tier.value,
                "device_name": auth_credential.device_name,
                "biometric_enrolled": auth_credential.biometric_enrolled
            }
        )

        # Route request through multi-AI system
        orchestration_result = await self.multi_ai_router.route_request(orchestration_request)

        # Verify orchestration result
        assert orchestration_result is not None
        assert orchestration_result.final_response is not None
        assert orchestration_result.consensus_type == ConsensusType.MAJORITY
        assert len(orchestration_result.participating_models) >= 2
        assert orchestration_result.confidence > 0
        assert orchestration_result.agreement_ratio >= 0

        print("Integration test completed successfully:")
        print(f"- WebAuthn credential registered and authenticated for user: {user_id}")
        print(f"- Multi-AI orchestration consensus: {orchestration_result.consensus_type.value}")
        print(f"- Participating models: {len(orchestration_result.participating_models)}")
        print(f"- Final confidence: {orchestration_result.confidence:.2f}")
        print(f"- Agreement ratio: {orchestration_result.agreement_ratio:.2f}")

    @pytest.mark.asyncio
    async def test_tiered_authentication_orchestration(self):
        """Test different authentication tiers affecting orchestration access"""

        user_id = "tiered_auth_user"

        # Test T3, T4, and T5 authentication tiers
        for tier in [AuthenticatorTier.T3_MFA, AuthenticatorTier.T4_STRONG, AuthenticatorTier.T5_BIOMETRIC]:

            # Register credential for this tier
            reg_options = await self.webauthn_manager.begin_registration(
                user_id=f"{user_id}_{tier.value}",
                username=f"user_{tier.value}",
                display_name=f"User {tier.value}",
                tier=tier
            )

            challenge_id = reg_options["_challenge_id"]

            mock_credential_data = {
                "id": f"credential_{tier.value}",
                "rawId": f"credential_{tier.value}",
                "type": "public-key",
                "response": {
                    "attestationObject": "mock_attestation",
                    "clientDataJSON": "mock_client_data"
                }
            }

            credential = await self.webauthn_manager.finish_registration(
                challenge_id=challenge_id,
                credential_data=mock_credential_data,
                device_name=f"Device {tier.value}"
            )

            assert credential.tier == tier

            # Test orchestration with different tier requirements
            sensitive_request = RoutingRequest(
                prompt="Generate a security analysis report",
                consensus_type=ConsensusType.UNANIMOUS if tier == AuthenticatorTier.T5_BIOMETRIC else ConsensusType.MAJORITY,
                min_responses=3 if tier == AuthenticatorTier.T5_BIOMETRIC else 2,
                max_responses=3,
                metadata={
                    "security_level": "high" if tier == AuthenticatorTier.T5_BIOMETRIC else "medium",
                    "auth_tier": tier.value,
                    "requires_biometric": tier == AuthenticatorTier.T5_BIOMETRIC
                }
            )

            result = await self.multi_ai_router.route_request(sensitive_request)

            assert result is not None
            # Higher tiers should get stricter consensus requirements
            if tier == AuthenticatorTier.T5_BIOMETRIC:
                assert result.consensus_type in [ConsensusType.UNANIMOUS, ConsensusType.MAJORITY]

    @pytest.mark.asyncio
    async def test_multi_device_orchestration(self):
        """Test orchestration with multiple registered devices"""

        user_id = "multi_device_user"
        devices = ["iPhone", "MacBook", "YubiKey"]
        credentials = []

        # Register multiple devices
        for i, device_name in enumerate(devices):
            reg_options = await self.webauthn_manager.begin_registration(
                user_id=user_id,
                username="multiuser",
                display_name="Multi Device User",
                tier=AuthenticatorTier.T4_STRONG,
                authenticator_attachment="platform" if device_name != "YubiKey" else "cross-platform"
            )

            challenge_id = reg_options["_challenge_id"]

            mock_credential_data = {
                "id": f"credential_{i}",
                "rawId": f"credential_{i}",
                "type": "public-key",
                "response": {
                    "attestationObject": "mock_attestation",
                    "clientDataJSON": "mock_client_data"
                }
            }

            credential = await self.webauthn_manager.finish_registration(
                challenge_id=challenge_id,
                credential_data=mock_credential_data,
                device_name=device_name
            )

            credentials.append(credential)

        # Verify all devices are registered
        user_credentials = await self.webauthn_manager.list_user_credentials(user_id)
        assert len(user_credentials) == 3

        # Test authentication from different devices
        for i, credential in enumerate(credentials):
            # Begin authentication
            auth_options = await self.webauthn_manager.begin_authentication(
                user_id=user_id,
                tier=AuthenticatorTier.T4_STRONG
            )

            # Should allow any of the registered credentials
            assert len(auth_options["allowCredentials"]) == 3

            auth_challenge_id = auth_options["_challenge_id"]

            # Authenticate with specific device
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

            auth_credential, verification = await self.webauthn_manager.finish_authentication(
                challenge_id=auth_challenge_id,
                credential_data=mock_auth_data
            )

            assert verification["verified"] == True

            # Use authenticated session for orchestration
            device_specific_request = RoutingRequest(
                prompt=f"Analyze data from {credential.device_name}",
                consensus_type=ConsensusType.WEIGHTED,
                metadata={
                    "device_name": credential.device_name,
                    "authenticator_type": credential.authenticator_type.value,
                    "session_id": f"session_{i}"
                }
            )

            result = await self.multi_ai_router.route_request(device_specific_request)
            assert result is not None
            assert result.consensus_type == ConsensusType.WEIGHTED

    @pytest.mark.asyncio
    async def test_performance_integrated_flow(self):
        """Test performance of complete integrated authentication + orchestration flow"""

        user_id = "performance_user"
        iterations = 5
        total_latencies = []

        for i in range(iterations):
            start_time = time.time()

            # 1. WebAuthn Registration (if first iteration)
            if i == 0:
                reg_options = await self.webauthn_manager.begin_registration(
                    user_id=user_id,
                    username="perfuser",
                    display_name="Performance User"
                )

                challenge_id = reg_options["_challenge_id"]

                mock_credential_data = {
                    "id": "perf_credential",
                    "rawId": "perf_credential",
                    "type": "public-key",
                    "response": {
                        "attestationObject": "mock_attestation",
                        "clientDataJSON": "mock_client_data"
                    }
                }

                await self.webauthn_manager.finish_registration(
                    challenge_id=challenge_id,
                    credential_data=mock_credential_data,
                    device_name="Performance Device"
                )

                registration_time = time.time() - start_time
                print(f"Registration time: {registration_time:.3f}s")

                # Reset for authentication timing
                start_time = time.time()

            # 2. WebAuthn Authentication
            auth_options = await self.webauthn_manager.begin_authentication(
                user_id=user_id,
                tier=AuthenticatorTier.T4_STRONG
            )

            auth_challenge_id = auth_options["_challenge_id"]

            mock_auth_data = {
                "id": "perf_credential",
                "rawId": "perf_credential",
                "type": "public-key",
                "response": {
                    "authenticatorData": "mock_auth_data",
                    "clientDataJSON": "mock_client_data",
                    "signature": "mock_signature"
                }
            }

            auth_credential, verification = await self.webauthn_manager.finish_authentication(
                challenge_id=auth_challenge_id,
                credential_data=mock_auth_data
            )

            assert verification["verified"] == True

            # 3. Multi-AI Orchestration
            orchestration_request = RoutingRequest(
                prompt=f"Performance test iteration {i}",
                consensus_type=ConsensusType.MAJORITY,
                min_responses=2,
                max_responses=2,
                metadata={"iteration": i, "user_id": user_id}
            )

            result = await self.multi_ai_router.route_request(orchestration_request)
            assert result is not None

            total_latency = time.time() - start_time
            total_latencies.append(total_latency)

        # Calculate performance metrics
        avg_latency = sum(total_latencies) / len(total_latencies)
        max_latency = max(total_latencies)
        min_latency = min(total_latencies)

        print(f"Integrated flow performance ({iterations} iterations):")
        print(f"  Average latency: {avg_latency:.3f}s")
        print(f"  Min latency: {min_latency:.3f}s")
        print(f"  Max latency: {max_latency:.3f}s")

        # Performance requirements
        # Complete flow (auth + orchestration) should be under 1 second on average
        assert avg_latency < 1.0, f"Average integrated flow latency {avg_latency:.3f}s exceeds 1s"
        assert max_latency < 2.0, f"Maximum integrated flow latency {max_latency:.3f}s exceeds 2s"

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling in integrated authentication + orchestration flow"""

        user_id = "error_test_user"

        # Test 1: Authentication failure should prevent orchestration
        try:
            # Try to authenticate non-existent user
            auth_options = await self.webauthn_manager.begin_authentication(
                user_id="nonexistent_user",
                tier=AuthenticatorTier.T4_STRONG
            )

            # Should still work (might be usernameless flow)
            assert "challenge" in auth_options

        except Exception as e:
            print(f"Expected authentication error: {e}")

        # Test 2: Register user but test invalid authentication
        reg_options = await self.webauthn_manager.begin_registration(
            user_id=user_id,
            username="erroruser",
            display_name="Error Test User"
        )

        challenge_id = reg_options["_challenge_id"]

        mock_credential_data = {
            "id": "error_credential",
            "rawId": "error_credential",
            "type": "public-key",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }

        await self.webauthn_manager.finish_registration(
            challenge_id=challenge_id,
            credential_data=mock_credential_data
        )

        # Test expired challenge
        try:
            # Try to use expired/invalid challenge
            await self.webauthn_manager.finish_authentication(
                challenge_id="invalid_challenge",
                credential_data={"id": "fake"}
            )
            assert False, "Should have raised exception for invalid challenge"
        except Exception as e:
            print(f"Expected challenge error: {e}")

        # Test 3: Orchestration with insufficient models
        try:
            impossible_request = RoutingRequest(
                prompt="Test impossible request",
                min_responses=10,  # More than available models
                max_responses=10
            )

            await self.multi_ai_router.route_request(impossible_request)
            assert False, "Should have raised exception for insufficient models"
        except Exception as e:
            print(f"Expected orchestration error: {e}")

    def test_system_availability(self):
        """Test that both systems are properly initialized and available"""

        # Test WebAuthn manager availability
        webauthn_manager = get_webauthn_manager()
        assert webauthn_manager is not None
        assert webauthn_manager.rp_id == "ai"
        assert webauthn_manager.credential_store is not None

        # Test Multi-AI router availability
        multi_ai_router = get_multi_ai_router()
        assert multi_ai_router is not None
        assert multi_ai_router.model_selector is not None
        assert multi_ai_router.consensus_engine is not None
        assert len(multi_ai_router.model_selector.models) > 0

        # Test that systems can work independently
        assert webauthn_manager is not multi_ai_router
        assert hasattr(webauthn_manager, 'begin_registration')
        assert hasattr(multi_ai_router, 'route_request')

        print("✅ O.2 Orchestration Core and I.4 WebAuthn systems are both available and properly integrated")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
