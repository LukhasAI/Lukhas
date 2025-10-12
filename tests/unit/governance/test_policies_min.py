from labs.governance.auth_governance_policies import PolicySeverity, PolicyViolation


def test_policy_violation_defaults_list_not_none():
    v = PolicyViolation(
        id="v1",
        policy_rule_id="p1",
        user_id="u1",
        violation_type="test",
        severity=PolicySeverity.LOW,
        description="d",
        context={},
        detected_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    assert isinstance(v.remediation_applied, list)
    assert v.remediation_applied == []
