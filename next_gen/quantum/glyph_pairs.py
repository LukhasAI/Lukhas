#!/usr/bin/env python3
"""
Quantum Auth Glyph Pairs - Quantum-entangled symbolic authentication
Creates cryptographic pairs of glyphs for secure multi-party authentication ⚛️
"""
from consciousness.qi import qi
import random
import streamlit as st
from datetime import timezone

import base64
import contextlib
import hashlib
import json
import logging
import secrets
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__, timezone)


@dataclass
class GlyphPair:
    """Quantum-entangled glyph pair"""

    pair_id: str
    primary_glyph: str
    secondary_glyph: str
    entanglement_key: str  # Shared cryptographic key
    created_at: datetime
    trust_score: float  # 0.0 to 1.0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def compute_correlation(self, other_pair: "GlyphPair") -> float:
        """Compute quantum correlation with another pair"""
        # Simulate quantum correlation using cryptographic properties
        combined_key = self.entanglement_key + other_pair.entanglement_key
        hash_result = hashlib.sha3_256(combined_key.encode()).digest()

        # Convert to correlation coefficient (-1 to 1)
        correlation = (int.from_bytes(hash_result[:4], "big") / (2**32 - 1)) * 2 - 1
        return correlation

    def measure_state(self, observer_id: str) -> str:
        """Measure quantum state (collapses to deterministic glyph)"""
        # Quantum measurement simulation
        measurement_seed = f"{self.pair_id}_{observer_id}_{datetime.now(timezone.utc).timestamp()}"
        measurement_hash = hashlib.blake3(measurement_seed.encode()).hexdigest()

        # Use hash to determine which glyph is observed
        observed_glyph = self.primary_glyph if int(measurement_hash[0], 16) % 2 == 0 else self.secondary_glyph

        # Update usage statistics
        self.usage_count += 1
        self.last_used = datetime.now(timezone.utc)

        return observed_glyph


@dataclass
class QIAuthentication:
    """Quantum authentication challenge-response"""

    auth_id: str
    challenge_pair: GlyphPair
    response_pair: GlyphPair
    expected_correlation: float
    timestamp: datetime
    challenger_id: str
    respondent_id: str
    verified: bool = False
    verification_time: Optional[datetime] = None


class QIGlyphSystem:
    """
    Quantum-inspired glyph authentication system
    Creates entangled glyph pairs for secure authentication protocols
    """

    # Quantum glyph alphabet - carefully chosen for visual distinctiveness
    QUANTUM_GLYPHS = [
        "🔐",
        "🔓",
        "🗝️",
        "🔑",  # Lock/key family
        "⚛️",
        "🧬",
        "🔬",
        "🧪",  # Science family
        "🪷",
        "🌸",
        "🌺",
        "🌻",  # Flower family
        "💎",
        "💠",
        "🔮",
        "✨",  # Crystal family
        "🌀",
        "🌪️",
        "💫",
        "⭐",  # Motion family
        "🛡️",
        "⚔️",
        "🗡️",
        "🏹",  # Protection family
        "🔥",
        "💧",
        "🌊",
        "❄️",  # Element family
        "🌙",
        "☀️",
        "🌟",
        "🪐",  # Celestial family
    ]

    # Entanglement rules - which glyphs can be paired
    ENTANGLEMENT_RULES = {
        "lock_key": (["🔐", "🔓"], ["🗝️", "🔑"]),
        "science": (["⚛️", "🧬"], ["🔬", "🧪"]),
        "nature": (["🪷", "🌸"], ["🌺", "🌻"]),
        "crystal": (["💎", "💠"], ["🔮", "✨"]),
        "motion": (["🌀", "🌪️"], ["💫", "⭐"]),
        "protection": (["🛡️", "⚔️"], ["🗡️", "🏹"]),
        "element": (["🔥", "💧"], ["🌊", "❄️"]),
        "celestial": (["🌙", "☀️"], ["🌟", "🪐"]),
    }

    def __init__(self, keystore_path: str = "qi_glyphs.json"):
        self.keystore_path = Path(keystore_path)
        self.glyph_pairs: dict[str, GlyphPair] = {}
        self.entanglement_network: dict[str, set[str]] = defaultdict(set)
        self.authentication_log: list[QIAuthentication] = []
        self.correlation_matrix: dict[tuple[str, str], float] = {}

        # Load existing pairs
        self._load_keystore()

        logger.info("⚛️ Quantum Glyph System initialized")
        logger.info(f"   Glyph alphabet: {len(self.QUANTUM_GLYPHS)} symbols")
        logger.info(f"   Entanglement rules: {len(self.ENTANGLEMENT_RULES)} families")
        logger.info(f"   Existing pairs: {len(self.glyph_pairs)}")

    def _load_keystore(self):
        """Load glyph pairs from storage"""
        if self.keystore_path.exists():
            try:
                with open(self.keystore_path) as f:
                    data = json.load(f)

                # Load glyph pairs
                for pair_id, pair_data in data.get("pairs", {}).items():
                    self.glyph_pairs[pair_id] = GlyphPair(
                        pair_id=pair_data["pair_id"],
                        primary_glyph=pair_data["primary_glyph"],
                        secondary_glyph=pair_data["secondary_glyph"],
                        entanglement_key=pair_data["entanglement_key"],
                        created_at=datetime.fromisoformat(pair_data["created_at"]),
                        trust_score=pair_data.get("trust_score", 0.5),
                        usage_count=pair_data.get("usage_count", 0),
                        last_used=(
                            datetime.fromisoformat(pair_data["last_used"]) if pair_data.get("last_used") else None
                        ),
                        metadata=pair_data.get("metadata", {}),
                    )

                # Rebuild correlation matrix
                self._rebuild_correlation_matrix()

            except Exception as e:
                logger.warning(f"Could not load quantum keystore: {e}")

    def _save_keystore(self):
        """Save glyph pairs to storage"""
        data = {
            "version": "1.0.0",
            "created": datetime.now(timezone.utc).isoformat(),
            "qi_system": True,
            "pairs": {},
            "statistics": {
                "total_pairs": len(self.glyph_pairs),
                "total_authentications": len(self.authentication_log),
                "correlation_entries": len(self.correlation_matrix),
            },
        }

        # Save pairs
        for pair_id, pair in self.glyph_pairs.items():
            data["pairs"][pair_id] = {
                "pair_id": pair.pair_id,
                "primary_glyph": pair.primary_glyph,
                "secondary_glyph": pair.secondary_glyph,
                "entanglement_key": pair.entanglement_key,
                "created_at": pair.created_at.isoformat(),
                "trust_score": pair.trust_score,
                "usage_count": pair.usage_count,
                "last_used": pair.last_used.isoformat() if pair.last_used else None,
                "metadata": pair.metadata,
            }

        with open(self.keystore_path, "w") as f:
            json.dump(data, f, indent=2)

    def create_entangled_pair(self, family: Optional[str] = None) -> Optional[GlyphPair]:
        """Create a new quantum-entangled glyph pair"""
        if family and family not in self.ENTANGLEMENT_RULES:
            logger.error(f"Unknown entanglement family: {family}")
            return None

        # Select glyph family
        if family:
            primary_pool, secondary_pool = self.ENTANGLEMENT_RULES[family]
        else:
            # Random family selection
            family = secrets.choice(list(self.ENTANGLEMENT_RULES.keys()))
            primary_pool, secondary_pool = self.ENTANGLEMENT_RULES[family]

        # Select glyphs
        primary_glyph = secrets.choice(primary_pool)
        secondary_glyph = secrets.choice(secondary_pool)

        # Generate entanglement key
        entropy = secrets.token_bytes(32)
        entanglement_key = base64.b64encode(entropy).decode()

        # Create pair
        pair_id = f"qpair_{datetime.now(timezone.utc).timestamp()}_{family}"
        pair = GlyphPair(
            pair_id=pair_id,
            primary_glyph=primary_glyph,
            secondary_glyph=secondary_glyph,
            entanglement_key=entanglement_key,
            created_at=datetime.now(timezone.utc),
            trust_score=1.0,  # New pairs start with full trust
            metadata={"family": family, "entropy_bits": 256},
        )

        # Store pair
        self.glyph_pairs[pair_id] = pair
        self.entanglement_network[pair_id] = set()

        # Update correlations
        self._update_correlations(pair)

        # Save keystore
        self._save_keystore()

        logger.info(f"⚛️ Created entangled pair: {primary_glyph}↔{secondary_glyph}")
        logger.info(f"   Pair ID: {pair_id}")
        logger.info(f"   Family: {family}")

        return pair

    def _update_correlations(self, new_pair: GlyphPair):
        """Update correlation matrix with new pair"""
        for pair_id, existing_pair in self.glyph_pairs.items():
            if pair_id != new_pair.pair_id:
                correlation = new_pair.compute_correlation(existing_pair)
                self.correlation_matrix[(new_pair.pair_id, pair_id)] = correlation
                self.correlation_matrix[(pair_id, new_pair.pair_id)] = correlation

                # Add to entanglement network if highly correlated
                if abs(correlation) > 0.7:
                    self.entanglement_network[new_pair.pair_id].add(pair_id)
                    self.entanglement_network[pair_id].add(new_pair.pair_id)

    def _rebuild_correlation_matrix(self):
        """Rebuild the complete correlation matrix"""
        self.correlation_matrix.clear()
        pairs = list(self.glyph_pairs.values())

        for i, pair1 in enumerate(pairs):
            for _j, pair2 in enumerate(pairs[i + 1 :], i + 1):
                correlation = pair1.compute_correlation(pair2)
                self.correlation_matrix[(pair1.pair_id, pair2.pair_id)] = correlation
                self.correlation_matrix[(pair2.pair_id, pair1.pair_id)] = correlation

    def create_authentication_challenge(self, challenger_id: str, respondent_id: str) -> Optional[QIAuthentication]:
        """Create quantum authentication challenge"""
        if len(self.glyph_pairs) < 2:
            logger.error("Need at least 2 glyph pairs for authentication")
            return None

        # Select two pairs for challenge-response
        pair_ids = list(self.glyph_pairs.keys())
        challenge_pair_id = secrets.choice(pair_ids)

        # Find a correlated pair for response
        response_candidates = [
            pid for pid in pair_ids if pid != challenge_pair_id and (challenge_pair_id, pid) in self.correlation_matrix
        ]

        if not response_candidates:
            # No correlated pairs, use random
            response_candidates = [pid for pid in pair_ids if pid != challenge_pair_id]

        response_pair_id = secrets.choice(response_candidates)

        challenge_pair = self.glyph_pairs[challenge_pair_id]
        response_pair = self.glyph_pairs[response_pair_id]

        # Get expected correlation
        expected_correlation = self.correlation_matrix.get((challenge_pair_id, response_pair_id), 0.0)

        # Create authentication
        auth_id = f"qauth_{datetime.now(timezone.utc).timestamp()}"
        auth = QIAuthentication(
            auth_id=auth_id,
            challenge_pair=challenge_pair,
            response_pair=response_pair,
            expected_correlation=expected_correlation,
            timestamp=datetime.now(timezone.utc),
            challenger_id=challenger_id,
            respondent_id=respondent_id,
        )

        self.authentication_log.append(auth)

        logger.info(f"🎯 Created quantum auth challenge: {auth_id}")
        logger.info(f"   Challenge: {challenge_pair.primary_glyph}↔{challenge_pair.secondary_glyph}")
        logger.info(f"   Response: {response_pair.primary_glyph}↔{response_pair.secondary_glyph}")
        logger.info(f"   Expected correlation: {expected_correlation:.3f}")

        return auth

    def verify_authentication(self, auth_id: str, challenge_measurement: str, response_measurement: str) -> bool:
        """Verify quantum authentication response"""
        # Find authentication
        auth = None
        for a in self.authentication_log:
            if a.auth_id == auth_id:
                auth = a
                break

        if not auth:
            logger.error(f"Authentication {auth_id} not found")
            return False

        if auth.verified:
            logger.warning(f"Authentication {auth_id} already verified")
            return True

        # Verify measurements are valid for the pairs
        challenge_valid = (
            challenge_measurement == auth.challenge_pair.primary_glyph
            or challenge_measurement == auth.challenge_pair.secondary_glyph
        )

        response_valid = (
            response_measurement == auth.response_pair.primary_glyph
            or response_measurement == auth.response_pair.secondary_glyph
        )

        if not (challenge_valid and response_valid):
            logger.error("Invalid glyph measurements")
            return False

        # Calculate correlation between measurements
        measurement_correlation = self._calculate_measurement_correlation(
            challenge_measurement,
            response_measurement,
            auth.challenge_pair,
            auth.response_pair,
        )

        # Verify correlation matches expectation (within tolerance)
        correlation_diff = abs(measurement_correlation - auth.expected_correlation)
        tolerance = 0.3  # Allow some quantum uncertainty

        if correlation_diff <= tolerance:
            auth.verified = True
            auth.verification_time = datetime.now(timezone.utc)

            # Update trust scores
            auth.challenge_pair.trust_score = min(1.0, auth.challenge_pair.trust_score + 0.1)
            auth.response_pair.trust_score = min(1.0, auth.response_pair.trust_score + 0.1)

            logger.info(f"✅ Quantum authentication verified: {auth_id}")
            logger.info(f"   Correlation match: {measurement_correlation:.3f} ≈ {auth.expected_correlation:.3f}")

            self._save_keystore()
            return True
        else:
            logger.warning(f"❌ Quantum authentication failed: {auth_id}")
            logger.warning(f"   Correlation mismatch: {measurement_correlation:.3f} vs {auth.expected_correlation:.3f}")

            # Reduce trust scores
            auth.challenge_pair.trust_score = max(0.0, auth.challenge_pair.trust_score - 0.2)
            auth.response_pair.trust_score = max(0.0, auth.response_pair.trust_score - 0.2)

            return False

    def _calculate_measurement_correlation(
        self,
        challenge_glyph: str,
        response_glyph: str,
        challenge_pair: GlyphPair,
        response_pair: GlyphPair,
    ) -> float:
        """Calculate correlation between specific glyph measurements"""
        # Encode glyph states as binary
        challenge_state = 1 if challenge_glyph == challenge_pair.primary_glyph else 0
        response_state = 1 if response_glyph == response_pair.primary_glyph else 0

        # Simple correlation calculation
        if challenge_state == response_state:
            return 0.8  # Positive correlation
        else:
            return -0.8  # Negative correlation

    def get_entangled_pairs(self, pair_id: str) -> list[GlyphPair]:
        """Get all pairs entangled with the given pair"""
        if pair_id not in self.entanglement_network:
            return []

        entangled_ids = self.entanglement_network[pair_id]
        return [self.glyph_pairs[pid] for pid in entangled_ids if pid in self.glyph_pairs]

    def measure_glyph_state(self, pair_id: str, observer_id: str) -> Optional[str]:
        """Measure the quantum state of a glyph pair"""
        if pair_id not in self.glyph_pairs:
            return None

        pair = self.glyph_pairs[pair_id]
        measured_glyph = pair.measure_state(observer_id)

        logger.info(f"📏 Quantum measurement: {pair_id} → {measured_glyph}")
        logger.info(f"   Observer: {observer_id}")

        self._save_keystore()
        return measured_glyph

    def get_system_report(self) -> dict[str, Any]:
        """Generate comprehensive system report"""
        # Trust distribution
        trust_scores = [pair.trust_score for pair in self.glyph_pairs.values()]
        avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0

        # Usage statistics
        total_usage = sum(pair.usage_count for pair in self.glyph_pairs.values())

        # Authentication statistics
        verified_auths = sum(1 for auth in self.authentication_log if auth.verified)

        # Glyph family distribution
        family_dist = {}
        for pair in self.glyph_pairs.values():
            family = pair.metadata.get("family", "unknown")
            family_dist[family] = family_dist.get(family, 0) + 1

        return {
            "total_pairs": len(self.glyph_pairs),
            "entanglement_connections": sum(len(connections) for connections in self.entanglement_network.values())
            // 2,
            "correlation_entries": len(self.correlation_matrix),
            "average_trust_score": avg_trust,
            "total_measurements": total_usage,
            "authentications": {
                "total": len(self.authentication_log),
                "verified": verified_auths,
                "success_rate": (verified_auths / len(self.authentication_log) if self.authentication_log else 0),
            },
            "family_distribution": family_dist,
            "qi_alphabet_size": len(self.QUANTUM_GLYPHS),
            "entanglement_families": len(self.ENTANGLEMENT_RULES),
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Create quantum glyph system
    qgs = QIGlyphSystem(keystore_path="demo_qi.json")

    print("⚛️ Quantum Glyph Authentication Demo")
    print("=" * 60)

    # Create some entangled pairs
    print("\n🔗 Creating entangled pairs...")
    pair1 = qgs.create_entangled_pair("lock_key")
    pair2 = qgs.create_entangled_pair("science")
    pair3 = qgs.create_entangled_pair("crystal")

    # Test quantum measurements
    print("\n📏 Testing quantum measurements...")
    if pair1:
        measurement1 = qgs.measure_glyph_state(pair1.pair_id, "alice")
        measurement2 = qgs.measure_glyph_state(pair1.pair_id, "bob")
        print(f"   Alice measured: {measurement1}")
        print(f"   Bob measured: {measurement2}")

    # Test authentication
    print("\n🎯 Testing quantum authentication...")
    auth = qgs.create_authentication_challenge("alice", "bob")
    if auth:
        # Simulate measurements
        challenge_measurement = qgs.measure_glyph_state(auth.challenge_pair.pair_id, "alice")
        response_measurement = qgs.measure_glyph_state(auth.response_pair.pair_id, "bob")

        if challenge_measurement and response_measurement:
            verified = qgs.verify_authentication(auth.auth_id, challenge_measurement, response_measurement)
            print(f"   Authentication result: {'✅ VERIFIED' if verified else '❌ FAILED'}")

    # Generate system report
    print("\n📊 Quantum System Report:")
    report = qgs.get_system_report()
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"     {k}: {v}")
        else:
            print(f"   {key}: {value}")

    # Cleanup demo file
    import os

    with contextlib.suppress(BaseException):
        os.unlink("demo_qi.json")
