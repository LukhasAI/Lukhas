from datetime import datetime, timezone

import pytest

from guardian.emit import emit_guardian_decision


class FakeDB:
    def __init__(self) -> None:
        self.calls = []

    def execute(self, query, params):
        self.calls.append((query, params))


def test_emit_guardian_decision_requires_consent_for_sensitive_tags():
    """PII/financial tags must include consent evidence."""

    with pytest.raises(ValueError):
        emit_guardian_decision(
            db=None,
            plan_id="plan-1",
            lambda_id="lambda",
            action="warn",
            rule_name="pii_rule",
            tags=["pii"],
            confidences={"pii": 0.9},
            band="high",
        )  # # ΛTAG: consent_guardrail


def test_emit_guardian_decision_serializes_consent_fields():
    """New consent fields are persisted alongside core ledger data."""

    db = FakeDB()
    consent_ts = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    emit_guardian_decision(
        db=db,
        plan_id="plan-2",
        lambda_id="lambda",
        action="warn",
        rule_name="finance_rule",
        tags=["financial"],
        confidences={"financial": 0.95},
        band="high",
        user_consent_timestamp=consent_ts,
        consent_method="explicit",
    )

    assert db.calls
    _, params = db.calls[0]
    assert params["consent_method"] == "explicit"
    assert params["user_consent_timestamp"].startswith(consent_ts.isoformat())
