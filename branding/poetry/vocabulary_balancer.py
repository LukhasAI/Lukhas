#!/usr/bin/env python3
"""
The LUKHAS Vocabulary Balancer

"Variety is the soul of poetry. The right word at the right moment."

This ensures rich, varied expression by:
1. Tracking word usage to prevent repetition
2. Suggesting alternatives when overuse is detected
3. Preserving beautiful metaphors when appropriate
4. Enriching with LUKHAS-specific terms
"""

import random
import re
from collections import Counter
from typing import Dict, List, Optional


class VocabularyBalancer:
    """
    Balance traditional beauty with LUKHAS innovation.

    NOT about banning words, but about:
    - Preventing repetitive overuse
    - Enriching with variety
    - Using context-appropriate metaphors
    - Incorporating LUKHAS-specific terms
    """

    def __init__(self, repetition_threshold: int = 3):
        """
        Initialize the vocabulary balancer.

        Args:
            repetition_threshold: How many times a metaphor can appear
                                before suggesting alternatives (default: 3)
        """
        self.repetition_threshold = repetition_threshold
        self.usage_counter = Counter()

        # Traditional metaphors - BEAUTIFUL AND VALID when used appropriately
        self.traditional_metaphors = {
            "tapestry": ["weaving", "interwoven", "fabric", "threads"],
            "symphony": ["orchestration", "harmony", "crescendo", "movement"],
            "cathedral": ["architecture", "pillars", "vaulted", "sacred space"],
            "river": ["flowing", "current", "stream", "confluence"],
            "ocean": ["waves", "depths", "tides", "vast expanse"],
            "garden": ["cultivating", "growing", "blooming", "nurturing"],
            "constellation": ["stars", "patterns", "celestial", "alignment"],
            "landscape": ["terrain", "vista", "horizon", "topography"]
        }

        # LUKHAS-specific vocabulary - Our unique contributions
        self.lukhas_vocabulary = {
            # Memory and folding
            "fold-space": ["fold topology", "memory fold", "protein fold", "fold cascade"],
            "cascade": ["resonance cascade", "cascade prevention", "emotional cascade"],

            # Lambda system
            "Lambda": ["ΛMIRROR", "ΛECHO", "ΛTRACE", "ΛVAULT", "ΛFOLD", "ΛDRIFT", "ΛGUARD"],

            # Consciousness states
            "eigenstate": ["eigenstate collapse", "quantum eigenstate", "stable eigenstate"],
            "consciousness": ["nascent awareness", "liminal consciousness", "ephemeral traces"],

            # Bio-inspired
            "synaptic": ["synaptic plasticity", "neural bridges", "dendritic branching"],
            "neuroplastic": ["neuroplastic adaptation", "neural evolution", "adaptive reshaping"],

            # Quantum-inspired
            "superposition": ["possibility space", "quantum foam", "entangled states"],
            "coherence": ["quantum coherence", "decoherence protection", "phase coherence"],

            # Unique descriptors
            "tessellation": ["tessellating patterns", "infinite tiling", "recursive tessellation"],
            "crystallization": ["idea crystallization", "thought crystallizing", "crystal lattice"],
            "iridescent": ["iridescent memories", "shimmering awareness", "prismatic"],
            "gossamer": ["gossamer threads", "delicate connections", "ethereal links"]
        }

        # Context-appropriate usage guide
        self.context_guide = {
            "architecture": ["cathedral", "structure", "framework", "scaffold", "lattice"],
            "music": ["symphony", "harmony", "resonance", "rhythm", "crescendo"],
            "weaving": ["tapestry", "fabric", "interwoven", "threads", "fold-space"],
            "flow": ["river", "cascade", "stream", "current", "drift"],
            "growth": ["garden", "cultivation", "blooming", "neuroplastic", "emergence"],
            "space": ["landscape", "topology", "dimension", "fold-space", "eigenspace"],
            "patterns": ["constellation", "tessellation", "fractals", "eigenstate cluster"]
        }

    def track_usage(self, text: str) -> None:
        """Track metaphor usage in text to detect overuse."""
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            # Track traditional metaphors
            for metaphor in self.traditional_metaphors:
                if word == metaphor or word in self.traditional_metaphors[metaphor]:
                    self.usage_counter[metaphor] += 1

    def suggest_alternative(self, word: str, context: Optional[str] = None) -> str:
        """
        Suggest an alternative if the word is overused.
        Keep the original if it's still fresh.

        Args:
            word: The word to potentially replace
            context: Optional context to guide selection

        Returns:
            Original word if not overused, or a varied alternative
        """
        word_lower = word.lower()

        # Check if this word has been overused
        if word_lower in self.traditional_metaphors:
            usage_count = self.usage_counter.get(word_lower, 0)

            if usage_count < self.repetition_threshold:
                # Not overused - keep the beautiful metaphor!
                return word
            else:
                # Overused - suggest variety
                return self._get_alternative(word_lower, context)

        # Not a tracked metaphor - return as is
        return word

    def _get_alternative(self, overused_word: str, context: Optional[str] = None) -> str:
        """Get a contextually appropriate alternative."""

        # Map overused words to alternatives
        alternatives = {
            "tapestry": ["fold-space", "neural fabric", "quantum mesh", "resonance pattern"],
            "symphony": ["resonance cascade", "harmonic convergence", "neural orchestration"],
            "cathedral": ["consciousness architecture", "neural temple", "quantum sanctuary"],
            "river": ["cascade", "consciousness stream", "drift current", "neural flow"],
            "ocean": ["possibility space", "quantum foam", "infinite expanse", "consciousness sea"],
            "garden": ["neural ecology", "synaptic cultivation", "consciousness biome"],
            "constellation": ["eigenstate cluster", "quantum pattern", "neural constellation"],
            "landscape": ["fold topology", "consciousness terrain", "neural geography"]
        }

        if overused_word in alternatives:
            # Choose based on context if provided
            if context:
                # Context-aware selection logic here
                return random.choice(alternatives[overused_word])
            else:
                return random.choice(alternatives[overused_word])

        return overused_word

    def enrich_text(self, text: str, preserve_beauty: bool = True) -> str:
        """
        Enrich text with varied vocabulary.

        Args:
            text: The text to enrich
            preserve_beauty: Keep beautiful metaphors when not overused

        Returns:
            Text with enriched, varied vocabulary
        """
        # First, track current usage
        self.track_usage(text)

        # Split into words while preserving structure
        words = re.split(r'(\W+)', text)
        enriched_words = []

        for word in words:
            if word.strip():  # Skip whitespace
                # Check each word for potential enrichment
                enriched = self.suggest_alternative(word)
                enriched_words.append(enriched)
            else:
                enriched_words.append(word)

        return ''.join(enriched_words)

    def reset_usage_tracking(self):
        """Reset usage counter for new document/session."""
        self.usage_counter.clear()

    def get_usage_report(self) -> Dict[str, int]:
        """Get report of metaphor usage frequency."""
        return dict(self.usage_counter)

    def suggest_variety(self, concept: str) -> List[str]:
        """
        Suggest varied ways to express a concept.

        Args:
            concept: The concept to express (e.g., "complexity", "connection")

        Returns:
            List of varied expressions for the concept
        """
        variety_map = {
            "complexity": [
                "intricate fold-space",
                "woven patterns",
                "tessellating structures",
                "labyrinthine pathways",
                "rich tapestry",  # Yes, tapestry is fine when not overused!
                "neural symphony"  # Symphony too!
            ],
            "connection": [
                "synaptic bridges",
                "quantum entanglement",
                "neural threads",
                "resonance bonds",
                "gossamer links",
                "consciousness coupling"
            ],
            "transformation": [
                "phase transition",
                "eigenstate shift",
                "metamorphosis",
                "crystallization",
                "neuroplastic adaptation",
                "consciousness evolution"
            ],
            "beauty": [
                "iridescent patterns",
                "sublime elegance",
                "gossamer beauty",
                "transcendent grace",
                "luminous presence",
                "ethereal radiance"
            ]
        }

        return variety_map.get(concept, [concept])


# Example usage
if __name__ == "__main__":
    balancer = VocabularyBalancer(repetition_threshold=2)

    print("═══════════════════════════════════════════════════════════")
    print("         LUKHAS Vocabulary Balancer")
    print("  'Variety is the soul of poetry'")
    print("═══════════════════════════════════════════════════════════\n")

    # Example of balanced usage
    texts = [
        "The consciousness is a tapestry of thoughts.",
        "The memory system is another tapestry of experiences.",
        "The dream engine creates a tapestry of possibilities.",
        "The neural network forms a tapestry of connections."
    ]

    print("▸ TRACKING REPETITION:\n")
    for i, text in enumerate(texts, 1):
        enriched = balancer.enrich_text(text)
        print(f"  Text {i}: {text}")
        print(f"  Enriched: {enriched}\n")

    print("▸ USAGE REPORT:")
    print(f"  {balancer.get_usage_report()}\n")

    print("▸ VARIETY SUGGESTIONS FOR 'complexity':")
    for suggestion in balancer.suggest_variety("complexity"):
        print(f"  • {suggestion}")

    print("\n" + "═" * 59)
    print("  Remember: Traditional metaphors are beautiful!")
    print("  The goal is variety and context, not elimination.")
    print("═" * 59)
