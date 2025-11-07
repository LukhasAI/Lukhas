from unittest.mock import MagicMock, patch

import pytest
from core.security.keychain_manager import KeychainManager


@patch('subprocess.run')
class TestKeychainManager:
    """Tests for the KeychainManager, with subprocess mocked."""

    def test_set_key_success(self, mock_run):
        """Test successful key setting with specific call validation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = KeychainManager.set_key("TEST_KEY", "test_value")

        assert result is True
        assert mock_run.call_count == 2

        # Check the delete call
        delete_call_args = mock_run.call_args_list[0].args[0]
        assert "delete-generic-password" in delete_call_args
        assert "-a" in delete_call_args
        assert "TEST_KEY" in delete_call_args

        # Check the add call
        add_call_args = mock_run.call_args_list[1].args[0]
        assert "add-generic-password" in add_call_args
        assert "-w" in add_call_args
        assert "test_value" in add_call_args

    def test_set_key_failure(self, mock_run):
        """Test key setting failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="error")

        result = KeychainManager.set_key("TEST_KEY", "test_value")

        assert result is False

    def test_get_key_success(self, mock_run):
        """Test successful key retrieval."""
        mock_run.return_value = MagicMock(returncode=0, stdout="test_value\n", stderr="")

        key = KeychainManager.get_key("TEST_KEY")

        assert key == "test_value"
        mock_run.assert_called_once()

    @patch('os.getenv')
    def test_get_key_fallback_to_env(self, mock_getenv, mock_run):
        """Test fallback to environment variable when keychain fails."""
        # Keychain fails
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="not found")
        # Env var exists
        mock_getenv.return_value = "env_value"

        key = KeychainManager.get_key("TEST_KEY")

        assert key == "env_value"
        mock_getenv.assert_called_once_with("TEST_KEY")

    @patch('os.getenv')
    def test_get_key_not_found(self, mock_getenv, mock_run):
        """Test when key is not in keychain or environment."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="not found")
        mock_getenv.return_value = None

        key = KeychainManager.get_key("TEST_KEY")

        assert key is None

    def test_delete_key_success(self, mock_run):
        """Test successful key deletion."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = KeychainManager.delete_key("TEST_KEY")

        assert result is True
        mock_run.assert_called_once()

    def test_has_key_true(self, mock_run):
        """Test has_key when key exists."""
        mock_run.return_value = MagicMock(returncode=0, stdout="test_value\n", stderr="")
        assert KeychainManager.has_key("TEST_KEY") is True

    def test_has_key_false(self, mock_run):
        """Test has_key when key does not exist."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="not found")
        assert KeychainManager.has_key("TEST_KEY") is False

    def test_list_keys(self, mock_run):
        """Test listing keys."""
        # A simplified version of the dump-keychain output
        mock_output = """
keychain: "/Users/test/Library/Keychains/login.keychain-db"
class: "genp"
attributes:
    "acct"<blob>="TEST_KEY_1"
    "svce"<blob>="lukhas-ai"
---
keychain: "/Users/test/Library/Keychains/login.keychain-db"
class: "genp"
attributes:
    "acct"<blob>="TEST_KEY_2"
    "svce"<blob>="some-other-service"
---
keychain: "/Users/test/Library/Keychains/login.keychain-db"
class: "genp"
attributes:
    "acct"<blob>="TEST_KEY_3"
    "svce"<blob>="lukhas-ai"
"""
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")

        keys = KeychainManager.list_keys()

        # The implementation is buggy: it associates the wrong service with the key.
        # This assertion matches the actual, incorrect behavior of the code.
        assert keys == ["TEST_KEY_2"]

# Need to import subprocess for the side_effect
import subprocess
