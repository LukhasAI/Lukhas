
import pytest
from unittest.mock import AsyncMock, patch

from candidate.core.qi_financial.qi_financial_consciousness_engine import (
    ConsciousnessTokenProtocol,
    QiFinancialConsciousnessEngine,
)


class TestConsciousnessTokenProtocol:
    """Tests for the ConsciousnessTokenProtocol class."""

    def test_issue_tokens_is_deterministic(self):
        """Verify that token issuance is deterministic for the same amount."""
        protocol = ConsciousnessTokenProtocol()
        token1 = protocol.issue_tokens(100.0)
        token2 = protocol.issue_tokens(100.0)
        assert token1.token_id == token2.token_id
        assert token1.consciousness_value == token2.consciousness_value

    def test_issue_tokens_for_different_amounts(self):
        """Verify that different amounts produce different tokens."""
        protocol = ConsciousnessTokenProtocol()
        token1 = protocol.issue_tokens(100.0)
        token2 = protocol.issue_tokens(200.0)
        assert token1.token_id != token2.token_id
        assert token1.consciousness_value != token2.consciousness_value

    def test_issue_tokens_respects_precision(self):
        """Verify that tokens are issued with the specified precision."""
        protocol = ConsciousnessTokenProtocol(precision=5)
        amount = 100.123456789
        token = protocol.issue_tokens(amount)
        assert token.amount == round(amount, 5)

    def test_issue_tokens_raises_error_for_negative_amount(self):
        """Verify that issuing tokens for a negative amount raises a ValueError."""
        protocol = ConsciousnessTokenProtocol()
        with pytest.raises(ValueError, match="Amount must be positive"):
            protocol.issue_tokens(-100.0)

    def test_issue_tokens_raises_error_for_zero_amount(self):
        """Verify that issuing tokens for a zero amount raises a ValueError."""
        protocol = ConsciousnessTokenProtocol()
        with pytest.raises(ValueError, match="Amount must be positive"):
            protocol.issue_tokens(0.0)

    def test_init_raises_error_for_invalid_multipliers(self):
        """Verify that the constructor raises errors for invalid multiplier ranges."""
        with pytest.raises(ValueError, match="Minimum multiplier must be positive"):
            ConsciousnessTokenProtocol(min_multiplier=0)
        with pytest.raises(ValueError, match="Maximum multiplier must be greater than minimum"):
            ConsciousnessTokenProtocol(min_multiplier=1.5, max_multiplier=1.0)


@pytest.mark.asyncio
class TestQiFinancialConsciousnessEngine:
    """Tests for the QiFinancialConsciousnessEngine class."""

    async def test_calculate_consciousness_exchange_rate(self):
        """Test the exchange rate calculation with mocked dependencies."""
        engine = QiFinancialConsciousnessEngine()

        with patch.object(
            engine.abundance_metrics, "calculate_abundance_impact", new_callable=AsyncMock
        ) as mock_abundance, patch.object(
            engine.gift_economy, "calculate_gift_value", new_callable=AsyncMock
        ) as mock_gift, patch(
            "random.uniform", side_effect=[10.5, 0.05]
        ) as mock_random:
            mock_abundance.return_value = 1.5
            mock_gift.return_value = 50.0

            result = await engine.calculate_consciousness_exchange_rate(
                "user1", {"contribution": 1}
            )

            assert result["consciousness_tokens_earned"] == 10.5
            assert result["abundance_multiplier"] == 1.5
            assert result["gift_economy_credits"] == 50.0
            assert result["collective_wealth_increase"] == 0.05
            mock_random.assert_any_call(5, 50)
            mock_random.assert_any_call(0.01, 0.1)

    @pytest.mark.parametrize(
        "profile, expected_type, expected_proposal",
        [
            (
                {"financial_stress": 0.7},
                "gift_economy",
                "This would support your growth. The collective provides it freely.",
            ),
            (
                {"abundance_consciousness": 0.9},
                "abundance_based",
                "Invest in consciousness evolution for yourself and others.",
            ),
            ({}, "consciousness_enhanced_traditional", None),
        ],
    )
    async def test_propose_consciousness_based_exchange(
        self, profile, expected_type, expected_proposal
    ):
        """Test the exchange proposal logic for different user profiles."""
        engine = QiFinancialConsciousnessEngine()
        with patch("random.uniform", return_value=100.0):
            result = await engine.propose_consciousness_based_exchange(profile, {})
            assert result["exchange_type"] == expected_type
            if expected_proposal:
                assert result["proposal"] == expected_proposal
