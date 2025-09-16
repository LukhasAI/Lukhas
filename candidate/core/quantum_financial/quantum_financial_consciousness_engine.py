"""
Quantum Financial Consciousness Engine for the NIAS Transcendence Platform.

This module transcends traditional monetary exchange by valuing and
transacting based on consciousness contribution and collective abundance.
"""
from __future__ import annotations

import hashlib
import logging
import random
from dataclasses import dataclass
from typing import Any, Optional

# ΛTAG: logging, deterministic
logger = logging.getLogger(__name__)


def _normalize_metric(
    value: Any,
    *,
    default: float = 1.0,
    minimum: float = 0.0,
    maximum: float = 5.0,
) -> float:
    """Normalize numeric metrics for deterministic quantum finance calculations."""

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default

    if numeric < minimum:
        return minimum
    if numeric > maximum:
        return maximum
    return numeric


# --- Dataclasses for Typed Responses ---

@dataclass
class ConsciousnessExchange:
    """Represents the result of a consciousness-based value calculation."""
    consciousness_tokens_earned: float
    abundance_multiplier: float
    gift_economy_credits: float
    collective_wealth_increase: float

@dataclass
class ExchangeProposal:
    """Represents a proposed exchange based on consciousness value."""
    exchange_type: str
    proposal: str
    financial_requirement: Optional[float] = None
    suggested_contribution: Optional[float] = None
    fair_price: Optional[float] = None
    growth_investment_framing: Optional[bool] = None


# --- Deterministic Helper Classes ---

class ConsciousnessBlockchain:
    """Placeholder for a consciousness-based transaction ledger."""
    def record_transaction(self, transaction: dict[str, Any]):
        """Records a transaction in the consciousness ledger."""
        print(f"Recording transaction on consciousness blockchain: {transaction}")


class AbundanceCalculator:
    """Calculates abundance impact deterministically."""
    def __init__(self, rng: random.Random):
        self.rng = rng

    async def calculate_abundance_impact(
        self, contribution: dict[str, Any]
    ) -> float:
        """Calculates abundance impact based on contribution and deterministic randomness."""
        base = self.rng.uniform(1.0, 2.0)
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
        multiplier = round(base * composite, 4)

        logger.debug(
            "quantum_financial.abundance",
            extra={
                "impact": impact,
                "collective": collective,
                "awareness": awareness,
                "intention": intention,
                "driftScore": round(abs(composite - 1.0), 4),
            },
        )
        return multiplier


class ConsciousnessTokenProtocol:
    """Issues consciousness tokens deterministically."""
    def __init__(self, rng: random.Random):
        self.rng = rng

    def issue_tokens(
        self, amount: float
    ) -> str:
        """Issues a deterministic token based on a seeded random generator."""
        normalized_amount = _normalize_metric(
            amount, default=0.0, minimum=0.0, maximum=1_000_000.0
        )
        quantized = int(round(normalized_amount * 1000))
        entropy = self.rng.random()
        fingerprint = hashlib.sha256(f"{quantized}:{entropy:.8f}".encode("utf-8")).hexdigest()
        token = f"token_{quantized:08x}_{fingerprint[:8]}"

        # ΛTAG: quantum_token_generation
        logger.debug(
            "quantum_financial.token_issued",
            extra={
                "amount": normalized_amount,
                "quantized": quantized,
                "entropy": round(entropy, 6),
                "token": token,
            },
        )
        return token


class GiftEconomyEngine:
    """Calculates gift economy value deterministically."""
    def __init__(self, rng: random.Random):
        self.rng = rng

    async def calculate_gift_value(
        self, contribution: dict[str, Any]
    ) -> float:
        """Calculates gift value based on contribution magnitude and deterministic randomness."""
        base = self.rng.uniform(10, 100)
        contribution_value = _normalize_metric(
            contribution.get("value"), default=1.0, minimum=0.1, maximum=10.0
        )
        love_index = _normalize_metric(
            contribution.get("love_index"), default=0.5, minimum=0.0, maximum=1.0
        )
        reciprocity = _normalize_metric(
            contribution.get("reciprocity"), default=0.5, minimum=0.0, maximum=1.0
        )
        community_alignment = _normalize_metric(
            contribution.get("community_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )

        # ΛTAG: quantum_gift_economy
        emotional_multiplier = 1.0 + (love_index * 0.3) + (reciprocity * 0.4) + (community_alignment * 0.3)
        gift_value = round(base * contribution_value * emotional_multiplier, 4)

        logger.debug(
            "quantum_financial.gift_value",
            extra={
                "base": base,
                "contribution_value": contribution_value,
                "love_index": love_index,
                "reciprocity": reciprocity,
                "community_alignment": community_alignment,
                "affect_delta": round(emotional_multiplier - 1.0, 4),
            },
        )
        return gift_value


# --- Main Engine ---

class QuantumFinancialConsciousnessEngine:
    """
    Transcends traditional monetary exchange using deterministic, seeded operations.
    """

    # ΛTAG: quantum, financial, economy

    def __init__(self, seed: int = 42):
        """
        Initializes the QuantumFinancialConsciousnessEngine with a seed for deterministic behavior.
        """
        self.rng = random.Random(seed)
        self.blockchain_consciousness = ConsciousnessBlockchain()
        self.abundance_metrics = AbundanceCalculator(self.rng)
        self.consciousness_tokens = ConsciousnessTokenProtocol(self.rng)
        self.gift_economy = GiftEconomyEngine(self.rng)

    async def calculate_consciousness_exchange_rate(
        self,
        user_id: str,
        consciousness_contribution: dict[
            str, Any
        ],
    ) -> ConsciousnessExchange:
        """
        Calculates value in consciousness rather than money, returning a typed dataclass.
        """
        profile_vector = self._derive_profile_vector(user_id, consciousness_contribution)
        abundance_multiplier = await self.abundance_metrics.calculate_abundance_impact(
            consciousness_contribution
        )
        gift_credits = await self.gift_economy.calculate_gift_value(consciousness_contribution)

        # ΛTAG: quantum_exchange_rate
        token_seed = self.rng.uniform(0.8, 1.2)
        consciousness_tokens = round(
            (profile_vector["creative_flux"] * 10.0 + abundance_multiplier * 2.5) * token_seed,
            4,
        )

        wealth_increase = round(
            profile_vector["collective_alignment"] * 0.06 + gift_credits / 12_000,
            4,
        )

        logger.debug(
            "quantum_financial.exchange_rate",
            extra={
                "user_id": profile_vector["user_hash"],
                "tokens": consciousness_tokens,
                "abundance_multiplier": abundance_multiplier,
                "gift_credits": gift_credits,
            },
        )

        return ConsciousnessExchange(
            consciousness_tokens_earned=consciousness_tokens,
            abundance_multiplier=abundance_multiplier,
            gift_economy_credits=gift_credits,
            collective_wealth_increase=wealth_increase,
        )

    async def propose_consciousness_based_exchange(
        self,
        user_consciousness_profile: dict[str, Any],
        product_consciousness_value: dict[
            str, Any
        ],
    ) -> ExchangeProposal:
        """
        Proposes an exchange based on consciousness value, returning a typed dataclass.
        """
        stress_level = _normalize_metric(
            user_consciousness_profile.get("financial_stress"), default=0.0, minimum=0.0, maximum=1.0
        )
        abundance = _normalize_metric(
            user_consciousness_profile.get("abundance_consciousness"), default=0.5, minimum=0.0, maximum=1.0
        )

        depth = _normalize_metric(
            product_consciousness_value.get("depth"), default=0.5, minimum=0.0, maximum=1.0
        )
        rarity = _normalize_metric(
            product_consciousness_value.get("rarity"), default=0.5, minimum=0.0, maximum=1.0
        )
        mission_alignment = _normalize_metric(
            product_consciousness_value.get("mission_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )
        base_value = _normalize_metric(
            product_consciousness_value.get("base_value"), default=40.0, minimum=5.0, maximum=500.0
        )

        resonance = (depth * 0.4) + (mission_alignment * 0.4) + (rarity * 0.2)

        # ΛTAG: quantum_exchange_logic
        if stress_level > 0.6 and resonance < 0.65:
            logger.debug(
                "quantum_financial.exchange_proposal",
                extra={"mode": "gift", "resonance": resonance, "stress": stress_level},
            )
            return ExchangeProposal(
                exchange_type="gift_economy",
                proposal="This would support your growth. The collective provides it freely.",
                financial_requirement=0,
            )

        if abundance > 0.8 or resonance >= 0.8:
            contribution = round(base_value * (0.6 + resonance), 2)
            logger.debug(
                "quantum_financial.exchange_proposal",
                extra={"mode": "abundance", "resonance": resonance, "suggested": contribution},
            )
            return ExchangeProposal(
                exchange_type="abundance_based",
                proposal="Invest in consciousness evolution for yourself and others.",
                suggested_contribution=contribution,
            )

        fair_price = round(base_value * (0.45 + resonance * 0.55), 2)
        logger.debug(
            "quantum_financial.exchange_proposal",
            extra={"mode": "traditional", "resonance": resonance, "price": fair_price},
        )
        return ExchangeProposal(
            exchange_type="consciousness_enhanced_traditional",
            proposal="A fair exchange for mutual growth.",
            fair_price=fair_price,
            growth_investment_framing=True,
        )

    def _derive_profile_vector(
        self, user_id: str, contribution: dict[str, Any]
    ) -> dict[str, float | str]:
        """Generate a deterministic signature describing user contribution resonance."""

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

        alignment = _normalize_metric(
            contribution.get("collective_alignment"), default=0.5, minimum=0.0, maximum=1.0
        )

        profile_vector = {
            "user_hash": user_hash,
            "creative_flux": round(coherence / 2.5, 4),
            "collective_alignment": round(alignment, 4),
        }

        logger.debug(
            "quantum_financial.profile_vector",
            extra={
                "user_id": user_hash,
                "creative_flux": profile_vector["creative_flux"],
                "collective_alignment": profile_vector["collective_alignment"],
            },
        )

        return profile_vector
