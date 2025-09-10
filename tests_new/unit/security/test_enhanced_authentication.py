import asyncio
import unittest

from candidate.core.security.auth import EnhancedAuthenticationSystem


class TestEnhancedAuthenticationSystem(unittest.TestCase):
    def setUp(self):
        """Set up a new EnhancedAuthenticationSystem for each test."""
        self.auth_system = EnhancedAuthenticationSystem()

    def test_generate_api_key(self):
        """Test the generation of a new API key."""
        user_id = "test_user_123"
        scopes = ["read", "write"]
        key_id, key_secret = self.auth_system.generate_api_key(user_id, scopes)

        self.assertIsInstance(key_id, str)
        self.assertIsInstance(key_secret, str)
        self.assertTrue(len(key_id) > 10)
        self.assertTrue(len(key_secret) > 20)

    def test_verify_api_key_valid(self):
        """Test verification of a valid API key."""
        user_id = "test_user_valid"
        scopes = ["read:all"]
        key_id, key_secret = self.auth_system.generate_api_key(user_id, scopes)

        async def run_test():
            key_data = await self.auth_system.verify_api_key(key_id, key_secret)
            self.assertIsNotNone(key_data)
            self.assertEqual(key_data["user_id"], user_id)
            self.assertEqual(key_data["scopes"], scopes)

        asyncio.run(run_test())

    def test_verify_api_key_invalid_secret(self):
        """Test that verification fails with an invalid secret."""
        user_id = "test_user_invalid_secret"
        scopes = ["read"]
        key_id, _ = self.auth_system.generate_api_key(user_id, scopes)

        async def run_test():
            key_data = await self.auth_system.verify_api_key(key_id, "wrong_secret")
            self.assertIsNone(key_data)

        asyncio.run(run_test())

    def test_verify_api_key_invalid_id(self):
        """Test that verification fails with an invalid key_id."""
        user_id = "test_user_invalid_id"
        scopes = ["read"]
        _, key_secret = self.auth_system.generate_api_key(user_id, scopes)

        async def run_test():
            key_data = await self.auth_system.verify_api_key("wrong_id", key_secret)
            self.assertIsNone(key_data)

        asyncio.run(run_test())

    def test_revoke_api_key(self):
        """Test that a revoked API key cannot be verified."""
        user_id = "test_user_revoked"
        scopes = ["admin"]
        key_id, key_secret = self.auth_system.generate_api_key(user_id, scopes)

        async def run_test():
            # First, verify it's valid
            key_data_before = await self.auth_system.verify_api_key(key_id, key_secret)
            self.assertIsNotNone(key_data_before)

            # Revoke the key
            await self.auth_system.revoke_api_key(key_id)

            # Now, it should not be valid
            key_data_after = await self.auth_system.verify_api_key(key_id, key_secret)
            self.assertIsNone(key_data_after)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()