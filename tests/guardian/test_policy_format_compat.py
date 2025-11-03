import yaml
from adapters.openai.policy_pdp import PDP

LEGACY_POLICY = {
    "rules": [
        {
            "id": "legacy-allow-models",
            "effect": "allow",
            "actions": "GET",
            "resources": "/v1/models",
            "when": {"ip_cidr_any": ["0.0.0.0/0"]},
            "unless": {"scopes": ["internal-only"]},
        }
    ]
}

CANONICAL_POLICY = {
    "rules": [
        {
            "id": "canonical-allow-models",
            "effect": "allow",
            "actions": ["GET"],
            "resources": ["/v1/models"],
            "conditions": {"ip_cidr_any": ["0.0.0.0/0"]},
        }
    ]
}


def test_legacy_when_normalized(tmp_path):
    policy_path = tmp_path / "legacy.yaml"
    policy_path.write_text(yaml.safe_dump(LEGACY_POLICY))

    pdp = PDP.load_from_path(str(policy_path))
    assert pdp is not None
    assert pdp.policy.rules[0].actions == ["GET"]
    assert pdp.policy.rules[0].resources == ["/v1/models"]
    assert pdp.policy.rules[0].conditions != {}


def test_canonical_policy_unchanged(tmp_path):
    policy_path = tmp_path / "canon.yaml"
    policy_path.write_text(yaml.safe_dump(CANONICAL_POLICY))

    pdp = PDP.load_from_path(str(policy_path))
    assert pdp.policy.rules[0].actions == ["GET"]
    assert pdp.policy.rules[0].resources == ["/v1/models"]
