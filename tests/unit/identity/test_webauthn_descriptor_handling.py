import base64
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "lukhas_website"
    / "lukhas"
    / "identity"
    / "webauthn_production.py"
)


def _install_opentelemetry_stub() -> None:
    if "opentelemetry" in sys.modules:
        return

    trace_module = ModuleType("opentelemetry.trace")

    class _DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def set_attribute(self, *_args, **_kwargs):
            return None

        def record_exception(self, *_args, **_kwargs):
            return None

        def set_status(self, *_args, **_kwargs):
            return None

    class _DummyTracer:
        def start_span(self, _name):
            return _DummySpan()

    def _get_tracer(_name):
        return _DummyTracer()

    class _Status:
        def __init__(self, status_code, description=None):
            self.status_code = status_code
            self.description = description

    class _StatusCode:
        ERROR = "ERROR"

    trace_module.get_tracer = _get_tracer  # type: ignore[attr-defined]
    trace_module.Status = _Status  # type: ignore[attr-defined]
    trace_module.StatusCode = _StatusCode  # type: ignore[attr-defined]

    opentelemetry_pkg = ModuleType("opentelemetry")
    opentelemetry_pkg.trace = trace_module  # type: ignore[attr-defined]

    sys.modules.setdefault("opentelemetry", opentelemetry_pkg)
    sys.modules.setdefault("opentelemetry.trace", trace_module)


def _install_prometheus_stub() -> None:
    if "prometheus_client" in sys.modules:
        return

    class _Metric:
        def __init__(self, *_args, **_kwargs):
            pass

        def labels(self, *_args, **_kwargs):
            return self

        def observe(self, *_args, **_kwargs):
            return None

        def inc(self, *_args, **_kwargs):
            return None

        def set(self, *_args, **_kwargs):
            return None

    prometheus_module = ModuleType("prometheus_client")
    prometheus_module.Counter = _Metric  # type: ignore[attr-defined]
    prometheus_module.Gauge = _Metric  # type: ignore[attr-defined]
    prometheus_module.Histogram = _Metric  # type: ignore[attr-defined]

    sys.modules.setdefault("prometheus_client", prometheus_module)


def _load_webauthn_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "identity.webauthn_production",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load WebAuthn production module")

    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    sys.modules[spec.name] = module
    loader.exec_module(module)
    sys.modules.setdefault("identity.webauthn_production", module)
    return module


webauthn = sys.modules.get("identity.webauthn_production")
if webauthn is None:
    _install_opentelemetry_stub()
    _install_prometheus_stub()
    webauthn = _load_webauthn_module()


@pytest.mark.asyncio
async def test_begin_authentication_uses_public_key_credential_descriptor(monkeypatch):
    store = webauthn.WebAuthnCredentialStore()
    manager = webauthn.WebAuthnManager(
        rp_id="example.com",
        rp_name="Example",
        origin="https://example.com",
        credential_store=store,
    )

    raw_id = b"credential-id"
    encoded_id = base64.urlsafe_b64encode(raw_id).decode().rstrip("=")
    await store.store_credential(
        webauthn.WebAuthnCredential(
            credential_id=encoded_id,
            public_key="test",
            user_id="user-123",
            status=webauthn.CredentialStatus.ACTIVE,
            tier=webauthn.AuthenticatorTier.T4_STRONG,
        )
    )

    captured_kwargs = {}

    class DummyDescriptor:
        def __init__(self, *, id, type):  # - match library signature
            self.id = id
            self.type = type

    def fake_generate_authentication_options(**kwargs):
        captured_kwargs.update(kwargs)

        class _DummyOptions:
            challenge = "server-challenge"

            def model_dump(self):
                return {
                    "challenge": "server-challenge",
                    "allowCredentials": [
                        {"id": "placeholder", "type": "public-key"}
                    ],
                }

        return _DummyOptions()

    monkeypatch.setattr(webauthn, "WEBAUTHN_AVAILABLE", True)
    monkeypatch.setattr(
        webauthn,
        "PublicKeyCredentialDescriptor",
        DummyDescriptor,
        raising=False,
    )
    monkeypatch.setattr(
        webauthn,
        "generate_authentication_options",
        fake_generate_authentication_options,
        raising=False,
    )
    monkeypatch.setattr(
        webauthn,
        "UserVerificationRequirement",
        type(
            "_UserVerificationRequirement",
            (),
            {"REQUIRED": "required", "PREFERRED": "preferred"},
        ),
        raising=False,
    )
    monkeypatch.setattr(
        webauthn.secrets,
        "token_urlsafe",
        lambda _size: "fixed-challenge-id",
    )

    result = await manager.begin_authentication(user_id="user-123")

    assert result["_challenge_id"] == "fixed-challenge-id"
    assert captured_kwargs["allow_credentials"], "Expected descriptors to be provided"
    descriptor = captured_kwargs["allow_credentials"][0]
    assert isinstance(descriptor, DummyDescriptor)
    assert descriptor.id == raw_id
    assert descriptor.type == "public-key"


@pytest.mark.asyncio
async def test_begin_authentication_skips_invalid_credentials(monkeypatch):
    store = webauthn.WebAuthnCredentialStore()
    manager = webauthn.WebAuthnManager(
        rp_id="example.com",
        rp_name="Example",
        origin="https://example.com",
        credential_store=store,
    )

    await store.store_credential(
        webauthn.WebAuthnCredential(
            credential_id="!!!invalid!!!",
            public_key="test",
            user_id="user-123",
            status=webauthn.CredentialStatus.ACTIVE,
            tier=webauthn.AuthenticatorTier.T4_STRONG,
        )
    )

    assert webauthn._decode_credential_id("!!!invalid!!!") is None

    captured_kwargs = {}

    class DummyDescriptor:
        def __init__(self, *, id, type):  # - match library signature
            self.id = id
            self.type = type

    def fake_generate_authentication_options(**kwargs):
        captured_kwargs.update(kwargs)

        class _DummyOptions:
            challenge = "server-challenge"

            def model_dump(self):
                return {"challenge": "server-challenge", "allowCredentials": []}

        return _DummyOptions()

    monkeypatch.setattr(webauthn, "WEBAUTHN_AVAILABLE", True)
    monkeypatch.setattr(
        webauthn,
        "PublicKeyCredentialDescriptor",
        DummyDescriptor,
        raising=False,
    )
    monkeypatch.setattr(
        webauthn,
        "generate_authentication_options",
        fake_generate_authentication_options,
        raising=False,
    )
    monkeypatch.setattr(
        webauthn,
        "UserVerificationRequirement",
        type(
            "_UserVerificationRequirement",
            (),
            {"REQUIRED": "required", "PREFERRED": "preferred"},
        ),
        raising=False,
    )
    monkeypatch.setattr(
        webauthn.secrets,
        "token_urlsafe",
        lambda _size: "fixed-challenge-id",
    )

    await manager.begin_authentication(user_id="user-123")

    assert captured_kwargs["allow_credentials"] == []
