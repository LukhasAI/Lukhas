"""Integration coverage for the consent ledger implementation."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from core.governance.consent_ledger.ledger_v1 import ConsentLedgerV1, PolicyVerdict

# ΛTAG: consent_ledger_integration


@pytest.fixture()
def ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ConsentLedgerV1:
    """Create a ledger instance backed by a temporary SQLite database."""
    monkeypatch.setenv("LUKHAS_CONSENT_SECRET", "integration-test-secret")
    db_path = tmp_path / "consent_ledger.db"
    return ConsentLedgerV1(db_path=str(db_path), enable_trinity_validation=True)


def _open_db(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def test_grant_and_check_consent_allows_scoped_action(ledger: ConsentLedgerV1) -> None:
    """Granting consent should allow actions within the declared scope."""
    lid = "test-lid"
    resource_type = "voice_biometrics"
    scopes = ["synthesize", "store"]
    consent = ledger.grant_consent(
        lid=lid,
        resource_type=resource_type,
        scopes=scopes,
        purpose="voiceprint enrollment",
    )

    assert consent.consent_id.startswith("CONSENT-")

    result = ledger.check_consent(lid, resource_type, "synthesize")
    assert result["allowed"] is True
    assert result["require_step_up"] is False
    assert result["consent_id"] == consent.consent_id
    assert result["lawful_basis"] == "consent"

    with _open_db(ledger.db_path) as conn:
        rows = conn.execute(
            "SELECT consent_id, is_active, scopes FROM consent_records WHERE lid = ?",
            (lid,),
        ).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["consent_id"] == consent.consent_id
    assert row["is_active"] == 1
    assert json.loads(row["scopes"]) == scopes


def test_revoke_consent_disables_future_checks(ledger: ConsentLedgerV1) -> None:
    """Revoked consent should no longer authorise actions."""
    lid = "revoke-lid"
    consent = ledger.grant_consent(
        lid=lid,
        resource_type="profile",
        scopes=["read"],
        purpose="profile access",
    )

    assert ledger.revoke_consent(consent.consent_id, lid, reason="user_requested") is True

    with _open_db(ledger.db_path) as conn:
        stored = conn.execute(
            "SELECT is_active, revoked_at FROM consent_records WHERE consent_id = ?",
            (consent.consent_id,),
        ).fetchone()
    assert stored is not None
    assert stored["is_active"] == 0
    assert stored["revoked_at"] is not None

    result = ledger.check_consent(lid, "profile", "read")
    assert result["allowed"] is False
    assert result["require_step_up"] is True
    assert result["reason"] == "no_active_consent"


def test_create_trace_records_constellation_metadata(ledger: ConsentLedgerV1) -> None:
    """Traces should persist audit metadata and Constellation validation scores."""
    trace = ledger.create_trace(
        lid="trace-lid",
        action="grant_consent",
        resource="profile",
        purpose="audit",
        verdict=PolicyVerdict.ALLOW,
        context={"capability": "invoke"},
        explanation_unl="integration test",
    )

    with _open_db(ledger.db_path) as conn:
        stored_trace = conn.execute(
            "SELECT * FROM lambda_traces WHERE trace_id = ?",
            (trace.trace_id,),
        ).fetchone()
        validation = conn.execute(
            "SELECT identity_score, consciousness_score, guardian_score, overall_score "
            "FROM constellation_validations WHERE trace_id = ?",
            (trace.trace_id,),
        ).fetchone()

    assert stored_trace is not None
    assert stored_trace["trace_id"] == trace.trace_id
    assert stored_trace["policy_verdict"] == PolicyVerdict.ALLOW.value
    assert len(stored_trace["hash"]) == 64
    assert len(stored_trace["signature"]) == 64
    assert json.loads(stored_trace["context"]) == {"capability": "invoke"}
    assert stored_trace["constellation_guardian_approved"] == 1
    assert stored_trace["constellation_identity_verified"] in (0, 1)
    assert stored_trace["constellation_consciousness_aligned"] in (0, 1)

    assert validation is not None
    assert validation["guardian_score"] == pytest.approx(1.0)
    assert validation["identity_score"] in {0.0, 1.0}
    assert validation["consciousness_score"] in {0.0, 1.0}
    assert validation["overall_score"] == pytest.approx(
        (validation["identity_score"] + validation["consciousness_score"] + 1.0) / 3
    )

    # ΛTAG: audit_trace_validation
