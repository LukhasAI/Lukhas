"""LGPD jurisdiction module."""

from __future__ import annotations

from typing import Any

from .base import BaseJurisdictionModule, JurisdictionSignal


class LGPDModule(BaseJurisdictionModule):
    """Detect and define LGPD compliance obligations."""

    code = "LGPD"
    name = "Brazil General Data Protection Law"
    policy_version = "2024-08-20"

    def _evaluate(self, user_data: dict[str, Any]) -> JurisdictionSignal | None:
        ip_country = self._get_ip_country(user_data)
        account_country = self._get_account_country(user_data)
        data_countries = set(self._get_data_processing_countries(user_data))

        reasons = []
        if ip_country == "BR":
            reasons.append("ip:BR")
        if account_country == "BR":
            reasons.append("account:BR")
        if "BR" in data_countries:
            reasons.append("processing:BR")

        if reasons:
            return JurisdictionSignal(True, ";".join(reasons), weight=3)
        return JurisdictionSignal(False, "no_br_signals")

    def policy_definition(self) -> dict[str, Any]:
        """Return the LGPD base compliance policy."""

        return {
            "code": self.code,
            "name": self.name,
            "policy_version": self.policy_version,
            "consent": "explicit",
            "data_retention_days": 365,
            "access_rights": {
                "access",
                "rectification",
                "portability",
                "anonimization",
            },
            "data_localization": "BR-preferred",
        }


__all__ = ["LGPDModule"]
