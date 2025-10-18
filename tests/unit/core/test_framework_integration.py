import importlib
from unittest.mock import MagicMock, patch

import pytest

# --- Mocks for dependencies ---


class MockTrinityFrameworkIntegrator:
    def __init__(self, config=None):
        self.config = config
        self.initialized = False

    async def initialize_constellation_frameworks(self):
        self.initialized = True
        return True


class MockLukhasException(Exception):
    pass


# --- Test Setup: Patching dependencies before import ---

mock_trinity_module = MagicMock()
mock_trinity_module.ConstellationFrameworkIntegrator = MockTrinityFrameworkIntegrator
mock_trinity_module.ConstellationIntegrationConfig = object()

mock_exceptions_module = MagicMock()
mock_exceptions_module.LukhasException = MockLukhasException

MOCK_MODULES = {
    "consciousness.constellation_integration": mock_trinity_module,
    "core.common.exceptions": mock_exceptions_module,
}

# --- Test Cases ---


def test_manager_initialization_active():
    """Tests that the manager initializes correctly in an active state."""
    with patch.dict("sys.modules", MOCK_MODULES):

        importlib.reload(candidate.core.framework_integration)  # noqa: F821  # TODO: candidate
        from core.framework_integration import FrameworkIntegrationManager

        manager = FrameworkIntegrationManager()
        assert manager.is_active
        assert isinstance(manager.trinity_integrator, MockTrinityFrameworkIntegrator)
        assert len(manager.module_adapters) == 4


@patch("labs.core.framework_integration.ConstellationFrameworkIntegrator", None)
def test_manager_initialization_inactive():
    """Tests that the manager initializes correctly in an inactive/degraded state."""
    from core.framework_integration import FrameworkIntegrationManager

    manager = FrameworkIntegrationManager()
    assert not manager.is_active
    assert manager.trinity_integrator is None


@pytest.mark.asyncio
async def test_register_module_active():
    """Tests module registration in an active manager."""
    with patch.dict("sys.modules", MOCK_MODULES):

        importlib.reload(candidate.core.framework_integration)  # noqa: F821  # TODO: candidate
        from core.framework_integration import FrameworkIntegrationManager, ModuleAdapter

        manager = FrameworkIntegrationManager()
        adapter = ModuleAdapter(prepare_payload=lambda x: x, module_type="test", triad_aspect="🧪")
        await manager.register_module("test_module", {}, adapter)
        assert "test_module" in manager.registered_modules


@pytest.mark.asyncio
@patch("labs.core.framework_integration.ConstellationFrameworkIntegrator", None)
@patch("labs.core.framework_integration.logger")
async def test_register_module_inactive(mock_logger):
    """Tests that module registration is ignored in an inactive manager."""
    from core.framework_integration import FrameworkIntegrationManager, ModuleAdapter

    manager = FrameworkIntegrationManager()
    adapter = ModuleAdapter(prepare_payload=lambda x: x, module_type="test", triad_aspect="🧪")
    await manager.register_module("test_module", {}, adapter)
    assert "test_module" not in manager.registered_modules
    mock_logger.warning.assert_called_with("Cannot register module: FrameworkIntegrationManager is inactive.")


@pytest.mark.asyncio
async def test_initialize_integrations_active():
    """Tests that initialize_integrations calls the trinity_integrator method when active."""
    with patch.dict("sys.modules", MOCK_MODULES):

        importlib.reload(candidate.core.framework_integration)  # noqa: F821  # TODO: candidate
        from core.framework_integration import FrameworkIntegrationManager

        manager = FrameworkIntegrationManager()
        result = await manager.initialize_integrations()
        assert result is True
        assert manager.trinity_integrator.initialized is True


@pytest.mark.asyncio
@patch("labs.core.framework_integration.ConstellationFrameworkIntegrator", None)
@patch("labs.core.framework_integration.logger")
async def test_initialize_integrations_inactive(mock_logger):
    """Tests that initialize_integrations returns False and logs an error when inactive."""
    from core.framework_integration import FrameworkIntegrationManager

    manager = FrameworkIntegrationManager()
    result = await manager.initialize_integrations()
    assert result is False
    mock_logger.error.assert_called_with("Cannot initialize integrations: FrameworkIntegrationManager is inactive.")


def test_default_adapters_creation():
    """Tests that the default adapters are created correctly."""
    with patch.dict("sys.modules", MOCK_MODULES):

        importlib.reload(candidate.core.framework_integration)  # noqa: F821  # TODO: candidate
        from core.framework_integration import FrameworkIntegrationManager

        manager = FrameworkIntegrationManager()
        assert "identity" in manager.module_adapters
        identity_adapter = manager.get_module_adapter("identity")
        assert identity_adapter.module_type == "identity"


@pytest.mark.asyncio
async def test_adapter_payload_function():
    """Tests that the prepare_payload function of an adapter can be called."""
    with patch.dict("sys.modules", MOCK_MODULES):

        importlib.reload(candidate.core.framework_integration)  # noqa: F821  # TODO: candidate
        from core.framework_integration import FrameworkIntegrationManager

        manager = FrameworkIntegrationManager()
        consciousness_adapter = manager.get_module_adapter("consciousness")
        payload = await consciousness_adapter.prepare_payload({"user_id": "test_user"})
        assert payload["consciousness_integration"] is True
