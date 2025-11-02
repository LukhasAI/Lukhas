"""Cross-jurisdiction compliance engine with automatic detection."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections.abc import Iterable, Mapping, MutableMapping

from .jurisdictions import CCPAModule, GDPRModule, LGPDModule, PIPEDAModule
from .jurisdictions.base import BaseJurisdictionModule
from .policy_engine import PolicyEngine, PolicyRecord

_CONSENT_PRIORITY = {
    "implied": 0,
    "opt_out": 1,
    "opt_in": 2,
    "explicit": 3,
}


@dataclass(frozen=True)
class JurisdictionDecision:
    """Represents a jurisdiction that applies to a user context."""

    code: str
    name: str
    reason: str
    weight: int
    version: Optional[str]
    history: Iterable[str]
    policy: Mapping[str, Any]


class MultiJurisdictionComplianceEngine:
    """Evaluate compliance obligations across multiple jurisdictions."""

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        jurisdiction_modules: Optional[Iterable[BaseJurisdictionModule]] = None,
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.policy_engine = policy_engine or PolicyEngine()
        self.jurisdiction_modules = list(jurisdiction_modules or self._default_modules())
        self._base_overrides = overrides or {}

        for module in self.jurisdiction_modules:
            if module.code not in self.policy_engine.list_codes():
                self.policy_engine.register_module(module)

    # ------------------------------------------------------------------
    @staticmethod
    def _default_modules() -> List[BaseJurisdictionModule]:
        return [
            GDPRModule(),
            CCPAModule(),
            PIPEDAModule(),
            LGPDModule(),
        ]

    # ------------------------------------------------------------------
    def detect_applicable_jurisdictions(self, user_data: Mapping[str, Any]) -> List[JurisdictionDecision]:
        """Detect all jurisdictions that apply to *user_data*."""

        decisions: List[JurisdictionDecision] = []
        per_j_overrides = self._resolve_overrides().get("jurisdictions", {})

        for module in self.jurisdiction_modules:
            signal = module.evaluate(dict(user_data))
            if not signal:
                continue

            policy_record = self.policy_engine.get_policy(module.code)
            policy_rules = self._apply_jurisdiction_overrides(policy_record, per_j_overrides.get(module.code))

            decisions.append(
                JurisdictionDecision(
                    code=module.code,
                    name=policy_record.metadata.get("name", module.name),
                    reason=signal.reason,
                    weight=signal.weight,
                    version=policy_record.metadata.get("version"),
                    history=tuple(policy_record.history),
                    policy=policy_rules,
                )
            )

        decisions.sort(key=lambda d: (-d.weight, d.code))
        return decisions

    # ------------------------------------------------------------------
    def get_effective_policy(
        self,
        user_data: Mapping[str, Any],
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Return the effective policy across all applicable jurisdictions."""

        decisions = self.detect_applicable_jurisdictions(user_data)
        aggregated = self._aggregate_policies(decisions)

        resolved_overrides = self._resolve_overrides(overrides)
        global_overrides = resolved_overrides.get("global")
        effective = copy.deepcopy(aggregated)
        PolicyEngine.apply_overrides(effective, copy.deepcopy(global_overrides) if global_overrides else None)

        return {
            "jurisdictions": decisions,
            "policy": effective,
        }

    # ------------------------------------------------------------------
    def _aggregate_policies(self, decisions: Iterable[JurisdictionDecision]) -> Dict[str, Any]:
        aggregated: Dict[str, Any] = {}
        for decision in decisions:
            for key, value in decision.policy.items():
                aggregator = getattr(self, f"_aggregate_{key}", None)
                if callable(aggregator):
                    aggregated[key] = aggregator(aggregated.get(key), value)
                else:
                    aggregated[key] = self._aggregate_default(aggregated.get(key), value)
        return aggregated

    @staticmethod
    def _aggregate_consent(current: Optional[str], new_value: Optional[str]) -> Optional[str]:
        if new_value is None:
            return current
        if current is None:
            return new_value
        return new_value if _CONSENT_PRIORITY.get(new_value, 0) >= _CONSENT_PRIORITY.get(current, 0) else current

    @staticmethod
    def _aggregate_data_retention_days(current: Optional[int], new_value: Optional[int]) -> Optional[int]:
        if new_value is None:
            return current
        if current is None:
            return new_value
        if new_value < 0:
            return current
        if current < 0:
            return new_value
        return min(current, new_value)

    @staticmethod
    def _aggregate_access_rights(current: Optional[Iterable[str]], new_value: Optional[Iterable[str]]) -> Iterable[str]:
        current_set = set(current or [])
        new_set = set(new_value or [])
        return current_set.union(new_set)

    @staticmethod
    def _aggregate_default(current: Any, new_value: Any) -> Any:
        if current is None:
            return copy.deepcopy(new_value)
        if isinstance(current, set):
            result = set(current)
            if isinstance(new_value, (set, list, tuple)):
                result.update(new_value)
            else:
                result.add(new_value)  # type: ignore[arg-type]
            return result
        if isinstance(new_value, set):
            result = set(new_value)
            if isinstance(current, (set, list, tuple)):
                result.update(current)
            else:
                result.add(current)  # type: ignore[arg-type]
            return result
        if current == new_value:
            return copy.deepcopy(current)
        return {str(current), str(new_value)}

    # ------------------------------------------------------------------
    def _resolve_overrides(self, overrides: Optional[Mapping[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        resolved: Dict[str, Dict[str, Any]] = {"global": {}, "jurisdictions": {}}
        for source in (self._base_overrides, overrides or {}):
            if not source:
                continue
            for key in ("global", "jurisdictions"):
                if key in source and isinstance(source[key], Mapping):
                    target = resolved[key]
                    for override_key, override_value in source[key].items():
                        if isinstance(override_value, Mapping):
                            nested = target.setdefault(override_key, {})
                            PolicyEngine.apply_overrides(nested, dict(override_value))
                        else:
                            target[override_key] = override_value
        return resolved

    @staticmethod
    def _apply_jurisdiction_overrides(record: PolicyRecord, overrides: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        policy_rules: MutableMapping[str, Any] = copy.deepcopy(dict(record.rules))
        if overrides:
            PolicyEngine.apply_overrides(policy_rules, dict(overrides))
        return dict(policy_rules)


__all__ = ["MultiJurisdictionComplianceEngine", "JurisdictionDecision"]
