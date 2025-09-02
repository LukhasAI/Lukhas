#!/usr/bin/env python3
"""
LUKHΛS Persona Similarity Engine
Symbolic matching between session attributes and persona profiles
Trinity Framework: ⚛️🧠🛡️
"""

# Note: Using custom implementation instead of sklearn for portability
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PersonaMatch:
    """Represents a persona similarity match"""

    persona_name: str
    similarity_score: float
    matching_glyphs: list[str]
    trait_alignment: dict[str, float]
    explanation: str
    confidence: str  # high/medium/low


class PersonaSimilarityEngine:
    """
    Engine for matching symbolic traces to persona profiles using embeddings.
    Supports real-time and batch persona recommendation based on glyphs,
    drift patterns, and Trinity coherence.
    """

    def __init__(self, persona_profile_path: str = "symbolic_persona_profile.yaml"):
        """
        Initialize the similarity engine.

        Args:
            persona_profile_path: Path to persona profile YAML
        """
        self.persona_profile_path = Path(persona_profile_path)
        self.personas = {}
        self.persona_embeddings = {}
        self.feature_map = {}  # Maps features to indices
        self.fallback_persona = "The Stabilizer"

        # Trinity core for reference
        self.trinity_core = {"⚛️", "🧠", "🛡️"}

        # Load personas
        self._load_personas()

        # Create embeddings
        self._create_embeddings()

        logger.info("🧬 Persona Similarity Engine initialized")
        logger.info(f"   Loaded {len(self.personas)} personas")
        logger.info("   Embedding style: symbolic_keywords + persona_traits")

    def _load_personas(self):
        """Load personas from YAML profile"""
        try:
            with open(self.persona_profile_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.personas = data.get("personas", {})

            # Validate structure
            for name, profile in self.personas.items():
                # Check for either traits or dominant_traits
                has_traits = "traits" in profile or "dominant_traits" in profile
                has_glyphs = "glyphs" in profile
                has_emotions = "emotional_resonance" in profile

                if not (has_glyphs and has_traits and has_emotions):
                    missing = []
                    if not has_glyphs:
                        missing.append("glyphs")
                    if not has_traits:
                        missing.append("traits/dominant_traits")
                    if not has_emotions:
                        missing.append("emotional_resonance")
                    logger.warning(f"Persona {name} missing fields: {missing}")

        except Exception as e:
            logger.error(f"Failed to load personas: {e}")
            self.personas = {}

    def _create_embeddings(self):
        """Create vector embeddings for each persona"""
        if not self.personas:
            logger.warning("No personas loaded for embedding")
            return

        # Collect all features
        all_features = set()

        for name, profile in self.personas.items():
            # Add glyphs as features
            glyphs = profile.get("glyphs", [])
            for glyph in glyphs:
                all_features.add(f"glyph_{glyph}")

            # Add traits as features
            traits = profile.get("traits", profile.get("dominant_traits", []))
            for trait in traits:
                all_features.add(f"trait_{trait}")

            # Add emotional resonance
            emotions = profile.get("emotional_resonance", [])
            for emotion in emotions:
                all_features.add(f"emotion_{emotion}")

            # Add thresholds
            thresholds = profile.get("thresholds", profile.get("drift_thresholds", {}))
            if isinstance(thresholds, dict):
                for k, v in thresholds.items():
                    all_features.add(f"threshold_{k}_{v}")

            # Trinity alignment
            if any(g in self.trinity_core for g in glyphs):
                all_features.add("trinity_aligned")

        # Create feature map
        self.feature_map = {feature: i for i, feature in enumerate(sorted(all_features))}
        feature_count = len(self.feature_map)

        # Create embeddings for each persona
        for name, profile in self.personas.items():
            # Initialize embedding vector
            embedding = np.zeros(feature_count)

            # Fill in features
            glyphs = profile.get("glyphs", [])
            for glyph in glyphs:
                if f"glyph_{glyph}" in self.feature_map:
                    embedding[self.feature_map[f"glyph_{glyph}"]] = 1.0

            traits = profile.get("traits", profile.get("dominant_traits", []))
            for trait in traits:
                if f"trait_{trait}" in self.feature_map:
                    embedding[self.feature_map[f"trait_{trait}"]] = 1.0

            emotions = profile.get("emotional_resonance", [])
            for emotion in emotions:
                if f"emotion_{emotion}" in self.feature_map:
                    embedding[self.feature_map[f"emotion_{emotion}"]] = 1.0

            thresholds = profile.get("thresholds", profile.get("drift_thresholds", {}))
            if isinstance(thresholds, dict):
                for k, v in thresholds.items():
                    if f"threshold_{k}_{v}" in self.feature_map:
                        embedding[self.feature_map[f"threshold_{k}_{v}"]] = 1.0

            if any(g in self.trinity_core for g in glyphs) and "trinity_aligned" in self.feature_map:
                embedding[self.feature_map["trinity_aligned"]] = 1.0

            # Normalize embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            self.persona_embeddings[name] = embedding

        logger.info(f"   Created embeddings with {feature_count} features")

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _create_session_embedding(self, symbolic_trace: dict[str, Any]) -> np.ndarray:
        """Create embedding for current session"""
        # Initialize embedding
        if not self.feature_map:
            return np.zeros(1)

        embedding = np.zeros(len(self.feature_map))

        # Extract features
        glyphs = symbolic_trace.get("glyphs", [])
        drift_score = symbolic_trace.get("drift_score", 0.5)
        entropy = symbolic_trace.get("entropy", 0.5)
        trinity_coherence = symbolic_trace.get("trinity_coherence", 0.5)

        # Add glyph features
        for glyph in glyphs:
            if f"glyph_{glyph}" in self.feature_map:
                embedding[self.feature_map[f"glyph_{glyph}"]] = 1.0

        # Derive and add trait features
        if drift_score < 0.3:
            for trait in ["stable", "grounded"]:
                if f"trait_{trait}" in self.feature_map:
                    embedding[self.feature_map[f"trait_{trait}"]] = 0.8
        elif drift_score > 0.7:
            for trait in ["chaotic", "unstable"]:
                if f"trait_{trait}" in self.feature_map:
                    embedding[self.feature_map[f"trait_{trait}"]] = 0.8
        else:
            for trait in ["balanced", "adaptive"]:
                if f"trait_{trait}" in self.feature_map:
                    embedding[self.feature_map[f"trait_{trait}"]] = 0.8

        # Add emotional features
        if entropy < 0.3:
            if "emotion_valence_positive" in self.feature_map:
                embedding[self.feature_map["emotion_valence_positive"]] = 0.7
            if "emotion_arousal_low" in self.feature_map:
                embedding[self.feature_map["emotion_arousal_low"]] = 0.7
        elif entropy > 0.7:
            if "emotion_valence_negative" in self.feature_map:
                embedding[self.feature_map["emotion_valence_negative"]] = 0.7
            if "emotion_arousal_high" in self.feature_map:
                embedding[self.feature_map["emotion_arousal_high"]] = 0.7

        # Trinity alignment
        if trinity_coherence > 0.7 and "trinity_aligned" in self.feature_map:
            embedding[self.feature_map["trinity_aligned"]] = 1.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def recommend_persona(self, symbolic_trace: dict[str, Any]) -> PersonaMatch:
        """
        Recommend the best matching persona for current symbolic state.

        Args:
            symbolic_trace: Dictionary with glyphs, drift_score, entropy, trinity_coherence

        Returns:
            PersonaMatch with top recommendation
        """
        matches = self.rank_personas(symbolic_trace, top_n=1)

        if matches:
            return matches[0]
        else:
            # Return fallback
            return PersonaMatch(
                persona_name=self.fallback_persona,
                similarity_score=0.0,
                matching_glyphs=[],
                trait_alignment={},
                explanation="No suitable match found - using fallback persona",
                confidence="low",
            )

    def rank_personas(self, symbolic_trace: dict[str, Any], top_n: int = 3) -> list[PersonaMatch]:
        """
        Rank all personas by similarity to current state.

        Args:
            symbolic_trace: Current symbolic state
            top_n: Number of top matches to return

        Returns:
            List of PersonaMatch objects sorted by similarity
        """
        # Create session embedding
        session_embedding = self._create_session_embedding(symbolic_trace)

        if session_embedding is None:
            return []

        # Calculate similarities
        similarities = []

        for persona_name, persona_embedding in self.persona_embeddings.items():
            # Cosine similarity
            similarity = self._cosine_similarity(session_embedding, persona_embedding)

            # Enhance with direct glyph matching
            session_glyphs = set(symbolic_trace.get("glyphs", []))
            persona_glyphs = set(self.personas[persona_name].get("glyphs", []))
            glyph_overlap = len(session_glyphs & persona_glyphs)

            # Weighted score
            weighted_score = (similarity * 0.7) + (glyph_overlap * 0.3 / max(len(persona_glyphs), 1))

            similarities.append((persona_name, weighted_score, glyph_overlap))

        # Sort by score
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Create PersonaMatch objects
        matches = []

        for persona_name, score, glyph_overlap in similarities[:top_n]:
            persona = self.personas[persona_name]

            # Calculate trait alignment
            trait_alignment = self._calculate_trait_alignment(symbolic_trace, persona)

            # Generate explanation
            explanation = self._generate_explanation(symbolic_trace, persona, score, glyph_overlap)

            # Determine confidence
            if score > 0.8:
                confidence = "high"
            elif score > 0.5:
                confidence = "medium"
            else:
                confidence = "low"

            # Get matching glyphs
            session_glyphs = set(symbolic_trace.get("glyphs", []))
            persona_glyphs = set(persona.get("glyphs", []))
            matching_glyphs = list(session_glyphs & persona_glyphs)

            matches.append(
                PersonaMatch(
                    persona_name=persona_name,
                    similarity_score=round(score, 3),
                    matching_glyphs=matching_glyphs,
                    trait_alignment=trait_alignment,
                    explanation=explanation,
                    confidence=confidence,
                )
            )

        return matches

    def _calculate_trait_alignment(self, symbolic_trace: dict[str, Any], persona: dict[str, Any]) -> dict[str, float]:
        """Calculate alignment between session state and persona traits"""
        alignment = {}

        # Drift alignment
        drift = symbolic_trace.get("drift_score", 0.5)
        thresholds = persona.get("thresholds", persona.get("drift_thresholds", {}))

        if isinstance(thresholds, dict) and "max" in thresholds:
            persona_drift = thresholds["max"]
            alignment["drift"] = 1.0 - abs(drift - persona_drift)
        else:
            alignment["drift"] = 0.5  # Default if no threshold

        # Entropy alignment
        entropy = symbolic_trace.get("entropy", 0.5)
        alignment["entropy"] = 1.0 - abs(entropy - 0.5)  # Default to medium entropy

        # Trinity alignment
        trinity = symbolic_trace.get("trinity_coherence", 0.5)
        session_glyphs = set(symbolic_trace.get("glyphs", []))
        trinity_present = len(session_glyphs & self.trinity_core) / 3
        alignment["trinity"] = (trinity + trinity_present) / 2

        return {k: round(v, 2) for k, v in alignment.items()}

    def _generate_explanation(
        self,
        symbolic_trace: dict[str, Any],
        persona: dict[str, Any],
        score: float,
        glyph_overlap: int,
    ) -> str:
        """Generate human-readable explanation for match"""
        explanations = []

        # Score-based explanation
        if score > 0.8:
            explanations.append("Strong symbolic alignment")
        elif score > 0.5:
            explanations.append("Moderate symbolic alignment")
        else:
            explanations.append("Weak symbolic alignment")

        # Glyph explanation
        if glyph_overlap > 2:
            explanations.append(f"{glyph_overlap} shared glyphs")
        elif glyph_overlap > 0:
            explanations.append(f"{glyph_overlap} shared glyph{'s' if glyph_overlap > 1 else ''}")

        # State explanation
        drift = symbolic_trace.get("drift_score", 0.5)
        if drift < 0.3:
            explanations.append("stable state matches persona baseline")
        elif drift > 0.7:
            explanations.append("high drift aligns with persona dynamics")

        return "; ".join(explanations)

    def evolve_persona(self, drift_history: list[dict[str, Any]], current_persona: str) -> dict[str, Any]:
        """
        Suggest persona evolution based on drift history.

        Args:
            drift_history: List of symbolic traces over time
            current_persona: Current active persona

        Returns:
            Evolution suggestion with rationale
        """
        if len(drift_history) < 3:
            return {
                "suggested_persona": current_persona,
                "evolution_type": "maintain",
                "rationale": "Insufficient history for evolution analysis",
            }

        # Analyze recent patterns
        recent_traces = drift_history[-5:]

        # Average metrics
        avg_drift = np.mean([t.get("drift_score", 0.5) for t in recent_traces])
        avg_entropy = np.mean([t.get("entropy", 0.5) for t in recent_traces])
        avg_trinity = np.mean([t.get("trinity_coherence", 0.5) for t in recent_traces])

        # Collect all recent glyphs
        all_glyphs = []
        for trace in recent_traces:
            all_glyphs.extend(trace.get("glyphs", []))

        # Create aggregate trace
        aggregate_trace = {
            "glyphs": list(set(all_glyphs)),
            "drift_score": avg_drift,
            "entropy": avg_entropy,
            "trinity_coherence": avg_trinity,
        }

        # Get best matches
        matches = self.rank_personas(aggregate_trace, top_n=3)

        if not matches:
            return {
                "suggested_persona": current_persona,
                "evolution_type": "maintain",
                "rationale": "No suitable evolution target found",
            }

        # Check if evolution is warranted
        top_match = matches[0]

        if top_match.persona_name == current_persona:
            return {
                "suggested_persona": current_persona,
                "evolution_type": "maintain",
                "rationale": "Current persona remains optimal",
                "stability_score": top_match.similarity_score,
            }

        # Check if change is significant
        if top_match.similarity_score > 0.7 and top_match.confidence == "high":
            # Check persona evolution paths
            current_profile = self.personas.get(current_persona, {})
            evolution_paths = current_profile.get("evolution_paths", [])

            if top_match.persona_name in evolution_paths:
                evolution_type = "natural_evolution"
                rationale = f"Natural progression from {current_persona} to {top_match.persona_name}"
            else:
                evolution_type = "adaptation"
                rationale = f"Symbolic state shift suggests adaptation to {top_match.persona_name}"

            return {
                "suggested_persona": top_match.persona_name,
                "evolution_type": evolution_type,
                "rationale": rationale,
                "similarity_score": top_match.similarity_score,
                "matching_glyphs": top_match.matching_glyphs,
                "trait_alignment": top_match.trait_alignment,
            }
        else:
            return {
                "suggested_persona": current_persona,
                "evolution_type": "maintain",
                "rationale": "Evolution confidence too low",
                "alternative": top_match.persona_name,
                "alternative_score": top_match.similarity_score,
            }

    def get_fallback_if_collapse(self, symbolic_trace: dict[str, Any]) -> dict[str, Any]:
        """
        Get fallback persona if symbolic collapse detected.

        Args:
            symbolic_trace: Current symbolic state

        Returns:
            Fallback recommendation with stabilization strategy
        """
        # Detect collapse conditions
        drift = symbolic_trace.get("drift_score", 0.5)
        entropy = symbolic_trace.get("entropy", 0.5)
        trinity = symbolic_trace.get("trinity_coherence", 0.5)

        collapse_detected = False
        collapse_type = []

        if drift > 0.9:
            collapse_detected = True
            collapse_type.append("extreme_drift")

        if entropy > 0.85:
            collapse_detected = True
            collapse_type.append("entropy_overflow")

        if trinity < 0.1:
            collapse_detected = True
            collapse_type.append("trinity_void")

        if not collapse_detected:
            return {"fallback_needed": False, "current_state": "stable"}

        # Determine appropriate fallback
        if "trinity_void" in collapse_type:
            # Use Trinity Keeper for void recovery
            fallback = "The Trinity Keeper"
            stabilization = ["⚛️", "🧠", "🛡️", "🌿"]
        elif "entropy_overflow" in collapse_type:
            # Use Stabilizer for entropy management
            fallback = self.fallback_persona
            stabilization = ["🧘", "🪷", "⚖️", "🛡️"]
        else:
            # Use Guardian for drift protection
            fallback = "The Guardian"
            stabilization = ["🛡️", "⚡", "🏛️", "🌿"]

        # Get fallback profile
        fallback_profile = self.personas.get(fallback, {})

        return {
            "fallback_needed": True,
            "collapse_type": collapse_type,
            "recommended_persona": fallback,
            "stabilization_glyphs": stabilization,
            "recovery_traits": fallback_profile.get("traits", []),
            "recovery_strategy": self._generate_recovery_strategy(collapse_type),
            "urgency": "critical" if len(collapse_type) > 1 else "high",
        }

    def _generate_recovery_strategy(self, collapse_types: list[str]) -> str:
        """Generate recovery strategy based on collapse type"""
        strategies = []

        if "extreme_drift" in collapse_types:
            strategies.append("Apply Guardian protection and ethical constraints")

        if "entropy_overflow" in collapse_types:
            strategies.append("Introduce grounding glyphs and reduce complexity")

        if "trinity_void" in collapse_types:
            strategies.append("Restore Trinity Framework with core glyphs")

        return "; ".join(strategies) if strategies else "General stabilization protocol"

    def batch_analyze(self, session_traces: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze multiple sessions for patterns and recommendations.

        Args:
            session_traces: List of symbolic traces to analyze

        Returns:
            Batch analysis with patterns and recommendations
        """
        if not session_traces:
            return {"status": "no_data"}

        # Analyze each session
        all_matches = []
        persona_frequencies = {}

        for trace in session_traces:
            match = self.recommend_persona(trace)
            all_matches.append(match)

            # Track frequencies
            persona = match.persona_name
            persona_frequencies[persona] = persona_frequencies.get(persona, 0) + 1

        # Find dominant persona
        dominant_persona = max(persona_frequencies.items(), key=lambda x: x[1])[0]

        # Calculate stability
        stability = persona_frequencies[dominant_persona] / len(session_traces)

        # Identify transitions
        transitions = []
        for i in range(1, len(all_matches)):
            if all_matches[i].persona_name != all_matches[i - 1].persona_name:
                transitions.append(
                    {
                        "from": all_matches[i - 1].persona_name,
                        "to": all_matches[i].persona_name,
                        "position": i,
                    }
                )

        return {
            "total_sessions": len(session_traces),
            "dominant_persona": dominant_persona,
            "stability_score": round(stability, 2),
            "persona_distribution": persona_frequencies,
            "transitions": transitions,
            "transition_rate": len(transitions) / max(len(session_traces) - 1, 1),
            "recommendations": self._generate_batch_recommendations(stability, transitions, dominant_persona),
        }

    def _generate_batch_recommendations(self, stability: float, transitions: list[dict], dominant: str) -> list[str]:
        """Generate recommendations from batch analysis"""
        recommendations = []

        if stability < 0.3:
            recommendations.append("High persona volatility - consider stabilization")
        elif stability > 0.8:
            recommendations.append("Stable persona alignment maintained")

        if len(transitions) > 5:
            recommendations.append("Frequent transitions detected - monitor for drift")

        # Check if dominant persona is high-risk
        dominant_profile = self.personas.get(dominant, {})
        thresholds = dominant_profile.get("thresholds", dominant_profile.get("drift_thresholds", {}))
        if isinstance(thresholds, dict) and thresholds.get("max", 0) > 0.7:
            recommendations.append(
                f"Dominant persona '{dominant}' has high drift threshold - ensure Guardian oversight"
            )

        return recommendations

    def export_similarity_report(
        self,
        symbolic_trace: dict[str, Any],
        output_path: str = "similarity_report.json",
    ) -> str:
        """
        Export detailed similarity report for audit.

        Args:
            symbolic_trace: Session to analyze
            output_path: Where to save report

        Returns:
            Path to saved report
        """
        # Get full analysis
        matches = self.rank_personas(symbolic_trace, top_n=len(self.personas))

        # Build report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_trace": symbolic_trace,
            "analysis": {
                "top_match": matches[0].__dict__ if matches else None,
                "all_matches": [m.__dict__ for m in matches],
                "embedding_features": list(self.feature_map.keys()),
                "trinity_alignment": any(g in self.trinity_core for g in symbolic_trace.get("glyphs", [])),
            },
            "recommendations": {
                "primary": (matches[0].persona_name if matches else self.fallback_persona),
                "alternatives": ([m.persona_name for m in matches[1:4]] if len(matches) > 1 else []),
                "confidence": matches[0].confidence if matches else "low",
            },
        }

        # Check for collapse
        collapse_check = self.get_fallback_if_collapse(symbolic_trace)
        if collapse_check.get("fallback_needed"):
            report["collapse_warning"] = collapse_check

        # Save report
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Similarity report exported to {output_path}")
        return str(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics"""
        embedding_dims = 0
        if self.persona_embeddings:
            first_embedding = self.persona_embeddings[next(iter(self.persona_embeddings))]
            embedding_dims = len(first_embedding) if hasattr(first_embedding, "__len__") else 0

        return {
            "personas_loaded": len(self.personas),
            "embeddings_created": len(self.persona_embeddings),
            "embedding_dimensions": embedding_dims,
            "fallback_persona": self.fallback_persona,
            "trinity_core": list(self.trinity_core),
        }


# Example usage
if __name__ == "__main__":
    print("🧬 LUKHΛS Persona Similarity Engine Test")
    print("=" * 50)

    # Initialize engine
    engine = PersonaSimilarityEngine()

    # Test symbolic trace
    test_trace = {
        "glyphs": ["🧠", "⚛️", "🌟"],
        "drift_score": 0.3,
        "entropy": 0.4,
        "trinity_coherence": 0.8,
    }

    print("\nTest trace:", test_trace)

    # Get recommendation
    match = engine.recommend_persona(test_trace)

    print(f"\nRecommended persona: {match.persona_name}")
    print(f"Similarity score: {match.similarity_score}")
    print(f"Explanation: {match.explanation}")
    print(f"Confidence: {match.confidence}")

    # Get rankings
    print("\nTop 3 persona matches:")
    rankings = engine.rank_personas(test_trace, top_n=3)
    for i, match in enumerate(rankings, 1):
        print(f"{i}. {match.persona_name} (score: {match.similarity_score})")

    print("\n✅ Persona Similarity Engine operational!")
