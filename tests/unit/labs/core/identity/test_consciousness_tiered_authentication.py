import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from labs.core.identity.consciousness_tiered_authentication import (
    TieredAuthenticationEngine,
    ConsciousnessWebAuthnManager,
    AuthenticationCredential,
    AuthenticationMethod,
    TierValidationResult,
)

class TestConsciousnessWebAuthnManager(unittest.TestCase):

    def setUp(self):
        modules_to_mock = {
            "labs.core.identity.lambda_id_core.WebAuthnPasskeyManager": MagicMock(),
            "labs.core.matriz_consciousness_signals": MagicMock(),
            "labs.core.identity.matriz_consciousness_identity_signals": MagicMock(),
        }

        self.patcher = patch.dict('sys.modules', modules_to_mock)
        self.patcher.start()

        self.manager = ConsciousnessWebAuthnManager()

    def tearDown(self):
        self.patcher.stop()

    def test_initiate_consciousness_registration(self):
        """Test the initiation of a consciousness-enhanced WebAuthn registration."""
        async def run_test():
            result = await self.manager.initiate_consciousness_registration("test_id", "test@example.com", {})
            self.assertIn("consciousness_challenge", result)

        asyncio.run(run_test())

    @patch('labs.core.identity.consciousness_tiered_authentication.WebAuthnPasskeyManager')
    def test_complete_consciousness_registration(self, mock_webauthn):
        """Test the completion of a consciousness-enhanced WebAuthn registration."""
        mock_webauthn_instance = mock_webauthn.return_value
        mock_webauthn_instance.complete_registration.return_value = True

        async def run_test():
            reg_init = await self.manager.initiate_consciousness_registration("test_id", "test@example.com", {})
            session_id = reg_init['consciousness_challenge']['session_id']

            success = await self.manager.complete_consciousness_registration("test_id", {}, {"session_id": session_id})
            self.assertTrue(success)

        asyncio.run(run_test())

    def test_get_tier_consciousness_requirements(self):
        """Test that the correct consciousness requirements are returned for each tier."""
        mock_auth_tier = MagicMock()
        mock_auth_tier.T1_BASIC.value = "T1_BASIC"
        mock_auth_tier.T5_TRANSCENDENT.value = "T5_TRANSCENDENT"

        with patch('labs.core.identity.consciousness_tiered_authentication.AuthenticationTier', mock_auth_tier):
            requirements_t1 = self.manager._get_tier_consciousness_requirements(mock_auth_tier.T1_BASIC)
            self.assertEqual(requirements_t1["minimum_consciousness_coherence"], 0.3)

            requirements_t5 = self.manager._get_tier_consciousness_requirements(mock_auth_tier.T5_TRANSCENDENT)
            self.assertEqual(requirements_t5["minimum_reflection_depth"], 3)

class TestTieredAuthenticationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TieredAuthenticationEngine()

    @patch('labs.core.identity.consciousness_tiered_authentication.ConsciousnessWebAuthnManager.verify_consciousness_authentication', new_callable=AsyncMock)
    def test_authenticate_with_tier_webauthn(self, mock_verify):
        """Test authentication with the WebAuthn method."""
        mock_verify.return_value = TierValidationResult(tier="T1_BASIC", success=True, confidence_score=0.8)

        async def run_test():
            creds = [AuthenticationCredential(method=AuthenticationMethod.WEBAUTHN_PASSKEY, credential_data={})]
            result = await self.engine.authenticate_with_tier("test_id", creds)
            self.assertTrue(result.success)
            self.assertEqual(result.tier, "T1_BASIC")

        asyncio.run(run_test())

    def test_handle_consciousness_authentication_success(self):
        """Test successful authentication with a pure consciousness signature."""
        async def run_test():
            creds = AuthenticationCredential(
                method=AuthenticationMethod.CONSCIOUSNESS_SIGNATURE,
                credential_data={"consciousness_signature": {"reflection_depth": 3, "metacognition_level": 0.7, "self_awareness": 0.8}}
            )
            result = await self.engine._handle_consciousness_authentication("test_id", creds, None)
            self.assertTrue(result.success)
            self.assertEqual(result.tier, "T3_CONSCIOUSNESS")

        asyncio.run(run_test())

    def test_handle_consciousness_authentication_failure(self):
        """Test failed authentication with a pure consciousness signature."""
        async def run_test():
            creds = AuthenticationCredential(
                method=AuthenticationMethod.CONSCIOUSNESS_SIGNATURE,
                credential_data={"consciousness_signature": {"reflection_depth": 1, "metacognition_level": 0.2, "self_awareness": 0.3}}
            )
            result = await self.engine._handle_consciousness_authentication("test_id", creds, None)
            self.assertFalse(result.success)

        asyncio.run(run_test())

    def test_handle_brainwave_authentication_success(self):
        """Test successful authentication with brainwave patterns."""
        async def run_test():
            with patch.object(self.engine.consciousness_webauthn, '_validate_brainwave_pattern', return_value=0.8):
                creds = AuthenticationCredential(
                    method=AuthenticationMethod.BRAINWAVE_AUTH,
                    credential_data={"brainwave_pattern": {"gamma": 0.9}}
                )
                result = await self.engine._handle_brainwave_authentication("test_id", creds, None)
                self.assertTrue(result.success)
                self.assertEqual(result.tier, "T3_CONSCIOUSNESS")

        asyncio.run(run_test())

    def test_handle_quantum_authentication_success(self):
        """Test successful authentication with quantum signatures."""
        async def run_test():
            with patch.object(self.engine.consciousness_webauthn, '_validate_quantum_entropy', return_value=0.9):
                creds = AuthenticationCredential(
                    method=AuthenticationMethod.QUANTUM_SIGNATURE,
                    credential_data={"quantum_signature": {"entropy_score": 0.9, "quantum_signature": "a"*16}}
                )
                result = await self.engine._handle_quantum_authentication("test_id", creds, None)
                self.assertTrue(result.success)
                self.assertEqual(result.tier, "T4_QUANTUM")

        asyncio.run(run_test())

    def test_handle_transcendent_authentication_success(self):
        """Test successful authentication with transcendent verification."""
        async def run_test():
            with patch.object(self.engine.consciousness_webauthn, '_validate_brainwave_pattern', return_value=0.95), \
                 patch.object(self.engine, '_handle_consciousness_authentication', new_callable=AsyncMock) as mock_handle_consciousness, \
                 patch.object(self.engine.consciousness_webauthn, '_validate_quantum_entropy', return_value=0.95):

                mock_handle_consciousness.return_value = TierValidationResult(tier="T3_CONSCIOUSNESS", success=True, confidence_score=0.95)

                creds = AuthenticationCredential(
                    method=AuthenticationMethod.TRANSCENDENT_VERIFICATION,
                    credential_data={
                        "brainwave_pattern": {"gamma": 0.9},
                        "consciousness_signature": {"reflection_depth": 4},
                        "quantum_signature": {"entropy_score": 0.9, "quantum_signature": "a"*16}
                    }
                )
                result = await self.engine._handle_transcendent_authentication("test_id", creds, None)
                self.assertTrue(result.success)
                self.assertEqual(result.tier, "T5_TRANSCENDENT")

        asyncio.run(run_test())


    def test_combine_validation_results(self):
        """Test the combination of multiple validation results."""
        results = [
            TierValidationResult(tier="T1_BASIC", success=True, confidence_score=0.7),
            TierValidationResult(tier="T3_CONSCIOUSNESS", success=True, confidence_score=0.9),
            TierValidationResult(tier="T2_ENHANCED", success=False, confidence_score=0.4),
        ]

        mock_auth_tier = MagicMock()
        mock_auth_tier.T3_CONSCIOUSNESS.value = "T3_CONSCIOUSNESS"

        with patch('labs.core.identity.consciousness_tiered_authentication.AuthenticationTier', mock_auth_tier):
            final_result = self.engine._combine_validation_results(results, mock_auth_tier.T3_CONSCIOUSNESS)
            self.assertTrue(final_result.success)
            self.assertEqual(final_result.tier, "T3_CONSCIOUSNESS")
            self.assertAlmostEqual(final_result.confidence_score, 0.85)


if __name__ == "__main__":
    unittest.main()
