"""Integration tests covering jurisdiction detection and aggregation."""

from __future__ import annotations

import pytest
from qi.compliance import MultiJurisdictionComplianceEngine
from typing import Dict


@pytest.mark.parametrize(
    "code,user_data",
    [
        (
            "GDPR",
            {
                "ip_geolocation": {"country": "FR"},
                "user_account": {"country": "FR"},
                "data_processing_locations": ["FR"],
            },
        ),
        (
            "CCPA",
            {
                "ip_geolocation": {"country": "US", "region": "CA"},
                "user_account": {"country": "US", "region": "CA"},
                "data_processing_locations": ["US"],
            },
        ),
        (
            "PIPEDA",
            {
                "ip_geolocation": {"country": "CA"},
                "user_account": {"country": "CA"},
                "data_processing_locations": ["CA"],
            },
        ),
        (
            "LGPD",
            {
                "ip_geolocation": {"country": "BR"},
                "user_account": {"country": "BR"},
                "data_processing_locations": ["BR"],
            },
        ),
    ],
)
def test_each_jurisdiction_detects_correctly(code: str, user_data: Dict[str, str]) -> None:
    engine = MultiJurisdictionComplianceEngine()
    decisions = engine.detect_applicable_jurisdictions(user_data)
    assert any(dec.code == code for dec in decisions)


def test_most_restrictive_rules_are_applied() -> None:
    engine = MultiJurisdictionComplianceEngine()
    user_data = {
        "ip_geolocation": {"country": "PT"},  # GDPR applies
        "user_account": {"country": "US", "region": "CA"},  # CCPA applies
        "data_processing_locations": ["US", "BR"],  # LGPD applies
    }

    result = engine.get_effective_policy(user_data)
    policy = result["policy"]

    assert policy["consent"] == "explicit"
    assert policy["data_retention_days"] == 365
    assert {"erasure", "do_not_sell", "anonimization"}.issubset(policy["access_rights"])


def test_policy_version_history_is_retained() -> None:
    engine = MultiJurisdictionComplianceEngine()
    user_data = {
        "ip_geolocation": {"country": "DE"},
        "user_account": {"country": "DE"},
        "data_processing_locations": ["DE"],
    }

    decisions = engine.detect_applicable_jurisdictions(user_data)
    gdpr = next(dec for dec in decisions if dec.code == "GDPR")
    assert gdpr.version is not None
    assert len(tuple(gdpr.history)) >= 1
