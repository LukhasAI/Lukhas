
import random
from contextlib import nullcontext
from dataclasses import asdict, is_dataclass
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from candidate.core.quantum_financial.quantum_financial_consciousness_engine import (
    AbundanceCalculator,
    ConsciousnessTokenProtocol,
    GiftEconomyEngine,
    QuantumFinancialConsciousnessEngine,
)

try:
    from candidate.core.quantum_financial.quantum_financial_consciousness_engine import (
        ConsciousnessToken,
    )
except ImportError:  # legacy engine exposes dict tokens only
    ConsciousnessToken = None


_ENGINE_MODULE = QuantumFinancialConsciousnessEngine.__module__
_USING_QI_ENGINE = "qi_financial" in _ENGINE_MODULE


def _random_uniform_path(obj: Any) -> str:
    """Return the import path to ``random.uniform`` for the object's module."""

    module_name = getattr(obj, "__module__", obj)
    return f"{module_name}.random.uniform"


def _token_field(token: Any, field: str, *aliases: str) -> Any:
    """Safely access a field on a token dataclass or legacy dictionary."""

    if isinstance(token, dict):
        for key in (field, *aliases):
            if key in token:
                return token[key]
        raise KeyError(f"Field {field!r} not available on token dict {token}")
    return getattr(token, field)


def _as_dict(value: Any) -> Dict[str, Any]:
    """Convert dataclass / namespace objects into dictionaries for assertions."""

    if isinstance(value, dict):
        return value
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "_asdict"):
        return value._asdict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    raise TypeError(f"Unsupported result type: {type(value)!r}")


def _make_token(consciousness_value: float, resonance: str = "harmonic") -> Any:
    """Create a token compatible with both modern and legacy engines."""

    if ConsciousnessToken is not None:
        try:
            return ConsciousnessToken(
                token_id="test_token",
                consciousness_value=consciousness_value,
                resonance_band=resonance,
            )
        except TypeError:
            # Fallback to dict-based token for mismatched signatures.
            pass
    return {
        "token_id": "test_token",
        "consciousness_value": consciousness_value,
        "resonance_band": resonance,
        "resonance_tier": resonance,
    }


def _create_engine(seed: int = 42) -> QuantumFinancialConsciousnessEngine:
    """Instantiate the engine, tolerating legacy constructors without seed."""

    try:
        return QuantumFinancialConsciousnessEngine(seed=seed)
    except TypeError:
        return QuantumFinancialConsciousnessEngine()


class TestAbundanceCalculator:
    """Tests for the AbundanceCalculator class."""

    @pytest.mark.asyncio
    async def test_calculate_abundance_impact_is_deterministic(self):
        """Verify that the abundance calculation is deterministic with a seed."""
        contribution = {"impact": 1.0, "collective_benefit": 0.5, "awareness_level": 1.2}
        random_path = _random_uniform_path(AbundanceCalculator)

        try:
            calculator1 = AbundanceCalculator(random.Random(42))
            calculator2 = AbundanceCalculator(random.Random(42))
            result1 = await calculator1.calculate_abundance_impact(contribution)
            result2 = await calculator2.calculate_abundance_impact(contribution)
        except TypeError:
            calculator1 = AbundanceCalculator()
            calculator2 = AbundanceCalculator()
            with patch(random_path, return_value=1.2345):
                result1 = await calculator1.calculate_abundance_impact(contribution)
                result2 = await calculator2.calculate_abundance_impact(contribution)

        assert result1 == result2

    @pytest.mark.asyncio
    async def test_calculate_abundance_impact_with_different_contributions(self):
        """Verify that different contributions result in different impacts."""
        contribution1 = {"impact": 1.0, "collective_benefit": 0.5}
        contribution2 = {"impact": 2.0, "collective_benefit": 1.0}
        random_path = _random_uniform_path(AbundanceCalculator)

        try:
            calculator = AbundanceCalculator(random.Random(42))
            result1 = await calculator.calculate_abundance_impact(contribution1)
            result2 = await calculator.calculate_abundance_impact(contribution2)
        except TypeError:
            calculator = AbundanceCalculator()
            with patch(random_path, side_effect=[1.25, 1.75]):
                result1 = await calculator.calculate_abundance_impact(contribution1)
                result2 = await calculator.calculate_abundance_impact(contribution2)
        assert result1 != result2


class TestConsciousnessTokenProtocol:
    """Tests for the ConsciousnessTokenProtocol class."""

    def test_issue_tokens_is_deterministic_with_bias(self):
        """Verify token issuance is deterministic with the same resonance bias."""
        protocol1 = ConsciousnessTokenProtocol(1.5)
        protocol2 = ConsciousnessTokenProtocol(1.5)
        token1 = protocol1.issue_tokens(100.0)
        token2 = protocol2.issue_tokens(100.0)
        assert _token_field(token1, "consciousness_value") == _token_field(
            token2, "consciousness_value"
        )
        assert _token_field(token1, "resonance_band", "resonance_tier") == _token_field(
            token2, "resonance_band", "resonance_tier"
        )

    def test_issue_tokens_value_increases_monotonically(self):
        """Verify that consciousness value increases with the amount."""
        protocol = ConsciousnessTokenProtocol()
        value1 = _token_field(protocol.issue_tokens(100.0), "consciousness_value")
        value2 = _token_field(protocol.issue_tokens(200.0), "consciousness_value")
        assert value2 > value1

    @pytest.mark.parametrize(
        "amount, expected_band",
        [
            (0, {"dormant"}),
            (0.5, {"dormant", "emergent"}),
            (2, {"dormant", "harmonic"}),
            (10, {"spark", "radiant"}),
        ],
    )
    def test_issue_tokens_assigns_correct_resonance_band(self, amount, expected_band):
        """Verify that tokens are assigned the correct resonance band."""
        protocol = ConsciousnessTokenProtocol()
        token = protocol.issue_tokens(amount)
        resonance = _token_field(token, "resonance_band", "resonance_tier")
        assert resonance in expected_band


@pytest.mark.asyncio
class TestGiftEconomyEngine:
    """Tests for the GiftEconomyEngine class."""

    async def test_calculate_gift_value_is_deterministic(self):
        """Verify that the gift value calculation is deterministic with a seed."""
        contribution = {"value": 1.0, "love_index": 0.8}
        random_path = _random_uniform_path(GiftEconomyEngine)

        try:
            engine1 = GiftEconomyEngine(random.Random(42))
            engine2 = GiftEconomyEngine(random.Random(42))
            result1 = await engine1.calculate_gift_value(contribution)
            result2 = await engine2.calculate_gift_value(contribution)
        except TypeError:
            engine = GiftEconomyEngine()
            with patch(random_path, return_value=55.0):
                result1 = await engine.calculate_gift_value(contribution)
                result2 = await engine.calculate_gift_value(contribution)

        assert result1 == result2


@pytest.mark.asyncio
class TestQuantumFinancialConsciousnessEngine:
    """Tests for the QuantumFinancialConsciousnessEngine class."""

    def test_engine_initializes_default_components(self):
        """Ensure the engine wires expected helper components regardless of version."""
        engine = _create_engine()
        assert isinstance(engine.abundance_metrics, AbundanceCalculator)
        assert isinstance(engine.consciousness_tokens, ConsciousnessTokenProtocol)
        assert isinstance(engine.gift_economy, GiftEconomyEngine)

    async def test_calculate_consciousness_exchange_rate(self):
        """Test the full exchange rate calculation with a seeded engine."""
        engine = _create_engine()
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
            mock_tokens.return_value = _make_token(1.5)

            user_signal_patch = (
                patch.object(engine, "_determine_user_signal", return_value=0.5322)
                if hasattr(engine, "_determine_user_signal")
                else nullcontext()
            )
            random_patch = (
                patch(_random_uniform_path(engine.__class__), side_effect=[1.5, 0.045322])
                if not _USING_QI_ENGINE
                else nullcontext()
            )

            with user_signal_patch, random_patch:
                result = await engine.calculate_consciousness_exchange_rate(
                    "user1", contribution
                )

        result_data = _as_dict(result)
        assert result_data["consciousness_tokens_earned"] == pytest.approx(1.5)
        assert result_data["abundance_multiplier"] == 2.0
        assert result_data["gift_economy_credits"] == 10.0
        assert result_data["collective_wealth_increase"] == pytest.approx(0.045322, 1e-6)

    @pytest.mark.parametrize(
        "profile, product_value, random_value, expected_type, expected_key, expected_value",
        [
            (
                {"financial_stress": 0.7},
                {},
                None,
                "gift_economy",
                "financial_requirement",
                0,
            ),
            (
                {"abundance_consciousness": 0.9},
                {"base_value": 100, "depth": 0.8, "rarity": 0.6, "mission_alignment": 0.7},
                42.0,
                "abundance_based",
                "suggested_contribution",
                120.00,
            ),
            (
                {},
                {"base_value": 100, "depth": 0.2, "rarity": 0.3, "mission_alignment": 0.1},
                88.0,
                "consciousness_enhanced_traditional",
                "fair_price",
                70.00,
            ),
        ],
    )
    async def test_propose_consciousness_based_exchange(
        self,
        profile,
        product_value,
        random_value,
        expected_type,
        expected_key,
        expected_value,
    ):
        """Test the exchange proposal logic for different scenarios."""
        engine = _create_engine()

        random_patch = (
            patch(_random_uniform_path(engine.__class__), return_value=random_value)
            if (random_value is not None and not _USING_QI_ENGINE)
            else nullcontext()
        )

        with random_patch:
            result = await engine.propose_consciousness_based_exchange(
                profile, product_value
            )

        result_data = _as_dict(result)
        assert result_data["exchange_type"] == expected_type

        if _USING_QI_ENGINE:
            assert result_data[expected_key] == expected_value
        else:
            # Legacy engine uses RNG for abundance and traditional paths.
            if random_value is not None:
                assert result_data[expected_key] == pytest.approx(random_value)
            else:
                assert result_data[expected_key] == expected_value

        if expected_type == "consciousness_enhanced_traditional" and "growth_investment_framing" in result_data:
            assert result_data["growth_investment_framing"] is True
