"""Unit tests for the Quantum Financial Consciousness Engine."""
from __future__ import annotations

import random

import pytest
from labs.core.qi_financial.quantum_financial_consciousness_engine import (
    AbundanceCalculator,
    ConsciousnessExchangeProposal,
    ConsciousnessTokenProtocol,
    GiftEconomyEngine,
    QuantumFinancialConsciousnessEngine,
)


@pytest.mark.asyncio
async def test_abundance_calculator_calculates_impact():
    """Test AbundanceCalculator calculates abundance impact correctly."""
    # Arrange
    calculator = AbundanceCalculator(rng=random.Random(42))
    contribution = {
        "impact": 10.0,
        "collective_benefit": 5.0,
        "awareness_level": 1.2,
    }

    # Act
    impact = await calculator.calculate_abundance_impact(contribution)

    # Assert
    assert isinstance(impact, float)
    assert impact > 0
    # Expected: log1p(15) * 1.2 + 1.0 + noise(0.05, 0.15)
    # With seed 42, noise is ~0.114
    # Expected: ~4.4410
    assert impact == pytest.approx(4.441049, abs=1e-4)


def test_consciousness_token_protocol_issues_tokens():
    """Test ConsciousnessTokenProtocol issues tokens."""
    # Arrange
    protocol = ConsciousnessTokenProtocol(rng_or_bias=random.Random(42))

    # Act
    token = protocol.issue_tokens(100.0)

    # Assert
    assert token.consciousness_value == pytest.approx(7.46, abs=1e-2)
    assert token.resonance_band == "radiant"
    assert token.token_id.startswith("token_")


def test_consciousness_token_protocol_handles_zero_amount():
    """Test ConsciousnessTokenProtocol handles zero amount correctly."""
    # Arrange
    protocol = ConsciousnessTokenProtocol(rng_or_bias=random.Random(42))

    # Act
    token = protocol.issue_tokens(0.0)

    # Assert
    assert token.consciousness_value == 0.0
    assert token.resonance_band == "dormant"


def test_consciousness_token_protocol_resonance_bands():
    """Test that resonance bands are assigned correctly."""
    # Using a bias of 1 to make thresholds easy to reason about.
    protocol = ConsciousnessTokenProtocol(resonance_bias=1.0)

    # consciousness_value = log1p(amount) * 1.0

    # log1p(0) = 0 -> dormant
    token_dormant = protocol.issue_tokens(0)
    assert token_dormant.resonance_band == "dormant"
    assert token_dormant.consciousness_value == 0

    # log1p(1) = 0.69 < 1.0 -> emergent
    token_emergent = protocol.issue_tokens(1)
    assert token_emergent.resonance_band == "emergent"
    assert 0 < token_emergent.consciousness_value < 1.0

    # log1p(e - 1) approx 1.0 -> harmonic
    # Using a value slightly greater than e-1 to ensure it crosses the threshold
    token_harmonic = protocol.issue_tokens(1.7183)
    assert token_harmonic.resonance_band == "harmonic"
    assert token_harmonic.consciousness_value == pytest.approx(1.0, abs=1e-5)

    # log1p(e^2 - 1) approx 2.0 -> radiant
    token_radiant = protocol.issue_tokens(6.3891)
    assert token_radiant.resonance_band == "radiant"
    assert token_radiant.consciousness_value == pytest.approx(2.0, abs=1e-5)


@pytest.mark.asyncio
async def test_gift_economy_engine_calculates_value():
    """Test GiftEconomyEngine calculates gift value correctly."""
    # Arrange
    engine = GiftEconomyEngine(rng=random.Random(42))
    contribution = {
        "value": 10.0,
        "love_index": 0.8,
        "reciprocity": 0.7,
        "community_alignment": 0.9,
    }

    # Act
    value = await engine.calculate_gift_value(contribution)

    # Assert
    # Expected: 10 * (1 + (0.8+0.7+0.9)/3) + 10 + noise(0,5)
    # With seed 42, noise is ~3.197
    # Expected: ~31.197
    assert value == pytest.approx(31.1971, abs=1e-2)


@pytest.mark.asyncio
async def test_qfce_calculate_exchange_rate():
    """Test QuantumFinancialConsciousnessEngine calculates exchange rate."""
    # Arrange
    engine = QuantumFinancialConsciousnessEngine(seed=42)
    contribution = {"impact": 20.0, "collective_benefit": 10.0}

    # Act
    rate = await engine.calculate_consciousness_exchange_rate("user123", contribution)

    # Assert
    assert rate.consciousness_tokens_earned > 0
    assert rate.abundance_multiplier > 0
    assert rate.gift_economy_credits > 0
    assert rate.collective_wealth_increase > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "profile, product_values, expected_proposal",
    [
        (
            {"financial_stress": 0.7},
            {"base_value": 10.0},
            ConsciousnessExchangeProposal(
                exchange_type="gift_economy",
                proposal="This would support your growth. The collective provides it freely.",
                financial_requirement=0,
            ),
        ),
        (
            {"abundance_consciousness": 0.9},
            {"base_value": 10.0, "depth": 0.8, "rarity": 0.8, "mission_alignment": 0.8},
            ConsciousnessExchangeProposal(
                exchange_type="abundance_based",
                proposal="Invest in consciousness evolution for yourself and others.",
                suggested_contribution=13.0,
            ),
        ),
        (
            {},
            {"base_value": 10.0, "depth": 0.5, "rarity": 0.5, "mission_alignment": 0.5},
            ConsciousnessExchangeProposal(
                exchange_type="consciousness_enhanced_traditional",
                proposal="Align contribution with consciousness resonance for mutual growth.",
                fair_price=10.0,
            ),
        ),
    ],
)
async def test_qfce_propose_exchange(profile, product_values, expected_proposal):
    """Test QuantumFinancialConsciousnessEngine proposes different exchanges."""
    # Arrange
    engine = QuantumFinancialConsciousnessEngine(seed=42)

    # Act
    proposal = await engine.propose_consciousness_based_exchange(profile, product_values)

    # Assert
    assert proposal == expected_proposal
