import base64
import unittest

import pytest
from starlette.testclient import TestClient

from candidate.core.security.auth import get_auth_system

# Import the FastAPI app and the auth system
# Skip this test if public_api is not available
try:
    from public_api import app

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    app = None


@pytest.mark.skipif(not API_AVAILABLE, reason="public_api module not available")
class TestPublicAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test client and a valid API key."""
        if API_AVAILABLE:
            self.client = TestClient(app)
        else:
            self.skipTest("Public API not available")

        # Get the auth system and generate a key for testing
        self.auth_system = get_auth_system()
        self.user_id = "test_api_user"
        self.key_id, self.key_secret = self.auth_system.generate_api_key(self.user_id, ["read", "write"])

        # Create a valid token
        valid_token = f"{self.key_id}:{self.key_secret}"
        self.valid_auth_header = {"Authorization": f"Bearer {base64.b64encode(valid_token.encode()).decode(}"}

        # Create an invalid token
        invalid_token = "invalid_id:invalid_secret"
        self.invalid_auth_header = {"Authorization": f"Bearer {base64.b64encode(invalid_token.encode()).decode(}"}

    def test_health_check(self):
        """Test the public health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_root_endpoint(self):
        """Test the root endpoint, which requires no authentication."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_chat_endpoint_no_auth(self):
        """Test that the chat endpoint fails without authentication."""
        response = self.client.post("/v1/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 401)

    def test_chat_endpoint_invalid_auth(self):
        """Test that the chat endpoint fails with an invalid API key."""
        response = self.client.post("/v1/chat", json={"message": "hello"}, headers=self.invalid_auth_header)
        self.assertEqual(response.status_code, 401)

    def test_chat_endpoint_valid_auth(self):
        """Test that the chat endpoint succeeds with a valid API key."""
        response = self.client.post("/v1/chat", json={"message": "hello"}, headers=self.valid_auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())

    def test_dreams_endpoint_no_auth(self):
        """Test that the dreams endpoint fails without authentication."""
        response = self.client.post("/v1/dreams", json={"prompt": "a dream"})
        self.assertEqual(response.status_code, 401)

    def test_dreams_endpoint_valid_auth(self):
        """Test that the dreams endpoint succeeds with a valid API key."""
        response = self.client.post("/v1/dreams", json={"prompt": "a dream"}, headers=self.valid_auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn("dream", response.json())

    def test_status_endpoint_optional_auth(self):
        """Test that the status endpoint works with and without authentication."""
        # Without auth
        response_no_auth = self.client.get("/status")
        self.assertEqual(response_no_auth.status_code, 200)
        self.assertTrue(response_no_auth.json()["operational"])

        # With auth
        response_with_auth = self.client.get("/status", headers=self.valid_auth_header)
        self.assertEqual(response_with_auth.status_code, 200)
        self.assertTrue(response_with_auth.json()["operational"])


if __name__ == "__main__":
    unittest.main()
