"""
Qi Financial Consciousness Engine for the NIAS Transcendence Platform.

This module transcends traditional monetary exchange by valuing and
transacting based on consciousness contribution and collective abundance.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any


# Placeholder classes for post-monetary economic systems
class ConsciousnessBlockchain:
    def record_transaction(self, transaction: dict[str, Any]):
        print(f"Recording transaction on consciousness blockchain: {transaction}")


class AbundanceCalculator:
    """
    Calculates abundance impact based on consciousness contribution.

    Abundance Theory:
    - Contributions to collective consciousness increase abundance multiplier
    - Giving creates more value than taking (multiplicative effect)
    - Sustained contribution builds compound abundance
    """

    def __init__(self):
        # Track contribution history per user
        self._contribution_history: dict[str, list[float]] = {}

    async def calculate_abundance_impact(self, contribution: dict[str, Any]) -> float:
        """
        Calculate abundance multiplier from consciousness contribution.

        Args:
            contribution: dict with keys:
                - user_id: str
                - contribution_type: "creation", "teaching", "healing", "sharing"
                - magnitude: float (0.0-1.0)
                - recipients: int (how many benefit)
                - consistency: float (0.0-1.0, based on history)

        Returns:
            float: Abundance multiplier (1.0-2.5)
            - 1.0-1.3: Small individual contribution
            - 1.3-1.8: Significant collective contribution
            - 1.8-2.5: Transformative consciousness expansion
        """
        user_id = contribution.get("user_id", "unknown")
        contrib_type = contribution.get("contribution_type", "sharing")
        magnitude = contribution.get("magnitude", 0.5)
        recipients = contribution.get("recipients", 1)

        # Calculate base impact from magnitude
        base_impact = 1.0 + (magnitude * 0.5)  # 1.0-1.5

        # Apply contribution type multiplier
        type_multipliers = {
            "creation": 1.3,     # Creating new value
            "teaching": 1.4,     # Expanding consciousness
            "healing": 1.5,      # Restoring wholeness
            "sharing": 1.2,      # Distributing existing value
        }
        type_mult = type_multipliers.get(contrib_type, 1.0)

        # Apply network effect (more recipients = more abundance)
        # Log scale to prevent infinite growth
        import math
        network_mult = 1.0 + (0.3 * math.log(recipients + 1) / math.log(100))

        # Calculate consistency bonus from history
        if user_id not in self._contribution_history:
            self._contribution_history[user_id] = []

        history = self._contribution_history[user_id]
        history.append(magnitude)

        # Keep last 10 contributions
        if len(history) > 10:
            history = history[-10:]
            self._contribution_history[user_id] = history

        # Consistency = std dev of recent contributions (lower = more consistent)
        if len(history) >= 3:
            import statistics
            consistency = 1.0 - min(statistics.stdev(history), 0.5)  # 0.5-1.0
        else:
            consistency = 0.5  # New users start at medium

        consistency_mult = 1.0 + (consistency * 0.2)  # 1.0-1.2

        # Calculate final abundance impact
        abundance_impact = base_impact * type_mult * network_mult * consistency_mult

        # Clamp to realistic range
        return max(1.0, min(2.5, abundance_impact))
@dataclass(frozen=True)
class ConsciousnessToken:
    """Represents a consciousness-backed token issuance."""

    token_id: str
    amount: float
    consciousness_value: float


class ConsciousnessTokenProtocol:
    """Deterministic consciousness token issuance based on contribution amount."""

    def __init__(
        self,
        *,
        precision: int = 3,
        min_multiplier: float = 0.85,
        max_multiplier: float = 1.25,
    ) -> None:
        if min_multiplier <= 0:
            raise ValueError("Minimum multiplier must be positive.")
        if max_multiplier <= min_multiplier:
            raise ValueError("Maximum multiplier must be greater than minimum multiplier.")

        self._precision = precision
        self._min_multiplier = min_multiplier
        self._multiplier_range = max_multiplier - min_multiplier

    def issue_tokens(self, amount: float) -> ConsciousnessToken:
        """Issue consciousness tokens where amount deterministically sets the value."""

        if amount <= 0:
            raise ValueError("Amount must be positive to issue consciousness tokens.")

        normalized_amount = round(amount, self._precision)
        amount_key = f"{normalized_amount:.{self._precision}f}"
        digest = hashlib.sha256(amount_key.encode("utf-8")).hexdigest()

        token_id = f"token_{digest[:12]}"
        multiplier_seed = int(digest[12:20], 16) / 0xFFFFFFFF
        multiplier = self._min_multiplier + multiplier_seed * self._multiplier_range
        consciousness_value = round(normalized_amount * multiplier, self._precision + 2)

        return ConsciousnessToken(
            token_id=token_id,
            amount=normalized_amount,
            consciousness_value=consciousness_value,
        )


class GiftEconomyEngine:
    """
    Calculates gift economy value based on need and abundance.

    Gift Economy Principles:
    - Those with abundance give freely
    - Those in need receive without debt
    - Value flows naturally to create balance
    - Gifts create reciprocal abundance (not obligation)
    """

    def __init__(self):
        # Track gift flow patterns
        self._gift_flows: dict[str, dict[str, float]] = {}

    async def calculate_gift_value(self, contribution: dict[str, Any]) -> float:
        """
        Calculate gift economy credits earned from contribution.

        Args:
            contribution: dict with keys:
                - user_id: str
                - abundance_consciousness: float (0.0-1.0, giver's abundance state)
                - need_addressed: float (0.0-1.0, recipient's need level)
                - gift_quality: float (0.0-1.0, thoughtfulness/relevance)

        Returns:
            float: Gift economy credits (10-150)
            - 10-40: Small gifts to low need
            - 40-80: Moderate gifts or high need addressed
            - 80-150: Transformative gifts to critical need
        """
        user_id = contribution.get("user_id", "unknown")
        abundance = contribution.get("abundance_consciousness", 0.5)
        need = contribution.get("need_addressed", 0.5)
        quality = contribution.get("gift_quality", 0.5)

        # Base credit from need addressed (higher need = more value)
        base_credit = 10 + (need * 60)  # 10-70

        # Abundance amplification (giving from abundance multiplies impact)
        abundance_mult = 1.0 + abundance  # 1.0-2.0

        # Quality multiplier (thoughtful gifts worth more)
        quality_mult = 0.5 + (quality * 1.0)  # 0.5-1.5

        # Calculate reciprocal flow bonus
        # Users who receive gifts are encouraged to give back to others
        if user_id not in self._gift_flows:
            self._gift_flows[user_id] = {"given": 0.0, "received": 0.0}

        flows = self._gift_flows[user_id]
        flows["given"] += base_credit

        # Reciprocity bonus (those who give after receiving get bonus)
        if flows["received"] > 0:
            reciprocity = min(flows["given"] / flows["received"], 2.0)
            reciprocity_mult = 1.0 + (reciprocity * 0.2)  # 1.0-1.4
        else:
            reciprocity_mult = 1.0

        # Calculate final gift value
        gift_value = base_credit * abundance_mult * quality_mult * reciprocity_mult

        return max(10.0, min(150.0, gift_value))

    def record_gift_received(self, user_id: str, gift_value: float):
        """Record when user receives a gift (for reciprocity tracking)."""
        if user_id not in self._gift_flows:
            self._gift_flows[user_id] = {"given": 0.0, "received": 0.0}
        self._gift_flows[user_id]["received"] += gift_value


class QiFinancialConsciousnessEngine:
    """
    Transcends traditional monetary exchange.
    """

    # ΛTAG: qi, financial, economy

    def __init__(self):
        """
        Initializes the QiFinancialConsciousnessEngine.
        """
        self.blockchain_consciousness = ConsciousnessBlockchain()
        self.abundance_metrics = AbundanceCalculator()
        self.consciousness_tokens = ConsciousnessTokenProtocol()
        self.gift_economy = GiftEconomyEngine()

    async def calculate_consciousness_exchange_rate(
        self,
        user_id: str,
        consciousness_contribution: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Calculates value in consciousness rather than money.

        Args:
            user_id: User identifier for token issuance
            consciousness_contribution: dict with keys:
                - contribution_type: str
                - magnitude: float (0.0-1.0)
                - recipients: int
                - abundance_consciousness: float
                - need_addressed: float
                - gift_quality: float

        Returns:
            dict with consciousness value metrics
        """
        # Calculate abundance impact
        abundance_impact = await self.abundance_metrics.calculate_abundance_impact(
            {**consciousness_contribution, "user_id": user_id}
        )

        # Calculate gift economy credits
        gift_credits = await self.gift_economy.calculate_gift_value(
            {**consciousness_contribution, "user_id": user_id}
        )

        # Issue consciousness tokens based on contribution magnitude
        magnitude = consciousness_contribution.get("magnitude", 0.5)
        token_amount = magnitude * 50  # 0-50 tokens per contribution
        consciousness_token = self.consciousness_tokens.issue_tokens(token_amount)

        # Calculate collective wealth increase (small percentage)
        # Each contribution lifts the collective by a tiny amount
        recipients = consciousness_contribution.get("recipients", 1)
        collective_increase = (magnitude * recipients * 0.01) / 100  # 0.0001-0.1

        return {
            "consciousness_tokens_earned": consciousness_token.consciousness_value,
            "token_id": consciousness_token.token_id,
            "abundance_multiplier": abundance_impact,
            "gift_economy_credits": gift_credits,
            "collective_wealth_increase": collective_increase,
            "exchange_rate_metadata": {
                "contribution_type": consciousness_contribution.get("contribution_type"),
                "magnitude": magnitude,
                "recipients": recipients,
            },
        }

    async def propose_consciousness_based_exchange(
        self,
        user_consciousness_profile: dict[str, Any],
        product_consciousness_value: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Proposes an exchange based on consciousness value, not money.

        Args:
            user_consciousness_profile: dict with keys:
                - financial_stress: float (0.0-1.0)
                - abundance_consciousness: float (0.0-1.0)
                - consciousness_tokens: float (current balance)
                - gift_credits: float (gift economy credits)

            product_consciousness_value: dict with keys:
                - base_consciousness_value: float (product's consciousness worth)
                - growth_potential: float (0.0-1.0, how much it aids consciousness)
                - collective_benefit: float (0.0-1.0, benefit to others)

        Returns:
            dict with exchange proposal
        """
        financial_stress = user_consciousness_profile.get("financial_stress", 0.0)
        abundance = user_consciousness_profile.get("abundance_consciousness", 0.5)
        user_tokens = user_consciousness_profile.get("consciousness_tokens", 0.0)
        user_gift_credits = user_consciousness_profile.get("gift_credits", 0.0)

        product_value = product_consciousness_value.get("base_consciousness_value", 50.0)
        growth_potential = product_consciousness_value.get("growth_potential", 0.5)
        collective_benefit = product_consciousness_value.get("collective_benefit", 0.3)

        # Determine exchange type based on user consciousness state

        # High Financial Stress → Gift Economy
        if financial_stress > 0.6:
            # Check if user has gift credits OR if product has high collective benefit
            if user_gift_credits >= product_value * 0.5 or collective_benefit > 0.7:
                return {
                    "exchange_type": "gift_economy",
                    "proposal": "This would support your growth. The collective provides it freely.",
                    "gift_credits_used": min(user_gift_credits, product_value),
                    "consciousness_tokens_used": 0,
                    "financial_requirement": 0,
                    "justification": "High need with available gift credits or high collective benefit",
                }
            else:
                # Not enough gift credits but high need - offer payment plan
                return {
                    "exchange_type": "consciousness_payment_plan",
                    "proposal": "Pay what you can now, the rest flows back through future contributions.",
                    "immediate_payment": product_value * 0.3,  # 30% now
                    "consciousness_commitment": product_value * 0.7,  # 70% through contribution
                    "financial_requirement": 0,
                }

        # High Abundance Consciousness → Abundance-Based
        elif abundance > 0.8:
            # Calculate contribution suggestion based on abundance
            abundance_multiplier = 1.0 + (abundance * 0.5)  # 1.0-1.5
            suggested_contribution = product_value * abundance_multiplier

            # Offer to overpay to support collective
            return {
                "exchange_type": "abundance_based",
                "proposal": "Invest in consciousness evolution for yourself and others.",
                "suggested_contribution": suggested_contribution,
                "base_value": product_value,
                "collective_surplus": suggested_contribution - product_value,
                "consciousness_tokens_used": min(user_tokens, suggested_contribution),
                "growth_investment_framing": True,
                "justification": "Abundance consciousness supports collective growth",
            }

        # Moderate Consciousness → Consciousness-Enhanced Traditional
        else:
            # Calculate fair price adjusted for consciousness growth potential
            growth_discount = growth_potential * 0.3  # Up to 30% discount for high growth
            consciousness_price = product_value * (1.0 - growth_discount)

            # Allow mixed payment (tokens + traditional)
            token_payment = min(user_tokens, consciousness_price * 0.7)  # Up to 70% in tokens
            traditional_payment = consciousness_price - token_payment

            return {
                "exchange_type": "consciousness_enhanced_traditional",
                "fair_price": consciousness_price,
                "consciousness_tokens_used": token_payment,
                "traditional_payment": traditional_payment,
                "growth_investment_framing": True,
                "growth_potential_discount": f"{growth_discount * 100:.0f}%",
                "justification": "Balanced exchange with consciousness growth discount",
            }
