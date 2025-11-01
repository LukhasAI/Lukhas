#!/usr/bin/env python3
"""Regression tests for WebAuthn registration import fallbacks."""

import builtins
import importlib.util
import sys
from pathlib import Path
from typing import Any


def test_registration_credential_alias_when_webauthn_missing(monkeypatch):
    """Ensure RegistrationCredential has a safe alias if the library is absent."""

    module_name = "tests.identity.webauthn_registration_alias"
    module_path = (
        Path(__file__).resolve().parents[2]
        / "lukhas_website"
        / "lukhas"
        / "identity"
        / "webauthn_production.py"
    )

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):  # type: ignore[override]
        if name.startswith("webauthn"):
            raise ImportError("mocked missing webauthn dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    assert module.WEBAUTHN_AVAILABLE is False
    assert module.RegistrationCredential is Any

    sys.modules.pop(module_name, None)
