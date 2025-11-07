
import pytest
import random
from unittest.mock import MagicMock, AsyncMock, patch

from candidate.core.quantum_financial.quantum_financial_consciousness_engine import (
    AbundanceCalculator,
    ConsciousnessTokenProtocol,
    GiftEconomyEngine,
    QuantumFinancialConsciousnessEngine,
    ConsciousnessToken,
)


class TestAbundanceCalculator:
    """Tests for the AbundanceCalculator class."""

    @pytest.mark.asyncio
    async def test_calculate_abundance_impact_is_deterministic(self):
        """Verify that the abundance calculation is deterministic with a seed."""
        rng = random.Random(42)
        calculator = AbundanceCalculator(rng)
        contribution = {"impact": 1.0, "collective_benefit": 0.5, "awareness_level": 1.2}
        result1 = await calculator.calculate_abundance_impact(contribution)

        rng = random.Random(42)
        calculator = AbundanceCalculator(rng)
        result2 = await calculator.calculate_abundance_impact(contribution)

        assert result1 == result2

    @pytest.mark.asyncio
    async def test_calculate_abundance_impact_with_different_contributions(self):
        """Verify that different contributions result in different impacts."""
        calculator = AbundanceCalculator(random.Random(42))
        contribution1 = {"impact": 1.0, "collective_benefit": 0.5}
        contribution2 = {"impact": 2.0, "collective_benefit": 1.0}
        result1 = await calculator.calculate_abundance_impact(contribution1)
        result2 = await calculator.calculate_abundance_impact(contribution2)
        assert result1 != result2


class TestConsciousnessTokenProtocol:
    """Tests for the ConsciousnessTokenProtocol class."""

    def test_issue_tokens_is_deterministic_with_bias(self):
        """Verify token issuance is deterministic with the same resonance bias."""
        protocol1 = ConsciousnessTokenProtocol(resonance_bias=1.5)
        protocol2 = ConsciousnessTokenProtocol(resonance_bias=1.5)
        token1 = protocol1.issue_tokens(100.0)
        token2 = protocol2.issue_tokens(100.0)
        assert token1.consciousness_value == token2.consciousness_value
        assert token1.resonance_band == token2.resonance_band

    def test_issue_tokens_value_increases_monotonically(self):
        """Verify that consciousness value increases with the amount."""
        protocol = ConsciousnessTokenProtocol()
        value1 = protocol.issue_tokens(100.0).consciousness_value
        value2 = protocol.issue_tokens(200.0).consciousness_value
        assert value2 > value1

    @pytest.mark.parametrize(
        "amount, expected_band",
        [
            (0, "dormant"),
            (0.5, "emergent"),
            (2, "harmonic"),
            (10, "radiant"),
        ],
    )
    def test_issue_tokens_assigns_correct_resonance_band(self, amount, expected_band):
        """Verify that tokens are assigned the correct resonance band."""
        protocol = ConsciousnessTokenProtocol()
        token = protocol.issue_tokens(amount)
        assert token.resonance_band == expected_band


@pytest.mark.asyncio
class TestGiftEconomyEngine:
    """Tests for the GiftEconomyEngine class."""

    async def test_calculate_gift_value_is_deterministic(self):
        """Verify that the gift value calculation is deterministic with a seed."""
        rng = random.Random(42)
        engine = GiftEconomyEngine(rng)
        contribution = {"value": 1.0, "love_index": 0.8}
        result1 = await engine.calculate_gift_value(contribution)

        rng = random.Random(42)
        engine = GiftEconomyEngine(rng)
        result2 = await engine.calculate_gift_value(contribution)

        assert result1 == result2


@pytest.mark.asyncio
class TestQuantumFinancialConsciousnessEngine:
    """Tests for the QuantumFinancialConsciousnessEngine class."""

    def test_engine_is_deterministic_with_seed(self):
        """Verify that the entire engine behaves deterministically with a seed."""
        engine1 = QuantumFinancialConsciousnessEngine(seed=42)
        engine2 = QuantumFinancialConsciousnessEngine(seed=42)
        assert engine1._determine_user_signal("user1") == engine2._determine_user_signal("user1")

    async def test_calculate_consciousness_exchange_rate(self):
        """Test the full exchange rate calculation with a seeded engine."""
        engine = QuantumFinancialConsciousnessEngine(seed=42)
        contribution = {"impact": 1.0, "collective_benefit": 0.5}

        with patch.object(
            engine.abundance_metrics, "calculate_abundance_impact", new_callable=AsyncMock
        ) as mock_abundance, patch.object(
            engine.gift_economy, "calculate_gift_value", new_callable=AsyncMock
        ) as mock_gift, patch.object(
            engine.consciousness_tokens, "issue_tokens"
        ) as mock_tokens:
            mock_abundance.return_value = 2.0
            mock_gift.return_value = 10.0
            mock_tokens.return_value = ConsciousnessToken(
                token_id="test_token", consciousness_value=1.5, resonance_band="harmonic"
            )

            result = await engine.calculate_consciousness_exchange_rate("user1", contribution)

            assert result.consciousness_tokens_earned == 1.5
            assert result.abundance_multiplier == 2.0
            assert result.gift_economy_credits == 10.0
            assert result.collective_wealth_increase == pytest.approx(0.045322, 1e-6)

    @pytest.mark.parametrize(
        "profile, product_value, expected_type, expected_suggestion",
        [
            (
                {"financial_stress": 0.7},
                {},
                "gift_economy",
                0,
            ),
            (
                {"abundance_consciousness": 0.9},
                {"base_value": 100, "depth": 0.8, "rarity": 0.6, "mission_alignment": 0.7},
                "abundance_based",
                120.00,
            ),
            (
                {},
                {"base_value": 100, "depth": 0.2, "rarity": 0.3, "mission_alignment": 0.1},
                "consciousness_enhanced_traditional",
                70.00,
            ),
        ],
    )
    async def test_propose_consciousness_based_exchange(
        self, profile, product_value, expected_type, expected_suggestion
    ):
        """Test the exchange proposal logic for different scenarios."""
        engine = QuantumFinancialConsciousnessEngine(seed=42)
        result = await engine.propose_consciousness_based_exchange(profile, product_value)
        assert result.exchange_type == expected_type
        if expected_type == "gift_economy":
            assert result.financial_requirement == expected_suggestion
        elif expected_type == "abundance_based":
            assert result.suggested_contribution == expected_suggestion
        elif expected_type == "consciousness_enhanced_traditional":
            assert result.fair_price == expected_suggestion
