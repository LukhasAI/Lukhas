#!/usr/bin/env python3
"""
Quantum Attention Economics
AI-powered attention valuation system with quantum entanglement properties.
Creates ethical attention economy with consent-based trading.
"""
import importlib as _importlib
import inspect
import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class ConsciousnessHubMessenger:
    """Lightweight adapter for sending notifications to the consciousness hub."""

    _CANDIDATE_FACTORIES = (
        ("consciousness.consciousness_hub", "get_consciousness_hub"),
        ("consciousness.consciousness_hub", "ConsciousnessHub"),
        ("consciousness.reflection.consciousness_hub", "get_consciousness_hub"),
        ("consciousness.reflection.consciousness_hub", "ConsciousnessHub"),
        ("labs.consciousness.reflection.consciousness_hub", "get_consciousness_hub"),
        ("labs.consciousness.reflection.consciousness_hub", "ConsciousnessHub"),
    )

    def __init__(self):
        self._hub: Optional[Any] = None
        self._load_attempted = False
        self._working_method = None

    def _resolve_hub(self) -> Optional[Any]:
        """Attempt to import and instantiate the consciousness hub."""

        if self._hub is not None or self._load_attempted:
            return self._hub

        self._load_attempted = True

        for module_name, factory_name in self._CANDIDATE_FACTORIES:
            try:
                module = __import__(module_name, fromlist=[factory_name])
            except ImportError as exc:  # pragma: no cover - optional dependency
                logger.debug("Consciousness hub module %s unavailable: %s", module_name, exc)
                continue

            factory = getattr(module, factory_name, None)
            if factory is None:
                continue

            try:
                hub_candidate = factory() if callable(factory) else None
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug(
                    "Consciousness hub factory %s from %s failed: %s",
                    factory_name,
                    module_name,
                    exc,
                )
                continue

            if inspect.isawaitable(hub_candidate):
                logger.debug(
                    "Consciousness hub factory %s returned awaitable; skipping synchronous resolution",
                    factory_name,
                )
                continue

            if hub_candidate is not None:
                self._hub = hub_candidate
                break

        if self._hub is None:
            try:
                _mod = _importlib.import_module("labs.core.integration.hub_registry")
                get_hub_registry = _mod.get_hub_registry

                registry = get_hub_registry()
                self._hub = registry.get_hub("consciousness")
            except ImportError as exc:  # pragma: no cover - optional dependency
                logger.debug("Hub registry unavailable for consciousness hub lookup: %s", exc)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug("Failed to retrieve consciousness hub from registry: %s", exc)

        if self._hub is None:
            logger.debug("Consciousness hub could not be resolved")

        return self._hub

    def _candidate_methods(self) -> list[Any]:
        hub = self._resolve_hub()
        if hub is None:
            return []

        if self._working_method is not None:
            return [self._working_method]

        method_names = [
            "send_notification",
            "enqueue_notification",
            "publish_event",
            "emit_event",
            "process_event",
            "handle_event",
            "dispatch_event",
        ]

        methods: list[Any] = []
        for name in method_names:
            method = getattr(hub, name, None)
            if callable(method):
                methods.append(method)

        return methods

    async def send_notification(self, channel: str, payload: dict[str, Any]) -> bool:
        """Send a notification to the consciousness hub if available."""

        envelope = {
            "channel": channel,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        methods = self._candidate_methods()
        if not methods:
            return False

        for method in methods:
            try:
                if await self._try_call(method, channel, payload, envelope):
                    self._working_method = method
                    return True
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception(
                    "Failed to send notification via consciousness hub method %s: %s",
                    getattr(method, "__name__", repr(method)),
                    exc,
                )

        return False

    async def _try_call(
        self,
        method: Any,
        channel: str,
        payload: dict[str, Any],
        envelope: dict[str, Any],
    ) -> bool:
        """Attempt to invoke a candidate hub method with flexible signatures."""

        call_attempts = [
            ((channel, envelope), {}),
            ((channel, payload), {}),
            ((envelope,), {}),
            ((payload,), {}),
            ((), {"channel": channel, "payload": payload}),
            ((), {"event_type": channel, "payload": payload}),
            ((), {"event_type": channel, "event": payload}),
            ((), {"notification": envelope}),
        ]

        for args, kwargs in call_attempts:
            try:
                result = method(*args, **kwargs)
            except TypeError as exc:
                message = str(exc).lower()
                if any(keyword in message for keyword in ("positional", "keyword", "argument")):
                    continue
                raise

            if inspect.isawaitable(result):
                result = await result

            return result is not False

        return False


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
    qi_state: dict[str, float] = field(default_factory=dict)  # Superposition weights
    entangled_with: list[str] = field(default_factory=list)  # Entangled token IDs
    consent_constraints: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def calculate_quantum_value(self) -> float:
        """Calculate value considering quantum properties"""
        base_value = self.value

        # Add quantum bonus for superposition states
        if len(self.qi_state) > 1:
            entropy = -sum(p * math.log(p) for p in self.qi_state.values() if p > 0)
            qi_bonus = entropy * 0.2  # 20% bonus per bit of entropy
            base_value *= 1 + qi_bonus

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
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class QIAttentionEconomics:
    """
    Quantum-enhanced attention economics system.

    Features:
    - AI-powered attention valuation
    - Quantum superposition for parallel attention states
    - Entanglement for shared attention experiences
    - Consent-based attention trading
    - Ethical constraints on attention manipulation
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        consciousness_messenger: Optional[ConsciousnessHubMessenger] = None,
    ):
        self.openai = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self._consciousness_messenger = consciousness_messenger or ConsciousnessHubMessenger()

        # Token storage
        self.tokens: dict[str, AttentionToken] = {}
        self.user_balances: dict[str, float] = {}

        # Market state
        self.bid_queue: list[AttentionBid] = []
        self.market_price: dict[AttentionTokenType, float] = dict.fromkeys(AttentionTokenType, 1.0)

        # Configuration
        self.min_ethical_score = 0.6
        self.max_attention_drain_rate = 0.3  # Max 30% of attention can be consumed per hour
        self.qi_coherence_threshold = 0.85

        logger.info("Quantum Attention Economics initialized")

    async def mint_attention_tokens(self, user_id: str, attention_state: dict[str, Any]) -> list[AttentionToken]:
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

                mint_params = json.loads(analysis.choices[0].message.function_call.arguments)

                # Create tokens based on AI analysis
                for token_type_str, amount in mint_params["token_distribution"].items():
                    if amount > 0:
                        token_type = AttentionTokenType[token_type_str.upper()]
                        token = AttentionToken(
                            token_id=f"token_{user_id}_{datetime.now(timezone.utc).timestamp()}_{token_type.value}",
                            owner_id=user_id,
                            token_type=token_type,
                            value=amount * mint_params["quality_multiplier"],
                            consent_constraints={
                                "level": mint_params.get("consent_level", "limited"),
                                "allowed_uses": self._get_allowed_uses(mint_params.get("consent_level", "limited")),
                            },
                            expires_at=datetime.now(timezone.utc) + timedelta(hours=4),  # Tokens expire after 4 hours
                        )

                        self.tokens[token.token_id] = token
                        tokens_minted.append(token)

                        # Update user balance
                        self.user_balances[user_id] = self.user_balances.get(user_id, 0) + token.value

            except Exception as e:
                logger.error(f"AI token minting failed: {e}")
                # Fallback to basic minting
                tokens_minted = await self._basic_token_minting(user_id, attention_state)
        else:
            tokens_minted = await self._basic_token_minting(user_id, attention_state)

        return tokens_minted

    def _get_allowed_uses(self, consent_level: str) -> list[str]:
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

    async def _basic_token_minting(self, user_id: str, attention_state: dict[str, Any]) -> list[AttentionToken]:
        """Basic token minting without AI"""
        base_capacity = attention_state.get("base_capacity", 100)
        stress_level = attention_state.get("stress", 0.5)

        # Reduce capacity based on stress
        adjusted_capacity = base_capacity * (1 - stress_level * 0.5)

        # Simple distribution
        token = AttentionToken(
            token_id=f"token_{user_id}_{datetime.now(timezone.utc).timestamp()}_mixed",
            owner_id=user_id,
            token_type=AttentionTokenType.AMBIENT,
            value=adjusted_capacity,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=4),
        )

        self.tokens[token.token_id] = token
        self.user_balances[user_id] = self.user_balances.get(user_id, 0) + adjusted_capacity

        return [token]

    async def create_quantum_attention_state(
        self,
        user_id: str,
        attention_types: list[AttentionTokenType],
        weights: Optional[list[float]] = None,
    ) -> AttentionToken:
        """Create a quantum superposition of attention states"""
        if weights is None:
            weights = [1.0 / len(attention_types)] * len(attention_types)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Create quantum token
        qi_token = AttentionToken(
            token_id=f"quantum_{user_id}_{datetime.now(timezone.utc).timestamp()}",
            owner_id=user_id,
            token_type=AttentionTokenType.QUANTUM,
            value=sum(self.market_price[t] for t in attention_types),  # Sum of component values
            qi_state={t.value: w for t, w in zip(attention_types, weights)},
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2),  # Quantum states are more fragile
        )

        self.tokens[qi_token.token_id] = qi_token

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
                logger.info(f"Quantum optimization suggestion: {optimization.choices[0].message.content}")

            except Exception as e:
                logger.error(f"Quantum optimization failed: {e}")

        return qi_token

    async def entangle_attention_tokens(self, token_ids: list[str], entanglement_type: str = "bell_state") -> bool:
        """Create quantum entanglement between attention tokens"""
        tokens = [self.tokens.get(tid) for tid in token_ids if tid in self.tokens]

        if len(tokens) < 2:
            return False

        # Create entanglement
        for token in tokens:
            token.entangled_with = [t.token_id for t in tokens if t.token_id != token.token_id]

        logger.info(f"Created {entanglement_type} entanglement between {len(tokens)} tokens")

        await self._notify_entanglement(tokens, entanglement_type)

        return True

    async def _notify_entanglement(
        self, tokens: list[AttentionToken], entanglement_type: str
    ) -> None:
        """Notify the consciousness hub about a new entanglement."""

        if not tokens or self._consciousness_messenger is None:
            return

        all_token_ids = [token.token_id for token in tokens]

        owner_map: dict[str, list[AttentionToken]] = {}
        for token in tokens:
            owner_map.setdefault(token.owner_id, []).append(token)

        unique_owner_ids = list(owner_map)

        for owner_id, owner_tokens in owner_map.items():
            payload = {
                "event": {
                    "type": "attention.entanglement.created",
                    "entanglement_type": entanglement_type,
                    "token_ids": all_token_ids,
                    "owner_token_ids": [t.token_id for t in owner_tokens],
                    "owner_token_types": [t.token_type.value for t in owner_tokens],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                "recipient": {
                    "user_id": owner_id,
                    "delivery_preference": "consciousness_hub",
                },
                "metadata": {
                    "total_tokens": len(all_token_ids),
                    "owner_token_count": len(owner_tokens),
                    "unique_owner_ids": unique_owner_ids,
                },
            }

            try:
                success = await self._consciousness_messenger.send_notification(
                    channel="attention.entanglement.created",
                    payload=payload,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception(
                    "Failed to notify consciousness hub for owner %s: %s", owner_id, exc
                )
                continue

            if not success:
                logger.warning(
                    "Consciousness hub notification declined for owner %s", owner_id
                )

    async def submit_attention_bid(self, bid: AttentionBid) -> dict[str, Any]:
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
                            "content": f"""Bid: {
                                json.dumps(
                                    {
                                        "amount": bid.bid_amount,
                                        "type": bid.bid_type.value,
                                        "content_preview": bid.content_preview,
                                        "ethical_score": bid.ethical_score,
                                        "urgency": bid.urgency,
                                    }
                                )
                            }
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
            "estimated_processing_time": (self.bid_queue.index(bid) + 1) * 30,  # seconds
        }

    async def process_attention_transaction(self, bid_id: str, user_consent: bool) -> dict[str, Any]:
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
                "transaction_id": f"tx_{datetime.now(timezone.utc).timestamp()}",
                "bid_id": bid_id,
                "user_id": bid.target_user_id,
                "amount": bid.bid_amount,
                "token_type": bid.bid_type.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
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

    async def calculate_attention_value(self, user_id: str, context: dict[str, Any]) -> dict[str, Any]:
        """Calculate fair market value for user's attention"""
        base_value = 100.0  # Base attention value

        # Factors that affect value
        factors = {
            "time_of_day": self._time_of_day_multiplier(datetime.now(timezone.utc)),
            "cognitive_load": 1.0 - context.get("cognitive_load", 0.5),
            "emotional_state": self._emotional_value_multiplier(context.get("emotional_state", {})),
            "rarity": self._calculate_rarity_multiplier(user_id),
            "expertise": context.get("expertise_multiplier", 1.0),
        }

        # Calculate total value
        total_multiplier = 1.0
        for mult in factors.values():
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

    def _emotional_value_multiplier(self, emotional_state: dict[str, float]) -> float:
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
        active_tokens = [t for t in user_tokens if t.expires_at and t.expires_at > datetime.now(timezone.utc)]

        # Fewer active tokens = higher rarity
        if len(active_tokens) == 0:
            return 2.0  # Very rare
        elif len(active_tokens) < 5:
            return 1.5  # Rare
        elif len(active_tokens) < 10:
            return 1.2  # Uncommon
        else:
            return 1.0  # Common

    async def get_market_report(self) -> dict[str, Any]:
        """Generate comprehensive market report"""
        total_tokens = len(self.tokens)
        active_tokens = len([t for t in self.tokens.values() if t.expires_at and t.expires_at > datetime.now(timezone.utc)])

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
            bidder_totals[bid.bidder_id] = bidder_totals.get(bid.bidder_id, 0) + bid.bid_amount

        report["top_bidders"] = sorted(bidder_totals.items(), key=lambda x: x[1], reverse=True)[:5]

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

    def get_user_attention_balance(self, user_id: str) -> dict[str, Any]:
        """Get user's attention token balance and details"""
        balance = self.user_balances.get(user_id, 0)
        user_tokens = [t for t in self.tokens.values() if t.owner_id == user_id]
        active_tokens = [t for t in user_tokens if t.expires_at and t.expires_at > datetime.now(timezone.utc)]

        return {
            "user_id": user_id,
            "total_balance": balance,
            "active_tokens": len(active_tokens),
            "token_details": [
                {
                    "token_id": t.token_id,
                    "type": t.token_type.value,
                    "value": t.value,
                    "qi_value": t.calculate_quantum_value(),
                    "expires_in": ((t.expires_at - datetime.now(timezone.utc)).total_seconds() if t.expires_at else None),
                    "entangled": len(t.entangled_with) > 0,
                }
                for t in active_tokens
            ],
            "market_value": balance * sum(self.market_price.values()) / len(self.market_price),
        }


# Singleton instance
_economics_instance = None


def get_quantum_attention_economics(
    openai_api_key: Optional[str] = None,
) -> QIAttentionEconomics:
    """Get or create the singleton Quantum Attention Economics instance"""
    global _economics_instance
    if _economics_instance is None:
        _economics_instance = QIAttentionEconomics(openai_api_key)
    return _economics_instance
