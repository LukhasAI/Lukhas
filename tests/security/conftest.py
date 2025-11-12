"""Security tests configuration and fixtures.

This conftest.py provides:
1. Mock imports for missing optional dependencies
2. Test fixtures for FastAPI clients
3. Shared authentication mocks
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock missing optional dependencies before test collection
# This allows security tests to run without full LUKHAS dependencies

# Mock observability.matriz_decorators (candidate/ lane dependency)
if "observability" not in sys.modules:
    sys.modules["observability"] = MagicMock()
if "observability.matriz_decorators" not in sys.modules:
    mock_decorators = MagicMock()
    # Create a passthrough decorator for @instrument
    def instrument(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if args else lambda f: f
    mock_decorators.instrument = instrument
    sys.modules["observability.matriz_decorators"] = mock_decorators

# Mock governance.ethics.meg_bridge (optional dependency)
if "governance" not in sys.modules:
    sys.modules["governance"] = MagicMock()
if "governance.ethics" not in sys.modules:
    sys.modules["governance.ethics"] = MagicMock()
if "governance.ethics.meg_bridge" not in sys.modules:
    sys.modules["governance.ethics.meg_bridge"] = MagicMock()

# Mock lz4 (optional compression library for Guardian serializers)
if "lz4" not in sys.modules:
    sys.modules["lz4"] = MagicMock()
if "lz4.frame" not in sys.modules:
    sys.modules["lz4.frame"] = MagicMock()

# Ensure repo root is on sys.path
_TESTS_SECURITY_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TESTS_SECURITY_DIR.parent.parent
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
