"""Tests covering WebAuthn enhanced module import behaviour."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LUKHAS_WEBSITE_ROOT = PROJECT_ROOT / "lukhas_website"
IDENTITY_DIR = LUKHAS_WEBSITE_ROOT / "lukhas" / "identity"
IDENTITY_PACKAGE = "lukhas_website.lukhas.identity"
ENHANCED_FILE = IDENTITY_DIR / "webauthn_enhanced.py"
BASE_FILE = IDENTITY_DIR / "webauthn.py"

if str(LUKHAS_WEBSITE_ROOT) not in sys.path:
    sys.path.insert(0, str(LUKHAS_WEBSITE_ROOT))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODULE_PATH = "lukhas_website.lukhas.identity.webauthn_enhanced"
BASE_MODULE_PATH = "lukhas_website.lukhas.identity.webauthn"


def _ensure_identity_packages() -> None:
    for name, path in (
        ("lukhas_website", LUKHAS_WEBSITE_ROOT),
        ("lukhas_website.lukhas", LUKHAS_WEBSITE_ROOT / "lukhas"),
        (IDENTITY_PACKAGE, IDENTITY_DIR),
    ):
        if name not in sys.modules:
            package = ModuleType(name)
            package.__path__ = [str(path)]
            package.__file__ = str(path / "__init__.py")
            package.__package__ = name
            sys.modules[name] = package


def _install_structlog_stub() -> None:
    if "structlog" in sys.modules:
        return

    structlog_module = ModuleType("structlog")

    class _Logger:
        def warning(self, *_args: object, **_kwargs: object) -> None:
            pass

        def info(self, *_args: object, **_kwargs: object) -> None:
            pass

        def debug(self, *_args: object, **_kwargs: object) -> None:
            pass

        def error(self, *_args: object, **_kwargs: object) -> None:
            pass

    def get_logger(_name: str | None = None) -> _Logger:
        return _Logger()

    structlog_module.get_logger = get_logger  # type: ignore[attr-defined]
    sys.modules["structlog"] = structlog_module


def _load_module_from_file(name: str, file_path: Path) -> ModuleType:
    _install_structlog_stub()
    _ensure_identity_packages()

    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    module.__package__ = IDENTITY_PACKAGE
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _reload_enhanced_module() -> ModuleType:
    sys.modules.pop(MODULE_PATH, None)
    return _load_module_from_file(MODULE_PATH, ENHANCED_FILE)


def test_webauthn_dependencies_available_sets_flag_true():
    """The module exposes WebAuthn primitives when dependencies import correctly."""

    base_module = _load_module_from_file(BASE_MODULE_PATH, BASE_FILE)
    module = _reload_enhanced_module()

    assert module.WEBAUTHN_BASE_AVAILABLE is True
    assert module.WebAuthnCredential is base_module.WebAuthnCredential
    assert module.WebAuthnManager is base_module.WebAuthnManager


def test_webauthn_dependency_failure_sets_flag_false():
    """If the base module lacks required exports the enhanced module should fallback."""

    original_module = sys.modules.get(BASE_MODULE_PATH)
    sys.modules[BASE_MODULE_PATH] = ModuleType(BASE_MODULE_PATH)

    try:
        module = _reload_enhanced_module()

        assert module.WEBAUTHN_BASE_AVAILABLE is False
    finally:
        sys.modules.pop(MODULE_PATH, None)
        if original_module is not None:
            sys.modules[BASE_MODULE_PATH] = original_module
        else:
            sys.modules.pop(BASE_MODULE_PATH, None)
