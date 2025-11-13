import pytest
from labs.core.qi_financial.qi_financial_consciousness_engine import (
    QiFinancialConsciousnessEngine,
    AbundanceCalculator,
    GiftEconomyEngine,
)


class TestAbundanceCalculator:
    """Test abundance impact calculations."""

    @pytest.mark.asyncio
    async def test_abundance_impact_range(self):
        """Test abundance impact returns 1.0-2.5."""
        calc = AbundanceCalculator()

        impact = await calc.calculate_abundance_impact({
            "user_id": "user1",
            "contribution_type": "teaching",
            "magnitude": 0.8,
            "recipients": 50,
        })

        assert 1.0 <= impact <= 2.5

    @pytest.mark.asyncio
    async def test_consistency_bonus(self):
        """Test consistent contributors get bonus."""
        calc = AbundanceCalculator()

        # Make 5 consistent contributions
        for _ in range(5):
            await calc.calculate_abundance_impact({
                "user_id": "consistent_user",
                "magnitude": 0.7,  # Same magnitude
                "recipients": 10,
            })

        # Should have higher impact due to consistency
        final_impact = await calc.calculate_abundance_impact({
            "user_id": "consistent_user",
            "magnitude": 0.7,
            "recipients": 10,
        })

        assert final_impact > 1.3  # Should include consistency bonus


class TestGiftEconomyEngine:
    """Test gift economy value calculations."""

    @pytest.mark.asyncio
    async def test_gift_value_range(self):
        """Test gift value returns 10-150."""
        engine = GiftEconomyEngine()

        value = await engine.calculate_gift_value({
            "user_id": "giver1",
            "abundance_consciousness": 0.9,
            "need_addressed": 0.8,
            "gift_quality": 0.7,
        })

        assert 10.0 <= value <= 150.0

    @pytest.mark.asyncio
    async def test_reciprocity_bonus(self):
        """Test reciprocity increases gift value."""
        engine = GiftEconomyEngine()

        # User receives a gift
        engine.record_gift_received("user1", 50.0)

        # User gives back - should get reciprocity bonus
        value_with_reciprocity = await engine.calculate_gift_value({
            "user_id": "user1",
            "need_addressed": 0.5,
            "gift_quality": 0.5,
        })

        assert value_with_reciprocity > 20  # Base + reciprocity


class TestQiFinancialEngine:
    """Test full consciousness economics engine."""

    @pytest.mark.asyncio
    async def test_calculate_consciousness_exchange_rate(self):
        """Test exchange rate calculation."""
        engine = QiFinancialConsciousnessEngine()

        result = await engine.calculate_consciousness_exchange_rate(
            user_id="user1",
            consciousness_contribution={
                "contribution_type": "creation",
                "magnitude": 0.7,
                "recipients": 20,
                "abundance_consciousness": 0.8,
                "need_addressed": 0.6,
                "gift_quality": 0.7,
            },
        )

        assert "consciousness_tokens_earned" in result
        assert "abundance_multiplier" in result
        assert "gift_economy_credits" in result
        assert 1.0 <= result["abundance_multiplier"] <= 2.5
        assert 10.0 <= result["gift_economy_credits"] <= 150.0

    @pytest.mark.asyncio
    async def test_gift_economy_for_high_stress(self):
        """Test high financial stress triggers gift economy."""
        engine = QiFinancialConsciousnessEngine()

        result = await engine.propose_consciousness_based_exchange(
            user_consciousness_profile={
                "financial_stress": 0.9,  # High stress
                "gift_credits": 50.0,
            },
            product_consciousness_value={
                "base_consciousness_value": 40.0,
                "collective_benefit": 0.8,
            },
        )

        assert result["exchange_type"] == "gift_economy"
        assert result["financial_requirement"] == 0

    @pytest.mark.asyncio
    async def test_abundance_exchange_for_high_consciousness(self):
        """Test abundance consciousness triggers overpayment."""
        engine = QiFinancialConsciousnessEngine()

        result = await engine.propose_consciousness_based_exchange(
            user_consciousness_profile={
                "abundance_consciousness": 0.95,  # Very high
                "consciousness_tokens": 100.0,
            },
            product_consciousness_value={
                "base_consciousness_value": 50.0,
            },
        )

        assert result["exchange_type"] == "abundance_based"
        assert result["suggested_contribution"] > result["base_value"]

    @pytest.mark.asyncio
    async def test_growth_discount_applied(self):
        """Test consciousness growth potential provides discount."""
        engine = QiFinancialConsciousnessEngine()

        result = await engine.propose_consciousness_based_exchange(
            user_consciousness_profile={
                "abundance_consciousness": 0.5,  # Moderate
                "consciousness_tokens": 50.0,
            },
            product_consciousness_value={
                "base_consciousness_value": 100.0,
                "growth_potential": 0.9,  # High growth potential
            },
        )

        assert result["exchange_type"] == "consciousness_enhanced_traditional"
        assert result["fair_price"] < 100.0  # Discounted
