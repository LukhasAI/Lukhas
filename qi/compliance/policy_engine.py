"""Composable policy evaluation engine for jurisdictional compliance."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None  # type: ignore


@dataclass(frozen=True)
class PolicyRecord:
    """Represents a policy registered in the engine."""

    metadata: Mapping[str, Any]
    rules: Mapping[str, Any]
    history: Iterable[str]


class PolicyEngine:
    """Rule evaluation engine backed by declarative policy definitions."""

    def __init__(self) -> None:
        self._policies: dict[str, PolicyRecord] = {}
        self._history: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    def register_policy(self, code: str, policy: Mapping[str, Any], version: str | None = None) -> None:
        """Register or update a policy for *code*.

        Parameters
        ----------
        code:
            Jurisdiction or policy identifier.
        policy:
            Declarative policy definition (dict-like). Metadata keys such as
            ``code``, ``name`` and ``policy_version`` are preserved.
        version:
            Optional override for the policy version metadata.
        """

        if not code:
            raise ValueError("policy code is required")

        policy_dict = dict(policy)
        metadata = {
            "code": code,
            "name": policy_dict.get("name", code),
        }
        effective_version = version or policy_dict.get("policy_version")
        if effective_version:
            metadata["version"] = str(effective_version)

        history = self._history.setdefault(code, [])
        if effective_version:
            if not history or history[-1] != effective_version:
                history.append(str(effective_version))
        elif not history:
            history.append("unversioned")

        rules = self._normalise_rules(policy_dict)
        self._policies[code] = PolicyRecord(metadata=metadata, rules=rules, history=tuple(history))

    def register_module(self, module: Any) -> None:
        """Register the policy supplied by a jurisdiction module."""

        policy = module.policy_definition()
        self.register_policy(module.code, policy, version=module.policy_version)

    def load_from_yaml(self, code: str, yaml_definition: str) -> None:
        """Register a policy from a YAML document."""

        if yaml is None:  # pragma: no cover - executed only without PyYAML
            raise RuntimeError("PyYAML is required to load policies from YAML")
        data = yaml.safe_load(yaml_definition)
        if not isinstance(data, Mapping):
            raise ValueError("YAML policy must evaluate to a mapping")
        self.register_policy(code, data)

    # ------------------------------------------------------------------
    def get_policy(self, code: str) -> PolicyRecord:
        try:
            record = self._policies[code]
        except KeyError as exc:  # pragma: no cover - defensive branch
            raise KeyError(f"policy not registered: {code}") from exc
        return PolicyRecord(
            metadata=copy.deepcopy(dict(record.metadata)),
            rules=copy.deepcopy(dict(record.rules)),
            history=tuple(record.history),
        )

    def list_codes(self) -> list[str]:
        return sorted(self._policies)

    # ------------------------------------------------------------------
    @staticmethod
    def apply_overrides(base: MutableMapping[str, Any], overrides: Mapping[str, Any] | None) -> MutableMapping[str, Any]:
        """Return *base* merged with *overrides* (non-destructive)."""

        if not overrides:
            return base

        def _merge(target: MutableMapping[str, Any], override_value: Any, key_path: str) -> None:
            if isinstance(override_value, Mapping):
                nested = target.setdefault(key_path, {}) if key_path not in target else target[key_path]
                if not isinstance(nested, MutableMapping):
                    raise ValueError(f"Override conflict at '{key_path}'")
                for nested_key, nested_value in override_value.items():
                    _merge(nested, nested_value, nested_key)
            else:
                target[key_path] = override_value

        for key, value in overrides.items():
            if isinstance(value, Mapping):
                target = base.setdefault(key, {}) if key not in base else base[key]
                if not isinstance(target, MutableMapping):
                    raise ValueError(f"Override conflict at '{key}'")
                for nested_key, nested_value in value.items():
                    _merge(target, nested_value, nested_key)
            else:
                base[key] = value

        return base

    # ------------------------------------------------------------------
    @staticmethod
    def _normalise_rules(policy_dict: Mapping[str, Any]) -> dict[str, Any]:
        normalised: dict[str, Any] = {}
        for key, value in policy_dict.items():
            if key in {"code", "name", "policy_version"}:
                continue
            if key == "access_rights":
                normalised[key] = set(value) if value is not None else set()
            else:
                normalised[key] = value
        return normalised


__all__ = ["PolicyEngine", "PolicyRecord"]
