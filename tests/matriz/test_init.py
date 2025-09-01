import pytest
import sys
from unittest.mock import patch

class TestMatrizInit:

    def test_successful_imports(self):
        """Test that key components are imported successfully."""
        try:
            from lukhas.matriz import PolicyEngine, RuntimeSupervisor, MatrizNode
            assert PolicyEngine is not None
            assert RuntimeSupervisor is not None
            assert MatrizNode is not None
        except ImportError:
            pytest.fail("Failed to import essential Matriz components.")

    def test_matriz_node_is_alias(self):
        """Test that MatrizNode is an alias for RuntimeSupervisor."""
        from lukhas.matriz import MatrizNode, RuntimeSupervisor
        assert MatrizNode is RuntimeSupervisor

    def test_all_variable(self):
        """Test the __all__ variable for correct exports."""
        import lukhas.matriz
        expected_exports = [
            "MatrizNode",
            "PolicyEngine",
            "RuntimeSupervisor",
        ]
        assert sorted(lukhas.matriz.__all__) == sorted(expected_exports)

    @patch.dict(sys.modules, {'lukhas.matriz.runtime.policy': None})
    def test_import_error_handling(self):
        """Test that components are None if an import fails."""
        # To re-trigger the import logic, we need to unload and reload the module
        if 'lukhas.matriz' in sys.modules:
            del sys.modules['lukhas.matriz']

        import lukhas.matriz

        assert lukhas.matriz.PolicyEngine is None
        assert lukhas.matriz.RuntimeSupervisor is None
        assert lukhas.matriz.MatrizNode is None

        # Clean up by removing the unloaded module to not affect other tests
        if 'lukhas.matriz' in sys.modules:
            del sys.modules['lukhas.matriz']
        # Also remove the patch to be safe
        if 'lukhas.matriz.runtime.policy' in sys.modules:
             del sys.modules['lukhas.matriz.runtime.policy']

    # It's good practice to ensure the module is in a clean state after tests
    def teardown_method(self, method):
        if 'lukhas.matriz' in sys.modules:
            del sys.modules['lukhas.matriz']
        if 'lukhas.matriz.runtime.policy' in sys.modules:
            del sys.modules['lukhas.matriz.runtime.policy']
        if 'lukhas.matriz.runtime.supervisor' in sys.modules:
            del sys.modules['lukhas.matriz.runtime.supervisor']
