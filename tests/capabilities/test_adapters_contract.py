"""
Capability smoke tests for adapter contract compliance
"""
import importlib
import pkgutil
from pathlib import Path

import pytest

import matriz.adapters
from matriz.node_contract import MatrizNode, MatrizResult
from tests.util.mk_msg import mk_test_message


def discover_adapters():
    """Dynamically discover all adapter classes"""
    adapters = []
    adapter_path = Path(matriz.adapters.__file__).parent

    for module_info in pkgutil.iter_modules([str(adapter_path)]):
        if module_info.name.endswith('_adapter'):
            module = importlib.import_module(f'matriz.adapters.{module_info.name}')
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, MatrizNode) and
                    attr != MatrizNode):
                    adapters.append(attr)

    return adapters


@pytest.mark.parametrize("adapter_class", discover_adapters())
def test_adapter_contract_compliance(adapter_class):
    """Test that each adapter implements the MatrizNode contract correctly"""
    # Instantiate adapter
    adapter = adapter_class()

    # Verify adapter has required attributes
    assert hasattr(adapter, 'name')
    assert hasattr(adapter, 'version')
    assert isinstance(adapter.name, str)
    assert isinstance(adapter.version, str)

    # Create minimal test message
    msg = mk_test_message(topic="ping", payload={})

    # Call handle method
    result = adapter.handle(msg)

    # Verify result shape
    assert isinstance(result, MatrizResult)
    assert hasattr(result, 'ok')
    assert hasattr(result, 'payload')
    assert hasattr(result, 'trace')
    assert hasattr(result, 'guardian_log')

    # Verify field types
    assert isinstance(result.ok, bool)
    assert isinstance(result.payload, dict)
    assert isinstance(result.trace, dict)
    assert isinstance(result.guardian_log, list)


def test_all_adapters_discoverable():
    """Ensure we can discover all expected adapters"""
    adapters = discover_adapters()
    adapter_names = [cls.__name__ for cls in adapters]

    expected_adapters = [
        'BioAdapter',
        'MemoryAdapter',
        'ConsciousnessAdapter',
        'BridgeAdapter',
        'GovernanceAdapter',
        'EmotionAdapter',
        'OrchestrationAdapter',
        'ComplianceAdapter',
        'IdentityAdapter',
        'ContradictionAdapter',
        'CreativeAdapter',
    ]

    for expected in expected_adapters:
        assert expected in adapter_names, f"Missing expected adapter: {expected}"

    assert len(adapters) >= len(expected_adapters), "Found fewer adapters than expected"