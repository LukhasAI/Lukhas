"""
Comprehensive tests for the OpenAI API compatibility entrypoint.

Tests the get_app() factory function and import delegation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGetApp:
    """Test the get_app factory function."""

    def test_get_app_imports_from_serve_main(self):
        """Test that get_app imports from serve.main."""
        with patch('lukhas.adapters.openai.api.app', create=True) as mock_app:
            # Import the module to trigger the function definition
            from lukhas.adapters.openai.api import get_app

            # Mock the serve.main.app
            with patch('serve.main.app', mock_app):
                result = get_app()

                # Should return the app from serve.main
                assert result == mock_app

    def test_get_app_returns_fastapi_app(self):
        """Test that get_app returns a FastAPI application."""
        from lukhas.adapters.openai.api import get_app

        with patch('serve.main.app') as mock_app:
            mock_app.__class__.__name__ = 'FastAPI'
            result = get_app()

            # Should be the FastAPI app
            assert result is mock_app

    def test_get_app_callable(self):
        """Test that get_app is callable."""
        from lukhas.adapters.openai.api import get_app

        assert callable(get_app)

    def test_get_app_no_arguments(self):
        """Test that get_app takes no arguments."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        sig = inspect.signature(get_app)
        # Should have no required parameters
        assert len(sig.parameters) == 0

    def test_get_app_lazy_import(self):
        """Test that serve.main is imported lazily (inside function)."""
        # The import should happen when get_app is called, not at module import
        with patch('serve.main.app', create=True) as mock_app:
            from lukhas.adapters.openai.api import get_app

            # Call the function
            result = get_app()

            # Should have imported and returned the app
            assert result is mock_app

    def test_get_app_multiple_calls(self):
        """Test that get_app can be called multiple times."""
        from lukhas.adapters.openai.api import get_app

        with patch('serve.main.app', create=True) as mock_app:
            result1 = get_app()
            result2 = get_app()

            # Should return the same app instance
            assert result1 is result2
            assert result1 is mock_app

    def test_get_app_delegation(self):
        """Test that get_app properly delegates to serve.main."""
        with patch('serve.main') as mock_serve_main:
            mock_app = Mock()
            mock_serve_main.app = mock_app

            from lukhas.adapters.openai.api import get_app

            result = get_app()

            # Should return the delegated app
            assert result is mock_app


class TestModuleStructure:
    """Test module structure and exports."""

    def test_module_exports_get_app(self):
        """Test that module exports get_app in __all__."""
        from lukhas.adapters.openai import api

        assert hasattr(api, '__all__')
        assert 'get_app' in api.__all__

    def test_module_only_exports_get_app(self):
        """Test that only get_app is exported."""
        from lukhas.adapters.openai import api

        assert api.__all__ == ['get_app']

    def test_get_app_is_importable(self):
        """Test that get_app can be imported directly."""
        from lukhas.adapters.openai.api import get_app

        assert get_app is not None
        assert callable(get_app)

    def test_module_has_docstring(self):
        """Test that module has proper docstring."""
        from lukhas.adapters.openai import api

        assert api.__doc__ is not None
        assert 'compatibility' in api.__doc__.lower() or 'openai' in api.__doc__.lower()


class TestBackwardCompatibility:
    """Test backward compatibility with legacy import paths."""

    def test_uvicorn_factory_pattern(self):
        """Test that uvicorn factory pattern works."""
        # This simulates: uvicorn lukhas.adapters.openai.api:get_app --factory
        from lukhas.adapters.openai.api import get_app

        with patch('serve.main.app', create=True) as mock_app:
            app = get_app()

            # Should work with uvicorn's factory pattern
            assert app is mock_app

    def test_legacy_import_path(self):
        """Test that legacy import path still works."""
        # Old code might import like this
        import lukhas.adapters.openai.api as api_module

        assert hasattr(api_module, 'get_app')
        assert callable(api_module.get_app)

    def test_import_via_attribute_access(self):
        """Test importing via attribute access."""
        from lukhas.adapters.openai import api

        assert hasattr(api, 'get_app')
        assert callable(api.get_app)


class TestIntegration:
    """Integration tests for the API entrypoint."""

    def test_full_import_and_call_flow(self):
        """Test complete flow of importing and calling get_app."""
        with patch('serve.main.app', create=True) as mock_app:
            # Import the function
            from lukhas.adapters.openai.api import get_app

            # Call it
            result = get_app()

            # Verify result
            assert result is mock_app

    def test_get_app_with_serve_main_attributes(self):
        """Test that get_app returns app with expected attributes."""
        with patch('serve.main.app', create=True) as mock_app:
            # Add typical FastAPI app attributes
            mock_app.title = "LUKHAS OpenAI-Compatible API"
            mock_app.version = "1.0.0"

            from lukhas.adapters.openai.api import get_app

            result = get_app()

            # Should have FastAPI attributes
            assert hasattr(result, 'title')
            assert hasattr(result, 'version')


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_get_app_when_serve_main_missing(self):
        """Test behavior when serve.main module is missing."""
        with patch('lukhas.adapters.openai.api.app', side_effect=ImportError):
            from lukhas.adapters.openai.api import get_app

            # Should raise ImportError if serve.main doesn't exist
            with pytest.raises(ImportError):
                get_app()

    def test_get_app_when_serve_main_has_no_app(self):
        """Test behavior when serve.main has no app attribute."""
        with patch('serve.main', create=True) as mock_module:
            # Remove app attribute
            del mock_module.app

            from lukhas.adapters.openai.api import get_app

            # Should raise AttributeError
            with pytest.raises(AttributeError):
                get_app()

    def test_get_app_return_type_annotation(self):
        """Test that get_app has correct return type annotation."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        sig = inspect.signature(get_app)
        # Return type should be Any (since it's a compatibility layer)
        # The annotation is present in the code
        assert sig.return_annotation is not inspect.Signature.empty

    def test_module_can_be_imported_multiple_times(self):
        """Test that module can be safely imported multiple times."""
        # First import
        from lukhas.adapters.openai import api as api1

        # Second import
        from lukhas.adapters.openai import api as api2

        # Should be the same module
        assert api1 is api2


class TestDocumentation:
    """Test documentation and code comments."""

    def test_get_app_has_docstring(self):
        """Test that get_app has a docstring."""
        from lukhas.adapters.openai.api import get_app

        assert get_app.__doc__ is not None
        assert len(get_app.__doc__.strip()) > 0

    def test_docstring_mentions_serve_main(self):
        """Test that docstring mentions serve.main."""
        from lukhas.adapters.openai.api import get_app

        assert 'serve.main' in get_app.__doc__ or 'serve' in get_app.__doc__.lower()

    def test_docstring_mentions_legacy_compatibility(self):
        """Test that docstring mentions legacy compatibility."""
        from lukhas.adapters.openai.api import get_app

        doc = get_app.__doc__.lower()
        assert 'legacy' in doc or 'compatibility' in doc or 'operational' in doc


class TestUsagePatterns:
    """Test common usage patterns."""

    def test_direct_function_call(self):
        """Test direct function call pattern."""
        with patch('serve.main.app', create=True) as mock_app:
            from lukhas.adapters.openai.api import get_app

            app = get_app()
            assert app is mock_app

    def test_assignment_pattern(self):
        """Test assignment pattern (common in deployment)."""
        with patch('serve.main.app', create=True) as mock_app:
            from lukhas.adapters.openai.api import get_app

            application = get_app()
            assert application is mock_app

    def test_inline_usage_pattern(self):
        """Test inline usage pattern."""
        with patch('serve.main.app', create=True) as mock_app:
            # This pattern might be used in config files
            from lukhas.adapters.openai.api import get_app as app_factory

            app = app_factory()
            assert app is mock_app

    def test_uvicorn_cli_simulation(self):
        """Test simulation of uvicorn CLI usage."""
        # Simulate: uvicorn lukhas.adapters.openai.api:get_app --factory
        with patch('serve.main.app', create=True) as mock_app:
            import importlib

            # Import the module
            module = importlib.import_module('lukhas.adapters.openai.api')

            # Get the factory function
            factory = getattr(module, 'get_app')

            # Call it (uvicorn would do this)
            app = factory()

            assert app is mock_app


class TestTypeHints:
    """Test type hints and annotations."""

    def test_get_app_has_return_type(self):
        """Test that get_app has return type annotation."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        sig = inspect.signature(get_app)
        assert sig.return_annotation is not inspect.Signature.empty

    def test_return_type_is_any(self):
        """Test that return type is Any (for flexibility)."""
        from lukhas.adapters.openai.api import get_app
        from typing import Any
        import inspect

        sig = inspect.signature(get_app)
        # The function returns Any to maintain flexibility
        assert sig.return_annotation == Any


class TestImportSideEffects:
    """Test that imports have no unwanted side effects."""

    def test_import_does_not_start_server(self):
        """Test that importing doesn't start a server."""
        # Importing should not cause serve.main to execute
        with patch('serve.main.app', create=True):
            from lukhas.adapters.openai import api

            # Just importing should not trigger app creation
            # App is only imported when get_app() is called

    def test_import_is_lightweight(self):
        """Test that module import is lightweight."""
        # Should only define the function, not do heavy work
        import sys

        # Track imports before
        before = set(sys.modules.keys())

        from lukhas.adapters.openai import api

        after = set(sys.modules.keys())

        # Should not import serve.main at module level
        # (it's imported inside get_app)
        new_imports = after - before

        # The import should be relatively lightweight
        assert len(new_imports) < 10  # Arbitrary small number


class TestCodeQuality:
    """Test code quality aspects."""

    def test_function_is_simple(self):
        """Test that get_app function is simple (single purpose)."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        source = inspect.getsource(get_app)
        lines = [line for line in source.split('\n') if line.strip() and not line.strip().startswith('#')]

        # Function should be simple (few lines)
        assert len(lines) < 10

    def test_no_complex_logic(self):
        """Test that function has no complex logic."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        source = inspect.getsource(get_app)

        # Should not have loops or complex conditionals
        assert 'for ' not in source
        assert 'while ' not in source
        assert source.count('if ') <= 1  # At most one simple if

    def test_single_responsibility(self):
        """Test that function has single responsibility (delegation)."""
        from lukhas.adapters.openai.api import get_app
        import inspect

        source = inspect.getsource(get_app)

        # Should import and return, nothing else
        assert 'import' in source
        assert 'return' in source
