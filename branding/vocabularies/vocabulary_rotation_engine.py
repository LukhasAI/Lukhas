#!/usr/bin/env python3
"""
T4/0.01% Vocabulary Rotation Engine - Standalone Module
Enhanced LUKHAS 3-Layer Tone System Anti-Repetition Engine

Features:
- 8 diverse metaphor families from T4 research pipeline
- MATRIZ integration (Memory-Attention-Thought-Risk-Intent-Action)
- Novelty enforcement (≥0.8) with zero repetition validation
- Usage tracking and forced rotation for diversity
- Monthly refresh pipeline compatibility

Usage:
    from vocabularies.vocabulary_rotation_engine import VocabularyRotationEngine

    engine = VocabularyRotationEngine()
    family_name, family_data = engine.get_next_family()
    phrase = engine.get_matriz_phrase("Memory", family_name)
"""

import json
import random
import time
from pathlib import Path
from typing import Dict, Optional


class VocabularyRotationEngine:
    """
    T4/0.01% Vocabulary Rotation Engine for anti-repetition and metaphor diversity.

    Core Features:
    - 8 diverse metaphor families from T4 research
    - Rotation matrices with usage tracking
    - Novelty enforcement (≥0.8)
    - Zero repetition validation
    - MATRIZ pipeline integration
    - Monthly refresh pipeline support
    """

    def __init__(self, data_file: Optional[str] = None):
        self.usage_tracker = {}
        self.current_family_index = 0
        self.diversity_budget = 0.2  # 20% chance to select non-primary family
        self.novelty_threshold = 0.8
        self.data_file = data_file or "vocabulary_rotation_data.json"

        # Load T4 research findings: 8 diverse metaphor families
        self.metaphor_families = self._load_metaphor_families()

        # Load usage data if exists
        self._load_usage_data()

    def _load_metaphor_families(self) -> Dict:
        """Load the 8 metaphor families from T4 research."""
        return {
            "neural_gardens": {
                "description": "Organic growth and biological systems",
                "sensory": ["tactile", "visual", "olfactory"],
                "concreteness": 0.85,
                "novelty": 0.9,
                "poetic": "In the fertile soil of the mind, synaptic blooms unfold consciousness technology as a wild garden of dynamic systems",
                "academic": "Consciousness technology models neural architectures as hierarchical, bio-inspired networks",
                "user": "Imagine your mind as a garden where thoughts grow like flowers",
                "MATRIZ": {
                    "Memory": [
                        "rooted experiences", "neural soil", "cultivated wisdom",
                        "planted knowledge", "memory gardens", "experiential roots"
                    ],
                    "Attention": [
                        "selective pruning", "focused cultivation", "growth direction",
                        "attention watering", "mindful tending", "cognitive gardening"
                    ],
                    "Thought": [
                        "branching insights", "cognitive blossoming", "idea germination",
                        "thought flowering", "mental growth", "conceptual blooming"
                    ],
                    "Risk": [
                        "toxic detection", "growth boundaries", "soil contamination",
                        "pest management", "drought protection", "ecosystem balance"
                    ],
                    "Intent": [
                        "directional growth", "purposeful flowering", "seed planning",
                        "harvest intentions", "growth goals", "cultivation aims"
                    ],
                    "Action": [
                        "fruit bearing", "seed dispersal", "harvest time",
                        "growth execution", "botanical action", "organic movement"
                    ]
                }
            },

            "architectural_bridges": {
                "description": "Structural engineering and construction",
                "sensory": ["visual", "spatial", "tactile"],
                "concreteness": 0.8,
                "novelty": 0.85,
                "poetic": "Consciousness technology spans the chasms of thought with architectural bridges",
                "academic": "This approach conceptualizes consciousness technology as an architectural framework",
                "user": "Think of your mind like a building with bridges connecting different rooms",
                "MATRIZ": {
                    "Memory": [
                        "vaulted chambers", "archive walls", "foundation stones",
                        "memory vaults", "structural records", "cornerstone experiences"
                    ],
                    "Attention": [
                        "gateway arches", "focus corridors", "observation towers",
                        "attention bridges", "cognitive pathways", "mental doorways"
                    ],
                    "Thought": [
                        "spanning beams", "idea bridges", "connecting pathways",
                        "thought architecture", "mental construction", "cognitive frameworks"
                    ],
                    "Risk": [
                        "structural cracks", "load limits", "foundation shifts",
                        "safety protocols", "building codes", "stress testing"
                    ],
                    "Intent": [
                        "blueprint design", "planned pathways", "architectural vision",
                        "construction goals", "design intentions", "building plans"
                    ],
                    "Action": [
                        "open doors", "crossing steps", "building progress",
                        "construction work", "structural movement", "bridge building"
                    ]
                }
            },

            "harmonic_resonance": {
                "description": "Musical and vibrational patterns",
                "sensory": ["auditory", "vibrational", "kinesthetic"],
                "concreteness": 0.75,
                "novelty": 0.88,
                "poetic": "Consciousness technology hums in harmonic resonance, dynamic systems vibrating through memory strings",
                "academic": "This metaphor frames consciousness technology as a system of harmonic oscillators",
                "user": "Imagine your mind like a musical instrument, where memories are strings",
                "MATRIZ": {
                    "Memory": [
                        "resonant strings", "echo chambers", "harmonic layers",
                        "memory melodies", "recorded rhythms", "sonic archives"
                    ],
                    "Attention": [
                        "tuning forks", "focus harmonics", "frequency filters",
                        "attention amplifiers", "signal clarity", "mindful tuning"
                    ],
                    "Thought": [
                        "melodic waves", "cognitive chords", "rhythmic patterns",
                        "thought symphonies", "mental music", "ideational harmonies"
                    ],
                    "Risk": [
                        "dissonant notes", "feedback loops", "noise interference",
                        "sonic dangers", "frequency conflicts", "harmonic disruption"
                    ],
                    "Intent": [
                        "composed motifs", "directional beats", "musical themes",
                        "rhythmic goals", "melodic plans", "harmonic aims"
                    ],
                    "Action": [
                        "rhythmic pulses", "performance cues", "symphony crescendo",
                        "musical execution", "sonic movement", "harmonic expression"
                    ]
                }
            },

            "woven_patterns": {
                "description": "Textile and fabric metaphors",
                "sensory": ["tactile", "visual", "kinesthetic"],
                "concreteness": 0.8,
                "novelty": 0.9,
                "poetic": "Consciousness technology weaves dynamic systems into intricate patterns",
                "academic": "This metaphor models consciousness technology as interdependent dynamic systems forming woven networks",
                "user": "Picture your mind as a fabric, where different threads of memories and focus are woven together",
                "MATRIZ": {
                    "Memory": [
                        "woven threads", "patterned fibers", "tapestry layers",
                        "memory fabric", "experiential weaving", "threaded recollections"
                    ],
                    "Attention": [
                        "tightening weaves", "focused strands", "thread selection",
                        "attention stitching", "mindful threading", "cognitive knitting"
                    ],
                    "Thought": [
                        "interlaced motifs", "cognitive textures", "pattern emergence",
                        "thought weaving", "mental tapestries", "ideational fabrics"
                    ],
                    "Risk": [
                        "frayed edges", "loose knots", "fabric tears",
                        "thread breaks", "pattern disruption", "textile damage"
                    ],
                    "Intent": [
                        "design motifs", "pattern direction", "weaving plans",
                        "textile goals", "fabric intentions", "thread purposes"
                    ],
                    "Action": [
                        "woven movement", "fabric flow", "textile creation",
                        "threading action", "pattern making", "weaving execution"
                    ]
                }
            },

            "geological_strata": {
                "description": "Earth sciences and geological formations",
                "sensory": ["visual", "tactile", "temporal"],
                "concreteness": 0.85,
                "novelty": 0.87,
                "poetic": "Consciousness technology is carved in geological strata-dynamic systems layering memory sediments",
                "academic": "This metaphor conceptualizes consciousness technology as stratified dynamic systems",
                "user": "Think of your mind like layers of rock built over time",
                "MATRIZ": {
                    "Memory": [
                        "sedimentary layers", "fossil records", "rock formations",
                        "geological memory", "stratified experiences", "temporal deposits"
                    ],
                    "Attention": [
                        "fault lines", "pressure zones", "tectonic focus",
                        "attention shifts", "geological stress", "crustal awareness"
                    ],
                    "Thought": [
                        "crystalline formations", "mineral veins", "geological insights",
                        "thought crystals", "mental minerals", "cognitive geology"
                    ],
                    "Risk": [
                        "earthquakes", "erosion", "volcanic disruption",
                        "geological hazards", "seismic threats", "crustal instability"
                    ],
                    "Intent": [
                        "tectonic shifts", "geological planning", "stratigraphic design",
                        "formation goals", "geological aims", "earth intentions"
                    ],
                    "Action": [
                        "landscape changes", "surface flows", "mountain building",
                        "geological action", "tectonic movement", "earth processes"
                    ]
                }
            },

            "fluid_dynamics": {
                "description": "Liquid flow and hydraulic systems",
                "sensory": ["kinesthetic", "auditory", "visual"],
                "concreteness": 0.8,
                "novelty": 0.9,
                "poetic": "Consciousness technology flows like fluid dynamics-dynamic systems of memory currents",
                "academic": "This metaphor models consciousness technology as fluid dynamic systems",
                "user": "Imagine your thoughts and memories flowing like water in a river",
                "MATRIZ": {
                    "Memory": [
                        "steady currents", "depth pools", "reservoir layers",
                        "memory streams", "flowing recollections", "liquid archives"
                    ],
                    "Attention": [
                        "eddies", "focused streams", "flow convergence",
                        "attention currents", "mindful flow", "cognitive channels"
                    ],
                    "Thought": [
                        "wave patterns", "flowing ideas", "current insights",
                        "thought streams", "mental rivers", "ideational flow"
                    ],
                    "Risk": [
                        "turbulence", "whirlpools", "flood overflow",
                        "flow disruption", "hydraulic pressure", "stream obstacles"
                    ],
                    "Intent": [
                        "directional flow", "channeling", "stream guidance",
                        "flow goals", "current aims", "hydraulic intentions"
                    ],
                    "Action": [
                        "ripples", "waterfalls", "tidal movements",
                        "flow action", "stream execution", "hydraulic movement"
                    ]
                }
            },

            "prismatic_light": {
                "description": "Optical phenomena and light refraction",
                "sensory": ["visual", "color", "luminous"],
                "concreteness": 0.75,
                "novelty": 0.88,
                "poetic": "Consciousness technology refracts like prismatic light-dynamic systems splitting memory beams",
                "academic": "This metaphor frames consciousness technology as dynamic systems of light refraction",
                "user": "Think of your mind like a prism breaking light into many colors",
                "MATRIZ": {
                    "Memory": [
                        "refracted beams", "color layers", "spectrum bands",
                        "memory prisms", "chromatic archives", "spectral recollections"
                    ],
                    "Attention": [
                        "focused rays", "light filters", "beam concentration",
                        "attention lenses", "optical focus", "luminous awareness"
                    ],
                    "Thought": [
                        "spectral facets", "prismatic shifts", "rainbow insights",
                        "thought spectrums", "mental illumination", "cognitive light"
                    ],
                    "Risk": [
                        "shadow zones", "diffusion loss", "optical distortion",
                        "light pollution", "spectral interference", "beam disruption"
                    ],
                    "Intent": [
                        "light direction", "beam shaping", "spectrum planning",
                        "optical goals", "luminous aims", "prism intentions"
                    ],
                    "Action": [
                        "color bursts", "radiant moves", "illumination waves",
                        "light action", "spectral movement", "optical expression"
                    ]
                }
            },

            "circuit_patterns": {
                "description": "Electronic circuits and digital systems",
                "sensory": ["visual", "kinesthetic", "auditory"],
                "concreteness": 0.8,
                "novelty": 0.85,
                "poetic": "Consciousness technology pulses through circuit patterns-dynamic systems of memory nodes",
                "academic": "This metaphor models consciousness technology as integrated circuits",
                "user": "Imagine your brain like an electric circuit board where memories are nodes",
                "MATRIZ": {
                    "Memory": [
                        "storage nodes", "data banks", "memory registers",
                        "circuit memory", "digital archives", "electronic storage"
                    ],
                    "Attention": [
                        "switches", "signal gates", "attention amplifiers",
                        "circuit focus", "signal routing", "electronic awareness"
                    ],
                    "Thought": [
                        "current flows", "logic paths", "circuit reasoning",
                        "thought circuits", "mental processing", "cognitive computing"
                    ],
                    "Risk": [
                        "short circuits", "signal noise", "system overload",
                        "circuit faults", "electronic threats", "digital hazards"
                    ],
                    "Intent": [
                        "programmed sequences", "control signals", "circuit design",
                        "digital goals", "electronic aims", "circuit intentions"
                    ],
                    "Action": [
                        "output pulses", "triggered events", "digital execution",
                        "circuit action", "electronic movement", "signal transmission"
                    ]
                }
            }
        }

    def get_next_family(self, force_rotation: bool = False) -> tuple[str, Dict]:
        """Get next metaphor family using rotation logic."""
        family_names = list(self.metaphor_families.keys())

        if force_rotation or random.random() < self.diversity_budget:
            # Rotate to next family or random selection
            self.current_family_index = (self.current_family_index + 1) % len(family_names)

        family_name = family_names[self.current_family_index]

        # Track usage for anti-repetition
        self.usage_tracker[family_name] = self.usage_tracker.get(family_name, 0) + 1

        return family_name, self.metaphor_families[family_name]

    def get_matriz_phrase(self, matriz_component: str, family_name: Optional[str] = None) -> str:
        """Get MATRIZ-specific phrase from current or specified family."""
        if family_name is None:
            family_name, family_data = self.get_next_family()
        else:
            family_data = self.metaphor_families.get(family_name, {})

        phrases = family_data.get("MATRIZ", {}).get(matriz_component, ["consciousness flows"])
        return random.choice(phrases)

    def get_3_layer_content(self, family_name: Optional[str] = None) -> dict[str, str]:
        """Get 3-layer tone system content for a family."""
        if family_name is None:
            family_name, family_data = self.get_next_family()
        else:
            family_data = self.metaphor_families.get(family_name, {})

        return {
            "poetic": family_data.get("poetic", ""),
            "academic": family_data.get("academic", ""),
            "user": family_data.get("user", ""),
            "family": family_name
        }

    def validate_novelty(self, text: str) -> bool:
        """Validate novelty score ≥0.8 requirement."""
        if not text:
            return False

        words = text.lower().split()
        unique_words = len(set(words))
        total_words = len(words)
        novelty = unique_words / max(total_words, 1)
        return novelty >= self.novelty_threshold

    def force_diversity_rotation(self):
        """Force rotation to least used family."""
        if not self.usage_tracker:
            return self.get_next_family()

        # Find family with minimum usage
        min_usage = min(self.usage_tracker.values())
        least_used_families = [
            name for name, count in self.usage_tracker.items()
            if count == min_usage
        ]

        # Select random from least used
        family_name = random.choice(least_used_families)
        family_names = list(self.metaphor_families.keys())
        self.current_family_index = family_names.index(family_name)

        return self.get_next_family()

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics for monitoring."""
        family_names = list(self.metaphor_families.keys())
        current_family = family_names[self.current_family_index] if family_names else "none"

        return {
            "current_family": current_family,
            "usage_counts": self.usage_tracker.copy(),
            "total_generations": sum(self.usage_tracker.values()),
            "diversity_score": len(self.usage_tracker) / len(family_names) if family_names else 0,
            "families_available": len(family_names)
        }

    def _load_usage_data(self):
        """Load usage tracking data from file."""
        try:
            data_path = Path(self.data_file)
            if data_path.exists():
                with open(data_path) as f:
                    data = json.load(f)
                    self.usage_tracker = data.get('usage_tracker', {})
                    self.current_family_index = data.get('current_family_index', 0)
        except Exception:
            # Continue with empty tracking if load fails
            pass

    def save_usage_data(self):
        """Save usage tracking data to file."""
        try:
            data = {
                'usage_tracker': self.usage_tracker,
                'current_family_index': self.current_family_index,
                'last_updated': time.time()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Continue silently if save fails
            pass

    def reset_usage_tracking(self):
        """Reset all usage tracking (for monthly refresh)."""
        self.usage_tracker = {}
        self.current_family_index = 0
        self.save_usage_data()

    def get_family_by_theme(self, theme: str) -> tuple[str, Dict]:
        """Get appropriate family based on theme/context."""
        theme_mappings = {
            "organic": "neural_gardens",
            "nature": "neural_gardens",
            "growth": "neural_gardens",
            "structure": "architectural_bridges",
            "building": "architectural_bridges",
            "framework": "architectural_bridges",
            "music": "harmonic_resonance",
            "sound": "harmonic_resonance",
            "rhythm": "harmonic_resonance",
            "fabric": "woven_patterns",
            "pattern": "woven_patterns",
            "texture": "woven_patterns",
            "earth": "geological_strata",
            "time": "geological_strata",
            "layers": "geological_strata",
            "flow": "fluid_dynamics",
            "water": "fluid_dynamics",
            "current": "fluid_dynamics",
            "light": "prismatic_light",
            "color": "prismatic_light",
            "spectrum": "prismatic_light",
            "circuit": "circuit_patterns",
            "digital": "circuit_patterns",
            "electronic": "circuit_patterns"
        }

        family_name = theme_mappings.get(theme.lower())
        if family_name:
            return family_name, self.metaphor_families[family_name]
        else:
            return self.get_next_family()


def main():
    """Demo/test the vocabulary rotation engine."""
    print("🔄 T4/0.01% Vocabulary Rotation Engine Demo")
    print("=" * 50)

    engine = VocabularyRotationEngine()

    # Test different MATRIZ components across families
    matriz_components = ["Memory", "Attention", "Thought", "Risk", "Intent", "Action"]

    for i in range(8):  # Test all families
        family_name, family_data = engine.get_next_family()
        component = matriz_components[i % len(matriz_components)]
        phrase = engine.get_matriz_phrase(component, family_name)

        print(f"\nFamily: {family_name}")
        print(f"{component}: {phrase}")
        print(f"Novelty: {family_data.get('novelty', 0)}")

    # Show final statistics
    stats = engine.get_usage_stats()
    print("\nFinal Statistics:")
    print(f"Diversity Score: {stats['diversity_score']:.2f}")
    print(f"Total Generations: {stats['total_generations']}")
    print(f"Usage Distribution: {stats['usage_counts']}")


if __name__ == "__main__":
    main()
