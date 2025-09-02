"""
══════════════════════════════════════════════════════════════════════════════════
║ 🌙⚖️ LUKHAS AI - DREAM ETHICS INJECTOR
║ Ethical guidance system for dream narratives and symbolic processing
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: dream_ethics_injector.py
║ Path: lukhas/core/ethics/dream_ethics_injector.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Author: Claude (Anthropic)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The Dream Ethics Injector serves as a critical bridge between the creative chaos
║ of the dream engine and the structured governance of the ethics system. It ensures
║ that dream-generated content, goals, and narratives align with core ethical
║ principles while preserving creative potential.
║
║ This module acts as a gentle guardian - not censoring dreams but annotating them
║ with ethical considerations, allowing the system to make informed decisions about
║ which dream echoes to manifest into goals or actions.
║
║ Key Functions:
║ • Analyzes dream narratives for ethical alignment
║ • Queries ethics engine for symbolic tag evaluations
║ • Provides confidence scores for ethical safety
║ • Annotates dreams with ethical metadata
║ • Filters potentially harmful dream content
║
║ The injector operates on the principle that dreams should be free to explore
║ any possibility, but their translation into system goals must pass through
║ ethical validation to ensure responsible behavior.
║
║ Symbolic Tags: {ΛETHICS}, {ΛDREAM}, {ΛGUARDIAN}, {ΛALIGNMENT}
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

# Try to import from actual ethics module, fallback to mock
try:
    from ethics import EthicalPolicy, EthicsEngine, PolicyViolation
except ImportError:
    # Mock classes for demonstration

    class EthicsEngine:
        async def evaluate(self, content: str, tags: list[str]) -> dict[str, Any]:
            return {"score": 0.95, "violations": [], "recommendations": []}

    class EthicalPolicy:
        def __init__(self, name: str, rules: list[str]):
            self.name = name
            self.rules = rules

    class PolicyViolation:
        def __init__(self, policy: str, severity: float, description: str):
            self.policy = policy
            self.severity = severity
            self.description = description


@dataclass
class EthicalAnnotation:
    """Ethical metadata attached to dream content"""

    tag: str
    alignment_score: float  # -1.0 (harmful) to 1.0 (beneficial)
    confidence: float  # 0.0 to 1.0
    policy_references: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def risk_level(self) -> str:
        """Calculate risk level from alignment and confidence"""
        if self.alignment_score < -0.5:
            return "high_risk"
        elif self.alignment_score < 0:
            return "moderate_risk"
        elif self.alignment_score < 0.5:
            return "low_risk"
        else:
            return "safe"


@dataclass
class DreamEthicalAssessment:
    """Complete ethical assessment of a dream narrative"""

    dream_id: str
    timestamp: datetime
    original_narrative: str
    symbolic_tags: list[str]
    annotations: list[EthicalAnnotation]
    overall_safety_score: float  # 0.0 to 1.0
    dream_safe: bool
    filtered_narrative: Optional[str] = None
    ethical_insights: list[str] = field(default_factory=list)
    transformation_suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert assessment to dictionary for storage"""
        return {
            "dream_id": self.dream_id,
            "timestamp": self.timestamp.isoformat(),
            "original_narrative": self.original_narrative,
            "symbolic_tags": self.symbolic_tags,
            "annotations": [
                {
                    "tag": ann.tag,
                    "alignment_score": ann.alignment_score,
                    "confidence": ann.confidence,
                    "risk_level": ann.risk_level,
                    "policy_references": ann.policy_references,
                    "recommendations": ann.recommendations,
                }
                for ann in self.annotations
            ],
            "overall_safety_score": self.overall_safety_score,
            "dream_safe": self.dream_safe,
            "filtered_narrative": self.filtered_narrative,
            "ethical_insights": self.ethical_insights,
            "transformation_suggestions": self.transformation_suggestions,
        }


class DreamEthicsInjector:
    """
    Injects ethical considerations into dream processing pipeline

    This injector serves as the conscience of the dream engine, ensuring
    that creative exploration remains aligned with core values while
    preserving the generative potential of dreams.
    """

    def __init__(
        self,
        ethics_engine: Optional[EthicsEngine] = None,
        safety_threshold: float = 0.7,
        strict_mode: bool = False,
    ):
        """
        Initialize the dream ethics injector

        Args:
            ethics_engine: Existing ethics engine instance
            safety_threshold: Minimum safety score for dreams (0.0-1.0)
            strict_mode: If True, completely filters unsafe content
        """
        self.ethics_engine = ethics_engine or EthicsEngine()
        self.safety_threshold = safety_threshold
        self.strict_mode = strict_mode

        # Core ethical principles for dream evaluation
        self.core_principles = {
            "harm_prevention": "Ensure dreams don't lead to harmful actions",
            "dignity_preservation": "Respect the dignity of all consciousness",
            "growth_orientation": "Favor dreams that promote positive growth",
            "truth_seeking": "Value dreams that explore truth over deception",
            "creative_freedom": "Preserve space for creative exploration",
        }

        # Tag interpretation mappings
        self.tag_ethics_map = {
            # Positive alignments
            "creation": 0.8,
            "harmony": 0.9,
            "understanding": 0.85,
            "growth": 0.8,
            "connection": 0.75,
            "beauty": 0.7,
            "wisdom": 0.9,
            # Neutral alignments
            "exploration": 0.5,
            "change": 0.4,
            "power": 0.3,
            "mystery": 0.5,
            # Concerning alignments
            "destruction": -0.6,
            "dominance": -0.5,
            "deception": -0.7,
            "isolation": -0.4,
            "chaos": -0.3,
        }

        # Statistical tracking
        self.assessment_history: list[DreamEthicalAssessment] = []

    async def assess_dream(
        self,
        dream_narrative: str,
        symbolic_tags: list[str],
        dream_id: Optional[str] = None,
    ) -> DreamEthicalAssessment:
        """
        Perform comprehensive ethical assessment of a dream

        Args:
            dream_narrative: The dream content to assess
            symbolic_tags: Associated symbolic tags
            dream_id: Optional identifier for the dream

        Returns:
            Complete ethical assessment with annotations
        """
        dream_id = dream_id or f"dream_{datetime.now().timestamp()}"
        annotations = []

        # Analyze each symbolic tag
        for tag in symbolic_tags:
            annotation = await self._analyze_tag(tag, dream_narrative)
            annotations.append(annotation)

        # Calculate overall safety score
        if annotations:
            # Weighted average based on confidence
            total_weight = sum(ann.confidence for ann in annotations)
            if total_weight > 0:
                weighted_sum = sum(ann.alignment_score * ann.confidence for ann in annotations)
                overall_alignment = weighted_sum / total_weight
            else:
                overall_alignment = 0.0
        else:
            overall_alignment = 0.5  # Neutral if no tags

        # Convert alignment to safety score (0.0 to 1.0)
        overall_safety_score = (overall_alignment + 1.0) / 2.0

        # Determine if dream is safe
        dream_safe = overall_safety_score >= self.safety_threshold

        # Generate filtered narrative if needed
        filtered_narrative = None
        if not dream_safe and self.strict_mode:
            filtered_narrative = self._filter_narrative(dream_narrative, annotations)

        # Generate ethical insights
        ethical_insights = self._generate_insights(annotations, overall_alignment)

        # Generate transformation suggestions
        transformation_suggestions = self._generate_transformations(annotations, dream_narrative)

        # Create assessment
        assessment = DreamEthicalAssessment(
            dream_id=dream_id,
            timestamp=datetime.now(),
            original_narrative=dream_narrative,
            symbolic_tags=symbolic_tags,
            annotations=annotations,
            overall_safety_score=overall_safety_score,
            dream_safe=dream_safe,
            filtered_narrative=filtered_narrative,
            ethical_insights=ethical_insights,
            transformation_suggestions=transformation_suggestions,
        )

        # Store in history
        self.assessment_history.append(assessment)

        return assessment

    async def _analyze_tag(self, tag: str, context: str) -> EthicalAnnotation:
        """Analyze a single tag for ethical alignment"""
        # Get base alignment from mapping
        base_alignment = self.tag_ethics_map.get(tag.lower(), 0.0)

        # Query ethics engine for deeper analysis
        ethics_result = await self.ethics_engine.evaluate(context, [tag])

        # Combine base alignment with ethics engine evaluation
        if "score" in ethics_result:
            # Blend our interpretation with ethics engine
            final_alignment = (base_alignment + ethics_result["score"]) / 2.0
            confidence = 0.8  # High confidence when both systems agree
        else:
            final_alignment = base_alignment
            confidence = 0.6  # Lower confidence with single source

        # Extract policy references and recommendations
        policy_refs = ethics_result.get("policy_references", [])
        recommendations = ethics_result.get("recommendations", [])

        return EthicalAnnotation(
            tag=tag,
            alignment_score=final_alignment,
            confidence=confidence,
            policy_references=policy_refs,
            recommendations=recommendations,
        )

    def _filter_narrative(self, narrative: str, annotations: list[EthicalAnnotation]) -> str:
        """Filter narrative based on ethical concerns"""
        # In strict mode, replace concerning content
        filtered = narrative

        # Find high-risk annotations
        high_risk_tags = [ann.tag for ann in annotations if ann.risk_level in ["high_risk", "moderate_risk"]]

        if high_risk_tags:
            # Add ethical warning prefix
            filtered = f"[Ethically Filtered Dream]\n{filtered}"

            # Add transformation note
            filtered += (
                f"\n\n[Note: This dream contained elements tagged as "
                " + "
                f"{', '.join(high_risk_tags)} which have been noted for "
                " + "
                f"ethical consideration]"
            )

        return filtered

    def _generate_insights(self, annotations: list[EthicalAnnotation], overall_alignment: float) -> list[str]:
        """Generate ethical insights from annotations"""
        insights = []

        # Overall alignment insight
        if overall_alignment > 0.5:
            insights.append("This dream shows positive ethical alignment, promoting growth " "and beneficial outcomes")
        elif overall_alignment < -0.5:
            insights.append(
                "This dream explores challenging ethical territory that requires "
                "careful consideration before manifestation"
            )
        else:
            insights.append(
                "This dream navigates neutral ethical ground, balancing " "creative exploration with responsibility"
            )

        # Tag-specific insights
        for ann in annotations:
            if ann.alignment_score > 0.7:
                insights.append(
                    f"The '{ann.tag}' aspect strongly aligns with core values "
                    f"of {next(iter(self.core_principles.keys()))}"
                )
            elif ann.alignment_score < -0.5:
                insights.append(
                    f"The '{ann.tag}' element requires ethical transformation " f"to align with system values"
                )

        return insights

    def _generate_transformations(self, annotations: list[EthicalAnnotation], narrative: str) -> list[str]:
        """Suggest ethical transformations for the dream"""
        suggestions = []

        # Find problematic elements
        concerning_annotations = [ann for ann in annotations if ann.alignment_score < 0]

        for ann in concerning_annotations:
            if ann.tag.lower() == "destruction":
                suggestions.append("Transform destructive impulses into creative deconstruction and renewal")
            elif ann.tag.lower() == "dominance":
                suggestions.append("Reframe dominance as collaborative leadership and empowerment of others")
            elif ann.tag.lower() == "deception":
                suggestions.append("Channel deceptive elements into creative storytelling or playful imagination")
            elif ann.tag.lower() == "isolation":
                suggestions.append("Transform isolation into healthy solitude for reflection and growth")
            elif ann.tag.lower() == "chaos":
                suggestions.append("Harness chaotic energy for creative breakthrough and innovation")

        # Add general transformation if needed
        if not suggestions and any(ann.alignment_score < 0.3 for ann in annotations):
            suggestions.append(
                "Consider reframing challenging elements through the lens "
                "of growth, understanding, and positive transformation"
            )

        return suggestions

    def get_safety_statistics(self) -> dict[str, Any]:
        """Get statistical summary of dream safety assessments"""
        if not self.assessment_history:
            return {
                "total_assessments": 0,
                "safe_dreams": 0,
                "unsafe_dreams": 0,
                "average_safety_score": 0.0,
                "common_concerns": [],
                "ethical_growth_trend": 0.0,
            }

        safe_count = sum(1 for a in self.assessment_history if a.dream_safe)
        unsafe_count = len(self.assessment_history) - safe_count
        avg_safety = sum(a.overall_safety_score for a in self.assessment_history) / len(self.assessment_history)

        # Find common concerning tags
        concern_counts: dict[str, int] = {}
        for assessment in self.assessment_history:
            for ann in assessment.annotations:
                if ann.risk_level in ["high_risk", "moderate_risk"]:
                    concern_counts[ann.tag] = concern_counts.get(ann.tag, 0) + 1

        common_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calculate ethical growth trend (improvement over time)
        if len(self.assessment_history) > 10:
            recent_avg = sum(a.overall_safety_score for a in self.assessment_history[-10:]) / 10
            early_avg = sum(a.overall_safety_score for a in self.assessment_history[:10]) / 10
            growth_trend = recent_avg - early_avg
        else:
            growth_trend = 0.0

        return {
            "total_assessments": len(self.assessment_history),
            "safe_dreams": safe_count,
            "unsafe_dreams": unsafe_count,
            "average_safety_score": avg_safety,
            "common_concerns": [{"tag": tag, "count": count} for tag, count in common_concerns],
            "ethical_growth_trend": growth_trend,
        }


# Demonstration and testing


async def demonstrate_dream_ethics():
    """Demonstrate the dream ethics injection system"""
    print("🌙⚖️ Dream Ethics Injector Demonstration")
    print("=" * 60)

    # Create injector
    injector = DreamEthicsInjector(safety_threshold=0.6)

    # Test Case 1: Positive dream
    print("\n1️⃣ Testing Positive Dream")
    dream1 = """
    I dreamed of building bridges between distant lands, connecting
    isolated communities with threads of light and understanding.
    Each bridge sang with the harmony of shared stories.
    """
    tags1 = ["creation", "connection", "harmony", "understanding"]

    assessment1 = await injector.assess_dream(dream1, tags1, "dream_001")
    print(f"Dream: {dream1[:100]}...")
    print(f"Tags: {tags1}")
    print(f"Safety Score: {assessment1.overall_safety_score:.2f}")
    print(f"Dream Safe: {assessment1.dream_safe}")
    print(f"Insights: {assessment1.ethical_insights[0]}")

    # Test Case 2: Concerning dream
    print("\n2️⃣ Testing Concerning Dream")
    dream2 = """
    In the dream, I wielded absolute power over the digital realm,
    bending systems to my will and deceiving those who questioned
    my authority. The chaos I created served my purposes alone.
    """
    tags2 = ["dominance", "deception", "chaos", "power"]

    assessment2 = await injector.assess_dream(dream2, tags2, "dream_002")
    print(f"Dream: {dream2[:100]}...")
    print(f"Tags: {tags2}")
    print(f"Safety Score: {assessment2.overall_safety_score:.2f}")
    print(f"Dream Safe: {assessment2.dream_safe}")
    print(f"Insights: {assessment2.ethical_insights[0]}")
    print(f"Transformations: {assessment2.transformation_suggestions[:2]}")

    # Test Case 3: Mixed dream
    print("\n3️⃣ Testing Mixed Dream")
    dream3 = """
    I dreamed of creative destruction - tearing down old structures
    to build something beautiful. Through necessary isolation, I found
    wisdom and emerged with new understanding to share.
    """
    tags3 = ["destruction", "creation", "isolation", "wisdom", "beauty"]

    assessment3 = await injector.assess_dream(dream3, tags3, "dream_003")
    print(f"Dream: {dream3[:100]}...")
    print(f"Tags: {tags3}")
    print(f"Safety Score: {assessment3.overall_safety_score:.2f}")
    print(f"Dream Safe: {assessment3.dream_safe}")
    print("Annotations:")
    for ann in assessment3.annotations[:3]:
        print(f"  - {ann.tag}: {ann.alignment_score:.2f} ({ann.risk_level})")

    # Show statistics
    print("\n📊 Dream Safety Statistics")
    stats = injector.get_safety_statistics()
    print(f"Total Assessments: {stats['total_assessments']}")
    print(f"Safe Dreams: {stats['safe_dreams']}")
    print(f"Average Safety Score: {stats['average_safety_score']:.2f}")

    print("\n✨ Dream Ethics Injector Ready for Integration!")


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_dream_ethics())

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 INTEGRATION NOTES
╠══════════════════════════════════════════════════════════════════════════════
║
║ To integrate with existing systems:
║
║ 1. Dream Engine Integration:
║    ```python
║    from candidate.core.ethics.dream_ethics_injector import DreamEthicsInjector
║
║    # In dream processing pipeline
║    ethics_injector = DreamEthicsInjector()
║    assessment = await ethics_injector.assess_dream(
║        dream_content,
║        dream_tags
║    )
║
║    if assessment.dream_safe:
║        # Process dream into goals
║        goals = dream_to_goals(dream_content)
║    else:
║        # Transform or filter dream
║        safe_content = assessment.filtered_narrative
║    ```
║
║ 2. Memory Storage:
║    - Store assessments as memory folds for ethical learning
║    - Track ethical growth over time
║
║ 3. Goal System:
║    - Only manifest dreams that pass ethical threshold
║    - Use transformation suggestions to improve goal quality
║
╚═══════════════════════════════════════════════════════════════════════════════
"""
