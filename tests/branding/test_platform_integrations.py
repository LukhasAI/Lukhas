"""Unit tests for OAuth handling in branding.apis.platform_integrations."""

import builtins
import importlib
import sys
import types

import pytest

MODULE_NAME = "branding.apis.platform_integrations"


def _prepare_import(monkeypatch):
    """Remove cached modules and stub native dependencies for branding imports."""

    for name in [MODULE_NAME, "branding.apis", "branding"]:
        sys.modules.pop(name, None)

    dummy_bridge = types.ModuleType("_bridgeutils")

    def bridge_from_candidates(*_args, **_kwargs):
        return [], {}

    dummy_bridge.bridge_from_candidates = bridge_from_candidates
    monkeypatch.setitem(sys.modules, "_bridgeutils", dummy_bridge)


@pytest.mark.unit
@pytest.mark.security
def test_oauth_client_imports_when_available(monkeypatch):
    """requests_oauthlib should expose OAuth2Session when available."""

    _prepare_import(monkeypatch)
    sys.modules.pop("requests_oauthlib", None)

    dummy_module = types.ModuleType("requests_oauthlib")

    class DummyOAuth2Session:  # pragma: no cover - simple sentinel
        pass

    dummy_module.OAuth2Session = DummyOAuth2Session
    monkeypatch.setitem(sys.modules, "requests_oauthlib", dummy_module)

    module = importlib.import_module(MODULE_NAME)

    assert module.OAUTH_AVAILABLE is True
    assert module.OAuth2Session is DummyOAuth2Session


@pytest.mark.unit
@pytest.mark.security
def test_oauth_client_flags_missing_dependency(monkeypatch):
    """The module should fall back cleanly when requests_oauthlib is absent."""

    _prepare_import(monkeypatch)
    sys.modules.pop("requests_oauthlib", None)

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "requests_oauthlib":
            raise ImportError("Simulated missing dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    module = importlib.import_module(MODULE_NAME)

    assert module.OAUTH_AVAILABLE is False
    assert module.OAuth2Session is None
