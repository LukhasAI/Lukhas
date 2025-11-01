"""CCPA jurisdiction module."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import BaseJurisdictionModule, JurisdictionSignal


class CCPAModule(BaseJurisdictionModule):
    """Detect and define CCPA compliance obligations."""

    code = "CCPA"
    name = "California Consumer Privacy Act"
    policy_version = "2024-10-01"

    def _evaluate(self, user_data: Dict[str, Any]) -> Optional[JurisdictionSignal]:
        ip_country = self._get_ip_country(user_data)
        ip_region = self._get_ip_region(user_data)
        account_country = self._get_account_country(user_data)
        account_region = self._get_account_region(user_data)
        data_countries = set(self._get_data_processing_countries(user_data))

        reasons = []
        if ip_country == "US" and ip_region == "CA":
            reasons.append("ip:US-CA")
        if account_country == "US" and account_region == "CA":
            reasons.append("account:US-CA")
        if "US" in data_countries:
            reasons.append("processing:US")

        if reasons:
            return JurisdictionSignal(True, ";".join(reasons), weight=4)
        return JurisdictionSignal(False, "no_ca_signals")

    def policy_definition(self) -> Dict[str, Any]:
        """Return the CCPA base compliance policy."""

        return {
            "code": self.code,
            "name": self.name,
            "policy_version": self.policy_version,
            "consent": "opt_out",
            "data_retention_days": 730,
            "access_rights": {
                "access",
                "deletion",
                "do_not_sell",
                "non_discrimination",
            },
            "data_localization": "US-required",
        }


__all__ = ["CCPAModule"]
