import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def unload_bridge_module():
    """Fixture to unload the bridge module before each test."""
    if "consciousness.enhanced_thought_engine" in sys.modules:
        del sys.modules["consciousness.enhanced_thought_engine"]


class TestEnhancedThoughtEngineBridge:
    """Unit tests for the enhanced_thought_engine bridge module."""

    def test_successful_import(self, unload_bridge_module):
        """
        Tests that the bridge successfully imports from the lukhas_website module
        when it is available.
        """
        mock_ete = MagicMock()
        mock_tc = MagicMock()

        mock_module = MagicMock()
        mock_module.EnhancedThoughtEngine = mock_ete
        mock_module.ThoughtComplexity = mock_tc

        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.consciousness.enhanced_thought_engine": mock_module},
        ):
            from consciousness import enhanced_thought_engine

            assert enhanced_thought_engine.EnhancedThoughtEngine is mock_ete
            assert enhanced_thought_engine.ThoughtComplexity is mock_tc

    def test_import_error_fallback(self, unload_bridge_module):
        """
        Tests that the bridge raises an ImportError when the lukhas_website
        module is not available.
        """
        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.consciousness.enhanced_thought_engine": None},
        ):
            with pytest.raises(ImportError):
                from consciousness import enhanced_thought_engine  # noqa: F401
