"""
Universal Symbol Exchange with Privacy Protection
=================================================
Implements privacy-preserving cross-user symbol matching and exchange.
Uses differential privacy and secure multi-party computation concepts.

Based on GPT5 audit recommendations for universal symbolic communication.
"""

import asyncio
import hashlib
import logging
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from lukhas.orchestration.signals.signal_bus import Signal, SignalBus, SignalType

# Import our components

logger = logging.getLogger(__name__)


class ExchangeProtocol(Enum):
    """Privacy-preserving exchange protocols"""

    DIRECT = "direct"  # Direct exchange (trusted users)
    HASHED = "hashed"  # Hash-based matching
    DIFFERENTIAL = "differential"  # Differential privacy
    FEDERATED = "federated"  # Federated learning style
    COLONY = "colony"  # Colony consensus based


@dataclass
class SymbolCandidate:
    """Candidate symbol for universal adoption"""

    symbol: str
    hash_signature: str
    support_count: int = 0
    confidence: float = 0.0
    origins: set[str] = field(default_factory=set)
    contexts: list[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)
    adoption_rate: float = 0.0


@dataclass
class ExchangeSession:
    """A symbol exchange session between users"""

    session_id: str
    participants: set[str]
    protocol: ExchangeProtocol
    symbols_exchanged: int = 0
    privacy_budget: float = 1.0  # Differential privacy budget
    started_at: float = field(default_factory=time.time)
    consensus_threshold: float = 0.7


class UniversalSymbolExchange:
    """
    Manages privacy-preserving symbol exchange between users.
    Discovers common symbolic patterns while protecting individual privacy.
    """

    def __init__(self, signal_bus: Optional[SignalBus] = None):
        self.signal_bus = signal_bus or SignalBus()

        # Exchange tracking
        self.active_sessions: dict[str, ExchangeSession] = {}
        self.symbol_candidates: dict[str, SymbolCandidate] = {}
        self.user_contributions: dict[str, set[str]] = defaultdict(set)

        # Privacy settings
        self.min_k_anonymity = 3  # Minimum users before revealing symbol
        self.noise_factor = 0.1  # Noise for differential privacy
        self.hash_rounds = 1000  # Rounds for hash computation

        # Colony integration
        self.colony_validators: list[Any] = []  # Colony instances for validation

        # Universal vocabulary (discovered symbols)
        self.universal_vocabulary: dict[str, float] = {}

    async def initiate_exchange(
        self,
        initiator_id: str,
        participant_ids: list[str],
        protocol: ExchangeProtocol = ExchangeProtocol.HASHED,
    ) -> str:
        """Initiate a symbol exchange session"""
        session_id = hashlib.sha256(f"{initiator_id}:{time.time()}".encode()).hexdigest()[:16]

        session = ExchangeSession(
            session_id=session_id,
            participants=set([initiator_id, *participant_ids]),
            protocol=protocol,
        )

        self.active_sessions[session_id] = session

        # Emit signal about exchange
        await self._emit_signal(
            SignalType.NOVELTY,
            0.3,
            {"action": "exchange_initiated", "protocol": protocol.value},
        )

        logger.info(f"Initiated exchange session {session_id} with {len(participant_ids)} participants")
        return session_id

    async def contribute_symbols(
        self,
        session_id: str,
        user_id: str,
        symbols: dict[str, str],  # symbol -> hashed meaning
    ) -> bool:
        """Contribute symbols to an exchange session"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        if user_id not in session.participants:
            return False

        # Apply privacy protocol
        processed_symbols = await self._apply_privacy_protocol(symbols, session.protocol, session.privacy_budget)

        # Add to candidates
        for symbol, hash_sig in processed_symbols.items():
            if symbol not in self.symbol_candidates:
                self.symbol_candidates[symbol] = SymbolCandidate(symbol=symbol, hash_signature=hash_sig)

            candidate = self.symbol_candidates[symbol]
            candidate.support_count += 1
            candidate.origins.add(user_id)
            candidate.last_seen = time.time()

            # Track user contribution
            self.user_contributions[user_id].add(symbol)

        session.symbols_exchanged += len(processed_symbols)

        # Check for consensus
        await self._check_consensus(session_id)

        return True

    async def _apply_privacy_protocol(
        self, symbols: dict[str, str], protocol: ExchangeProtocol, privacy_budget: float
    ) -> dict[str, str]:
        """Apply privacy-preserving protocol to symbols"""

        if protocol == ExchangeProtocol.DIRECT:
            # No modification for trusted exchange
            return symbols

        elif protocol == ExchangeProtocol.HASHED:
            # Apply additional hashing rounds
            processed = {}
            for symbol, meaning_hash in symbols.items():
                for _ in range(self.hash_rounds):
                    meaning_hash = hashlib.sha256(meaning_hash.encode()).hexdigest()
                processed[symbol] = meaning_hash[:16]  # Truncate for privacy
            return processed

        elif protocol == ExchangeProtocol.DIFFERENTIAL:
            # Add noise for differential privacy
            processed = {}
            for symbol, meaning_hash in symbols.items():
                # Add random symbols with probability based on noise factor
                if random.random() > self.noise_factor:
                    processed[symbol] = meaning_hash

                # Add fake symbols for plausible deniability
                if random.random() < self.noise_factor * privacy_budget:
                    fake_symbol = self._generate_fake_symbol()
                    processed[fake_symbol] = hashlib.sha256(f"fake:{time.time()}".encode()).hexdigest()[:16]

            return processed

        elif protocol == ExchangeProtocol.FEDERATED:
            # Federated learning style - only share aggregated info
            processed = {}
            symbol_list = list(symbols.keys())

            # Share only top-k symbols
            k = min(5, len(symbol_list))
            for symbol in random.sample(symbol_list, k):
                # Generalize the hash
                processed[symbol] = symbols[symbol][:8] + "********"

            return processed

        elif protocol == ExchangeProtocol.COLONY:
            # Use colony consensus for validation
            processed = {}
            for symbol, meaning_hash in symbols.items():
                # Validate through colony (if available)
                if self.colony_validators:
                    is_valid = await self._validate_through_colony(symbol)
                    if is_valid:
                        processed[symbol] = meaning_hash
                else:
                    processed[symbol] = meaning_hash

            return processed

        return symbols

    async def _check_consensus(self, session_id: str):
        """Check if consensus reached for any symbols"""
        session = self.active_sessions.get(session_id)
        if not session:
            return

        discovered_symbols = []

        for symbol, candidate in self.symbol_candidates.items():
            # Check k-anonymity
            if len(candidate.origins) < self.min_k_anonymity:
                continue

            # Calculate confidence
            participation_rate = len(candidate.origins) / len(session.participants)
            candidate.confidence = participation_rate

            # Check threshold
            if participation_rate >= session.consensus_threshold:
                # Symbol discovered!
                discovered_symbols.append(symbol)
                self.universal_vocabulary[symbol] = candidate.confidence

                logger.info(f"Universal symbol discovered: {symbol} (confidence: {candidate.confidence:.2f})")

        if discovered_symbols:
            # Emit discovery signal
            await self._emit_signal(
                SignalType.TRUST,
                0.7,
                {
                    "action": "symbols_discovered",
                    "count": len(discovered_symbols),
                    "symbols": discovered_symbols[:5],  # Share top 5
                },
            )

    async def get_recommendations(self, user_id: str, context: Optional[str] = None) -> list[tuple[str, float]]:
        """Get symbol recommendations for a user"""
        recommendations = []

        # Get user's contributed symbols
        user_symbols = self.user_contributions.get(user_id, set())

        # Find symbols with high confidence not yet adopted by user
        for symbol, confidence in self.universal_vocabulary.items():
            if symbol not in user_symbols and confidence > 0.5:
                # Adjust confidence based on context
                adjusted_confidence = confidence
                if context and symbol in self.symbol_candidates:
                    candidate = self.symbol_candidates[symbol]
                    if context in candidate.contexts:
                        adjusted_confidence *= 1.2  # Boost for matching context

                recommendations.append((symbol, adjusted_confidence))

        # Sort by confidence
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:10]  # Top 10 recommendations

    def get_privacy_metrics(self, session_id: str) -> dict[str, Any]:
        """Get privacy metrics for a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {}

        # Calculate privacy metrics
        total_symbols = len(self.symbol_candidates)
        revealed_symbols = len([s for s, c in self.symbol_candidates.items() if len(c.origins) >= self.min_k_anonymity])

        return {
            "session_id": session_id,
            "protocol": session.protocol.value,
            "privacy_budget_remaining": session.privacy_budget,
            "k_anonymity": self.min_k_anonymity,
            "total_symbols": total_symbols,
            "revealed_symbols": revealed_symbols,
            "privacy_preservation_rate": 1.0 - (revealed_symbols / max(1, total_symbols)),
            "participants": len(session.participants),
            "symbols_exchanged": session.symbols_exchanged,
        }

    async def _validate_through_colony(self, symbol: str) -> bool:
        """Validate symbol through colony consensus"""
        if not self.colony_validators:
            return True

        # Get validation from first available colony
        # In production, would aggregate from multiple colonies
        for colony in self.colony_validators:
            if hasattr(colony, "validate_symbol"):
                try:
                    result = await colony.validate_symbol(symbol)
                    return result.get("valid", True)
                except BaseException:
                    pass

        return True

    def _generate_fake_symbol(self) -> str:
        """Generate a fake symbol for differential privacy"""
        # Use existing emoji ranges
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc symbols
            (0x1F680, 0x1F6FF),  # Transport
            (0x1F900, 0x1F9FF),  # Supplemental symbols
        ]

        range_start, range_end = random.choice(emoji_ranges)
        code_point = random.randint(range_start, range_end)

        try:
            return chr(code_point)
        except BaseException:
            return "❓"  # Fallback

    async def _emit_signal(self, signal_type: SignalType, level: float, metadata: dict):
        """Emit signal through signal bus"""
        if self.signal_bus:
            signal = Signal(
                name=signal_type,
                source="universal_exchange",
                level=level,
                metadata=metadata,
            )
            self.signal_bus.publish(signal)

    def get_universal_stats(self) -> dict[str, Any]:
        """Get statistics about universal symbol adoption"""
        total_candidates = len(self.symbol_candidates)
        adopted_symbols = len(self.universal_vocabulary)

        # Calculate adoption metrics
        avg_confidence = np.mean(list(self.universal_vocabulary.values())) if self.universal_vocabulary else 0

        # Find most popular symbols
        popular_symbols = sorted(
            self.symbol_candidates.items(),
            key=lambda x: x[1].support_count,
            reverse=True,
        )[:5]

        return {
            "total_candidates": total_candidates,
            "adopted_symbols": adopted_symbols,
            "adoption_rate": adopted_symbols / max(1, total_candidates),
            "average_confidence": float(avg_confidence),
            "active_sessions": len(self.active_sessions),
            "total_contributors": len(self.user_contributions),
            "popular_symbols": [
                {
                    "symbol": symbol,
                    "support": candidate.support_count,
                    "confidence": candidate.confidence,
                }
                for symbol, candidate in popular_symbols
            ],
        }


# Demo usage
async def demo_universal_exchange():
    """Demonstrate universal symbol exchange"""

    # Create exchange system
    exchange = UniversalSymbolExchange()

    # Simulate multiple users contributing symbols
    users = ["alice", "bob", "charlie", "diana", "eve"]

    # Initiate exchange session
    session_id = await exchange.initiate_exchange(
        initiator_id="alice",
        participant_ids=users[1:],
        protocol=ExchangeProtocol.DIFFERENTIAL,
    )

    print(f"📡 Started exchange session: {session_id}")

    # Each user contributes their symbols
    common_symbols = {
        "🎯": hashlib.sha256(b"focus").hexdigest()[:16],
        "💪": hashlib.sha256(b"strength").hexdigest()[:16],
        "🌟": hashlib.sha256(b"excellence").hexdigest()[:16],
    }

    for user in users:
        # Add some common and unique symbols
        user_symbols = common_symbols.copy()

        # Add unique symbol
        unique = f"symbol_{user}"
        user_symbols["🔤"] = hashlib.sha256(unique.encode()).hexdigest()[:16]

        # Contribute
        await exchange.contribute_symbols(session_id, user, user_symbols)

    # Check discovered universal symbols
    stats = exchange.get_universal_stats()
    print(f"🌍 Universal symbols discovered: {stats['adopted_symbols']}")
    print(f"📊 Average confidence: {stats['average_confidence']:.2f}")

    # Get recommendations for a user
    recommendations = await exchange.get_recommendations("alice")
    if recommendations:
        print("💡 Recommendations for Alice:")
        for symbol, confidence in recommendations[:3]:
            print(f"  {symbol}: {confidence:.2f}")

    # Check privacy metrics
    privacy = exchange.get_privacy_metrics(session_id)
    print(f"🔒 Privacy preservation rate: {privacy['privacy_preservation_rate']:.1%}")

    return exchange


if __name__ == "__main__":
    asyncio.run(demo_universal_exchange())