"""
MATRIZ Thought Node
===================

Generates internal thought representations from attended features.
Implements symbolic reasoning, pattern synthesis, and creative ideation.

Performance Target: <100ms p95 latency
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import hashlib


@dataclass
class Thought:
    """Internal thought representation"""
    content: str
    confidence: float  # [0, 1]
    novelty: float  # [0, 1]
    symbolic_form: Dict
    reasoning_chain: List[str]
    thought_hash: str


class ThoughtNode:
    """
    Generate internal thought representations.

    Implements:
    - Symbolic reasoning (logic chains)
    - Pattern synthesis (analogy, metaphor)
    - Creative ideation (novelty generation)
    - Thought coherence validation
    """

    def __init__(self, lane: str = "experimental"):
        self.lane = lane
        self._thought_cache = {}  # Prevent duplicate thoughts

    def process(
        self,
        attention_map,  # AttentionMap from attention node
        memory_context: Dict,
        mode: str = "analytical"  # analytical | creative | reflective
    ) -> Thought:
        """
        Generate thought from attended features.

        Modes:
        - analytical: Logical reasoning, fact synthesis
        - creative: Novel combinations, metaphor generation
        - reflective: Meta-cognitive analysis
        """
        # Extract focused features
        focused_features = attention_map.features[attention_map.focus_window]

        # Generate symbolic representation
        symbolic = self._symbolize(focused_features, memory_context)

        # Build reasoning chain
        reasoning = self._build_reasoning_chain(symbolic, mode)

        # Synthesize thought content
        content = self._synthesize_content(reasoning, mode)

        # Compute novelty and confidence
        novelty = self._compute_novelty(content)
        confidence = self._compute_confidence(attention_map.attention_score, novelty)

        # Generate thought hash (for deduplication)
        thought_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        thought = Thought(
            content=content,
            confidence=confidence,
            novelty=novelty,
            symbolic_form=symbolic,
            reasoning_chain=reasoning,
            thought_hash=thought_hash
        )

        # Cache thought
        self._thought_cache[thought_hash] = thought

        return thought

    def _symbolize(self, features, memory) -> Dict:
        """Convert numeric features to symbolic representation"""
        # Simplified: map features to symbolic concepts
        # In production: use learned concept embeddings

        return {
            "concepts": ["concept_" + str(i) for i in range(len(features[:5]))],
            "relations": ["related_to", "part_of", "causes"],
            "attributes": {"salience": "high", "novelty": "medium"}
        }

    def _build_reasoning_chain(self, symbolic: Dict, mode: str) -> List[str]:
        """Build logical reasoning chain"""
        if mode == "analytical":
            return [
                "Observe: " + ", ".join(symbolic["concepts"][:2]),
                "Analyze: Pattern X relates to Y",
                "Conclude: Hypothesis H probable"
            ]
        elif mode == "creative":
            return [
                "Associate: Novel combination",
                "Synthesize: Metaphor generation",
                "Ideate: Creative insight"
            ]
        else:  # reflective
            return [
                "Monitor: Current thought process",
                "Evaluate: Thought quality high",
                "Meta-cognize: Awareness stable"
            ]

    def _synthesize_content(self, reasoning: List[str], mode: str) -> str:
        """Synthesize natural language thought content"""
        # Join reasoning chain
        content = " → ".join(reasoning)
        return content

    def _compute_novelty(self, content: str) -> float:
        """Compute thought novelty [0, 1]"""
        # Check against thought cache
        thought_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        if thought_hash in self._thought_cache:
            return 0.0  # Duplicate thought

        # Simple heuristic: longer thoughts = more novel
        # In production: use semantic similarity
        novelty = min(1.0, len(content) / 200)
        return novelty

    def _compute_confidence(self, attention_score: float, novelty: float) -> float:
        """Compute thought confidence [0, 1]"""
        # High attention + low novelty = high confidence
        # Low attention or very high novelty = low confidence

        confidence = attention_score * (1.0 - 0.5 * novelty)
        return max(0.0, min(1.0, confidence))
