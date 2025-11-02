from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from labs.governance.identity.core.sing.sso_engine import LambdaSSOEngine


def _build_token(
    token_id: str,
    user_id: str,
    created_at: datetime,
    expires_at: datetime,
    scope: list[str],
    platforms: list[str],
    biometric: bool,
) -> dict:
    return {
        "token_id": token_id,
        "user_id": user_id,
        "service_scope": scope,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "platform_compatibility": platforms,
        "biometric_fallback_enabled": biometric,
    }


def test_create_device_sync_token_builds_binding_hash_and_scope():
    engine = LambdaSSOEngine({"device_sync_token_ttl_hours": 6})

    now = datetime.now(timezone.utc)
    token_a = _build_token(
        "ΛSSO_a",
        "user-sync",
        now - timedelta(minutes=5),
        now + timedelta(hours=8),
        ["basic", "profile"],
        ["web", "mobile"],
        True,
    )
    token_b = _build_token(
        "ΛSSO_b",
        "user-sync",
        now - timedelta(minutes=2),
        now + timedelta(hours=10),
        ["email"],
        ["mobile", "ios"],
        False,
    )

    engine.device_registry["user-sync"] = {
        "device-sync-1": {"trust_level": 0.9},
    }

    sync_token = engine._create_device_sync_token(
        {token_a["token_id"]: token_a, token_b["token_id"]: token_b},
        "device-sync-1",
    )

    assert sync_token["user_id"] == "user-sync"
    assert sync_token["device_id"] == "device-sync-1"
    assert sync_token["service_scope"] == ["basic", "email", "profile"]
    assert sync_token["token_bindings"]["token_ids"] == ["ΛSSO_a", "ΛSSO_b"]
    assert sync_token["metadata"]["source_tokens"] == 2
    assert sync_token["metadata"]["primary_token"] == "ΛSSO_b"
    assert sync_token["metadata"]["trust_level"] == 0.9

    issued_at = datetime.fromisoformat(sync_token["issued_at"])
    expires_at = datetime.fromisoformat(sync_token["expires_at"])
    assert expires_at > issued_at
    assert expires_at <= datetime.fromisoformat(token_a["expires_at"])
    assert expires_at - issued_at <= timedelta(hours=6, seconds=1)

    expected_binding_material = {
        "device_id": "device-sync-1",
        "token_ids": ["ΛSSO_a", "ΛSSO_b"],
        "user_id": "user-sync",
        "issued_at": sync_token["issued_at"],
    }
    expected_hash = hashlib.sha256(
        json.dumps(expected_binding_material, sort_keys=True).encode()
    ).hexdigest()
    assert sync_token["token_bindings"]["binding_hash"] == expected_hash

    assert sync_token["platform_support"] == ["ios", "mobile", "web"]
    assert sync_token["biometric_fallback"] is True
    assert "sync_nonce" in sync_token["metadata"]


def test_create_device_sync_token_validates_inputs():
    engine = LambdaSSOEngine({})
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        engine._create_device_sync_token({}, "device-x")

    expired_token = _build_token(
        "ΛSSO_expired",
        "user-1",
        now - timedelta(days=2),
        now - timedelta(days=1),
        ["basic"],
        ["web"],
        False,
    )

    with pytest.raises(ValueError):
        engine._create_device_sync_token({expired_token["token_id"]: expired_token}, "device-x")

    active_token = _build_token(
        "ΛSSO_active",
        "user-1",
        now - timedelta(minutes=1),
        now + timedelta(hours=2),
        ["basic"],
        ["web"],
        False,
    )
    other_user_token = _build_token(
        "ΛSSO_other",
        "user-2",
        now - timedelta(minutes=1),
        now + timedelta(hours=2),
        ["basic"],
        ["web"],
        False,
    )

    with pytest.raises(ValueError):
        engine._create_device_sync_token(
            {
                active_token["token_id"]: active_token,
                other_user_token["token_id"]: other_user_token,
            },
            "device-x",
        )

    with pytest.raises(ValueError):
        engine._create_device_sync_token({active_token["token_id"]: active_token}, "")
