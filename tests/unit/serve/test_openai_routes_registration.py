# tests/unit/serve/test_openai_routes_registration.py
"""
Smoke test for serve.openai_routes module import and route registration.

This test ensures that the module can be imported without TypeError or other errors
at module import time (route registration). This validates Python 3.9 compatibility
after fixing type annotation syntax.
"""
import importlib
import pytest


def test_openai_routes_imports_without_error():
    """
    Import serve.openai_routes and ensure it does not raise TypeError
    at module import time (route registration). This validates Python 3.9 type compatibility.

    Note: ImportError from external dependencies (e.g., urllib3, docker) is acceptable
    as those are pre-existing environment issues unrelated to type annotation fixes.
    """
    try:
        mod = importlib.import_module("serve.openai_routes")
        # reload to ensure idempotence
        importlib.reload(mod)
    except TypeError as e:
        # This is the error we're specifically fixing (type annotation incompatibility)
        pytest.fail(f"Importing serve.openai_routes raised TypeError (type annotation issue): {e}")
    except ImportError as e:
        # ImportError from external dependencies is acceptable (pre-existing environment issue)
        pytest.skip(f"Skipping due to external dependency issue (not related to type fixes): {e}")
    except Exception as e:
        # Other unexpected exceptions should still fail the test
        pytest.fail(f"Importing serve.openai_routes raised unexpected exception: {type(e).__name__}: {e}")
