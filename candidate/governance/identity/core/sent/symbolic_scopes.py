"""Symbolic consent scope management utilities for ΛSENT."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


class SymbolicScopesManager:
    """Manage symbolic consent scopes across the ecosystem."""

    def __init__(self, config):
        self.config = config or {}
        self.scope_symbols = {
            "replay": "🔄",
            "memory": "🧠",
            "biometric": "👁️",
            "location": "📍",
            "audio": "🎵",
            "analytics": "📊",
            "integration": "🔗",
            "trace": "👁️‍🗨️",
            "tier_progression": "⬆️",
        }
        self.scope_hierarchy: dict[str, dict[str, Any]] = {}
        self.symbol_to_scope: dict[str, str] = {}

        self.tier_boundaries, self.validation_rules = self._load_tier_boundaries()
        self._initialize_scope_metadata()

    def define_scope(
        self,
        scope_name: str,
        symbol: str,
        description: str,
        tier_requirements: dict | None,
    ) -> None:
        """Define a new consent scope with symbolic representation."""

        requirements = tier_requirements or {}
        # ΛTAG: consent_scope_definition
        self.scope_symbols[scope_name] = symbol
        self.scope_hierarchy[scope_name] = {
            "symbol": symbol,
            "description": description,
            "tier_requirements": requirements,
        }
        self.symbol_to_scope[symbol] = scope_name

    def get_scope_requirements(self, scope_name: str, user_tier: int) -> dict[str, Any]:
        """Get consent requirements for scope based on user tier."""

        tier_key = f"tier_{user_tier}"
        tier_data = self.tier_boundaries.get(tier_key, {})
        available_scopes = set(tier_data.get("available_scopes", []))
        restricted_scopes = set(tier_data.get("restricted_scopes", []))

        scope_meta = self.scope_hierarchy.get(scope_name)
        if scope_meta is None and scope_name in self.scope_symbols:
            self.scope_hierarchy[scope_name] = {
                "symbol": self.scope_symbols[scope_name],
                "description": "",
                "tier_requirements": {},
            }
            scope_meta = self.scope_hierarchy[scope_name]

        requirements: dict[str, Any] = {}
        meta_requirements = (scope_meta or {}).get("tier_requirements", {})
        if isinstance(meta_requirements, dict):
            if tier_key in meta_requirements:
                requirements.update(meta_requirements[tier_key])
            else:
                requirements.update(meta_requirements)

        tier_specific = tier_data.get("consent_requirements", {}).get(scope_name, {})
        requirements.update(tier_specific)

        overrides = self.config.get("scope_overrides", {}).get(scope_name, {})
        if isinstance(overrides, dict):
            if tier_key in overrides:
                requirements.update(overrides[tier_key])
            else:
                requirements.update(overrides)

        immutable_scopes = set(self.validation_rules.get("immutable_scopes", []))
        if scope_name in immutable_scopes:
            requirements["required"] = True
            requirements["revocable"] = False

        required = bool(
            requirements.get("required", scope_name in tier_data.get("consent_requirements", {}))
        )
        revocable = bool(requirements.get("revocable", scope_name not in immutable_scopes))

        # ΛTAG: consent_requirement_mapping
        return {
            "scope": scope_name,
            "symbol": (scope_meta or {}).get("symbol", self.scope_symbols.get(scope_name, "❓")),
            "description": (scope_meta or {}).get("description", ""),
            "tier": user_tier,
            "available": scope_name in available_scopes if tier_data else scope_name in self.scope_symbols,
            "restricted": scope_name in restricted_scopes,
            "requirements": requirements,
            "required": required,
            "revocable": revocable,
        }

    def validate_scope_access(self, user_id: str, scope_name: str) -> bool:
        """Validate if user has access to consent scope."""

        user_tier = self._resolve_user_tier(user_id)
        info = self.get_scope_requirements(scope_name, user_tier)
        if not info["available"] or info["restricted"]:
            return False

        granted_registry = self.config.get("granted_scopes")
        if granted_registry is not None:
            user_grants = granted_registry.get(user_id, [])
            if info["required"]:
                return scope_name in user_grants
            if user_grants:
                return scope_name in user_grants
            return not info["required"]

        validator: Callable[[str, str, dict[str, Any]], bool] | None = self.config.get(
            "scope_validator"
        )
        if callable(validator):
            # ΛTAG: tier_boundary_validation
            return bool(validator(user_id, scope_name, info))

        return True

    def get_symbolic_representation(self, consented_scopes: list) -> str:
        """Generate symbolic representation of consented scopes."""

        symbols = [self.scope_symbols.get(scope, "❓") for scope in consented_scopes]
        return "".join(symbols)

    def parse_symbolic_consent(self, symbolic_string: str) -> list[str]:
        """Parse symbolic consent string back to scope list."""

        if not symbolic_string:
            return []

        parsed: list[str] = []
        pointer = 0
        ordered_symbols = sorted(
            self.symbol_to_scope.items(), key=lambda item: len(item[0]), reverse=True
        )

        # ΛTAG: symbolic_parse
        while pointer < len(symbolic_string):
            for symbol, scope in ordered_symbols:
                if symbolic_string.startswith(symbol, pointer):
                    parsed.append(scope)
                    pointer += len(symbol)
                    break
            else:
                pointer += 1

        return parsed

    def _load_tier_boundaries(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Load tier boundary configuration from consent_tiers.json or overrides."""

        config_path = self.config.get("consent_tiers_path")
        if config_path:
            path = Path(config_path)
        else:
            path = Path(__file__).with_name("consent_tiers.json")

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}, {}
        except json.JSONDecodeError:
            return {}, {}

        return (
            data.get("tier_consent_boundaries", {}),
            data.get("consent_validation_rules", {}),
        )

    def _initialize_scope_metadata(self) -> None:
        """Populate scope hierarchy and symbol lookups."""

        descriptions = self.config.get("scope_descriptions", {})
        requirements = self.config.get("scope_requirements", {})

        for scope_name, symbol in list(self.scope_symbols.items()):
            self.scope_hierarchy.setdefault(
                scope_name,
                {
                    "symbol": symbol,
                    "description": descriptions.get(scope_name, ""),
                    "tier_requirements": requirements.get(scope_name, {}),
                },
            )
            self.symbol_to_scope[symbol] = scope_name

        for definition in self.config.get("additional_scopes", []):
            if not isinstance(definition, dict):
                continue
            name = definition.get("name")
            symbol = definition.get("symbol")
            if not name or not symbol:
                continue
            self.define_scope(
                name,
                symbol,
                definition.get("description", ""),
                definition.get("tier_requirements", {}),
            )

    def _resolve_user_tier(self, user_id: str) -> int:
        """Resolve a user's tier using provided configuration."""

        resolver: Callable[[str], int] | None = self.config.get("tier_resolver")
        if callable(resolver):
            try:
                # ΛTAG: tier_lookup
                return int(resolver(user_id))
            except Exception:
                return int(self.config.get("default_tier", 0))

        user_tiers = self.config.get("user_tiers", {})
        return int(user_tiers.get(user_id, self.config.get("default_tier", 0)))
