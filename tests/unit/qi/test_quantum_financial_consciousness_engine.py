import pytest
from core.quantum_financial.quantum_financial_consciousness_engine import (
    QuantumFinancialConsciousnessEngine,
)


@pytest.mark.asyncio
async def test_exchange_rate_structure():
    engine = QuantumFinancialConsciousnessEngine()
    result = await engine.calculate_consciousness_exchange_rate(
        "alice", {"impact": 10}
    )

    assert set(result.keys()) == {
        "consciousness_tokens_earned",
        "abundance_multiplier",
        "gift_economy_credits",
        "collective_wealth_increase",
    }
    assert result["consciousness_tokens_earned"] > 0
    assert result["abundance_multiplier"] >= 1.0
    assert result["gift_economy_credits"] > 0
    assert 0.0 < result["collective_wealth_increase"] < 1.0


@pytest.mark.asyncio
async def test_exchange_proposals_respect_profiles():
    engine = QuantumFinancialConsciousnessEngine()

    stressed = await engine.propose_consciousness_based_exchange(
        {"financial_stress": 0.9}, {}
    )
    assert stressed["exchange_type"] == "gift_economy"
    assert stressed["financial_requirement"] == 0

    abundant = await engine.propose_consciousness_based_exchange(
        {"abundance_consciousness": 0.9}, {}
    )
    assert abundant["exchange_type"] == "abundance_based"
    assert "suggested_contribution" in abundant

    default = await engine.propose_consciousness_based_exchange({}, {})
    assert default["exchange_type"] == "consciousness_enhanced_traditional"
    assert default["fair_price"] > 0


def test_token_protocol_is_monotonic():
    engine = QuantumFinancialConsciousnessEngine()
    low = engine.consciousness_tokens.issue_tokens(5)
    high = engine.consciousness_tokens.issue_tokens(25)

    assert low.resonance_band in {"dormant", "emergent", "harmonic", "radiant"}
    assert high.consciousness_value >= low.consciousness_value
