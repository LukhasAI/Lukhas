"""
Qi Financial Consciousness Engine for the NIAS Transcendence Platform.

This module transcends traditional monetary exchange by valuing and
transacting based on consciousness contribution and collective abundance.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

# ΛTAG: logging, deterministic
logger = logging.getLogger(__name__)


def _normalize_metric(
    value: Any,
    *,
    default: float = 1.0,
    minimum: float = 0.0,
    maximum: float = 5.0,
) -> float:
    """Normalize arbitrary numeric input into a bounded deterministic range."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default

    if numeric < minimum:
        return minimum
    if numeric > maximum:
        return maximum
    return numeric


# Placeholder classes for post-monetary economic systems
class ConsciousnessBlockchain:
    def record_transaction(self, transaction: dict[str, Any]):
        print(f"Recording transaction on consciousness blockchain: {transaction}")


class AbundanceCalculator:
    async def calculate_abundance_impact(
        self, contribution: dict[str, Any]
    ) -> float:
        """Derive an abundance multiplier from contribution metadata."""

        impact = _normalize_metric(contribution.get("impact"))
        collective = _normalize_metric(
            contribution.get("collective_benefit"), default=impact, minimum=0.0, maximum=5.0
        )
        awareness = _normalize_metric(
            contribution.get("awareness_level"), default=1.0, minimum=0.0, maximum=5.0
        )
        intention = _normalize_metric(
            contribution.get("intention_purity"), default=1.0, minimum=0.0, maximum=5.0
        )

        # ΛTAG: quantum_abundance
        composite = (impact * 0.4) + (collective * 0.3) + (awareness * 0.2) + (intention * 0.1)
        drift_score = abs(composite - 1.0) / 2

        multiplier = max(0.5, round(0.85 + composite * 0.3, 4))
        logger.debug(
            "qi_financial.abundance_multiplier",
            extra={
                "impact": impact,
                "collective": collective,
                "awareness": awareness,
                "intention": intention,
                "driftScore": round(drift_score, 4),
            },
        )
        return multiplier


class ConsciousnessTokenProtocol:
    def issue_tokens(self, amount: float) -> str:
        """Generate a deterministic consciousness token encoded with the amount."""

        normalized_amount = _normalize_metric(amount, default=0.0, minimum=0.0, maximum=1_000_000.0)
        quantized = int(round(normalized_amount * 1000))
        fingerprint_source = f"{normalized_amount:.6f}:{quantized}"
        digest = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()

        token = f"token_{quantized:08x}_{digest[:10]}"

        # ΛTAG: token_quantization
        logger.debug(
            "qi_financial.token_issued",
            extra={"amount": normalized_amount, "quantized": quantized, "token": token},
        )
        return token


class GiftEconomyEngine:
    async def calculate_gift_value(self, contribution: dict[str, Any]) -> float:
        """Translate contribution sentiment into a consciousness gift value."""

        base_value = _normalize_metric(contribution.get("value"), default=1.0, minimum=0.1, maximum=10.0)
        love_index = _normalize_metric(
            contribution.get("love_index"), default=0.5, minimum=0.0, maximum=1.0
        )
        gratitude = _normalize_metric(
            contribution.get("gratitude"), default=0.5, minimum=0.0, maximum=1.0
        )
        community_alignment = _normalize_metric(
            contribution.get("community_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )

        # ΛTAG: gift_economy
        emotional_multiplier = 1.0 + (love_index * 0.4) + (gratitude * 0.35) + (community_alignment * 0.25)
        gift_value = round(base_value * 20 * emotional_multiplier, 4)

        logger.debug(
            "qi_financial.gift_value",
            extra={
                "base_value": base_value,
                "love_index": love_index,
                "gratitude": gratitude,
                "community_alignment": community_alignment,
                "affect_delta": round(emotional_multiplier - 1.0, 4),
            },
        )
        return gift_value


class QiFinancialConsciousnessEngine:
    """
    Transcends traditional monetary exchange.
    """

    # ΛTAG: qi, financial, economy

    def __init__(self):
        """Initialise deterministic consciousness finance components."""

        self.blockchain_consciousness = ConsciousnessBlockchain()
        self.abundance_metrics = AbundanceCalculator()
        self.consciousness_tokens = ConsciousnessTokenProtocol()
        self.gift_economy = GiftEconomyEngine()

    async def calculate_consciousness_exchange_rate(
        self,
        user_id: str,
        consciousness_contribution: dict[
            str, Any
        ],  # TODO[QUANTUM-BIO:specialist] - User ID for consciousness profile mapping
    ) -> dict[str, Any]:
        """
        Calculates value in consciousness rather than money.
        """
        abundance_multiplier = await self.abundance_metrics.calculate_abundance_impact(
            consciousness_contribution
        )
        gift_credits = await self.gift_economy.calculate_gift_value(consciousness_contribution)

        profile_vector = self._derive_profile_vector(user_id, consciousness_contribution)

        # ΛTAG: exchange_tokens
        signature_boost = 1.0 + profile_vector["signature_scalar"] * 0.3
        token_base = profile_vector["creative_flux"] * 8.0 * signature_boost
        token_bonus = abundance_multiplier * 3.0
        consciousness_tokens = round(token_base + token_bonus, 4)

        collective_gain = round(
            profile_vector["collective_alignment"] * 0.05 + gift_credits / 10_000,
            4,
        )

        logger.debug(
            "qi_financial.exchange_rate",
            extra={
                "user_id": profile_vector["user_hash"],
                "tokens": consciousness_tokens,
                "gift_credits": gift_credits,
                "abundance_multiplier": abundance_multiplier,
                "signature_scalar": profile_vector["signature_scalar"],
            },
        )

        return {
            "consciousness_tokens_earned": consciousness_tokens,
            "abundance_multiplier": abundance_multiplier,
            "gift_economy_credits": gift_credits,
            "collective_wealth_increase": collective_gain,
        }

    async def propose_consciousness_based_exchange(
        self,
        user_consciousness_profile: dict[str, Any],
        product_consciousness_value: dict[
            str, Any
        ],  # TODO[QUANTUM-BIO:specialist] - Product consciousness value in exchange calculation
    ) -> dict[str, Any]:
        """
        Proposes an exchange based on consciousness value, not money.
        """
        product_depth = _normalize_metric(
            product_consciousness_value.get("depth"), default=0.5, minimum=0.0, maximum=1.0
        )
        rarity = _normalize_metric(
            product_consciousness_value.get("rarity"), default=0.5, minimum=0.0, maximum=1.0
        )
        mission_alignment = _normalize_metric(
            product_consciousness_value.get("mission_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )
        base_value = _normalize_metric(
            product_consciousness_value.get("base_value"), default=50.0, minimum=5.0, maximum=500.0
        )

        stress_level = _normalize_metric(
            user_consciousness_profile.get("financial_stress"), default=0.0, minimum=0.0, maximum=1.0
        )
        abundance = _normalize_metric(
            user_consciousness_profile.get("abundance_consciousness"), default=0.5, minimum=0.0, maximum=1.0
        )

        resonance = (product_depth * 0.4) + (mission_alignment * 0.35) + (rarity * 0.25)

        # ΛTAG: exchange_logic
        if stress_level > 0.6 and resonance < 0.6:
            return {
                "exchange_type": "gift_economy",
                "proposal": "This would support your growth. The collective provides it freely.",
                "financial_requirement": 0,
            }

        if abundance > 0.8 or resonance >= 0.75:
            suggested = round(base_value * (0.5 + resonance), 2)
            return {
                "exchange_type": "abundance_based",
                "proposal": "Invest in consciousness evolution for yourself and others.",
                "suggested_contribution": suggested,
            }

        fair_price = round(base_value * (0.4 + resonance * 0.6), 2)
        return {
            "exchange_type": "consciousness_enhanced_traditional",
            "fair_price": fair_price,
            "growth_investment_framing": True,
        }

    def _derive_profile_vector(
        self, user_id: str, contribution: dict[str, Any]
    ) -> dict[str, float | str]:
        """Create a stable signature describing the contributor's energetic profile."""

        user_hash = hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
        contribution_score = _normalize_metric(
            contribution.get("contribution_score"), default=1.0, minimum=0.1, maximum=5.0
        )
        creativity = _normalize_metric(
            contribution.get("creative_output"), default=1.0, minimum=0.0, maximum=5.0
        )
        service = _normalize_metric(
            contribution.get("service_level"), default=1.0, minimum=0.0, maximum=5.0
        )
        coherence = (contribution_score * 0.5) + (creativity * 0.3) + (service * 0.2)

        collective_alignment = _normalize_metric(
            contribution.get("collective_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )

        signature_scalar = (int(user_hash, 16) % 997) / 997

        profile_vector = {
            "user_hash": user_hash,
            "creative_flux": round(coherence / 2.5, 4),
            "collective_alignment": round(collective_alignment, 4),
            "signature_scalar": round(signature_scalar, 4),
        }

        logger.debug(
            "qi_financial.profile_vector",
            extra={
                "user_id": user_hash,
                "creative_flux": profile_vector["creative_flux"],
                "collective_alignment": profile_vector["collective_alignment"],
            },
        )

        return profile_vector
