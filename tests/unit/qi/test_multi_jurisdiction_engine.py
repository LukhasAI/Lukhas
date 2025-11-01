"""Unit tests for the MultiJurisdictionComplianceEngine."""

from __future__ import annotations

from qi.compliance import MultiJurisdictionComplianceEngine


def _engine(overrides=None):
    return MultiJurisdictionComplianceEngine(overrides=overrides)


def test_detects_multiple_jurisdictions():
    engine = _engine()
    user_data = {
        "ip_geolocation": {"country": "DE"},
        "user_account": {"country": "US", "region": "CA"},
        "data_processing_locations": ["US", "DE"],
    }

    result = engine.get_effective_policy(user_data)

    jurisdictions = {decision.code for decision in result["jurisdictions"]}
    assert jurisdictions == {"GDPR", "CCPA"}
    assert result["policy"]["consent"] == "explicit"
    assert result["policy"]["data_retention_days"] == 365
    assert {"access", "rectification"}.issubset(result["policy"]["access_rights"])


def test_policy_overrides_apply():
    overrides = {
        "global": {"data_retention_days": 180},
        "jurisdictions": {"CCPA": {"consent": "explicit"}},
    }
    engine = _engine(overrides=overrides)
    user_data = {
        "ip_geolocation": {"country": "US", "region": "CA"},
        "user_account": {"country": "US", "region": "CA"},
        "data_processing_locations": ["US"],
    }

    result = engine.get_effective_policy(user_data)
    decision = next(dec for dec in result["jurisdictions"] if dec.code == "CCPA")

    assert result["policy"]["data_retention_days"] == 180
    assert decision.policy["consent"] == "explicit"


def test_no_matching_jurisdiction_returns_empty():
    engine = _engine()
    user_data = {
        "ip_geolocation": {"country": "IN"},
        "user_account": {"country": "IN"},
        "data_processing_locations": ["IN"],
    }

    result = engine.get_effective_policy(user_data)
    assert result["jurisdictions"] == []
    assert result["policy"] == {}
