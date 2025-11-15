import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def unload_bridge_module():
    """Fixture to unload the bridge module before each test."""
    if "orchestration.externalized_orchestrator" in sys.modules:
        del sys.modules["orchestration.externalized_orchestrator"]


class TestExternalizedOrchestratorBridge:
    """Unit tests for the externalized_orchestrator bridge module."""

    def test_successful_import(self, unload_bridge_module):
        """
        Tests that the bridge successfully imports from the lukhas_website module
        when it is available.
        """
        mock_get_eo = MagicMock()

        mock_module = MagicMock()
        mock_module.get_externalized_orchestrator = mock_get_eo

        with patch.dict(
            sys.modules,
            {
                "lukhas_website.lukhas.orchestration.externalized_orchestrator": mock_module
            },
        ):
            from orchestration import externalized_orchestrator

            assert (
                externalized_orchestrator.get_externalized_orchestrator is mock_get_eo
            )

    def test_import_error_fallback(self, unload_bridge_module):
        """
        Tests that the bridge raises an ImportError when the lukhas_website
        module is not available.
        """
        with patch.dict(
            sys.modules,
            {"lukhas_website.lukhas.orchestration.externalized_orchestrator": None},
        ):
            with pytest.raises(ImportError):
                from orchestration import externalized_orchestrator  # noqa: F401
