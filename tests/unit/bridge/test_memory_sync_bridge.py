import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def unload_bridge_module():
    """Fixture to unload the bridge module before each test."""
    if "memory.sync" in sys.modules:
        del sys.modules["memory.sync"]


class TestMemorySyncBridge:
    """Unit tests for the memory_sync bridge module."""

    def test_successful_import(self, unload_bridge_module):
        """
        Tests that the bridge successfully imports from the lukhas_website module
        when it is available.
        """
        mock_ms = MagicMock()
        mock_sbc = MagicMock()
        mock_sr = MagicMock()

        mock_module = MagicMock()
        mock_module.MemorySynchronizer = mock_ms
        mock_module.SyncBudgetConfig = mock_sbc
        mock_module.SyncResult = mock_sr

        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.memory.sync": mock_module},
        ):
            from memory import sync

            assert sync.MemorySynchronizer is mock_ms
            assert sync.SyncBudgetConfig is mock_sbc
            assert sync.SyncResult is mock_sr

    def test_import_error_fallback(self, unload_bridge_module):
        """
        Tests that the bridge raises an ImportError when the lukhas_website
        module is not available.
        """
        with patch.dict(sys.modules, {"lukhas_website.lukhas.memory.sync": None}):
            with pytest.raises(ImportError):
                from memory import sync  # noqa: F401
