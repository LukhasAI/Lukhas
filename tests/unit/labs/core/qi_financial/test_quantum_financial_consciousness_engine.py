"""Unit tests for the Quantum Financial Consciousness Engine."""

import pytest
import random
from labs.core.qi_financial.quantum_financial_consciousness_engine import (
    AbundanceCalculator,
    ConsciousnessTokenProtocol,
    GiftEconomyEngine,
    QuantumFinancialConsciousnessEngine,
)


@pytest.mark.asyncio
async def test_abundance_calculator_basic():
    """Test AbundanceCalculator with a basic contribution."""
    rng = random.Random(42)
    calculator = AbundanceCalculator(rng)
    contribution = {"impact": 10, "collective_benefit": 5, "awareness_level": 1.2}
    result = await calculator.calculate_abundance_impact(contribution)
    # Expected: 1.0 + log1p(15) * 1.2 + rng.uniform(0.05, 0.15)
    # log1p(15) is approx 2.7725887
    # base_multiplier = 1.0 + 2.7725887 * 1.2 = 4.327106
    # rng.uniform(0.05, 0.15) with seed 42 is ~0.113943
    # Expected result = 4.327106 + 0.113943 = 4.441049
    assert result == pytest.approx(4.441049, abs=1e-6)


@pytest.mark.asyncio
async def test_abundance_calculator_zero_contribution():
    """Test AbundanceCalculator with zero contribution."""
    rng = random.Random(42)
    calculator = AbundanceCalculator(rng)
    contribution = {"impact": 0, "collective_benefit": 0, "awareness_level": 1.0}
    result = await calculator.calculate_abundance_impact(contribution)
    # Expected: 1.0 + log1p(0) * 1.0 + rng.uniform(0.05, 0.15)
    # base_multiplier = 1.0
    # rng.uniform(0.05, 0.15) with seed 42 is ~0.113943
    # Expected result = 1.0 + 0.113943 = 1.113943
    assert result == pytest.approx(1.113943, abs=1e-6)


def test_consciousness_token_protocol_deterministic():
    """Test that ConsciousnessTokenProtocol is deterministic."""
    protocol1 = ConsciousnessTokenProtocol(rng_or_bias=random.Random(42))
    protocol2 = ConsciousnessTokenProtocol(rng_or_bias=random.Random(42))
    token1 = protocol1.issue_tokens(100)
    token2 = protocol2.issue_tokens(100)
    assert token1.token_id == token2.token_id
    assert token1.consciousness_value == token2.consciousness_value
    assert token1.resonance_band == token2.resonance_band


def test_consciousness_token_protocol_resonance_bands():
    """Test resonance band assignments in ConsciousnessTokenProtocol."""
    protocol = ConsciousnessTokenProtocol()
    assert protocol.issue_tokens(0).resonance_band == "dormant"
    assert protocol.issue_tokens(1).resonance_band == "emergent"
    assert protocol.issue_tokens(4).resonance_band == "harmonic"
    assert protocol.issue_tokens(10).resonance_band == "radiant"


def test_consciousness_token_protocol_zero_and_negative_amount():
    """Test ConsciousnessTokenProtocol with zero and negative amounts."""
    protocol = ConsciousnessTokenProtocol()
    zero_token = protocol.issue_tokens(0)
    negative_token = protocol.issue_tokens(-10)
    assert zero_token.consciousness_value == 0
    assert negative_token.consciousness_value == 0


@pytest.mark.asyncio
async def test_gift_economy_engine_basic():
    """Test GiftEconomyEngine with a basic contribution."""
    rng = random.Random(42)
    engine = GiftEconomyEngine(rng)
    contribution = {
        "value": 50,
        "love_index": 0.8,
        "reciprocity": 0.7,
        "community_alignment": 0.9,
    }
    result = await engine.calculate_gift_value(contribution)
    # Expected: 50 * (1 + (0.8+0.7+0.9)/3) + 10 + rng.uniform(0, 5)
    # 50 * 1.8 + 10 + 3.197134 = 103.197134
    assert result == pytest.approx(103.197134, abs=1e-5)


@pytest.mark.asyncio
async def test_gift_economy_engine_zero_contribution():
    """Test GiftEconomyEngine with a zero contribution."""
    rng = random.Random(42)
    engine = GiftEconomyEngine(rng)
    contribution = {
        "value": 0,
        "love_index": 0,
        "reciprocity": 0,
        "community_alignment": 0,
    }
    result = await engine.calculate_gift_value(contribution)
    # Expected: 0 * (1 + 0) + 10 + rng.uniform(0, 5)
    # 10 + 3.197134 = 13.197134
    assert result == pytest.approx(13.197134, abs=1e-5)


class TestQuantumFinancialConsciousnessEngine:
    """Test suite for the Quantum Financial Consciousness Engine."""

    @pytest.fixture
    def engine(self):
        """Fixture for a seeded QuantumFinancialConsciousnessEngine."""
        return QuantumFinancialConsciousnessEngine(seed=42)

    def test_initialization(self, engine):
        """Test that the engine initializes correctly."""
        assert engine is not None

    @pytest.mark.asyncio
    async def test_calculate_consciousness_exchange_rate(self, engine, mocker):
        """Test the consciousness exchange rate calculation with mocked sub-components."""
        mocker.patch.object(engine.abundance_metrics, 'calculate_abundance_impact', return_value=1.5)
        mocker.patch.object(engine.consciousness_tokens, 'issue_tokens', return_value=mocker.Mock(consciousness_value=10.0))
        mocker.patch.object(engine.gift_economy, 'calculate_gift_value', return_value=20.0)

        contribution = {"impact": 10, "collective_benefit": 5}
        rate = await engine.calculate_consciousness_exchange_rate("user123", contribution)

        assert rate.consciousness_tokens_earned == 10.0
        assert rate.abundance_multiplier == 1.5
        assert rate.gift_economy_credits == 20.0
        assert rate.collective_wealth_increase == pytest.approx(0.310505, abs=1e-6)

    @pytest.mark.asyncio
    async def test_propose_exchange_gift_economy(self, engine):
        """Test proposal for gift economy exchange."""
        user_profile = {"financial_stress": 0.7, "abundance_consciousness": 0.5}
        product_value = {"base_value": 100}
        proposal = await engine.propose_consciousness_based_exchange(user_profile, product_value)
        assert proposal.exchange_type == "gift_economy"
        assert proposal.financial_requirement == 0

    @pytest.mark.asyncio
    async def test_propose_exchange_abundance_based(self, engine):
        """Test proposal for abundance-based exchange."""
        user_profile = {"financial_stress": 0.2, "abundance_consciousness": 0.9}
        product_value = {"base_value": 100, "depth": 0.8, "rarity": 0.7, "mission_alignment": 0.9}
        proposal = await engine.propose_consciousness_based_exchange(user_profile, product_value)
        assert proposal.exchange_type == "abundance_based"
        assert proposal.suggested_contribution is not None and proposal.suggested_contribution > 0

    @pytest.mark.asyncio
    async def test_propose_exchange_traditional(self, engine):
        """Test proposal for consciousness-enhanced traditional exchange."""
        user_profile = {"financial_stress": 0.2, "abundance_consciousness": 0.5}
        product_value = {"base_value": 100, "depth": 0.8, "rarity": 0.7, "mission_alignment": 0.9}
        proposal = await engine.propose_consciousness_based_exchange(user_profile, product_value)
        assert proposal.exchange_type == "consciousness_enhanced_traditional"
        assert proposal.fair_price is not None and proposal.fair_price > 0
