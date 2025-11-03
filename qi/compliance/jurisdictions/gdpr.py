"""GDPR jurisdiction module."""

from __future__ import annotations

from typing import Any, Dict

from .base import BaseJurisdictionModule, JurisdictionSignal

_EU_COUNTRIES = {
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
}


class GDPRModule(BaseJurisdictionModule):
    """Detect and define GDPR compliance obligations."""

    code = "GDPR"
    name = "EU General Data Protection Regulation"
    policy_version = "2024-11-01"
    supported_countries = tuple(sorted(_EU_COUNTRIES))

    def _evaluate(self, user_data: Dict[str, Any]) -> JurisdictionSignal | None:
        ip_country = self._get_ip_country(user_data)
        account_country = self._get_account_country(user_data)
        data_countries = set(self._get_data_processing_countries(user_data))

        reasons = []
        if ip_country in _EU_COUNTRIES:
            reasons.append(f"ip:{ip_country}")
        if account_country in _EU_COUNTRIES:
            reasons.append(f"account:{account_country}")
        eu_processing = sorted(data_countries.intersection(_EU_COUNTRIES))
        if eu_processing:
            reasons.append(f"processing:{','.join(eu_processing)}")

        if reasons:
            return JurisdictionSignal(True, ";".join(reasons), weight=5)
        return JurisdictionSignal(False, "no_eu_signals")

    def policy_definition(self) -> Dict[str, Any]:
        """Return the GDPR base compliance policy."""

        return {
            "code": self.code,
            "name": self.name,
            "policy_version": self.policy_version,
            "consent": "explicit",
            "data_retention_days": 365,
            "access_rights": {
                "access",
                "rectification",
                "erasure",
                "restriction",
                "portability",
                "objection",
            },
            "data_localization": "EU-preferred",
        }


__all__ = ["GDPRModule"]
