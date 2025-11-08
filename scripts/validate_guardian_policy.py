#!/usr/bin/env python3
"""Basic schema validation for Guardian policy YAML."""

import json
import sys
from pathlib import Path
import yaml

ALLOWED_EFFECTS = {"allow", "deny"}


def _ensure_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("configs/policy/guardian_policies.yaml")
    if not path.exists():
        print(json.dumps({"ok": False, "errors": [f"{path} not found"]}, indent=2))
        return 1

    document = yaml.safe_load(path.read_text()) or {}
    raw_rules = document.get("rules") or []
    if not isinstance(raw_rules, list):
        raw_rules = [raw_rules]

    errors = []
    for idx, rule in enumerate(raw_rules):
        if not isinstance(rule, dict):
            errors.append(f"rule[{idx}]: expected mapping, got {type(rule).__name__}")
            continue

        rule_id = rule.get("id", f"rule:{idx}")

        effect = (rule.get("effect") or "deny").lower()
        if effect not in ALLOWED_EFFECTS:
            errors.append(f"{rule_id}: invalid effect '{rule.get('effect')}' (allowed: {sorted(ALLOWED_EFFECTS)})")

        actions = _ensure_list(rule.get("actions"))
        if not actions:
            errors.append(f"{rule_id}: actions must be a non-empty string or list of strings")
        elif not all(isinstance(a, str) for a in actions):
            errors.append(f"{rule_id}: actions must contain only strings")

        resources = _ensure_list(rule.get("resources"))
        if not resources:
            errors.append(f"{rule_id}: resources must be a non-empty string or list of strings")
        else:
            for resource in resources:
                if not isinstance(resource, str):
                    errors.append(f"{rule_id}: resource entries must be strings (got {type(resource).__name__})")
                elif not resource.startswith("/"):
                    errors.append(f"{rule_id}: resource must start with '/': {resource!r}")

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        return 1

    print(json.dumps({"ok": True, "rules": len(raw_rules)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
