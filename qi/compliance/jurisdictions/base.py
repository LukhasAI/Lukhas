"""Base classes and utilities for jurisdiction modules."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class JurisdictionSignal:
    """Information returned by a jurisdiction module when it applies."""

    applies: bool
    reason: str
    weight: int = 0


class BaseJurisdictionModule:
    """Interface for jurisdiction detection and policy metadata."""

    code: str = ""
    name: str = ""
    policy_version: str = ""
    supported_countries: Iterable[str] = ()

    def evaluate(self, user_data: Dict[str, Any]) -> Optional[JurisdictionSignal]:
        """Return a signal when the jurisdiction applies to *user_data*."""

        signal = self._evaluate(user_data)
        if signal and signal.applies:
            return signal
        return None

    # NOTE: Implementers should override this method.
    def _evaluate(self, user_data: Dict[str, Any]) -> Optional[JurisdictionSignal]:
        raise NotImplementedError

    # Helper accessors -----------------------------------------------------
    @staticmethod
    def _get_ip_country(user_data: Dict[str, Any]) -> Optional[str]:
        ip_info = user_data.get("ip_geolocation") or {}
        country = ip_info.get("country")
        if country:
            return country.upper()
        return None

    @staticmethod
    def _get_ip_region(user_data: Dict[str, Any]) -> Optional[str]:
        ip_info = user_data.get("ip_geolocation") or {}
        region = ip_info.get("region")
        if region:
            return region.upper()
        return None

    @staticmethod
    def _get_account_country(user_data: Dict[str, Any]) -> Optional[str]:
        account = user_data.get("user_account") or {}
        country = account.get("country") or account.get("country_code")
        if country:
            return country.upper()
        return None

    @staticmethod
    def _get_account_region(user_data: Dict[str, Any]) -> Optional[str]:
        account = user_data.get("user_account") or {}
        region = account.get("region") or account.get("state")
        if region:
            return region.upper()
        return None

    @staticmethod
    def _get_data_processing_countries(user_data: Dict[str, Any]) -> Iterable[str]:
        locations = user_data.get("data_processing_locations") or []
        for item in locations:
            if not item:
                continue
            yield str(item).upper()

    def policy_definition(self) -> Dict[str, Any]:
        """Return the jurisdiction's base policy definition."""

        raise NotImplementedError


__all__ = ["BaseJurisdictionModule", "JurisdictionSignal"]
