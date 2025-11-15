import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def unload_bridge_module():
    """Fixture to unload the bridge module before each test."""
    if "identity.auth_service" in sys.modules:
        del sys.modules["identity.auth_service"]


class TestAuthServiceBridge:
    """Unit tests for the auth_service bridge module."""

    def test_successful_import(self, unload_bridge_module):
        """
        Tests that the bridge successfully imports from the lukhas_website module
        when it is available.
        """
        mock_verify_token = MagicMock()

        mock_module = MagicMock()
        mock_module.verify_token = mock_verify_token

        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.identity.auth_service": mock_module},
        ):
            from identity import auth_service

            assert auth_service.verify_token is mock_verify_token

    def test_import_error_fallback(self, unload_bridge_module):
        """
        Tests that the bridge raises an ImportError when the lukhas_website
        module is not available.
        """
        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.identity.auth_service": None},
        ):
            with pytest.raises(ImportError):
                from identity import auth_service  # noqa: F401
