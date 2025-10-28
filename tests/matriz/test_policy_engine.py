import pytest
from MATRIZ.runtime.policy import PolicyEngine

def test_policy_engine_uses_custom_evaluator_allows():
    recorded = []

    def evaluator(trigger):
        recorded.append(trigger.get('id'))
        return True
    engine = PolicyEngine(constitution_evaluator=evaluator)
    trigger = {'id': 'alpha'}
    assert engine.evaluate_trigger(trigger) is True
    assert recorded == ['alpha']

def test_policy_engine_blocks_when_evaluator_reports_violation():
    engine = PolicyEngine(constitution_evaluator=lambda _: False)
    assert engine.evaluate_trigger({}) is False

def test_policy_engine_string_rule_enforces_forbidden_label():
    engine = PolicyEngine(constitution_rules=['forbidden'], constitution_evaluator=lambda _: True)
    assert engine.evaluate_trigger({'constitution': ['allowed']}) is True
    assert engine.evaluate_trigger({'constitution': ['forbidden']}) is False

def test_policy_engine_requires_labels_when_marked():
    engine = PolicyEngine(constitution_rules=['require:guardian'], constitution_evaluator=lambda _: True)
    assert engine.evaluate_trigger({'constitution': ['guardian', 'ethics']}) is True
    assert engine.evaluate_trigger({'constitution': ['ethics']}) is False

def test_policy_engine_rejects_non_mapping_input():
    engine = PolicyEngine(constitution_evaluator=lambda _: True)
    with pytest.raises(TypeError):
        engine.evaluate_trigger('invalid')