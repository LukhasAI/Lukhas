#!/usr/bin/env python3
"""Compatibility tests for WebAuthn production implementation."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from enum import Enum

import pytest


@pytest.mark.usefixtures("monkeypatch")
def test_authenticator_attachment_fallback(monkeypatch):
    """Ensure a compatibility shim is used when AuthenticatorAttachment is absent."""

    module_name = "identity.webauthn_production"
    sys.modules.pop(module_name, None)

    # Stub webauthn core module
    webauthn_module = ModuleType("webauthn")

    class _Options:
        challenge = "dummy"

        def model_dump(self):
            return {"challenge": self.challenge}

    def _registration_options(**_kwargs):
        return _Options()

    def _authentication_options(**_kwargs):
        return _Options()

    def _verify_registration_response(**_kwargs):
        return SimpleNamespace(
            credential_public_key=b"key",
            credential_id=b"id",
            sign_count=0,
            authenticator_attachment="platform",
            backup_eligible=False,
            backup_state=False,
            aaguid=b"",
        )

    def _verify_authentication_response(**_kwargs):
        return SimpleNamespace(
            credential_public_key=b"key",
            new_sign_count=1,
            authenticator_attachment="platform",
            backup_eligible=False,
            backup_state=False,
            aaguid=b"",
        )

    webauthn_module.generate_registration_options = _registration_options
    webauthn_module.generate_authentication_options = _authentication_options
    webauthn_module.verify_registration_response = _verify_registration_response
    webauthn_module.verify_authentication_response = _verify_authentication_response

    # Stub helpers module
    helpers_module = ModuleType("webauthn.helpers")
    helpers_module.parse_registration_credential_json = lambda payload: payload
    helpers_module.parse_authentication_credential_json = lambda payload: payload

    # Stub structs module without AuthenticatorAttachment
    structs_module = ModuleType("webauthn.helpers.structs")

    class _AttestationConveyancePreference(str, Enum):
        DIRECT = "direct"
        INDIRECT = "indirect"
        NONE = "none"

    class _AuthenticatorSelectionCriteria:
        def __init__(self, authenticator_attachment=None, resident_key=None, user_verification=None):
            self.authenticator_attachment = authenticator_attachment
            self.resident_key = resident_key
            self.user_verification = user_verification

    class _ResidentKeyRequirement(str, Enum):
        REQUIRED = "required"
        DISCOURAGED = "discouraged"

    class _UserVerificationRequirement(str, Enum):
        REQUIRED = "required"
        PREFERRED = "preferred"

    structs_module.AttestationConveyancePreference = _AttestationConveyancePreference
    structs_module.AuthenticatorSelectionCriteria = _AuthenticatorSelectionCriteria
    structs_module.ResidentKeyRequirement = _ResidentKeyRequirement
    structs_module.UserVerificationRequirement = _UserVerificationRequirement

    monkeypatch.setitem(sys.modules, "webauthn", webauthn_module)
    monkeypatch.setitem(sys.modules, "webauthn.helpers", helpers_module)
    monkeypatch.setitem(sys.modules, "webauthn.helpers.structs", structs_module)

    module_path = Path(__file__).resolve().parents[2] / "lukhas_website" / "lukhas" / "identity" / "webauthn_production.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    loader = spec.loader
    assert loader is not None
    loader.exec_module(module)

    attachment_enum = module.AuthenticatorAttachment
    assert issubclass(attachment_enum, Enum)
    assert attachment_enum.PLATFORM.value == "platform"
    assert attachment_enum.CROSS_PLATFORM.value == "cross-platform"
    assert module.WEBAUTHN_AVAILABLE is True
    sys.modules.pop(module_name, None)
