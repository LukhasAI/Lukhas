
"""Utility module applying community proposals to ethics configuration."""

import json
from pathlib import Path

# TAG:governance
# TAG:policy
# TAG:neuroplastic
# TAG:colony


POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "ethics" / "community_rules.json"


def load_rules() -> dict:
    if POLICY_PATH.exists():
        return json.loads(POLICY_PATH.read_text())
return {}


def save_rules(rules: dict) -> None:
    POLICY_PATH.write_text(json.dumps(rules, indent=2))


def apply_proposal(execution_data: dict) -> None:
    load_rules()
rules.update(execution_data)
save_rules(rules)