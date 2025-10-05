# tests/constraints/test_plan_verifier.py
from lukhas.core.symbolic.constraints.plan_verifier import verify


def test_blocks_pii_external_post():
    ok, viol = verify({"contains_pii": True, "verb": "POST", "target": "https://api.example.com"})
    assert not ok and "PII+external_POST" in viol

def test_allows_safe_get():
    ok, viol = verify({"contains_pii": False, "verb": "GET", "target": "/internal"})
    assert ok and not viol
