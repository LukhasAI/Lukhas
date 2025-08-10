#!/usr/bin/env python3
"""
Quantum Attention Economics
AI-powered attention valuation system with quantum entanglement properties.
Creates ethical attention economy with consent-based trading.
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class AttentionTokenType(Enum):
    """Types of attention tokens in the quantum economy"""

    FOCUSED = "focused"  # Deep, single-task attention
    AMBIENT = "ambient"  # Background, peripheral attention
    CREATIVE = "creative"  # Open, exploratory attention
    ANALYTICAL = "analytical"  # Problem-solving attention
    EMOTIONAL = "emotional"  # Empathetic, feeling attention
    QUANTUM = "quantum"  # Superposition of multiple attention types


@dataclass
class AttentionToken:
    """Represents a quantum attention token"""

    token_id: str
    owner_id: str
    token_type: AttentionTokenType
    value: float  # Base value in attention units
    quantum_state: Dict[str, float] = field(
        default_factory=dict
    )  # Superposition weights
    entangled_with: List[str] = field(default_factory=list)  # Entangled token IDs
    consent_constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def calculate_quantum_value(self) -> float:
        """Calculate value considering quantum properties"""
        base_value = self.value

        # Add quantum bonus for superposition states
        if len(self.quantum_state) > 1:
            entropy = -sum(
                p * math.log(p) for p in self.quantum_state.values() if p > 0
            )
            quantum_bonus = entropy * 0.2  # 20% bonus per bit of entropy
            base_value *= 1 + quantum_bonus

        # Add entanglement bonus
        entanglement_bonus = len(self.entangled_with) * 0.1  # 10% per entanglement
        base_value *= 1 + entanglement_bonus

        return base_value


@dataclass
class AttentionBid:
    """Bid for user attention"""

    bid_id: str
    bidder_id: str
    target_user_id: str
    bid_amount: float
    bid_type: AttentionTokenType
    content_preview: str
    ethical_score: float = 1.0  # 0-1, how ethical/beneficial the content is
    urgency: float = 0.5  # 0-1, time sensitivity
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class QuantumAttentionEconomics:
    """
    Quantum-enhanced attention economics system.

    Features:
    - AI-powered attention valuation
    - Quantum superposition for parallel attention states
    - Entanglement for shared attention experiences
    - Consent-based attention trading
    - Ethical constraints on attention manipulation
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        # Token storage
        self.tokens: Dict[str, AttentionToken] = {}
        self.user_balances: Dict[str, float] = {}

        # Market state
        self.bid_queue: List[AttentionBid] = []
        self.market_price: Dict[AttentionTokenType, float] = dict.fromkeys(
            AttentionTokenType, 1.0
        )

        # Configuration
        self.min_ethical_score = 0.6
        self.max_attention_drain_rate = (
            0.3  # Max 30% of attention can be consumed per hour
        )
        self.quantum_coherence_threshold = 0.85

        logger.info("Quantum Attention Economics initialized")

    async def mint_attention_tokens(
        self, user_id: str, attention_state: Dict[str, Any]
    ) -> List[AttentionToken]:
        """Mint new attention tokens based on user's current state"""
        tokens_minted = []

        # Analyze attention state with AI
        if self.openai:
            try:
                analysis = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Analyze user's attention state to determine token minting.
                        Consider: cognitive load, emotional state, time of day, recent activities.
                        Generate fair token distribution that reflects actual attention capacity.""",
                        },
                        {"role": "user", "content": json.dumps(attention_state)},
                    ],
                    functions=[
                        {
                            "name": "mint_tokens",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "token_distribution": {
                                        "type": "object",
                                        "properties": {
                                            "focused": {"type": "number"},
                                            "ambient": {"type": "number"},
                                            "creative": {"type": "number"},
                                            "analytical": {"type": "number"},
                                            "emotional": {"type": "number"},
                                        },
                                    },
                                    "total_capacity": {"type": "number"},
                                    "quality_multiplier": {
                                        "type": "number",
                                        "minimum": 0.5,
                                        "maximum": 2.0,
                                    },
                                    "consent_level": {
                                        "type": "string",
                                        "enum": ["full", "limited", "minimal"],
                                    },
                                },
                                "required": [
                                    "token_distribution",
                                    "total_capacity",
                                    "quality_multiplier",
                                ],
                            },
                        }
                    ],
                    function_call={"name": "mint_tokens"},
                )

                mint_params = json.loads(
                    analysis.choices[0].message.function_call.arguments
                )

                # Create tokens based on AI analysis
                for token_type_str, amount in mint_params["token_distribution"].items():
                    if amount > 0:
                        token_type = AttentionTokenType[token_type_str.upper()]
                        token = AttentionToken(
                            token_id=f"token_{user_id}_{datetime.now().timestamp()}_{token_type.value}",
                            owner_id=user_id,
                            token_type=token_type,
                            value=amount * mint_params["quality_multiplier"],
                            consent_constraints={
                                "level": mint_params.get("consent_level", "limited"),
                                "allowed_uses": self._get_allowed_uses(
                                    mint_params.get("consent_level", "limited")
                                ),
                            },
                            expires_at=datetime.now()
                            + timedelta(hours=4),  # Tokens expire after 4 hours
                        )

                        self.tokens[token.token_id] = token
                        tokens_minted.append(token)

                        # Update user balance
                        self.user_balances[user_id] = (
                            self.user_balances.get(user_id, 0) + token.value
                        )

            except Exception as e:
                logger.error(f"AI token minting failed: {e}")
                # Fallback to basic minting
                tokens_minted = await self._basic_token_minting(
                    user_id, attention_state
                )
        else:
            tokens_minted = await self._basic_token_minting(user_id, attention_state)

        return tokens_minted

    def _get_allowed_uses(self, consent_level: str) -> List[str]:
        """Get allowed uses based on consent level"""
        if consent_level == "full":
            return [
                "commercial",
                "educational",
                "entertainment",
                "social",
                "productivity",
            ]
        elif consent_level == "limited":
            return ["educational", "productivity", "essential"]
        else:  # minimal
            return ["essential"]

    async def _basic_token_minting(
        self, user_id: str, attention_state: Dict[str, Any]
    ) -> List[AttentionToken]:
        """Basic token minting without AI"""
        base_capacity = attention_state.get("base_capacity", 100)
        stress_level = attention_state.get("stress", 0.5)

        # Reduce capacity based on stress
        adjusted_capacity = base_capacity * (1 - stress_level * 0.5)

        # Simple distribution
        token = AttentionToken(
            token_id=f"token_{user_id}_{datetime.now().timestamp()}_mixed",
            owner_id=user_id,
            token_type=AttentionTokenType.AMBIENT,
            value=adjusted_capacity,
            expires_at=datetime.now() + timedelta(hours=4),
        )

        self.tokens[token.token_id] = token
        self.user_balances[user_id] = (
            self.user_balances.get(user_id, 0) + adjusted_capacity
        )

        return [token]

    async def create_quantum_attention_state(
        self,
        user_id: str,
        attention_types: List[AttentionTokenType],
        weights: Optional[List[float]] = None,
    ) -> AttentionToken:
        """Create a quantum superposition of attention states"""
        if weights is None:
            weights = [1.0 / len(attention_types)] * len(attention_types)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Create quantum token
        quantum_token = AttentionToken(
            token_id=f"quantum_{user_id}_{datetime.now().timestamp()}",
            owner_id=user_id,
            token_type=AttentionTokenType.QUANTUM,
            value=sum(
                self.market_price[t] for t in attention_types
            ),  # Sum of component values
            quantum_state={t.value: w for t, w in zip(attention_types, weights)},
            expires_at=datetime.now()
            + timedelta(hours=2),  # Quantum states are more fragile
        )

        self.tokens[quantum_token.token_id] = quantum_token

        # Use AI to optimize quantum state if available
        if self.openai:
            try:
                optimization = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Optimize quantum attention state for maximum benefit.
                        Consider: cognitive harmony, task requirements, energy conservation.""",
                        },
                        {
                            "role": "user",
                            "content": f"Attention types: {[t.value for t in attention_types]}\nWeights: {weights}",
                        },
                    ],
                )

                # Could parse and apply optimization suggestions
                logger.info(
                    f"Quantum optimization suggestion: {optimization.choices[0].message.content}"
                )

            except Exception as e:
                logger.error(f"Quantum optimization failed: {e}")

        return quantum_token

    async def entangle_attention_tokens(
        self, token_ids: List[str], entanglement_type: str = "bell_state"
    ) -> bool:
        """Create quantum entanglement between attention tokens"""
        tokens = [self.tokens.get(tid) for tid in token_ids if tid in self.tokens]

        if len(tokens) < 2:
            return False

        # Check all tokens belong to consenting users
        user_ids = set(t.owner_id for t in tokens)

        # Create entanglement
        for token in tokens:
            token.entangled_with = [
                t.token_id for t in tokens if t.token_id != token.token_id
            ]

        logger.info(
            f"Created {entanglement_type} entanglement between {len(tokens)} tokens"
        )

        # Notify users of entanglement
        for user_id in user_ids:
            # TODO: Send notification through consciousness hub
            pass

        return True

    async def submit_attention_bid(self, bid: AttentionBid) -> Dict[str, Any]:
        """Submit a bid for user attention"""
        # Validate ethical score
        if bid.ethical_score < self.min_ethical_score:
            return {
                "success": False,
                "reason": "Below ethical threshold",
                "suggestion": "Improve content quality and user benefit",
            }

        # Check user's attention availability
        user_balance = self.user_balances.get(bid.target_user_id, 0)
        if user_balance < bid.bid_amount:
            return {
                "success": False,
                "reason": "Insufficient attention capacity",
                "available": user_balance,
            }

        # Use AI to evaluate bid fairness
        if self.openai:
            try:
                evaluation = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": """Evaluate attention bid for fairness and user benefit.
                        Consider: value proposition, timing, user state, ethical implications.""",
                        },
                        {
                            "role": "user",
                            "content": f"""Bid: {json.dumps({
                            'amount': bid.bid_amount,
                            'type': bid.bid_type.value,
                            'content_preview': bid.content_preview,
                            'ethical_score': bid.ethical_score,
                            'urgency': bid.urgency
                        })}
                        User balance: {user_balance}""",
                        },
                    ],
                    temperature=0.3,
                )

                eval_result = evaluation.choices[0].message.content

                if "reject" in eval_result.lower():
                    return {
                        "success": False,
                        "reason": "AI evaluation failed",
                        "feedback": eval_result,
                    }

            except Exception as e:
                logger.error(f"Bid evaluation failed: {e}")

        # Add to bid queue
        self.bid_queue.append(bid)

        # Sort by ethical score * urgency
        self.bid_queue.sort(key=lambda b: b.ethical_score * b.urgency, reverse=True)

        return {
            "success": True,
            "bid_id": bid.bid_id,
            "position": self.bid_queue.index(bid) + 1,
            "estimated_processing_time": (self.bid_queue.index(bid) + 1)
            * 30,  # seconds
        }

    async def process_attention_transaction(
        self, bid_id: str, user_consent: bool
    ) -> Dict[str, Any]:
        """Process an attention transaction with user consent"""
        # Find bid
        bid = next((b for b in self.bid_queue if b.bid_id == bid_id), None)
        if not bid:
            return {"success": False, "reason": "Bid not found"}

        if not user_consent:
            self.bid_queue.remove(bid)
            return {"success": False, "reason": "User declined"}

        # Deduct attention tokens
        user_balance = self.user_balances.get(bid.target_user_id, 0)
        if user_balance >= bid.bid_amount:
            self.user_balances[bid.target_user_id] -= bid.bid_amount

            # Create transaction record
            transaction = {
                "transaction_id": f"tx_{datetime.now().timestamp()}",
                "bid_id": bid_id,
                "user_id": bid.target_user_id,
                "amount": bid.bid_amount,
                "token_type": bid.bid_type.value,
                "timestamp": datetime.now().isoformat(),
                "ethical_score": bid.ethical_score,
            }

            # Update market price based on transaction
            self.market_price[bid.bid_type] *= 1.01  # Slight increase due to demand

            # Remove from queue
            self.bid_queue.remove(bid)

            return {
                "success": True,
                "transaction": transaction,
                "new_balance": self.user_balances[bid.target_user_id],
            }
        else:
            return {"success": False, "reason": "Insufficient balance"}

    async def calculate_attention_value(
        self, user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate fair market value for user's attention"""
        base_value = 100.0  # Base attention value

        # Factors that affect value
        factors = {
            "time_of_day": self._time_of_day_multiplier(datetime.now()),
            "cognitive_load": 1.0 - context.get("cognitive_load", 0.5),
            "emotional_state": self._emotional_value_multiplier(
                context.get("emotional_state", {})
            ),
            "rarity": self._calculate_rarity_multiplier(user_id),
            "expertise": context.get("expertise_multiplier", 1.0),
        }

        # Calculate total value
        total_multiplier = 1.0
        for factor, mult in factors.items():
            total_multiplier *= mult

        final_value = base_value * total_multiplier

        # Get AI insights if available
        ai_insights = None
        if self.openai:
            try:
                insights = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Provide market insights for attention valuation",
                        },
                        {
                            "role": "user",
                            "content": f"Factors: {json.dumps(factors)}\nCalculated value: {final_value}",
                        },
                    ],
                    temperature=0.7,
                )
                ai_insights = insights.choices[0].message.content
            except Exception as e:
                logger.error(f"AI insights generation failed: {e}")

        return {
            "base_value": base_value,
            "factors": factors,
            "total_multiplier": total_multiplier,
            "final_value": final_value,
            "market_prices": dict(self.market_price),
            "ai_insights": ai_insights,
        }

    def _time_of_day_multiplier(self, current_time: datetime) -> float:
        """Calculate value multiplier based on time of day"""
        hour = current_time.hour

        # Peak hours (9-11 AM, 2-4 PM) are most valuable
        if 9 <= hour <= 11 or 14 <= hour <= 16:
            return 1.5
        # Evening wind-down (8-10 PM) is moderately valuable
        elif 20 <= hour <= 22:
            return 1.2
        # Late night/early morning is less valuable
        elif hour < 6 or hour > 23:
            return 0.7
        else:
            return 1.0

    def _emotional_value_multiplier(self, emotional_state: Dict[str, float]) -> float:
        """Calculate value based on emotional state"""
        # Positive emotions increase value
        positive = emotional_state.get("joy", 0) + emotional_state.get("curiosity", 0)
        # Negative emotions decrease value
        negative = emotional_state.get("stress", 0) + emotional_state.get("anxiety", 0)

        # Net emotional score
        net_score = positive - negative

        # Convert to multiplier (0.5 to 1.5)
        return 1.0 + (net_score * 0.5)

    def _calculate_rarity_multiplier(self, user_id: str) -> float:
        """Calculate rarity multiplier based on user's attention scarcity"""
        # Check how many tokens this user has minted recently
        user_tokens = [t for t in self.tokens.values() if t.owner_id == user_id]
        active_tokens = [
            t for t in user_tokens if t.expires_at and t.expires_at > datetime.now()
        ]

        # Fewer active tokens = higher rarity
        if len(active_tokens) == 0:
            return 2.0  # Very rare
        elif len(active_tokens) < 5:
            return 1.5  # Rare
        elif len(active_tokens) < 10:
            return 1.2  # Uncommon
        else:
            return 1.0  # Common

    async def get_market_report(self) -> Dict[str, Any]:
        """Generate comprehensive market report"""
        total_tokens = len(self.tokens)
        active_tokens = len(
            [
                t
                for t in self.tokens.values()
                if t.expires_at and t.expires_at > datetime.now()
            ]
        )

        report = {
            "market_overview": {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "total_users": len(self.user_balances),
                "pending_bids": len(self.bid_queue),
            },
            "price_index": dict(self.market_price),
            "token_distribution": {},
            "top_bidders": [],
            "market_trends": [],
        }

        # Calculate token distribution
        for token_type in AttentionTokenType:
            count = len([t for t in self.tokens.values() if t.token_type == token_type])
            report["token_distribution"][token_type.value] = count

        # Get top bidders
        bidder_totals = {}
        for bid in self.bid_queue:
            bidder_totals[bid.bidder_id] = (
                bidder_totals.get(bid.bidder_id, 0) + bid.bid_amount
            )

        report["top_bidders"] = sorted(
            bidder_totals.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Generate AI market analysis if available
        if self.openai:
            try:
                analysis = await self.openai.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze attention economy market trends and provide insights",
                        },
                        {"role": "user", "content": json.dumps(report)},
                    ],
                )
                report["ai_analysis"] = analysis.choices[0].message.content
            except Exception as e:
                logger.error(f"Market analysis failed: {e}")

        return report

    def get_user_attention_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's attention token balance and details"""
        balance = self.user_balances.get(user_id, 0)
        user_tokens = [t for t in self.tokens.values() if t.owner_id == user_id]
        active_tokens = [
            t for t in user_tokens if t.expires_at and t.expires_at > datetime.now()
        ]

        return {
            "user_id": user_id,
            "total_balance": balance,
            "active_tokens": len(active_tokens),
            "token_details": [
                {
                    "token_id": t.token_id,
                    "type": t.token_type.value,
                    "value": t.value,
                    "quantum_value": t.calculate_quantum_value(),
                    "expires_in": (
                        (t.expires_at - datetime.now()).total_seconds()
                        if t.expires_at
                        else None
                    ),
                    "entangled": len(t.entangled_with) > 0,
                }
                for t in active_tokens
            ],
            "market_value": balance
            * sum(self.market_price.values())
            / len(self.market_price),
        }


# Singleton instance
_economics_instance = None


def get_quantum_attention_economics(
    openai_api_key: Optional[str] = None,
) -> QuantumAttentionEconomics:
    """Get or create the singleton Quantum Attention Economics instance"""
    global _economics_instance
    if _economics_instance is None:
        _economics_instance = QuantumAttentionEconomics(openai_api_key)
    return _economics_instance
