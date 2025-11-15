import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from lukhas.identity.qrg_keystore import QRGKeystore


class TestQRGKeystore(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the keystore
        self.test_dir = tempfile.mkdtemp()
        self.keystore = QRGKeystore(key_dir=self.test_dir)

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_store_and_get_key_from_file(self):
        """Test storing and retrieving a key from the file-based cache."""
        key_id = "test_file_key"
        secret_key = b"super_secret_file_key"

        # Key should not exist initially
        self.assertIsNone(self.keystore.get_key(key_id))

        # Store the key
        self.keystore.store_key(key_id, secret_key)

        # Retrieve the key and verify it's correct
        retrieved_key = self.keystore.get_key(key_id)
        self.assertEqual(retrieved_key, secret_key)

    @patch.dict(os.environ, {"QRG_SECRET_TEST_ENV_KEY": "super_secret_env_key"})
    def test_get_key_from_env_var(self):
        """Test retrieving a key from an environment variable (simulating GitHub secret)."""
        key_id = "test_env_key"
        secret_key = b"super_secret_env_key"

        # Key should not be in the file cache initially
        key_path = os.path.join(self.test_dir, key_id)
        self.assertFalse(os.path.exists(key_path))

        # Retrieve the key - it should come from the mocked environment variable
        retrieved_key = self.keystore.get_key(key_id)
        self.assertEqual(retrieved_key, secret_key)

    @patch.dict(os.environ, {"QRG_SECRET_TEST_CACHE_KEY": "super_secret_cache_key"})
    def test_get_key_from_env_var_caches_locally(self):
        """Test that a key from an env var is cached to the local file store."""
        key_id = "test_cache_key"
        secret_key = b"super_secret_cache_key"

        # Check that the key file doesn't exist yet
        key_path = os.path.join(self.test_dir, key_id)
        self.assertFalse(os.path.exists(key_path))

        # First retrieval gets it from the environment
        retrieved_key = self.keystore.get_key(key_id)
        self.assertEqual(retrieved_key, secret_key)

        # Check that the key has now been cached to a local file
        self.assertTrue(os.path.exists(key_path))
        with open(key_path, "rb") as f:
            self.assertEqual(f.read(), secret_key)

        # Now, retrieve it again with the env var removed to prove it comes from the file cache
        with patch.dict(os.environ, {}, clear=True):
            retrieved_key_from_file = self.keystore.get_key(key_id)
            self.assertEqual(retrieved_key_from_file, secret_key)

    def test_get_nonexistent_key(self):
        """Test retrieving a key that does not exist in any source."""
        key_id = "nonexistent_key"
        # Ensure no corresponding environment variable is set
        with patch.dict(os.environ, {}, clear=True):
            retrieved_key = self.keystore.get_key(key_id)
            self.assertIsNone(retrieved_key)


if __name__ == '__main__':
    unittest.main()
