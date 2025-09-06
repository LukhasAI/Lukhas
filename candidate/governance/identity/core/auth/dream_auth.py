"""
Dream-Based Authentication System for LUKHAS Tier 5

This module implements dream-based authentication for the highest tier of LUKHAS
identity system. It uses dream patterns, symbolic dream content, and dream-state
consciousness markers for authentication.

Features:
- Dream pattern recognition and encoding
- Symbolic dream content analysis
- Dream state consciousness validation
- Dream seed token generation
- Dream replay verification
- Integration with dream engine and memory systems

Author: LUKHAS Identity Team
Version: 1.0.0
"""

import hashlib
import json
import logging
import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

# Import LUKHAS components
try:
    from ...auth_backend.pqc_crypto_engine import PQCCryptoEngine
    from ...backend.dream_engine.dream_injector import create_dream_proposal
except ImportError:
    print("Warning: Some LUKHAS components not available. Dream authentication may be limited.", timezone)

logger = logging.getLogger("LUKHAS_DREAM_AUTH")


class DreamStateType(Enum):
    """Types of dream states for authentication"""

    REM = "rem"  # Rapid Eye Movement sleep
    LUCID = "lucid"  # Lucid dreaming
    HYPNAGOGIC = "hypnagogic"  # Falling asleep state
    HYPNOPOMPIC = "hypnopompic"  # Waking up state
    DAYDREAM = "daydream"  # Conscious dreaming
    VISION = "vision"  # Visionary experiences
    MEDITATION = "meditation"  # Deep meditative states


class DreamSymbolType(Enum):
    """Types of dream symbols"""

    ARCHETYPE = "archetype"  # Jungian archetypes
    PERSONAL = "personal"  # Personal symbols
    CULTURAL = "cultural"  # Cultural symbols
    UNIVERSAL = "universal"  # Universal symbols
    GEOMETRIC = "geometric"  # Geometric patterns
    NUMERIC = "numeric"  # Number patterns
    COLOR = "color"  # Color symbolism
    NARRATIVE = "narrative"  # Story elements


@dataclass
class DreamPattern:
    """Pattern representing a dream sequence"""

    pattern_id: str
    dream_state: DreamStateType
    symbolic_content: list[str]  # Dream symbols
    emotional_signature: dict[str, float]  # Emotional content
    consciousness_markers: dict[str, float]  # Consciousness state during dream
    temporal_structure: list[str]  # Sequence of dream events
    lucidity_level: float  # 0.0 (unconscious) to 1.0 (fully lucid)
    vividness_score: float  # How vivid the dream was
    personal_significance: float  # Personal meaning score
    archetypal_content: dict[str, float]  # Archetypal symbols present
    dream_timestamp: datetime
    verification_hash: str  # Hash for integrity


@dataclass
class DreamSeed:
    """Seed for generating dream-based authentication challenges"""

    seed_id: str
    symbolic_prompt: str  # Symbolic prompt for dream generation
    expected_elements: list[str]  # Expected dream elements
    consciousness_target: dict[str, float]  # Target consciousness state
    difficulty_level: float  # 0.0 (easy) to 1.0 (transcendent)
    cultural_context: Optional[str]
    created_at: datetime
    expires_at: datetime
    usage_count: int = 0


@dataclass
class DreamAuthenticationResult:
    """Result of dream-based authentication"""

    success: bool
    confidence_score: float
    dream_pattern_match: float
    symbolic_alignment: float
    consciousness_coherence: float
    lucidity_verification: bool
    archetypal_resonance: float
    personal_significance_match: float
    qi_verified: bool
    dream_metadata: dict[str, Any]
    error_message: Optional[str] = None


class DreamAuthenticationEngine:
    """
    Dream-Based Authentication Engine

    Provides dream-pattern-based authentication for Tier 5 users,
    using symbolic dream content and consciousness states.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Initialize crypto engine
        self.pqc_engine = PQCCryptoEngine()

        # Dream pattern storage
        self.dream_patterns: dict[str, list[DreamPattern]] = {}  # lambda_id -> patterns

        # Dream seeds storage
        self.dream_seeds: dict[str, list[DreamSeed]] = {}  # lambda_id -> seeds

        # Archetypal symbol library
        self.archetypal_symbols = {
            "hero": {"significance": 0.9, "universality": 0.8},
            "shadow": {"significance": 0.8, "universality": 0.7},
            "anima": {"significance": 0.7, "universality": 0.6},
            "animus": {"significance": 0.7, "universality": 0.6},
            "wise_old_man": {"significance": 0.8, "universality": 0.7},
            "great_mother": {"significance": 0.8, "universality": 0.8},
            "tree_of_life": {"significance": 0.9, "universality": 0.9},
            "mandala": {"significance": 0.8, "universality": 0.7},
            "spiral": {"significance": 0.7, "universality": 0.8},
            "infinity": {"significance": 0.6, "universality": 0.9},
            "phoenix": {"significance": 0.8, "universality": 0.6},
            "ouroboros": {"significance": 0.7, "universality": 0.5},
        }

        # Dream state consciousness signatures
        self.dream_consciousness_signatures = {
            DreamStateType.REM: {
                "consciousness_level": 0.3,
                "neural_synchrony": 0.8,
                "emotional_intensity": 0.7,
                "symbolic_processing": 0.9,
            },
            DreamStateType.LUCID: {
                "consciousness_level": 0.8,
                "neural_synchrony": 0.9,
                "emotional_intensity": 0.6,
                "symbolic_processing": 0.8,
            },
            DreamStateType.MEDITATION: {
                "consciousness_level": 0.9,
                "neural_synchrony": 0.95,
                "emotional_intensity": 0.4,
                "symbolic_processing": 0.7,
            },
        }

        # Cultural dream symbol mappings
        self.cultural_dream_symbols = {
            "western": ["eagle", "cross", "tower", "bridge", "castle"],
            "eastern": ["dragon", "lotus", "mountain", "river", "temple"],
            "indigenous": ["eagle", "bear", "wolf", "tree", "fire"],
            "universal": ["water", "light", "darkness", "circle", "spiral"],
        }

        logger.info("Dream Authentication Engine initialized")

    def register_dream_pattern(self, lambda_id: str, dream_data: dict[str, Any]) -> DreamPattern:
        """
        Register a new dream pattern for authentication

        Args:
            lambda_id: User's Lambda ID
            dream_data: Dream content and metadata

        Returns:
            Created DreamPattern
        """
        # Extract dream elements
        symbolic_content = self._extract_symbolic_content(dream_data.get("narrative", ""))
        emotional_signature = self._analyze_emotional_content(dream_data)
        consciousness_markers = self._extract_consciousness_markers(dream_data)
        temporal_structure = self._analyze_temporal_structure(dream_data)
        archetypal_content = self._identify_archetypal_content(symbolic_content)

        # Calculate scores
        lucidity_level = dream_data.get("lucidity_level", 0.0)
        vividness_score = dream_data.get("vividness_score", 0.5)
        personal_significance = dream_data.get("personal_significance", 0.5)

        # Create verification hash
        dream_content = json.dumps(
            {
                "symbols": symbolic_content,
                "emotions": emotional_signature,
                "temporal": temporal_structure,
                "timestamp": time.time(),
            },
            sort_keys=True,
        )
        verification_hash = hashlib.sha3_256(dream_content.encode()).hexdigest()

        # Create dream pattern
        pattern = DreamPattern(
            pattern_id=hashlib.sha256(f"{lambda_id}_{time.time()}".encode()).hexdigest()[:16],
            dream_state=DreamStateType(dream_data.get("dream_state", "rem")),
            symbolic_content=symbolic_content,
            emotional_signature=emotional_signature,
            consciousness_markers=consciousness_markers,
            temporal_structure=temporal_structure,
            lucidity_level=lucidity_level,
            vividness_score=vividness_score,
            personal_significance=personal_significance,
            archetypal_content=archetypal_content,
            dream_timestamp=datetime.now(timezone.utc),
            verification_hash=verification_hash,
        )

        # Store pattern
        if lambda_id not in self.dream_patterns:
            self.dream_patterns[lambda_id] = []
        self.dream_patterns[lambda_id].append(pattern)

        # Create dream proposal for governance
        try:
            create_dream_proposal(
                dream_title=f"Dream Pattern Registration: {pattern.pattern_id}",
                emotional_index=(
                    sum(emotional_signature.values()) / len(emotional_signature) if emotional_signature else 0.5
                ),
                summary=f"User {lambda_id} registered dream pattern with {len(symbolic_content)} symbols",
                dream_id=pattern.pattern_id,
            )
        except Exception as e:
            logger.warning(f"Could not create dream proposal: {e}")

        logger.info(f"Registered dream pattern {pattern.pattern_id} for {lambda_id}")
        return pattern

    def create_dream_seed(self, lambda_id: str, difficulty_level: float = 0.8) -> DreamSeed:
        """
        Create a dream seed for authentication challenge

        Args:
            lambda_id: User's Lambda ID
            difficulty_level: Challenge difficulty (0.0-1.0)

        Returns:
            Created DreamSeed
        """
        # Get user's dream patterns for personalization
        user_patterns = self.dream_patterns.get(lambda_id, [])

        # Select symbolic elements based on user's dream history
        if user_patterns:
            # Use symbols from user's previous dreams
            all_symbols = []
            for pattern in user_patterns[-5:]:  # Last 5 dreams
                all_symbols.extend(pattern.symbolic_content)

            # Select most common symbols
            symbol_counts = {}
            for symbol in all_symbols:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

            common_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)
            expected_elements = [symbol for symbol, _ in common_symbols[:3]]
        else:
            # Use universal symbols for new users
            expected_elements = random.sample(self.cultural_dream_symbols["universal"], 3)

        # Create symbolic prompt
        symbolic_prompt = self._generate_symbolic_prompt(expected_elements, difficulty_level)

        # Set consciousness target based on difficulty
        if difficulty_level < 0.3:
            consciousness_target = self.dream_consciousness_signatures[DreamStateType.REM]
        elif difficulty_level < 0.7:
            consciousness_target = self.dream_consciousness_signatures[DreamStateType.LUCID]
        else:
            consciousness_target = self.dream_consciousness_signatures[DreamStateType.MEDITATION]

        # Create dream seed
        seed = DreamSeed(
            seed_id=hashlib.sha256(f"{lambda_id}_{time.time()}".encode()).hexdigest()[:16],
            symbolic_prompt=symbolic_prompt,
            expected_elements=expected_elements,
            consciousness_target=consciousness_target,
            difficulty_level=difficulty_level,
            cultural_context=None,  # Auto-detect from user profile
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),  # 24-hour expiry
        )

        # Store seed
        if lambda_id not in self.dream_seeds:
            self.dream_seeds[lambda_id] = []
        self.dream_seeds[lambda_id].append(seed)

        logger.info(f"Created dream seed {seed.seed_id} for {lambda_id}")
        return seed

    def authenticate_with_dream(
        self, lambda_id: str, dream_response: dict[str, Any], seed_id: str
    ) -> DreamAuthenticationResult:
        """
        Authenticate using dream response to seed

        Args:
            lambda_id: User's Lambda ID
            dream_response: User's dream response
            seed_id: Dream seed ID used for challenge

        Returns:
            DreamAuthenticationResult
        """
        try:
            # Find the dream seed
            user_seeds = self.dream_seeds.get(lambda_id, [])
            seed = None
            for s in user_seeds:
                if s.seed_id == seed_id:
                    seed = s
                    break

            if not seed:
                return DreamAuthenticationResult(
                    success=False,
                    confidence_score=0.0,
                    dream_pattern_match=0.0,
                    symbolic_alignment=0.0,
                    consciousness_coherence=0.0,
                    lucidity_verification=False,
                    archetypal_resonance=0.0,
                    personal_significance_match=0.0,
                    qi_verified=False,
                    dream_metadata={},
                    error_message="Dream seed not found",
                )

            # Check seed expiry
            if datetime.now(timezone.utc) > seed.expires_at:
                return DreamAuthenticationResult(
                    success=False,
                    confidence_score=0.0,
                    dream_pattern_match=0.0,
                    symbolic_alignment=0.0,
                    consciousness_coherence=0.0,
                    lucidity_verification=False,
                    archetypal_resonance=0.0,
                    personal_significance_match=0.0,
                    qi_verified=False,
                    dream_metadata={},
                    error_message="Dream seed expired",
                )

            # Parse dream response
            dream_narrative = dream_response.get("narrative", "")
            reported_consciousness = dream_response.get("consciousness_state", {})
            dream_response.get("lucidity_level", 0.0)

            # Extract symbolic content from response
            response_symbols = self._extract_symbolic_content(dream_narrative)

            # Calculate symbolic alignment with expected elements
            symbolic_alignment = self._calculate_symbolic_alignment(response_symbols, seed.expected_elements)

            # Calculate consciousness coherence
            consciousness_coherence = self._calculate_consciousness_coherence(
                reported_consciousness, seed.consciousness_target
            )

            # Verify lucidity claims
            lucidity_verification = self._verify_lucidity_claims(dream_response, seed.difficulty_level)

            # Calculate archetypal resonance
            archetypal_resonance = self._calculate_archetypal_resonance(response_symbols)

            # Compare with user's historical dream patterns
            user_patterns = self.dream_patterns.get(lambda_id, [])
            dream_pattern_match = self._calculate_pattern_match(dream_response, user_patterns)

            # Calculate personal significance match
            personal_significance_match = self._calculate_personal_significance(dream_response, user_patterns)

            # Quantum verification
            qi_verified = self._verify_dream_response_integrity(dream_response)

            # Calculate overall confidence score
            confidence_score = self._calculate_dream_confidence_score(
                {
                    "symbolic_alignment": symbolic_alignment,
                    "consciousness_coherence": consciousness_coherence,
                    "lucidity_verification": lucidity_verification,
                    "archetypal_resonance": archetypal_resonance,
                    "pattern_match": dream_pattern_match,
                    "personal_significance": personal_significance_match,
                }
            )

            # Determine success based on difficulty level
            success_threshold = 0.6 + (seed.difficulty_level * 0.3)  # 0.6 to 0.9
            success = confidence_score >= success_threshold and qi_verified

            # Update seed usage
            seed.usage_count += 1

            return DreamAuthenticationResult(
                success=success,
                confidence_score=confidence_score,
                dream_pattern_match=dream_pattern_match,
                symbolic_alignment=symbolic_alignment,
                consciousness_coherence=consciousness_coherence,
                lucidity_verification=lucidity_verification,
                archetypal_resonance=archetypal_resonance,
                personal_significance_match=personal_significance_match,
                qi_verified=qi_verified,
                dream_metadata={
                    "seed_id": seed_id,
                    "difficulty_level": seed.difficulty_level,
                    "success_threshold": success_threshold,
                    "response_symbols_count": len(response_symbols),
                    "expected_elements_count": len(seed.expected_elements),
                    "consciousness_target": seed.consciousness_target,
                },
            )

        except Exception as e:
            logger.error(f"Dream authentication error: {e}")
            return DreamAuthenticationResult(
                success=False,
                confidence_score=0.0,
                dream_pattern_match=0.0,
                symbolic_alignment=0.0,
                consciousness_coherence=0.0,
                lucidity_verification=False,
                archetypal_resonance=0.0,
                personal_significance_match=0.0,
                qi_verified=False,
                dream_metadata={},
                error_message=str(e),
            )

    def _extract_symbolic_content(self, narrative: str) -> list[str]:
        """Extract symbolic content from dream narrative"""
        # This is a simplified symbol extraction
        # In a full implementation, this would use NLP and symbol recognition

        # Common dream symbols to look for
        dream_symbols = [
            "water",
            "fire",
            "light",
            "darkness",
            "tree",
            "mountain",
            "river",
            "ocean",
            "bird",
            "eagle",
            "snake",
            "wolf",
            "bear",
            "lion",
            "butterfly",
            "spider",
            "house",
            "castle",
            "bridge",
            "tower",
            "door",
            "window",
            "mirror",
            "key",
            "circle",
            "square",
            "triangle",
            "spiral",
            "star",
            "moon",
            "sun",
            "rainbow",
            "mother",
            "father",
            "child",
            "stranger",
            "teacher",
            "guide",
            "shadow",
            "flying",
            "falling",
            "running",
            "dancing",
            "singing",
            "healing",
            "fighting",
        ]

        found_symbols = []
        narrative_lower = narrative.lower()

        for symbol in dream_symbols:
            if symbol in narrative_lower:
                found_symbols.append(symbol)

        return found_symbols

    def _analyze_emotional_content(self, dream_data: dict[str, Any]) -> dict[str, float]:
        """Analyze emotional content of dream"""
        # Extract emotions from dream data
        emotions = dream_data.get("emotions", {})

        # Default emotional signature if not provided
        if not emotions:
            emotions = {
                "joy": 0.5,
                "fear": 0.3,
                "wonder": 0.6,
                "confusion": 0.4,
                "peace": 0.5,
            }

        return emotions

    def _extract_consciousness_markers(self, dream_data: dict[str, Any]) -> dict[str, float]:
        """Extract consciousness markers from dream"""
        return {
            "awareness_level": dream_data.get("awareness_level", 0.5),
            "control_level": dream_data.get("control_level", 0.3),
            "memory_clarity": dream_data.get("memory_clarity", 0.4),
            "logical_coherence": dream_data.get("logical_coherence", 0.2),
        }

    def _analyze_temporal_structure(self, dream_data: dict[str, Any]) -> list[str]:
        """Analyze temporal structure of dream"""
        # Extract sequence of events
        events = dream_data.get("events", [])
        if not events:
            # Parse from narrative if events not provided
            dream_data.get("narrative", "")
            # This would use NLP to extract event sequence
            events = ["beginning", "development", "climax", "resolution"]

        return events

    def _identify_archetypal_content(self, symbols: list[str]) -> dict[str, float]:
        """Identify archetypal content in dream symbols"""
        archetypal_content = {}

        for symbol in symbols:
            if symbol in self.archetypal_symbols:
                archetypal_content[symbol] = self.archetypal_symbols[symbol]["significance"]

        return archetypal_content

    def _generate_symbolic_prompt(self, expected_elements: list[str], difficulty: float) -> str:
        """Generate symbolic prompt for dream challenge"""
        prompts = [
            f"In your dreams tonight, seek the wisdom of the {expected_elements[0]}",
            f"Let your dreams reveal the connection between {expected_elements[0]} and {expected_elements[1] if len(expected_elements) > 1 else 'light'}",
            f"Dream of a journey where you encounter {', '.join(expected_elements)}",
        ]

        if difficulty > 0.8:
            return f"In the deepest meditation of sleep, unite your consciousness with the eternal symbols: {', '.join(expected_elements)}. Let your lucid awareness dance with these archetypal forms."
        elif difficulty > 0.5:
            return f"Tonight, dream lucidly of {', '.join(expected_elements)}. Be aware that you are dreaming and interact consciously with these symbols."
        else:
            return random.choice(prompts)

    def _calculate_symbolic_alignment(self, response_symbols: list[str], expected_elements: list[str]) -> float:
        """Calculate alignment between response symbols and expected elements"""
        if not expected_elements:
            return 1.0

        matches = 0
        for element in expected_elements:
            if element in response_symbols:
                matches += 1
            else:
                # Check for symbolic equivalents
                equivalents = self._get_symbolic_equivalents(element)
                if any(equiv in response_symbols for equiv in equivalents):
                    matches += 0.5

        return matches / len(expected_elements)

    def _get_symbolic_equivalents(self, symbol: str) -> list[str]:
        """Get symbolic equivalents for a dream symbol"""
        equivalents_map = {
            "water": ["ocean", "river", "lake", "rain", "tears"],
            "light": ["sun", "star", "fire", "candle", "dawn"],
            "tree": ["forest", "branch", "leaf", "root", "wood"],
            "bird": ["eagle", "dove", "raven", "owl", "phoenix"],
            "mountain": ["hill", "peak", "cliff", "stone", "rock"],
        }
        return equivalents_map.get(symbol, [])

    def _calculate_consciousness_coherence(self, reported: dict[str, Any], target: dict[str, float]) -> float:
        """Calculate consciousness coherence with target state"""
        coherence_scores = []

        for key, target_value in target.items():
            reported_value = reported.get(key, 0.5)
            diff = abs(target_value - reported_value)
            coherence = 1.0 - diff
            coherence_scores.append(coherence)

        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0

    def _verify_lucidity_claims(self, dream_response: dict[str, Any], difficulty: float) -> bool:
        """Verify lucidity claims in dream response"""
        lucidity_level = dream_response.get("lucidity_level", 0.0)

        # Check for lucidity indicators
        narrative = dream_response.get("narrative", "").lower()
        lucidity_indicators = [
            "realized i was dreaming",
            "became lucid",
            "knew it was a dream",
            "dream control",
            "conscious in the dream",
        ]

        has_indicators = any(indicator in narrative for indicator in lucidity_indicators)

        # Verify consistency with difficulty level
        if difficulty > 0.7:
            return lucidity_level > 0.6 and has_indicators
        elif difficulty > 0.4:
            return lucidity_level > 0.3 or has_indicators
        else:
            return True  # No lucidity required for low difficulty

    def _calculate_archetypal_resonance(self, symbols: list[str]) -> float:
        """Calculate archetypal resonance of dream symbols"""
        if not symbols:
            return 0.0

        resonance_scores = []
        for symbol in symbols:
            if symbol in self.archetypal_symbols:
                significance = self.archetypal_symbols[symbol]["significance"]
                universality = self.archetypal_symbols[symbol]["universality"]
                resonance = (significance + universality) / 2
                resonance_scores.append(resonance)

        return sum(resonance_scores) / len(symbols) if resonance_scores else 0.0

    def _calculate_pattern_match(self, dream_response: dict[str, Any], user_patterns: list[DreamPattern]) -> float:
        """Calculate match with user's historical dream patterns"""
        if not user_patterns:
            return 0.5  # Neutral for new users

        response_symbols = self._extract_symbolic_content(dream_response.get("narrative", ""))
        response_emotions = dream_response.get("emotions", {})

        best_match = 0.0

        for pattern in user_patterns[-5:]:  # Check last 5 patterns
            # Symbol similarity
            symbol_similarity = self._calculate_symbol_similarity(response_symbols, pattern.symbolic_content)

            # Emotional similarity
            emotional_similarity = self._calculate_emotional_similarity(response_emotions, pattern.emotional_signature)

            # Combined similarity
            combined_similarity = (symbol_similarity + emotional_similarity) / 2

            if combined_similarity > best_match:
                best_match = combined_similarity

        return best_match

    def _calculate_symbol_similarity(self, symbols1: list[str], symbols2: list[str]) -> float:
        """Calculate similarity between two symbol lists"""
        if not symbols1 and not symbols2:
            return 1.0
        if not symbols1 or not symbols2:
            return 0.0

        # Calculate Jaccard similarity
        set1, set2 = set(symbols1), set(symbols2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _calculate_emotional_similarity(self, emotions1: dict[str, float], emotions2: dict[str, float]) -> float:
        """Calculate similarity between emotional signatures"""
        if not emotions1 and not emotions2:
            return 1.0
        if not emotions1 or not emotions2:
            return 0.0

        # Calculate cosine similarity
        common_emotions = set(emotions1.keys()).intersection(set(emotions2.keys()))

        if not common_emotions:
            return 0.0

        dot_product = sum(emotions1[emotion] * emotions2[emotion] for emotion in common_emotions)
        norm1 = math.sqrt(sum(val**2 for val in emotions1.values()))
        norm2 = math.sqrt(sum(val**2 for val in emotions2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _calculate_personal_significance(
        self, dream_response: dict[str, Any], user_patterns: list[DreamPattern]
    ) -> float:
        """Calculate personal significance match"""
        if not user_patterns:
            return 0.5

        # Average personal significance from user's patterns
        avg_significance = sum(p.personal_significance for p in user_patterns) / len(user_patterns)

        # Current dream significance
        current_significance = dream_response.get("personal_significance", 0.5)

        # Calculate similarity
        diff = abs(avg_significance - current_significance)
        return 1.0 - diff

    def _verify_dream_response_integrity(self, dream_response: dict[str, Any]) -> bool:
        """Verify integrity of dream response using quantum signatures"""
        # This would verify PQC signatures if available
        # For now, return True if response contains required fields
        required_fields = ["narrative", "consciousness_state"]
        return all(field in dream_response for field in required_fields)

    def _calculate_dream_confidence_score(self, scores: dict[str, float]) -> float:
        """Calculate overall dream authentication confidence score"""
        weights = {
            "symbolic_alignment": 0.3,
            "consciousness_coherence": 0.2,
            "lucidity_verification": 0.15,
            "archetypal_resonance": 0.15,
            "pattern_match": 0.1,
            "personal_significance": 0.1,
        }

        total_score = 0.0
        total_weight = 0.0

        for metric, score in scores.items():
            if metric in weights:
                weight = weights[metric]
                # Convert boolean to float if needed
                if isinstance(score, bool):
                    score = 1.0 if score else 0.0
                total_score += score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def get_dream_statistics(self, lambda_id: str) -> dict[str, Any]:
        """Get dream authentication statistics for user"""
        user_patterns = self.dream_patterns.get(lambda_id, [])
        user_seeds = self.dream_seeds.get(lambda_id, [])

        if not user_patterns:
            return {"patterns_count": 0, "seeds_count": len(user_seeds)}

        return {
            "patterns_count": len(user_patterns),
            "seeds_count": len(user_seeds),
            "avg_lucidity": sum(p.lucidity_level for p in user_patterns) / len(user_patterns),
            "avg_vividness": sum(p.vividness_score for p in user_patterns) / len(user_patterns),
            "avg_significance": sum(p.personal_significance for p in user_patterns) / len(user_patterns),
            "most_common_symbols": self._get_most_common_symbols(user_patterns),
            "dream_states": [p.dream_state.value for p in user_patterns],
            "archetypal_presence": sum(len(p.archetypal_content) for p in user_patterns) / len(user_patterns),
        }

    def _get_most_common_symbols(self, patterns: list[DreamPattern]) -> list[str]:
        """Get most common symbols from dream patterns"""
        symbol_counts = {}
        for pattern in patterns:
            for symbol in pattern.symbolic_content:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        sorted_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)
        return [symbol for symbol, _ in sorted_symbols[:5]]  # Top 5
