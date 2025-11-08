import unittest
from unittest.mock import patch
from labs.core.identity.id_manager import get_current_sid, get_user_tier, register_new_user

class TestIdManager(unittest.TestCase):

    @patch('labs.core.identity.id_manager.CURRENT_USER_SID', 'test_sid')
    def test_get_current_sid(self):
        """Test that the correct SID is returned."""
        self.assertEqual(get_current_sid(), 'test_sid')

    @patch('labs.core.identity.id_manager.USER_TIERS', {'test_sid': 3})
    def test_get_user_tier(self):
        """Test that the correct tier is returned for a given SID."""
        self.assertEqual(get_user_tier('test_sid'), 3)
        self.assertEqual(get_user_tier('unknown_sid'), 0)

    @patch('labs.core.identity.id_manager.USER_TIERS', {})
    def test_register_new_user(self):
        """Test that a new user is registered correctly."""
        new_sid = register_new_user('new_user', 2)
        self.assertTrue(new_sid.startswith('new_user_sid_'))
        self.assertEqual(get_user_tier(new_sid), 2)

if __name__ == '__main__':
    unittest.main()
