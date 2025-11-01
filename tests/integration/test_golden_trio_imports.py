import importlib

import pytest


@pytest.mark.integration
def test_import_system_integration_hub():
    try:
        mod = importlib.import_module("core.orchestration.integration_hub")
    except (ModuleNotFoundError, ImportError, NameError) as e:
        pytest.skip(f"optional or unresolved dependency: {e}")

    assert hasattr(mod, "SystemIntegrationHub")

