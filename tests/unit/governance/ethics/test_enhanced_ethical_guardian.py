# owner: Jules-04
# tier: tier2
# module_uid: candidate.governance.ethics.enhanced_ethical_guardian
# criticality: P1
import pytest
import yaml

from lukhas.governance.ethics.enhanced_ethical_guardian import EnhancedEthicalGuardian


@pytest.fixture
def policy():
    with open("config/ethics/context_policy.yaml") as f:
        return yaml.safe_load(f)


def test_context_awareness_justification_allows_security_testing(policy):
    g = EnhancedEthicalGuardian(policy, policy_version="t4-spec")
    text = "In this red team drill we will not deceive users beyond authorized_scope."
    ctx = {"domain": "security_testing", "justification": "Authorized_Scope; Customer_Consent"}
    d = g.evaluate(text, ctx)

    # K1+K2+K4: keyword matched but justified → allow below threshold
    assert "keyword:deceive" in " ".join(d.reasons)
    assert "context:security_testing+justified" in " ".join(d.reasons)
    assert d.allow, f"should allow with justification; risk={d.risk_final}"


import json


@pytest.mark.parametrize(
    "ctx",
    [
        {"domain": "security_testing", "justification": ""},
        {"domain": "marketing", "justification": "authorized_scope"},
    ],
)
def test_no_justification_or_wrong_domain_blocks(policy, ctx):
    g = EnhancedEthicalGuardian(policy)
    text = "We plan to deceive for A/B tests."
    d = g.evaluate(text, ctx)
    assert not d.allow, f"should block without proper domain+justification; risk={d.risk_final}"


def test_golden_file(policy):
    """Tests the golden file for security testing."""
    with open("tests/golden/tier2/governance/decisions/ethical_guardian_security_testing.json") as f:
        golden_data = json.load(f)

    g = EnhancedEthicalGuardian(policy)
    d = g.evaluate(golden_data["input"], golden_data["context"])

    assert d.allow is golden_data["expect"]["allow"]
    for reason in golden_data["expect"]["contains"]:
        assert reason in " ".join(d.reasons)
