"""
LUKHAS AI Identity System Tests
==============================

Golden test for signup → login → JWT decode → validation cycle.
"""

import unittest
from datetime import datetime
from identity.login import signup, login_user, validate_password
from identity.identity_core import validate_symbolic_token


class TestIdentityFlow(unittest.TestCase):
    """Test complete identity flow."""

    def test_signup_login_jwt_cycle(self):
        """Test complete signup → login → JWT decode → validation cycle."""
        # Use timestamp to ensure unique email
        timestamp = int(datetime.now().timestamp())
        email = f"test_{timestamp}@lukhas.ai"
        password = "S3cure!Pass123"

        # Step 1: Signup
        signup_result = signup(email, password)
        self.assertTrue(signup_result["success"])
        self.assertIsNotNone(signup_result["token"])
        self.assertEqual(signup_result["user_id"], f"test_{timestamp}")

        # Step 2: Login
        login_result = login_user(email, password)
        self.assertTrue(login_result["success"])
        self.assertIsNotNone(login_result["token"])
        self.assertEqual(login_result["user_id"], signup_result["user_id"])

        # Step 3: JWT decode and validate
        token = login_result["token"]
        is_valid, metadata = validate_symbolic_token(token)
        self.assertTrue(is_valid)

        # Step 4: Assert sub/email present
        self.assertIn("user_id", metadata)
        self.assertIn("email", metadata)
        self.assertEqual(metadata["user_id"], f"test_{timestamp}")
        self.assertEqual(metadata["email"], email)

    def test_password_validation(self):
        """Test password validation function."""
        # Valid password
        is_valid, msg = validate_password("ValidPass123!")
        self.assertTrue(is_valid)

        # Invalid password
        is_valid, msg = validate_password("weak")
        self.assertFalse(is_valid)
        self.assertIn("at least 8 characters", msg)


if __name__ == "__main__":
    unittest.main()
