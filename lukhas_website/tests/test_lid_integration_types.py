"""Unit tests for LiD token integration helpers."""

from __future__ import annotations

import atexit
import importlib
import importlib.util
import sys
import types
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1] / "lukhas"
IDENTITY_PATH = BASE_PATH / "identity"

_CREATED_PACKAGES: set[str] = set()
_ORIGINAL_PATHS: dict[str, list[str]] = {}


def ensure_package(name: str, path: Path) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            module = types.ModuleType(name)
            module.__path__ = [str(path)]  # type: ignore[attr-defined]
            sys.modules[name] = module
            _CREATED_PACKAGES.add(name)
            parent_name, _, attr = name.rpartition(".")
            if parent_name:
                parent_path = path.parent if path.parent != path else path
                parent = ensure_package(parent_name, parent_path)
                setattr(parent, attr, module)
        else:
            if hasattr(module, "__path__"):
                if str(path) not in module.__path__:
                    _ORIGINAL_PATHS.setdefault(name, list(module.__path__))
                    module.__path__.append(str(path))
            else:
                module.__path__ = [str(path)]  # type: ignore[attr-defined]
    else:
        if hasattr(module, "__path__"):
            if str(path) not in module.__path__:
                _ORIGINAL_PATHS.setdefault(name, list(module.__path__))
                module.__path__.append(str(path))
        else:
            module.__path__ = [str(path)]  # type: ignore[attr-defined]
    return module


def _restore_packages() -> None:
    for name in sorted(_CREATED_PACKAGES, reverse=True):
        parent_name, _, attr = name.rpartition(".")
        if parent_name:
            parent = sys.modules.get(parent_name)
            if parent is not None and hasattr(parent, attr):
                delattr(parent, attr)
        sys.modules.pop(name, None)

    for name, original_path in _ORIGINAL_PATHS.items():
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "__path__"):
            module.__path__ = original_path


atexit.register(_restore_packages)


def stub_module(name: str) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__path__ = []  # type: ignore[attr-defined]
        sys.modules[name] = module
    parent_name, _, attr = name.rpartition(".")
    if parent_name:
        parent = stub_module(parent_name)
        setattr(parent, attr, module)
    return module


ensure_package("lukhas", BASE_PATH)
ensure_package("lukhas.identity", IDENTITY_PATH)

for module_name in [
    "cryptography",
    "cryptography.hazmat",
    "cryptography.hazmat.primitives",
    "cryptography.hazmat.primitives.hashes",
    "cryptography.hazmat.primitives.serialization",
    "cryptography.hazmat.primitives.asymmetric",
    "cryptography.hazmat.primitives.asymmetric.padding",
    "cryptography.hazmat.primitives.asymmetric.rsa",
    "cryptography.hazmat.primitives.ciphers",
    "cryptography.hazmat.primitives.ciphers.algorithms",
    "cryptography.hazmat.primitives.ciphers.modes",
]:
    stub_module(module_name)

structlog_stub = stub_module("structlog")


class _MockStructLogger:
    def __getattr__(self, _name):
        return self

    def info(self, *_args, **_kwargs):
        return None

    def warning(self, *_args, **_kwargs):
        return None

    def error(self, *_args, **_kwargs):
        return None


def _get_logger(*_args, **_kwargs):
    return _MockStructLogger()


structlog_stub.get_logger = _get_logger  # type: ignore[attr-defined]


class _MockMetric:
    def labels(self, **_kwargs):
        return self

    def inc(self, amount: int = 1) -> None:
        return None

    def observe(self, _value: float) -> None:
        return None

    def set(self, _value: float) -> None:
        return None


prometheus_stub = stub_module("prometheus_client")
prometheus_stub.Counter = lambda *args, **kwargs: _MockMetric()  # type: ignore[attr-defined]
prometheus_stub.Gauge = lambda *args, **kwargs: _MockMetric()  # type: ignore[attr-defined]
prometheus_stub.Histogram = lambda *args, **kwargs: _MockMetric()  # type: ignore[attr-defined]


class _MockSpan:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def set_attribute(self, *_args, **_kwargs):
        return None


class _MockTracer:
    def start_as_current_span(self, _name: str) -> _MockSpan:
        return _MockSpan()


opentelemetry_stub = stub_module("opentelemetry")
trace_stub = stub_module("opentelemetry.trace")
trace_stub.get_tracer = lambda *_args, **_kwargs: _MockTracer()  # type: ignore[attr-defined]
opentelemetry_stub.trace = trace_stub  # type: ignore[attr-defined]

MODULE_NAME = "lukhas.identity.test_lid_integration"
MODULE_PATH = IDENTITY_PATH / "test_lid_integration.py"

spec = importlib.util.spec_from_file_location(
    MODULE_NAME,
    MODULE_PATH,
    submodule_search_locations=[str(IDENTITY_PATH)],
)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load LiD integration module for testing")

lid_module = importlib.util.module_from_spec(spec)
sys.modules[MODULE_NAME] = lid_module
spec.loader.exec_module(lid_module)

LiDTokenSystemTest = getattr(lid_module, "LiDTokenSystemTest")
TierLevel = getattr(lid_module, "TierLevel")
ValidationResult = getattr(lid_module, "ValidationResult")


def test_normalize_validation_tier_defaults_to_authenticated():
    """Ensure normalization defaults to AUTHENTICATED when tier missing."""

    system_test = LiDTokenSystemTest()
    result = ValidationResult(valid=True)

    assert system_test._normalize_validation_tier(result) is TierLevel.AUTHENTICATED


def test_normalize_validation_tier_preserves_explicit_level():
    """Ensure explicit tier levels remain intact after normalization."""

    system_test = LiDTokenSystemTest()
    privileged_result = ValidationResult(valid=True, tier_level=TierLevel.PRIVILEGED)

    assert system_test._normalize_validation_tier(privileged_result) is TierLevel.PRIVILEGED
