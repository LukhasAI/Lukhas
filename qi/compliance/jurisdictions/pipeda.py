"""PIPEDA jurisdiction module."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseJurisdictionModule, JurisdictionSignal


class PIPEDAModule(BaseJurisdictionModule):
    """Detect and define PIPEDA compliance obligations."""

    code = "PIPEDA"
    name = "Canada Personal Information Protection and Electronic Documents Act"
    policy_version = "2024-09-15"

    def _evaluate(self, user_data: Dict[str, Any]) -> Optional[JurisdictionSignal]:
        ip_country = self._get_ip_country(user_data)
        account_country = self._get_account_country(user_data)
        data_countries = set(self._get_data_processing_countries(user_data))

        reasons = []
        if ip_country == "CA":
            reasons.append("ip:CA")
        if account_country == "CA":
            reasons.append("account:CA")
        if "CA" in data_countries:
            reasons.append("processing:CA")

        if reasons:
            return JurisdictionSignal(True, ";".join(reasons), weight=3)
        return JurisdictionSignal(False, "no_ca_signals")

    def policy_definition(self) -> Dict[str, Any]:
        """Return the PIPEDA base compliance policy."""

        return {
            "code": self.code,
            "name": self.name,
            "policy_version": self.policy_version,
            "consent": "opt_in",
            "data_retention_days": 548,
            "access_rights": {
                "access",
                "rectification",
                "complaint",
            },
            "data_localization": "CA-preferred",
        }


__all__ = ["PIPEDAModule"]
