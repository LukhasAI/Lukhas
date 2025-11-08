import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from labs.core.identity.consciousness_namespace_isolation import (
    ConsciousnessNamespaceManager,
    ConsciousnessDomain,
    IsolationLevel,
    AccessPermissionType,
)

class TestConsciousnessNamespaceManager(unittest.TestCase):

    def setUp(self):
        # To support running tests in environments where some modules are not available,
        # we are creating mock objects for the missing modules.
        # In a real-world scenario, it would be preferable to install all the required modules.
        modules_to_mock = {
            "labs.core.matriz_consciousness_signals": MagicMock(),
            "labs.core.identity.matriz_consciousness_identity_signals": MagicMock(),
        }

        self.patcher = patch.dict('sys.modules', modules_to_mock)
        self.patcher.start()

        self.manager = ConsciousnessNamespaceManager()

    def tearDown(self):
        self.patcher.stop()

    def test_create_consciousness_namespace(self):
        """Test the creation of a new consciousness namespace."""
        async def run_test():
            namespace_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.USER_CONSCIOUSNESS, IsolationLevel.MODERATE
            )
            self.assertIsNotNone(namespace_id)
            self.assertIn(namespace_id, self.manager.namespace_instances)

        asyncio.run(run_test())

    def test_create_consciousness_namespace_with_overrides(self):
        """Test creating a namespace with policy overrides."""
        async def run_test():
            overrides = {"consciousness_bridge_enabled": False}
            namespace_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.USER_CONSCIOUSNESS, IsolationLevel.MODERATE, policy_overrides=overrides
            )
            self.assertFalse(self.manager.namespace_instances[namespace_id].policy.consciousness_bridge_enabled)

        asyncio.run(run_test())


    def test_assign_identity_to_namespace(self):
        """Test assigning an identity to a namespace."""
        async def run_test():
            namespace_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.USER_CONSCIOUSNESS, IsolationLevel.MODERATE
            )
            success = await self.manager.assign_identity_to_namespace("test_id", namespace_id)
            self.assertTrue(success)
            self.assertIn("test_id", self.manager.namespace_instances[namespace_id].active_identities)

        asyncio.run(run_test())

    def test_assign_identity_to_namespace_not_found(self):
        """Test that assigning an identity to a non-existent namespace fails."""
        async def run_test():
            success = await self.manager.assign_identity_to_namespace("test_id", "unknown_id")
            self.assertFalse(success)

        asyncio.run(run_test())

    def test_validate_cross_domain_access_allowed(self):
        """Test that cross-domain access is allowed when policies permit it."""
        async def run_test():
            source_ns_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.USER_CONSCIOUSNESS, IsolationLevel.MODERATE
            )
            target_ns_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.AGENT_CONSCIOUSNESS, IsolationLevel.HIGH
            )
            await self.manager.assign_identity_to_namespace(
                "test_id", source_ns_id, [AccessPermissionType.READ_ONLY, AccessPermissionType.CONSCIOUSNESS_BRIDGE]
            )

            result = await self.manager.validate_cross_domain_access("test_id", source_ns_id, target_ns_id, "read")
            self.assertTrue(result["allowed"])

        asyncio.run(run_test())

    def test_validate_cross_domain_access_denied(self):
        """Test that cross-domain access is denied when policies prohibit it."""
        async def run_test():
            source_ns_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.USER_CONSCIOUSNESS, IsolationLevel.MODERATE
            )
            target_ns_id = await self.manager.create_consciousness_namespace(
                ConsciousnessDomain.SYSTEM_CONSCIOUSNESS, IsolationLevel.MAXIMUM
            )
            await self.manager.assign_identity_to_namespace("test_id", source_ns_id)

            result = await self.manager.validate_cross_domain_access("test_id", source_ns_id, target_ns_id, "read")
            self.assertFalse(result["allowed"])

        asyncio.run(run_test())

    def test_create_cross_domain_bridge_allowed(self):
        """Test that creating a cross-domain bridge is allowed when policies permit it."""
        async def run_test():
            bridge_id = await self.manager.create_cross_domain_bridge(
                ConsciousnessDomain.USER_CONSCIOUSNESS, ConsciousnessDomain.AGENT_CONSCIOUSNESS
            )
            self.assertIsNotNone(bridge_id)
            self.assertIn(bridge_id, self.manager.cross_domain_bridges)

        asyncio.run(run_test())

    def test_create_cross_domain_bridge_denied(self):
        """Test that creating a cross-domain bridge is denied when policies prohibit it."""
        async def run_test():
            bridge_id = await self.manager.create_cross_domain_bridge(
                ConsciousnessDomain.USER_CONSCIOUSNESS, ConsciousnessDomain.SYSTEM_CONSCIOUSNESS
            )
            self.assertIsNone(bridge_id)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
