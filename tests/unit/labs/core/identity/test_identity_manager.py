import unittest
from labs.core.identity.identity_manager import IdentityManager

class TestIdentityManager(unittest.TestCase):

    def test_initialization_with_config(self):
        """Test that the IdentityManager initializes correctly with a config."""
        config = {"test_key": "test_value"}
        manager = IdentityManager(config=config)
        self.assertEqual(manager.config, config)
        self.assertIsNone(manager.active_identity)

    def test_initialization_without_config(self):
        """Test that the IdentityManager initializes correctly without a config."""
        manager = IdentityManager()
        self.assertEqual(manager.config, {})
        self.assertIsNone(manager.active_identity)

    def test_set_and_get_identity(self):
        """Test that setting and getting an identity works correctly."""
        manager = IdentityManager()
        identity = {"name": "test_user", "type": "user"}
        manager.set_identity(identity)
        self.assertEqual(manager.get_current_identity(), identity)

    def test_validate_identity_valid(self):
        """Test that a valid identity passes validation."""
        manager = IdentityManager()
        identity = {"name": "test_user", "type": "user"}
        self.assertTrue(manager.validate_identity(identity))

    def test_validate_identity_invalid_missing_name(self):
        """Test that an identity with a missing name fails validation."""
        manager = IdentityManager()
        identity = {"type": "user"}
        self.assertFalse(manager.validate_identity(identity))

    def test_validate_identity_invalid_missing_type(self):
        """Test that an identity with a missing type fails validation."""
        manager = IdentityManager()
        identity = {"name": "test_user"}
        self.assertFalse(manager.validate_identity(identity))

    def test_validate_identity_empty(self):
        """Test that an empty identity fails validation."""
        manager = IdentityManager()
        identity = {}
        self.assertFalse(manager.validate_identity(identity))

if __name__ == "__main__":
    unittest.main()
