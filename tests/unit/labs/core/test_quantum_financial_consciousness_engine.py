"""Tests for the labs quantum financial consciousness engine."""

import importlib.util
import math
import pathlib
from collections.abc import Iterable

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[4]
MODULE_PATH = PROJECT_ROOT / "labs" / "core" / "quantum_financial" / "quantum_financial_consciousness_engine.py"

_spec = importlib.util.spec_from_file_location(
    "labs.core.quantum_financial.quantum_financial_consciousness_engine", MODULE_PATH
)
engine = importlib.util.module_from_spec(_spec)
assert _spec is not None and _spec.loader is not None
_spec.loader.exec_module(engine)


def _expected_value(protocol: engine.ConsciousnessTokenProtocol, amount: float) -> float:
    normalized_amount = math.log1p(amount)
    resonance_multiplier = 1 + normalized_amount * protocol.resonance_curve
    return round(protocol.base_resonance + amount * resonance_multiplier, 6)


def _randint_sequence(values: Iterable[int]):
    iterator = iter(values)

    def _next(_low: int, _high: int) -> int:
        return next(iterator)

    return _next


def test_issue_tokens_uses_amount_for_consciousness_value(monkeypatch):
    protocol = engine.ConsciousnessTokenProtocol()
    monkeypatch.setattr(engine.random, "randint", _randint_sequence([1337]))

    token = protocol.issue_tokens(42.0)

    assert token["token_id"] == "token_1337"
    assert token["consciousness_value"] == pytest.approx(_expected_value(protocol, 42.0))


def test_issue_tokens_assigns_resonance_tier(monkeypatch):
    protocol = engine.ConsciousnessTokenProtocol()
    monkeypatch.setattr(engine.random, "randint", _randint_sequence([1111, 2222, 3333]))

    dormant = protocol.issue_tokens(0)
    spark = protocol.issue_tokens(12)
    radiant = protocol.issue_tokens(75)

    assert dormant["resonance_tier"] == "dormant"
    assert spark["resonance_tier"] == "spark"
    assert radiant["resonance_tier"] == "radiant"
    assert radiant["consciousness_value"] > spark["consciousness_value"] > dormant["consciousness_value"]


def test_issue_tokens_rejects_negative_amount():
    protocol = engine.ConsciousnessTokenProtocol()

    with pytest.raises(ValueError):
        protocol.issue_tokens(-1)
