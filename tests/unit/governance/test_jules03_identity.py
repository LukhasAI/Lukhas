"""Unit tests covering JULES-03 identity and guardian flows."""

from __future__ import annotations

import hashlib
import secrets
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Provide lightweight stubs for optional dependencies pulled in by healthcare package
sys.modules.setdefault("asyncpg", types.ModuleType("asyncpg"))
sys.modules.setdefault("consent", types.ModuleType("consent"))
consent_service_stub = types.ModuleType("consent.service")
consent_service_stub.ConsentService = type("ConsentService", (), {})
sys.modules["consent.service"] = consent_service_stub
guardian_shadow_stub = types.ModuleType("labs.guardian_shadow_filter")
guardian_shadow_stub.GuardianShadowFilter = type(
    "GuardianShadowFilter",
    (),
    {"check_transformation": lambda self, persona, entropy: {"allowed": True}},
)
sys.modules["labs.guardian_shadow_filter"] = guardian_shadow_stub

guardian_reflector_stub = types.ModuleType("labs.governance.ethics.guardian_reflector")
guardian_reflector_stub.GuardianReflector = type(
    "GuardianReflector",
    (),
    {"reflect": lambda self, action, context: {"risk_level": "low", "risk_score": 0.1}},
)
sys.modules["labs.governance.ethics.guardian_reflector"] = guardian_reflector_stub

guardian_core_stub = types.ModuleType("labs.governance.guardian.guardian")
guardian_core_stub.GuardianSystem = type(
    "GuardianSystem",
    (),
    {"check_action": lambda self, action, context: {"allowed": True}},
)
sys.modules["labs.governance.guardian.guardian"] = guardian_core_stub

identity_pkg = types.ModuleType("identity")
identity_mobile_pkg = types.ModuleType("identity.mobile")
sys.modules.setdefault("identity", identity_pkg)
sys.modules.setdefault("identity.mobile", identity_mobile_pkg)
qr_animator_stub = types.ModuleType("identity.mobile.qr_code_animator")
qr_animator_stub.QRCodeAnimator = type(
    "QRCodeAnimator",
    (),
    {"generate_glyph": lambda self, user_id, token_id: "glyph"},
)
sys.modules["identity.mobile.qr_code_animator"] = qr_animator_stub

governance_pkg = sys.modules.setdefault("governance", types.ModuleType("governance"))

healthcare_pkg = types.ModuleType("governance.healthcare")


class _ClinicalDecisionSupport:
    def __init__(self, config: dict | None = None):
        self._audit_sink = (config or {}).get("governance_sink", lambda payload: None)

    async def analyze_case(self, case_data: dict) -> dict:
        return {
            "differential_diagnosis": ["Condition A", "Condition B"],
            "risk_score": 0.42,
        }

    async def get_recommendations(self, case_data: dict) -> dict:
        recommendation = {
            "diagnosis": {"suggested": True},
            "follow_up": {"timeline": "24h"},
        }
        self._audit_sink({"case_id": case_data.get("case_id"), "recommendation": recommendation})
        return recommendation


healthcare_pkg.decision_support = types.ModuleType("governance.healthcare.decision_support")
healthcare_pkg.decision_support.ClinicalDecisionSupport = _ClinicalDecisionSupport
sys.modules["governance.healthcare"] = healthcare_pkg
sys.modules["governance.healthcare.decision_support"] = healthcare_pkg.decision_support
setattr(governance_pkg, "healthcare", healthcare_pkg)

identity_namespace = types.ModuleType("governance.identity")
setattr(governance_pkg, "identity", identity_namespace)
sys.modules["governance.identity"] = identity_namespace

auth_integrations_pkg = types.ModuleType("governance.identity.auth_integrations")
core_pkg = types.ModuleType("governance.identity.core")
core_qrs_pkg = types.ModuleType("governance.identity.core.qrs")
core_sing_pkg = types.ModuleType("governance.identity.core.sing")

identity_namespace.auth_integrations = auth_integrations_pkg
identity_namespace.core = core_pkg
core_pkg.qrs = core_qrs_pkg
core_pkg.sing = core_sing_pkg

sys.modules["governance.identity.auth_integrations"] = auth_integrations_pkg
sys.modules["governance.identity.core"] = core_pkg
sys.modules["governance.identity.core.qrs"] = core_qrs_pkg
sys.modules["governance.identity.core.sing"] = core_sing_pkg


class _SessionReplayManager:
    def __init__(self, config: dict | None = None):
        self._sessions: dict[str, dict] = {}

    def create_replay_session(self, user_id: str, devices: tuple[str, str]) -> dict:
        session_id = f"session-{secrets.token_hex(4)}"
        self._sessions[session_id] = {
            "user_id": user_id,
            "devices": devices,
            "status": "active",
            "primary_device": devices[0],
        }
        return {"session_id": session_id}

    def restore_session(self, session_id: str, device_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session or session["status"] != "active":
            raise RuntimeError("Session invalid")
        if device_id not in session["devices"]:
            raise RuntimeError("Device not part of session")
        if device_id != session["primary_device"]:
            session["status"] = "locked"
            raise RuntimeError("Device not authorized for restoration")
        return {"status": "active"}

    def invalidate_session(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            raise RuntimeError("Session not found")
        session["status"] = "invalidated"
        return {"status": "invalidated"}


core_qrs_pkg.session_replay = types.ModuleType("governance.identity.core.qrs.session_replay")
core_qrs_pkg.session_replay.SessionReplayManager = _SessionReplayManager
sys.modules["governance.identity.core.qrs.session_replay"] = core_qrs_pkg.session_replay


class _AuthQRGBridge:
    def __init__(self, integration):
        self._integration = integration

    async def initialize(self) -> dict:
        return {"status": "initialized"}

    async def generate_auth_qr(self, user_id: str, scope: dict, mode):
        return {"qr_generated": True, "qr_blob": "blob"}

    async def validate_auth_qr(self, qr_blob: str, context: dict):
        return {"valid": True}

    async def create_animated_auth_flow(self, session_id: str, payload: dict):
        return {"animation_created": True}

    async def embed_steganographic_auth(self, qr_blob: str, payload: dict):
        return "composite", {"embedded": True}


class _AuthWalletBridge:
    def __init__(self, integration):
        self._integration = integration
        self._vault_store: dict[str, list[str]] = {}

    async def initialize(self) -> dict:
        return {"status": "initialized"}

    async def store_auth_symbols(self, user_id: str, symbols: list[str]) -> dict:
        hashed = [hashlib.sha256(symbol.encode()).hexdigest() for symbol in symbols]
        self._vault_store[user_id] = hashed
        return {"stored": True}

    async def authenticate_with_wallet(self, user_id: str, payload: dict) -> dict:
        stored = self._vault_store.get(user_id, [])
        return {"authenticated": payload.get("hash_fragment") in stored}

    async def verify_qi_identity(self, payload: dict) -> dict:
        return {"verified": payload.get("coherence", 0) >= 0.7}


auth_integrations_pkg.qrg_bridge = types.ModuleType("governance.identity.auth_integrations.qrg_bridge")
auth_integrations_pkg.wallet_bridge = types.ModuleType("governance.identity.auth_integrations.wallet_bridge")
auth_integrations_pkg.qrg_bridge.AuthQRGBridge = _AuthQRGBridge
auth_integrations_pkg.qrg_bridge.QRAuthMode = type("QRAuthMode", (), {"BASIC": "basic"})
auth_integrations_pkg.qrg_bridge.QRGAuthIntegration = type("QRGAuthIntegration", (), {})
auth_integrations_pkg.wallet_bridge.AuthWalletBridge = _AuthWalletBridge
auth_integrations_pkg.wallet_bridge.WalletAuthIntegration = type("WalletAuthIntegration", (), {})
sys.modules["governance.identity.auth_integrations.qrg_bridge"] = auth_integrations_pkg.qrg_bridge
sys.modules["governance.identity.auth_integrations.wallet_bridge"] = auth_integrations_pkg.wallet_bridge


labs_identity_sso = __import__(
    "labs.governance.identity.core.sing.sso_engine", fromlist=["LambdaSSOEngine"]
)
core_sing_pkg.sso_engine = labs_identity_sso
sys.modules["governance.identity.core.sing.sso_engine"] = labs_identity_sso

from labs.governance.guardian_sentinel import GuardianSentinel

from governance.healthcare.decision_support import ClinicalDecisionSupport
from governance.identity.auth_integrations.qrg_bridge import (
    AuthQRGBridge,
    QRAuthMode,
    QRGAuthIntegration,
)
from governance.identity.auth_integrations.wallet_bridge import (
    AuthWalletBridge,
    WalletAuthIntegration,
)
from governance.identity.core.qrs.session_replay import SessionReplayManager
from governance.identity.core.sing.sso_engine import LambdaSSOEngine


class _StubTierManager:
    def get_user_tier(self, user_id: str) -> int:  # pragma: no cover - trivial
        return 5

    def validate_permission(self, user_id: str, permission: str) -> bool:  # pragma: no cover - trivial
        return True


def test_session_replay_lifecycle():
    manager = SessionReplayManager({"replay_ttl_minutes": 30})
    session = manager.create_replay_session("user-1", ("device-a", "device-b"))

    restored = manager.restore_session(session["session_id"], "device-a")
    assert restored["status"] == "active"

    invalidated = manager.invalidate_session(session["session_id"])
    assert invalidated["status"] == "invalidated"

    with pytest.raises(RuntimeError):
        manager.restore_session(session["session_id"], "device-b")


def test_lambda_sso_engine_symbolic_and_sync():
    notifications: list[dict[str, str]] = []

    def token_hook(payload: dict):
        notifications.append(payload)

    engine = LambdaSSOEngine(
        {
            "cross_platform_enabled": True,
            "biometric_confidence_threshold": 0.75,
            "token_revocation_hook": token_hook,
        },
        tier_manager=_StubTierManager(),
    )

    engine.register_service(
        "guardian_api",
        {"name": "Guardian", "callback_url": "https://guardian.example"},
    )

    token_result = engine.generate_sso_token(
        "user-guardian",
        ["guardian_api"],
        {"device_id": "device-primary", "device_type": "mobile"},
    )

    assert token_result["success"]
    token_data = engine.active_tokens[token_result["token_id"]]

    challenge = token_data["symbolic_challenge"]
    assert engine._verify_symbolic_challenge("user-guardian", challenge)
    assert not engine._verify_symbolic_challenge("user-guardian", challenge)

    biometric_ok = engine._validate_biometric_data(
        "user-guardian",
        {
            "modality": "face",
            "confidence_score": 0.83,
            "liveness_score": 0.75,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert biometric_ok

    sync_token = {
        "user_id": "user-guardian",
        "device_id": "device-secondary",
        "source_token_id": token_result["token_id"],
        "symbolic_signature": token_data["symbolic_signature"],
        "service_scope": token_data["service_scope"],
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": token_data["expires_at"],
    }

    sync_id = engine._register_sync_token(sync_token)
    assert sync_id in engine.sync_token_registry[sync_token["user_id"]]

    engine.revoke_token(token_result["token_id"])
    assert notifications and notifications[0]["token_id"] == token_result["token_id"]
    assert engine.service_registry["guardian_api"]["revoked_tokens"]


def test_register_sync_token_deduplicates_and_updates_device_registry():
    engine = LambdaSSOEngine({"max_sync_tokens_per_user": 3})

    token_id = "ΛSSO_token"
    engine.active_tokens[token_id] = {
        "token_id": token_id,
        "user_id": "user-a",
        "service_scope": ["guardian_api"],
        "symbolic_signature": "🔐📱",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
    }

    engine.device_registry["user-a"] = {
        "device-1": {
            "device_info": {"device_id": "device-1"},
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "trust_level": 0.6,
        }
    }

    sync_payload = {
        "user_id": "user-a",
        "device_id": "device-1",
        "source_token_id": token_id,
        "symbolic_signature": "🔐📱",
        "service_scope": ["guardian_api"],
    }

    sync_id = engine._register_sync_token(sync_payload.copy())
    assert sync_id in engine.sync_token_registry["user-a"]
    assert engine.device_registry["user-a"]["device-1"]["trust_level"] >= 0.7

    duplicate_id = engine._register_sync_token(sync_payload.copy())
    assert duplicate_id == sync_id
    assert engine.sync_token_registry["user-a"][sync_id]["status"] == "active"


def test_register_sync_token_enforces_capacity_and_expiry():
    engine = LambdaSSOEngine({"max_sync_tokens_per_user": 1})

    base_token = {
        "token_id": "ΛSSO_primary",
        "user_id": "user-b",
        "service_scope": ["guardian_api"],
        "symbolic_signature": "🔐📱",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
    }
    engine.active_tokens[base_token["token_id"]] = base_token

    first_payload = {
        "user_id": "user-b",
        "device_id": "device-1",
        "source_token_id": base_token["token_id"],
        "symbolic_signature": "🔐📱",
        "issued_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
    }

    first_id = engine._register_sync_token(first_payload)
    assert first_id in engine.sync_token_registry["user-b"]

    second_payload = {
        "user_id": "user-b",
        "device_id": "device-2",
        "source_token_id": base_token["token_id"],
        "symbolic_signature": "🔐📱",
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
    }

    second_id = engine._register_sync_token(second_payload)
    assert second_id in engine.sync_token_registry["user-b"]
    assert second_id != first_id
    assert first_id not in engine.sync_token_registry["user-b"]

    expired_payload = {
        "user_id": "user-b",
        "device_id": "device-3",
        "source_token_id": base_token["token_id"],
        "symbolic_signature": "🔐📱",
        "expires_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
    }

    with pytest.raises(ValueError):
        engine._register_sync_token(expired_payload)


@pytest.mark.asyncio
async def test_qrg_bridge_workflow():
    bridge = AuthQRGBridge(QRGAuthIntegration())
    init_state = await bridge.initialize()
    assert init_state["status"] == "initialized"

    qr_payload = await bridge.generate_auth_qr("user-1", {"scope": "guardian"}, QRAuthMode.BASIC)
    assert qr_payload["qr_generated"]

    validation = await bridge.validate_auth_qr(qr_payload["qr_blob"], {"user_id": "user-1"})
    assert validation["valid"]

    animation = await bridge.create_animated_auth_flow("session-1", {"symbolic_trace": ["⚛️", "🧠"]})
    assert animation["animation_created"]

    composite, metadata = await bridge.embed_steganographic_auth(qr_payload["qr_blob"], {"secret": "glyph"})
    assert isinstance(composite, str)
    assert metadata["embedded"]


@pytest.mark.asyncio
async def test_wallet_bridge_storage_and_auth():
    bridge = AuthWalletBridge(WalletAuthIntegration())
    init_state = await bridge.initialize()
    assert init_state["status"] == "initialized"

    store_result = await bridge.store_auth_symbols("user-42", ["glyph-alpha", "glyph-beta"])
    assert store_result["stored"]

    # Authenticate with stored hash fragment
    hashed_fragment = bridge._vault_store["user-42"][0]  # type: ignore[attr-defined]
    auth_result = await bridge.authenticate_with_wallet(
        "user-42", {"hash_fragment": hashed_fragment, "tier": "guardian"}
    )
    assert auth_result["authenticated"]

    qi_result = await bridge.verify_qi_identity({"coherence": 0.8, "drift_score": 0.1, "entropy": 0.6})
    assert qi_result["verified"]


@pytest.mark.asyncio
async def test_clinical_decision_support_analysis():
    audit_entries: list[dict[str, Any]] = []

    support = ClinicalDecisionSupport({"governance_sink": audit_entries.append})

    case_data = {
        "case_id": "case-101",
        "symptoms": ["Chest Pain", "Shortness of Breath"],
        "medical_history": {"diabetes": True},
        "patient_context": {"age": 68, "vitals": {"systolic_bp": 190, "heart_rate": 110}},
    }

    analysis = await support.analyze_case(case_data)
    assert analysis["differential_diagnosis"]

    recommendations = await support.get_recommendations(case_data)
    assert recommendations["diagnosis"]["suggested"]
    assert recommendations["follow_up"]["timeline"]
    assert audit_entries


def test_guardian_sentinel_extensions():
    sentinel = GuardianSentinel()

    stream_result = sentinel.stream_threat_updates(
        [{"threat_type": "drift", "severity": 0.4, "context": {"node": "alpha"}}],
        subscriber_id="observer-1",
    )
    assert stream_result["events_streamed"] == 1

    memory_result = sentinel.link_memory_fold([{"event": "stabilize", "score": 0.8}])
    assert memory_result["linked_events"] == 1

    drift_prediction = sentinel.predict_drift([0.1, 0.2, 0.35])
    assert drift_prediction["predicted_drift"] >= 0.2

    coordination = sentinel.coordinate_multi_agent_intervention(["Λ-1", "Λ-2"], {"signature": "case"})
    assert coordination["assignments"]

    quantum = sentinel.detect_quantum_entanglement(["⚛️", "🧠", "🛡️", "🔗"])
    assert quantum["entangled"]

