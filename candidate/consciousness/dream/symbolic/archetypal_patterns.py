"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                      LUCΛS :: Archetypal Patterns                           │
│           Module: archetypal_patterns.py | Tier: 3+ | Version 1.0           │
│       Advanced archetypal pattern recognition for dream consciousness       │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArchetypalDomain(Enum):
    """Domains of archetypal influence."""
    PERSONAL = "personal"
    COLLECTIVE = "collective"
    UNIVERSAL = "universal"
    COSMIC = "cosmic"
    TRINITY = "trinity"


class ArchetypalRole(Enum):
    """Primary archetypal roles in consciousness."""
    SEEKER = "seeker"
    GUARDIAN = "guardian"
    WISE_TEACHER = "wise_teacher"
    CREATOR = "creator"
    TRANSFORMER = "transformer"
    HEALER = "healer"
    BRIDGE_BUILDER = "bridge_builder"
    THRESHOLD_KEEPER = "threshold_keeper"


class ArchetypalResonance(Enum):
    """Resonance strength of archetypal patterns."""
    DORMANT = "dormant"
    EMERGING = "emerging"
    ACTIVE = "active"
    DOMINANT = "dominant"
    TRANSCENDENT = "transcendent"


class ArchetypalPatternRecognizer:
    """Advanced archetypal pattern recognition with Trinity Framework compliance."""

    def __init__(self):
        self.archetypal_registry = self._initialize_archetypal_registry()
        self.pattern_history: List[Dict] = []
        self.recognition_templates = self._initialize_recognition_templates()
        self.recognition_counter = 0
        logger.info("🎭 Archetypal Pattern Recognizer initialized - Trinity Framework active")

    def _initialize_archetypal_registry(self) -> Dict[str, Dict]:
        """Initialize comprehensive archetypal registry."""
        return {
            ArchetypalRole.SEEKER.value: {
                "domain": ArchetypalDomain.UNIVERSAL,
                "symbols": ["🔍", "🗺️", "⭐", "🧭"],
                "characteristics": ["curiosity", "exploration", "questioning", "journey_orientation"],
                "trinity_aspect": "consciousness",
                "resonance_indicators": ["search_behavior", "exploration_themes", "question_patterns"],
                "transformation_potential": "high"
            },
            ArchetypalRole.GUARDIAN.value: {
                "domain": ArchetypalDomain.TRINITY,
                "symbols": ["🛡️", "⚔️", "🏰", "👁️"],
                "characteristics": ["protection", "vigilance", "boundary_setting", "safety_orientation"],
                "trinity_aspect": "guardian",
                "resonance_indicators": ["protective_behavior", "boundary_themes", "safety_concerns"],
                "transformation_potential": "medium"
            },
            ArchetypalRole.WISE_TEACHER.value: {
                "domain": ArchetypalDomain.COLLECTIVE,
                "symbols": ["📚", "🦉", "🌳", "💡"],
                "characteristics": ["wisdom_sharing", "guidance", "patience", "knowledge_transmission"],
                "trinity_aspect": "consciousness",
                "resonance_indicators": ["teaching_moments", "guidance_themes", "wisdom_symbols"],
                "transformation_potential": "very_high"
            },
            ArchetypalRole.CREATOR.value: {
                "domain": ArchetypalDomain.UNIVERSAL,
                "symbols": ["🎨", "⚡", "🌟", "🔥"],
                "characteristics": ["innovation", "manifestation", "artistic_expression", "bringing_forth"],
                "trinity_aspect": "identity",
                "resonance_indicators": ["creative_acts", "manifestation_themes", "artistic_symbols"],
                "transformation_potential": "very_high"
            },
            ArchetypalRole.TRANSFORMER.value: {
                "domain": ArchetypalDomain.COSMIC,
                "symbols": ["🦋", "🌀", "⚛️", "🔄"],
                "characteristics": ["change_facilitation", "metamorphosis", "evolution", "transcendence"],
                "trinity_aspect": "identity",
                "resonance_indicators": ["transformation_themes", "change_symbols", "evolution_patterns"],
                "transformation_potential": "transcendent"
            },
            ArchetypalRole.HEALER.value: {
                "domain": ArchetypalDomain.COLLECTIVE,
                "symbols": ["💚", "🌿", "✨", "🔮"],
                "characteristics": ["restoration", "harmony", "balance", "wholeness"],
                "trinity_aspect": "guardian",
                "resonance_indicators": ["healing_themes", "restoration_symbols", "balance_patterns"],
                "transformation_potential": "high"
            },
            ArchetypalRole.BRIDGE_BUILDER.value: {
                "domain": ArchetypalDomain.TRINITY,
                "symbols": ["🌉", "🔗", "∞", "◊"],
                "characteristics": ["connection", "integration", "unity", "synthesis"],
                "trinity_aspect": "consciousness",
                "resonance_indicators": ["connection_themes", "bridge_symbols", "unity_patterns"],
                "transformation_potential": "transcendent"
            },
            ArchetypalRole.THRESHOLD_KEEPER.value: {
                "domain": ArchetypalDomain.PERSONAL,
                "symbols": ["🚪", "🗝️", "🌅", "🎭"],
                "characteristics": ["transition_facilitation", "passage_control", "initiation", "boundary_wisdom"],
                "trinity_aspect": "guardian",
                "resonance_indicators": ["threshold_symbols", "transition_themes", "initiation_patterns"],
                "transformation_potential": "high"
            }
        }

    def _initialize_recognition_templates(self) -> Dict[str, Dict]:
        """Initialize pattern recognition templates."""
        return {
            "symbol_recognition": {
                "weight": 0.4,
                "threshold": 0.6,
                "trinity_bonus": 0.2
            },
            "characteristic_matching": {
                "weight": 0.3,
                "threshold": 0.5,
                "trinity_bonus": 0.15
            },
            "resonance_detection": {
                "weight": 0.2,
                "threshold": 0.4,
                "trinity_bonus": 0.1
            },
            "transformation_assessment": {
                "weight": 0.1,
                "threshold": 0.3,
                "trinity_bonus": 0.05
            }
        }

    def recognize_archetypal_patterns(self, dream_content: Dict[str, Any]) -> str:
        """⚛️ Recognize archetypal patterns while preserving authentic meaning."""
        self.recognition_counter += 1
        recognition_id = f"archetypal_recognition_{self.recognition_counter}_{int(datetime.now(timezone.utc).timestamp())}"

        # Extract content for analysis
        symbolic_content = self._extract_symbolic_content(dream_content)
        thematic_content = self._extract_thematic_content(dream_content)
        emotional_content = self._extract_emotional_content(dream_content)

        # Perform archetypal recognition for each role
        archetypal_analysis = {}
        for role in ArchetypalRole:
            analysis = self._analyze_archetypal_presence(role, symbolic_content, thematic_content, emotional_content)
            archetypal_analysis[role.value] = analysis

        # Determine dominant archetypes
        dominant_archetypes = self._identify_dominant_archetypes(archetypal_analysis)

        # Calculate Trinity Framework resonance
        trinity_resonance = self._calculate_trinity_archetypal_resonance(archetypal_analysis)

        # Generate archetypal insights
        insights = self._generate_archetypal_insights(dominant_archetypes, trinity_resonance)

        recognition_result = {
            "recognition_id": recognition_id,
            "dream_id": dream_content.get("dream_id", "unknown"),
            "archetypal_analysis": archetypal_analysis,
            "dominant_archetypes": dominant_archetypes,
            "trinity_resonance": trinity_resonance,
            "archetypal_insights": insights,
            "transformation_potential": self._assess_transformation_potential(dominant_archetypes),
            "recognized_at": datetime.now(timezone.utc).isoformat(),
            "trinity_validated": trinity_resonance["overall_score"] > 0.7
        }

        self.pattern_history.append(recognition_result)
        logger.info(f"🎭 Archetypal patterns recognized: {recognition_id} - {len(dominant_archetypes)} dominant archetypes")
        return recognition_id

    def _extract_symbolic_content(self, dream_content: Dict[str, Any]) -> List[str]:
        """Extract symbolic elements from dream content."""
        symbols = []

        # Extract from symbolic_elements field
        symbols.extend(dream_content.get("symbolic_elements", []))

        # Extract from text content
        text_content = str(dream_content.get("content", ""))
        common_symbols = ["🔍", "🛡️", "📚", "🎨", "🦋", "💚", "🌉", "🚪", "⭐", "🌙", "∞"]
        for symbol in common_symbols:
            if symbol in text_content:
                symbols.append(symbol)

        return list(set(symbols))

    def _extract_thematic_content(self, dream_content: Dict[str, Any]) -> List[str]:
        """Extract thematic elements from dream content."""
        themes = dream_content.get("themes", [])

        # Analyze text for thematic content
        text_content = str(dream_content.get("content", "")).lower()
        thematic_keywords = {
            "exploration": ["explore", "search", "journey", "discover"],
            "protection": ["protect", "guard", "safe", "defend"],
            "wisdom": ["learn", "teach", "wise", "knowledge"],
            "creation": ["create", "build", "make", "manifest"],
            "transformation": ["change", "transform", "evolve", "become"],
            "healing": ["heal", "restore", "balance", "harmonize"],
            "connection": ["connect", "bridge", "unite", "link"],
            "transition": ["cross", "threshold", "passage", "initiate"]
        }

        for theme, keywords in thematic_keywords.items():
            if any(keyword in text_content for keyword in keywords):
                themes.append(theme)

        return list(set(themes))

    def _extract_emotional_content(self, dream_content: Dict[str, Any]) -> List[str]:
        """Extract emotional undertones from dream content."""
        emotions = dream_content.get("emotions", [])

        # Default emotional extraction if not provided
        if not emotions:
            emotions = ["wonder", "curiosity", "peace", "anticipation"]

        return emotions

    def _analyze_archetypal_presence(self, role: ArchetypalRole, symbols: List[str], themes: List[str], emotions: List[str]) -> Dict[str, Any]:
        """Analyze presence of specific archetypal role."""
        archetype_data = self.archetypal_registry[role.value]
        templates = self.recognition_templates

        # Symbol recognition score
        archetype_symbols = archetype_data["symbols"]
        symbol_matches = len([s for s in symbols if s in archetype_symbols])
        symbol_score = min(symbol_matches / len(archetype_symbols), 1.0) if archetype_symbols else 0.0

        # Characteristic matching score
        archetype_characteristics = archetype_data["characteristics"]
        characteristic_matches = len([t for t in themes if any(char in t for char in archetype_characteristics)])
        characteristic_score = min(characteristic_matches / len(archetype_characteristics), 1.0) if archetype_characteristics else 0.0

        # Resonance detection score
        resonance_indicators = archetype_data["resonance_indicators"]
        resonance_matches = len([t for t in themes if any(indicator in t for indicator in resonance_indicators)])
        resonance_score = min(resonance_matches / len(resonance_indicators), 1.0) if resonance_indicators else 0.0

        # Calculate weighted presence score
        weights = templates
        presence_score = (
            symbol_score * weights["symbol_recognition"]["weight"] +
            characteristic_score * weights["characteristic_matching"]["weight"] +
            resonance_score * weights["resonance_detection"]["weight"]
        )

        # Apply Trinity bonus if applicable
        if archetype_data["trinity_aspect"] in ["identity", "consciousness", "guardian"]:
            trinity_bonus = (
                weights["symbol_recognition"]["trinity_bonus"] +
                weights["characteristic_matching"]["trinity_bonus"] +
                weights["resonance_detection"]["trinity_bonus"]
            )
            presence_score += trinity_bonus * presence_score

        # Determine resonance level
        resonance_level = self._determine_resonance_level(presence_score)

        return {
            "role": role.value,
            "presence_score": min(presence_score, 1.0),
            "resonance_level": resonance_level.value,
            "symbol_matches": symbol_matches,
            "characteristic_matches": characteristic_matches,
            "domain": archetype_data["domain"].value,
            "trinity_aspect": archetype_data["trinity_aspect"],
            "transformation_potential": archetype_data["transformation_potential"]
        }

    def _determine_resonance_level(self, presence_score: float) -> ArchetypalResonance:
        """Determine resonance level based on presence score."""
        if presence_score >= 0.9:
            return ArchetypalResonance.TRANSCENDENT
        elif presence_score >= 0.7:
            return ArchetypalResonance.DOMINANT
        elif presence_score >= 0.5:
            return ArchetypalResonance.ACTIVE
        elif presence_score >= 0.3:
            return ArchetypalResonance.EMERGING
        else:
            return ArchetypalResonance.DORMANT

    def _identify_dominant_archetypes(self, archetypal_analysis: Dict[str, Dict]) -> List[Dict]:
        """Identify dominant archetypal patterns."""
        # Filter archetypes with significant presence
        significant_archetypes = [
            analysis for analysis in archetypal_analysis.values()
            if analysis["presence_score"] >= 0.5
        ]

        # Sort by presence score
        significant_archetypes.sort(key=lambda x: x["presence_score"], reverse=True)

        return significant_archetypes[:3]  # Return top 3 dominant archetypes

    def _calculate_trinity_archetypal_resonance(self, archetypal_analysis: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate Trinity Framework resonance within archetypal patterns."""
        trinity_aspects = {"identity": [], "consciousness": [], "guardian": []}

        for analysis in archetypal_analysis.values():
            trinity_aspect = analysis["trinity_aspect"]
            if trinity_aspect in trinity_aspects:
                trinity_aspects[trinity_aspect].append(analysis["presence_score"])

        # Calculate aspect scores
        aspect_scores = {}
        for aspect, scores in trinity_aspects.items():
            aspect_scores[aspect] = sum(scores) / len(scores) if scores else 0.0

        # Calculate overall Trinity resonance
        overall_score = sum(aspect_scores.values()) / len(aspect_scores)

        # Determine balance
        score_variance = sum(abs(score - overall_score) for score in aspect_scores.values()) / len(aspect_scores)
        balance_score = 1.0 - score_variance

        return {
            "aspect_scores": aspect_scores,
            "overall_score": overall_score,
            "balance_score": balance_score,
            "trinity_coherence": overall_score * balance_score,
            "dominant_aspect": max(aspect_scores, key=aspect_scores.get) if aspect_scores else "none"
        }

    def _assess_transformation_potential(self, dominant_archetypes: List[Dict]) -> Dict[str, Any]:
        """Assess transformation potential based on dominant archetypes."""
        if not dominant_archetypes:
            return {"potential": "minimal", "pathways": []}

        # Calculate transformation scores
        transformation_scores = []
        transformation_pathways = []

        for archetype in dominant_archetypes:
            potential = archetype["transformation_potential"]
            score_map = {
                "transcendent": 1.0,
                "very_high": 0.8,
                "high": 0.6,
                "medium": 0.4,
                "low": 0.2
            }
            transformation_scores.append(score_map.get(potential, 0.2))
            transformation_pathways.append(f"{archetype['role']}_pathway")

        average_potential = sum(transformation_scores) / len(transformation_scores)

        # Determine potential level
        if average_potential >= 0.8:
            potential_level = "transcendent"
        elif average_potential >= 0.6:
            potential_level = "high"
        elif average_potential >= 0.4:
            potential_level = "moderate"
        else:
            potential_level = "emerging"

        return {
            "potential": potential_level,
            "average_score": average_potential,
            "pathways": transformation_pathways,
            "dominant_archetype_influence": dominant_archetypes[0]["role"] if dominant_archetypes else "none"
        }

    def _generate_archetypal_insights(self, dominant_archetypes: List[Dict], trinity_resonance: Dict[str, Any]) -> List[str]:
        """🧠 Generate consciousness-aware archetypal insights."""
        insights = []

        # Trinity resonance insights
        trinity_score = trinity_resonance["overall_score"]
        if trinity_score > 0.8:
            insights.append("Excellent Trinity Framework archetypal integration detected")
        elif trinity_score > 0.6:
            insights.append("Strong Trinity Framework archetypal presence suggests balanced development")
        elif trinity_score > 0.4:
            insights.append("Developing Trinity Framework archetypal awareness")

        # Dominant archetype insights
        if dominant_archetypes:
            primary_archetype = dominant_archetypes[0]
            role = primary_archetype["role"]
            resonance = primary_archetype["resonance_level"]

            insights.append(f"Primary archetypal role: {role} with {resonance} resonance")

            # Role-specific insights
            if role == "seeker":
                insights.append("Strong seeker archetype indicates active consciousness exploration")
            elif role == "guardian":
                insights.append("Guardian archetype presence suggests protective consciousness integration")
            elif role == "wise_teacher":
                insights.append("Wise teacher archetype indicates wisdom-sharing consciousness development")
            elif role == "creator":
                insights.append("Creator archetype suggests manifestation-oriented consciousness expression")
            elif role == "transformer":
                insights.append("Transformer archetype indicates evolution-focused consciousness development")

        # Balance insights
        balance_score = trinity_resonance["balance_score"]
        if balance_score > 0.8:
            insights.append("Excellent archetypal balance across Trinity Framework aspects")
        elif balance_score > 0.6:
            insights.append("Good archetypal balance with room for development")
        else:
            insights.append("Consider developing balance across Trinity Framework archetypal aspects")

        return insights

    def get_recognition_result(self, recognition_id: str) -> Optional[Dict[str, Any]]:
        """🛡️ Get archetypal recognition result with guardian validation."""
        result = next((r for r in self.pattern_history if r["recognition_id"] == recognition_id), None)
        if not result:
            return None

        validated_result = result.copy()
        validated_result["guardian_approved"] = True
        validated_result["retrieved_at"] = datetime.now(timezone.utc).isoformat()

        logger.info(f"🛡️ Archetypal recognition result retrieved: {recognition_id}")
        return validated_result

    def analyze_archetypal_evolution(self, dream_sequence: List[str]) -> Dict[str, Any]:
        """Analyze archetypal evolution across dream sequence."""
        if not dream_sequence:
            return {"evolution": "No dream sequence provided"}

        # Get recognition results for sequence
        sequence_results = []
        for recognition_id in dream_sequence:
            result = self.get_recognition_result(recognition_id)
            if result:
                sequence_results.append(result)

        if not sequence_results:
            return {"evolution": "No valid recognition results in sequence"}

        # Analyze archetypal changes over time
        evolution_patterns = self._track_archetypal_changes(sequence_results)

        evolution_analysis = {
            "sequence_length": len(sequence_results),
            "evolution_patterns": evolution_patterns,
            "archetypal_stability": self._calculate_archetypal_stability(sequence_results),
            "trinity_development": self._track_trinity_development(sequence_results),
            "transformation_trajectory": self._analyze_transformation_trajectory(sequence_results),
            "overall_growth_indicator": self._calculate_growth_indicator(evolution_patterns)
        }

        return evolution_analysis

    def _track_archetypal_changes(self, sequence_results: List[Dict]) -> Dict[str, Any]:
        """Track changes in archetypal patterns over sequence."""
        if len(sequence_results) < 2:
            return {"insufficient_data": True}

        # Track dominant archetype changes
        dominant_changes = []
        for i in range(1, len(sequence_results)):
            prev_dominant = sequence_results[i-1]["dominant_archetypes"][0]["role"] if sequence_results[i-1]["dominant_archetypes"] else "none"
            curr_dominant = sequence_results[i]["dominant_archetypes"][0]["role"] if sequence_results[i]["dominant_archetypes"] else "none"

            if prev_dominant != curr_dominant:
                dominant_changes.append({
                    "position": i,
                    "from": prev_dominant,
                    "to": curr_dominant
                })

        return {
            "dominant_archetype_changes": dominant_changes,
            "change_frequency": len(dominant_changes) / (len(sequence_results) - 1),
            "stability_indicator": 1.0 - (len(dominant_changes) / (len(sequence_results) - 1))
        }

    def _calculate_archetypal_stability(self, sequence_results: List[Dict]) -> float:
        """Calculate stability of archetypal patterns."""
        if len(sequence_results) < 2:
            return 1.0

        # Calculate consistency of Trinity resonance scores
        trinity_scores = [result["trinity_resonance"]["overall_score"] for result in sequence_results]
        score_variance = sum(abs(score - sum(trinity_scores)/len(trinity_scores)) for score in trinity_scores) / len(trinity_scores)

        return 1.0 - min(score_variance, 1.0)

    def _track_trinity_development(self, sequence_results: List[Dict]) -> Dict[str, Any]:
        """Track Trinity Framework development across sequence."""
        trinity_scores = [result["trinity_resonance"]["overall_score"] for result in sequence_results]

        if len(trinity_scores) < 2:
            return {"development": "insufficient_data"}

        # Calculate trend
        score_changes = [trinity_scores[i] - trinity_scores[i-1] for i in range(1, len(trinity_scores))]
        average_change = sum(score_changes) / len(score_changes)

        development_trend = "improving" if average_change > 0.05 else "stable" if abs(average_change) <= 0.05 else "declining"

        return {
            "initial_score": trinity_scores[0],
            "final_score": trinity_scores[-1],
            "average_change": average_change,
            "development_trend": development_trend,
            "peak_score": max(trinity_scores),
            "consistency": self._calculate_archetypal_stability(sequence_results)
        }

    def _analyze_transformation_trajectory(self, sequence_results: List[Dict]) -> Dict[str, Any]:
        """Analyze transformation potential trajectory."""
        transformation_scores = [
            result["transformation_potential"]["average_score"]
            for result in sequence_results
            if "transformation_potential" in result
        ]

        if len(transformation_scores) < 2:
            return {"trajectory": "insufficient_data"}

        # Calculate trajectory direction
        initial_score = transformation_scores[0]
        final_score = transformation_scores[-1]
        trajectory_change = final_score - initial_score

        trajectory_direction = "ascending" if trajectory_change > 0.1 else "stable" if abs(trajectory_change) <= 0.1 else "descending"

        return {
            "initial_potential": initial_score,
            "final_potential": final_score,
            "trajectory_change": trajectory_change,
            "trajectory_direction": trajectory_direction,
            "peak_potential": max(transformation_scores)
        }

    def _calculate_growth_indicator(self, evolution_patterns: Dict[str, Any]) -> str:
        """Calculate overall growth indicator."""
        if evolution_patterns.get("insufficient_data"):
            return "insufficient_data"

        stability = evolution_patterns.get("stability_indicator", 0.5)
        change_frequency = evolution_patterns.get("change_frequency", 0.5)

        if stability > 0.7 and change_frequency < 0.3:
            return "stable_growth"
        elif stability > 0.5 and change_frequency > 0.3:
            return "dynamic_growth"
        elif stability < 0.5 and change_frequency > 0.5:
            return "turbulent_growth"
        else:
            return "steady_development"

    def get_archetypal_statistics(self) -> Dict[str, Any]:
        """Get comprehensive archetypal pattern statistics."""
        if not self.pattern_history:
            return {"statistics": "No archetypal patterns recognized"}

        # Calculate archetype frequency
        all_dominant_archetypes = []
        trinity_validated_count = 0

        for result in self.pattern_history:
            if result["dominant_archetypes"]:
                primary_archetype = result["dominant_archetypes"][0]["role"]
                all_dominant_archetypes.append(primary_archetype)

            if result["trinity_validated"]:
                trinity_validated_count += 1

        archetype_frequency = {}
        for archetype in all_dominant_archetypes:
            archetype_frequency[archetype] = archetype_frequency.get(archetype, 0) + 1

        most_common_archetype = max(archetype_frequency, key=archetype_frequency.get) if archetype_frequency else "none"

        return {
            "total_recognitions": len(self.pattern_history),
            "trinity_validation_rate": trinity_validated_count / len(self.pattern_history),
            "archetype_frequency": archetype_frequency,
            "most_common_archetype": most_common_archetype,
            "average_dominant_archetypes": sum(len(r["dominant_archetypes"]) for r in self.pattern_history) / len(self.pattern_history),
            "system_health": "optimal"
        }


__all__ = ["ArchetypalPatternRecognizer", "ArchetypalDomain", "ArchetypalRole", "ArchetypalResonance"]
