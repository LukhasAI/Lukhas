"""Unit tests covering JULES-03 identity and guardian flows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import sys
import types

import pytest

# Provide lightweight stubs for optional dependencies pulled in by healthcare package
sys.modules.setdefault("asyncpg", types.ModuleType("asyncpg"))
sys.modules.setdefault("consent", types.ModuleType("consent"))
consent_service_stub = types.ModuleType("consent.service")
consent_service_stub.ConsentService = type("ConsentService", (), {})
sys.modules["consent.service"] = consent_service_stub
guardian_shadow_stub = types.ModuleType("candidate.guardian_shadow_filter")
guardian_shadow_stub.GuardianShadowFilter = type(
    "GuardianShadowFilter",
    (),
    {"check_transformation": lambda self, persona, entropy: {"allowed": True}},
)
sys.modules["candidate.guardian_shadow_filter"] = guardian_shadow_stub

guardian_reflector_stub = types.ModuleType("candidate.governance.ethics.guardian_reflector")
guardian_reflector_stub.GuardianReflector = type(
    "GuardianReflector",
    (),
    {"reflect": lambda self, action, context: {"risk_level": "low", "risk_score": 0.1}},
)
sys.modules["candidate.governance.ethics.guardian_reflector"] = guardian_reflector_stub

guardian_core_stub = types.ModuleType("candidate.governance.guardian.guardian")
guardian_core_stub.GuardianSystem = type(
    "GuardianSystem",
    (),
    {"check_action": lambda self, action, context: {"allowed": True}},
)
sys.modules["candidate.governance.guardian.guardian"] = guardian_core_stub

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

from candidate.governance.healthcare.decision_support import ClinicalDecisionSupport
from candidate.governance.identity.auth_integrations.qrg_bridge import (
    AuthQRGBridge,
    QRGAuthIntegration,
    QRAuthMode,
)
from candidate.governance.identity.auth_integrations.wallet_bridge import (
    AuthWalletBridge,
    WalletAuthIntegration,
)
from candidate.governance.identity.core.qrs.session_replay import SessionReplayManager
from candidate.governance.identity.core.sing.sso_engine import LambdaSSOEngine
from candidate.governance.guardian_sentinel import GuardianSentinel


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

    sync_token = engine._create_device_sync_token(engine.active_tokens, "device-secondary")
    sync_id = engine._register_sync_token(sync_token)
    assert sync_id in engine.sync_token_registry[sync_token["user_id"]]

    engine.revoke_token(token_result["token_id"])
    assert notifications and notifications[0]["token_id"] == token_result["token_id"]
    assert engine.service_registry["guardian_api"]["revoked_tokens"]


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

