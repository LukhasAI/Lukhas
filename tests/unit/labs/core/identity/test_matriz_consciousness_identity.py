import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from dataclasses import dataclass

@dataclass
class BioSymbolicData:
    pass

# Patch the BioSymbolicData name before importing the module that uses it
patch('labs.core.identity.matriz_consciousness_identity_signals.BioSymbolicData', BioSymbolicData, create=True).start()

from labs.core.identity.matriz_consciousness_identity import (
    MatrizConsciousnessIdentityManager,
    ConsciousnessIdentityProfile,
    IdentityConsciousnessType,
)

class TestMatrizConsciousnessIdentityManager(unittest.TestCase):

    def setUp(self):
        modules_to_mock = {
            "labs.core.consciousness.matriz_consciousness_state": MagicMock(),
            "labs.core.matriz_adapter": MagicMock(),
            "labs.core.identity.matriz_consciousness_identity_signals": MagicMock(),
            "labs.core.identity.lambda_id_core.LukhasIdentityService": MagicMock(),
        }

        self.patcher = patch.dict('sys.modules', modules_to_mock)
        self.patcher.start()

        self.manager = MatrizConsciousnessIdentityManager()

    def tearDown(self):
        self.patcher.stop()
        patch.stopall()

    @patch('labs.core.identity.matriz_consciousness_identity.create_consciousness_state', new_callable=AsyncMock)
    def test_create_consciousness_identity(self, mock_create_consciousness_state):
        """Test the creation of a new consciousness-aware identity profile."""
        mock_create_consciousness_state.return_value = MagicMock(consciousness_id="consciousness-123")

        async def run_test():
            profile = await self.manager.create_consciousness_identity("test_user")
            self.assertIsInstance(profile, ConsciousnessIdentityProfile)
            self.assertEqual(profile.user_identifier, "test_user")

        asyncio.run(run_test())

    @patch('labs.core.identity.matriz_consciousness_identity.consciousness_state_manager', new_callable=MagicMock)
    def test_authenticate_consciousness_identity_success(self, mock_consciousness_state_manager):
        """Test the successful authentication of a consciousness-aware identity."""
        mock_consciousness_state_manager.evolve_consciousness = AsyncMock(return_value=MagicMock(
            evolutionary_stage=MagicMock(value="test_stage"),
            STATE={"consciousness_intensity": 0.5}
        ))

        async def run_test():
            profile = await self.manager.create_consciousness_identity("test_user")
            auth_context = {"method": "test", "authenticated": True, "password_valid": True}
            result = await self.manager.authenticate_consciousness_identity(profile.identity_id, auth_context)
            self.assertTrue(result["success"])
            self.assertEqual(result["identity_id"], profile.identity_id)

        asyncio.run(run_test())

    def test_authenticate_consciousness_identity_not_found(self):
        """Test that authentication fails for an unknown identity."""
        async def run_test():
            auth_context = {"method": "test", "authenticated": True}
            result = await self.manager.authenticate_consciousness_identity("unknown_id", auth_context)
            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Identity not found")

        asyncio.run(run_test())

    def test_evolve_identity_consciousness_type(self):
        """Test the evolution of the identity's consciousness type."""
        profile = ConsciousnessIdentityProfile(user_identifier="test_user")

        # Test evolution from ANONYMOUS to IDENTIFIED
        context = {"user_identifier": "test_user"}
        new_type = self.manager._evolve_identity_consciousness_type(profile, context)
        self.assertEqual(new_type, IdentityConsciousnessType.IDENTIFIED)

        # Test evolution from IDENTIFIED to AUTHENTICATED
        profile.identity_consciousness_type = IdentityConsciousnessType.IDENTIFIED
        context = {"authenticated": True}
        new_type = self.manager._evolve_identity_consciousness_type(profile, context)
        self.assertEqual(new_type, IdentityConsciousnessType.AUTHENTICATED)

        # Test evolution from AUTHENTICATED to CONSCIOUSNESS_LINKED
        profile.identity_consciousness_type = IdentityConsciousnessType.AUTHENTICATED
        profile.consciousness_id = "consciousness-123"
        new_type = self.manager._evolve_identity_consciousness_type(profile, {})
        self.assertEqual(new_type, IdentityConsciousnessType.CONSCIOUSNESS_LINKED)


    @patch('labs.core.identity.matriz_consciousness_identity.consciousness_state_manager', new_callable=MagicMock)
    def test_update_consciousness_memory(self, mock_consciousness_state_manager):
        """Test updating the consciousness memory for an identity."""
        mock_consciousness_state_manager.evolve_consciousness = AsyncMock()

        async def run_test():
            profile = await self.manager.create_consciousness_identity("test_user")
            success = await self.manager.update_consciousness_memory(profile.identity_id, "test_key", "test_value")
            self.assertTrue(success)
            self.assertIn("test_key", profile.consciousness_memories)

        asyncio.run(run_test())

    def test_update_consciousness_memory_not_found(self):
        """Test that updating consciousness memory for an unknown identity fails."""
        async def run_test():
            success = await self.manager.update_consciousness_memory("unknown_id", "test_key", "test_value")
            self.assertFalse(success)

        asyncio.run(run_test())

    def test_persist_and_restore_identity_state(self):
        """Test persisting and restoring an identity's state."""
        async def run_test():
            self.manager.signal_emitter = MagicMock()
            self.manager.signal_emitter.emit_identity_evolution_signal = AsyncMock()

            profile = await self.manager.create_consciousness_identity("test_user")
            profile.consciousness_depth = 0.7

            success = await self.manager.persist_identity_state(profile.identity_id)
            self.assertTrue(success)

            restored_profile = await self.manager.restore_identity_state(profile.identity_id)
            self.assertIsNotNone(restored_profile)
            self.assertEqual(restored_profile.consciousness_depth, 0.7)

        asyncio.run(run_test())

    def test_restore_identity_state_not_found(self):
        """Test that restoring a non-existent identity state returns None."""
        async def run_test():
            restored_profile = await self.manager.restore_identity_state("unknown_id")
            self.assertIsNone(restored_profile)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
