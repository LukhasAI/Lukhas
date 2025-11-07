
import unittest
from unittest.mock import MagicMock, patch

# The TestClient and app are imported inside setUp to ensure patches are active
# during the application's initialization.

class TestEmbeddingsAuth(unittest.TestCase):
    def setUp(self):
        # Patch get_auth_system before the app is imported.
        self.auth_system_patch = patch('serve.main.get_auth_system')
        self.mock_get_auth_system = self.auth_system_patch.start()
        self.mock_auth_instance = MagicMock()
        self.mock_get_auth_system.return_value = self.mock_auth_instance

        # Now that the auth patch is active, import the app and create the client.
        from fastapi.testclient import TestClient
        from serve.main import app
        self.client = TestClient(app)

    def tearDown(self):
        self.auth_system_patch.stop()

    def test_embeddings_uses_jwt_user_id(self):
        # Configure the mock to return a valid user payload from the token.
        self.mock_auth_instance.verify_jwt.return_value = {'user_id': 'test-user'}

        # Patch the index_manager and MEMORY_AVAILABLE flag directly in the serve.main
        # module's namespace, as this is where they are checked and used.
        with patch('serve.main.index_manager') as mock_index_manager, \
             patch('serve.main.MEMORY_AVAILABLE', True):

            mock_index = MagicMock()
            mock_index_manager.get_index.return_value = mock_index

            # Make the request to the endpoint.
            response = self.client.post(
                "/v1/embeddings",
                headers={"Authorization": "Bearer valid-token"},
                json={"input": "test text", "store": True}
            )

            # Assert that the request was successful.
            self.assertEqual(response.status_code, 200, response.json())

            # Verify that the JWT was checked and the correct user_id was used for the index.
            self.mock_auth_instance.verify_jwt.assert_called_once_with('valid-token')
            mock_index_manager.get_index.assert_called_once_with('test-user')
            mock_index.add.assert_called_once()

if __name__ == '__main__':
    unittest.main()
