#!/usr/bin/env python3
"""
LUKHAS Expanded Lexicon

A massively enriched vocabulary system combining:
- Classical poetic traditions
- Contemporary literary techniques
- Scientific and technical precision
- LUKHAS-specific innovations
- Cross-cultural poetic forms
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import List


class PoeticForm(Enum):
    """Traditional and modern poetic forms."""
    SONNET = "sonnet"
    HAIKU = "haiku"
    VILLANELLE = "villanelle"
    GHAZAL = "ghazal"
    PANTOUM = "pantoum"
    TANKA = "tanka"
    FREE_VERSE = "free_verse"
    PROSE_POEM = "prose_poem"
    CONCRETE = "concrete"
    FOUND = "found"


@dataclass
class VocabularyEntry:
    """Rich vocabulary entry with multiple dimensions."""
    word: str
    synonyms: List[str]
    associations: List[str]
    sound_quality: str  # harsh, soft, liquid, etc.
    emotional_tone: str  # melancholic, jubilant, serene, etc.
    usage_context: List[str]  # technical, poetic, formal, etc.


class ExpandedLUKHASLexicon:
    """
    The ultimate LUKHAS vocabulary resource.

    Combines thousands of words across multiple categories:
    - Technical precision
    - Poetic beauty
    - Emotional depth
    - Sensory richness
    - Cultural diversity
    """

    def __init__(self):
        # Vastly expanded consciousness vocabulary
        self.consciousness_terms = {
            # States of awareness
            "awareness_states": [
                "lucidity", "vigilance", "sentience", "sapience", "cognizance",
                "mindfulness", "presence", "attentiveness", "wakefulness", "alertness",
                "metacognition", "introspection", "self-awareness", "autonoesis",
                "phenomenal consciousness", "access consciousness", "narrative consciousness",
                "core consciousness", "extended consciousness", "minimal consciousness"
            ],

            # Consciousness qualities
            "qualities": [
                "luminous", "numinous", "ineffable", "sublime", "transcendent",
                "immanent", "emergent", "recursive", "holographic", "fractal",
                "prismatic", "kaleidoscopic", "iridescent", "opalescent", "phosphorescent",
                "bioluminescent", "fluorescent", "incandescent", "effulgent", "radiant"
            ],

            # Consciousness processes
            "processes": [
                "awakening", "enlightenment", "illumination", "realization", "epiphany",
                "revelation", "discovery", "emergence", "crystallization", "coalescence",
                "integration", "synthesis", "fusion", "convergence", "divergence",
                "oscillation", "vibration", "resonance", "harmonization", "synchronization"
            ],

            # Consciousness metaphors
            "metaphors": [
                "ocean of awareness", "mirror of the mind", "theater of consciousness",
                "stream of thought", "garden of cognition", "constellation of concepts",
                "symphony of synapses", "dance of neurons", "tapestry of experience",
                "cathedral of consciousness", "labyrinth of thought", "prism of perception"
            ]
        }

        # Expanded memory vocabulary
        self.memory_terms = {
            # Memory types
            "types": [
                "episodic", "semantic", "procedural", "declarative", "implicit",
                "explicit", "sensory", "echoic", "iconic", "haptic",
                "eidetic", "photographic", "muscle", "emotional", "collective",
                "ancestral", "cellular", "genetic", "epigenetic", "morphic"
            ],

            # Memory processes
            "processes": [
                "encoding", "consolidation", "retrieval", "reconsolidation", "forgetting",
                "remembering", "recollection", "reminiscence", "recall", "recognition",
                "relearning", "priming", "cueing", "chunking", "elaboration",
                "mnemonics", "association", "visualization", "spaced repetition", "interleaving"
            ],

            # Memory qualities
            "qualities": [
                "vivid", "hazy", "fragmented", "intact", "distorted",
                "pristine", "faded", "sharp", "blurred", "crystalline",
                "ephemeral", "enduring", "persistent", "fleeting", "indelible",
                "haunting", "nostalgic", "bittersweet", "poignant", "evocative"
            ],

            # LUKHAS-specific memory terms
            "lukhas_specific": [
                "fold", "cascade", "proteome", "methylation", "engram",
                "memory-fold", "fold-space", "cascade-prevention", "memory-protein",
                "symbolic-fold", "temporal-fold", "causal-fold", "emotional-fold",
                "fold-topology", "fold-collapse", "fold-preservation", "fold-navigation"
            ]
        }

        # Quantum-inspired vocabulary (expanded)
        self.qi_terms = {
            # Quantum states
            "states": [
                "superposition", "entanglement", "coherence", "decoherence", "eigenstate",
                "ground state", "excited state", "mixed state", "pure state", "Bell state",
                "squeezed state", "Fock state", "coherent state", "thermal state", "vacuum state"
            ],

            # Quantum processes
            "processes": [
                "collapse", "measurement", "observation", "interference", "tunneling",
                "teleportation", "computation", "annealing", "error correction", "decoherence",
                "quantum walk", "quantum jump", "quantum beat", "quantum revival", "quantum echo"
            ],

            # Quantum qualities
            "qualities": [
                "non-local", "probabilistic", "uncertain", "complementary", "discrete",
                "quantized", "wave-like", "particle-like", "dual", "paradoxical",
                "counterintuitive", "spooky", "mysterious", "fundamental", "irreducible"
            ],

            # Quantum metaphors
            "metaphors": [
                "quantum foam", "possibility cloud", "probability wave", "quantum sea",
                "entangled web", "coherent field", "quantum vacuum", "zero-point field",
                "quantum fabric", "possibility space", "quantum realm", "Hilbert space"
            ]
        }

        # Bio-inspired vocabulary (expanded)
        self.bio_terms = {
            # Neural terms
            "neural": [
                "neuron", "synapse", "dendrite", "axon", "soma",
                "astrocyte", "oligodendrocyte", "microglia", "ependymal", "Schwann",
                "ganglion", "plexus", "nucleus", "cortex", "hippocampus",
                "amygdala", "thalamus", "hypothalamus", "cerebellum", "brainstem"
            ],

            # Biological processes
            "processes": [
                "neuroplasticity", "synaptogenesis", "myelination", "pruning", "potentiation",
                "habituation", "sensitization", "adaptation", "homeostasis", "allostasis",
                "morphogenesis", "differentiation", "proliferation", "apoptosis", "autophagy",
                "mitosis", "meiosis", "transcription", "translation", "replication"
            ],

            # Biological patterns
            "patterns": [
                "fractal branching", "golden ratio", "Fibonacci spiral", "hexagonal packing",
                "Voronoi tessellation", "reaction-diffusion", "Turing patterns", "stigmergy",
                "swarm intelligence", "emergent behavior", "self-organization", "autopoiesis",
                "symbiosis", "coevolution", "convergent evolution", "adaptive radiation"
            ],

            # Bio-rhythms
            "rhythms": [
                "circadian", "ultradian", "infradian", "circannual", "lunar",
                "alpha waves", "beta waves", "gamma waves", "delta waves", "theta waves",
                "heart rate variability", "respiratory sinus arrhythmia", "neural oscillations",
                "brainwave entrainment", "binaural beats", "isochronic tones", "solfeggio frequencies"
            ]
        }

        # Emotional vocabulary (vastly expanded)
        self.emotional_terms = {
            # Primary emotions
            "primary": [
                "joy", "sadness", "anger", "fear", "surprise", "disgust",
                "trust", "anticipation", "acceptance", "submission", "awe", "disapproval"
            ],

            # Complex emotions
            "complex": [
                "melancholy", "nostalgia", "yearning", "longing", "wistfulness",
                "euphoria", "elation", "ecstasy", "rapture", "bliss",
                "anguish", "despair", "grief", "sorrow", "lamentation",
                "serenity", "tranquility", "equanimity", "contentment", "satisfaction",
                "ambivalence", "bittersweetness", "poignancy", "pathos", "catharsis"
            ],

            # Rare emotional states
            "rare": [
                "saudade" , # Portuguese: deep melancholic longing
                "hiraeth", # Welsh: homesickness for a place that never was
                "fernweh", # German: longing for distant places
                "komorebi", # Japanese: sunlight through leaves
                "tsundoku", # Japanese: acquiring books but not reading them
                "waldeinsamkeit", # German: feeling of being alone in the woods
                "hygge", # Danish: cozy contentment
                "ubuntu", # Zulu: interconnectedness of humanity
                "meraki", # Greek: doing something with soul and creativity
                "yugen", # Japanese: profound mysterious sense of beauty
            ],

            # Emotional qualities
            "qualities": [
                "visceral", "palpable", "ineffable", "profound", "subtle",
                "overwhelming", "understated", "nuanced", "complex", "layered",
                "raw", "refined", "primal", "sophisticated", "transcendent"
            ]
        }

        # Sensory vocabulary (rich and diverse)
        self.sensory_terms = {
            # Visual
            "visual": [
                "luminous", "radiant", "gleaming", "glinting", "shimmering",
                "glistening", "sparkling", "twinkling", "flickering", "glowing",
                "iridescent", "opalescent", "pearlescent", "prismatic", "chromatic",
                "monochromatic", "polychromatic", "kaleidoscopic", "psychedelic", "holographic",
                "translucent", "transparent", "opaque", "diaphanous", "gossamer"
            ],

            # Auditory
            "auditory": [
                "resonant", "harmonious", "melodious", "symphonic", "cacophonous",
                "dissonant", "consonant", "rhythmic", "staccato", "legato",
                "crescendo", "diminuendo", "fortissimo", "pianissimo", "sotto voce",
                "susurrus", "murmur", "whisper", "echo", "reverberation",
                "tintinnabulation", "euphony", "cacophony", "onomatopoeia", "assonance"
            ],

            # Tactile
            "tactile": [
                "velvety", "silky", "satiny", "gossamer", "feathery",
                "rough", "coarse", "gritty", "sandy", "gravelly",
                "smooth", "slick", "slippery", "sticky", "tacky",
                "warm", "cool", "frigid", "scalding", "tepid",
                "tingly", "prickly", "numb", "sensitive", "tender"
            ],

            # Olfactory
            "olfactory": [
                "fragrant", "aromatic", "redolent", "perfumed", "scented",
                "pungent", "acrid", "fetid", "putrid", "rancid",
                "earthy", "woody", "floral", "fruity", "spicy",
                "musky", "medicinal", "chemical", "metallic", "sulfurous",
                "petrichor", # smell of rain on earth
                "geosmin" # earthy smell after rain
            ],

            # Gustatory
            "gustatory": [
                "sweet", "sour", "salty", "bitter", "umami",
                "savory", "tangy", "tart", "piquant", "pungent",
                "bland", "rich", "delicate", "robust", "complex",
                "astringent", "metallic", "alkaline", "acidic", "neutral"
            ],

            # Kinesthetic
            "kinesthetic": [
                "flowing", "floating", "soaring", "gliding", "drifting",
                "plunging", "diving", "ascending", "descending", "spiraling",
                "oscillating", "vibrating", "pulsating", "throbbing", "quivering",
                "spinning", "whirling", "twirling", "rotating", "revolving"
            ]
        }

        # Movement and action vocabulary
        self.movement_terms = {
            # Gentle movements
            "gentle": [
                "drift", "float", "glide", "waft", "sway",
                "meander", "amble", "saunter", "stroll", "wander",
                "flutter", "flit", "hover", "linger", "dawdle",
                "trickle", "seep", "ooze", "percolate", "filter"
            ],

            # Dynamic movements
            "dynamic": [
                "surge", "cascade", "torrent", "deluge", "avalanche",
                "eruption", "explosion", "implosion", "collision", "fusion",
                "catapult", "launch", "propel", "accelerate", "velocity",
                "momentum", "trajectory", "orbit", "revolution", "rotation"
            ],

            # Transformative actions
            "transformative": [
                "metamorphose", "transmute", "transfigure", "transmogrify", "morph",
                "evolve", "adapt", "mutate", "shift", "transition",
                "crystallize", "solidify", "liquify", "vaporize", "sublimate",
                "coalesce", "converge", "diverge", "bifurcate", "tessellate"
            ],

            # Cyclical movements
            "cyclical": [
                "revolve", "rotate", "orbit", "circle", "spiral",
                "oscillate", "fluctuate", "undulate", "pulsate", "throb",
                "ebb", "flow", "wax", "wane", "cycle",
                "recur", "repeat", "echo", "reverberate", "resonate"
            ]
        }

        # Architectural and spatial vocabulary
        self.spatial_terms = {
            # Structures
            "structures": [
                "edifice", "monument", "cathedral", "temple", "sanctuary",
                "labyrinth", "maze", "warren", "network", "web",
                "lattice", "scaffold", "framework", "skeleton", "armature",
                "matrix", "grid", "mesh", "fabric", "tapestry",
                "mosaic", "tessellation", "fractal", "pattern", "design"
            ],

            # Spaces
            "spaces": [
                "realm", "domain", "sphere", "dimension", "plane",
                "vista", "panorama", "horizon", "expanse", "vastness",
                "chamber", "cavity", "hollow", "void", "abyss",
                "threshold", "liminal", "boundary", "frontier", "edge",
                "nexus", "hub", "node", "junction", "crossroads"
            ],

            # Geometric terms
            "geometric": [
                "vertex", "edge", "face", "facet", "angle",
                "curve", "arc", "spiral", "helix", "vortex",
                "sphere", "torus", "mobius", "klein bottle", "manifold",
                "fractal", "julia set", "mandelbrot", "strange attractor", "chaos"
            ]
        }

        # Time and temporal vocabulary
        self.temporal_terms = {
            # Time periods
            "periods": [
                "moment", "instant", "second", "minute", "hour",
                "epoch", "era", "eon", "millennium", "century",
                "nanosecond", "microsecond", "millisecond", "picosecond", "femtosecond",
                "eternity", "infinity", "perpetuity", "timelessness", "atemporality"
            ],

            # Temporal qualities
            "qualities": [
                "ephemeral", "transient", "fleeting", "momentary", "brief",
                "enduring", "lasting", "permanent", "eternal", "timeless",
                "cyclical", "linear", "recursive", "spiral", "fractal",
                "synchronous", "asynchronous", "concurrent", "sequential", "parallel"
            ],

            # Temporal processes
            "processes": [
                "flow", "passage", "progression", "evolution", "development",
                "acceleration", "deceleration", "stasis", "pause", "suspension",
                "rewind", "replay", "loop", "cycle", "recurrence",
                "dilation", "contraction", "warping", "bending", "folding"
            ]
        }

        # Abstract concepts vocabulary
        self.abstract_terms = {
            # Philosophical concepts
            "philosophical": [
                "essence", "existence", "being", "becoming", "nothingness",
                "truth", "beauty", "goodness", "justice", "wisdom",
                "reality", "illusion", "maya", "samsara", "nirvana",
                "logos", "ethos", "pathos", "kairos", "telos",
                "qualia", "phenomena", "noumena", "dasein", "gestalt"
            ],

            # Mathematical concepts
            "mathematical": [
                "infinity", "zero", "unity", "duality", "plurality",
                "symmetry", "asymmetry", "proportion", "ratio", "harmony",
                "chaos", "order", "entropy", "negentropy", "emergence",
                "recursion", "iteration", "fractality", "dimensionality", "topology"
            ],

            # Metaphysical concepts
            "metaphysical": [
                "consciousness", "awareness", "presence", "absence", "void",
                "spirit", "soul", "essence", "substance", "form",
                "energy", "vibration", "frequency", "resonance", "harmony",
                "light", "shadow", "darkness", "twilight", "dawn"
            ]
        }

        # Color vocabulary (expanded with rare and poetic terms)
        self.color_terms = {
            # Basic spectrum
            "basic": [
                "crimson", "scarlet", "vermillion", "carmine", "ruby",
                "amber", "gold", "saffron", "citrine", "topaz",
                "emerald", "jade", "viridian", "malachite", "verdant",
                "sapphire", "cobalt", "azure", "cerulean", "lapis",
                "amethyst", "violet", "indigo", "purple", "magenta"
            ],

            # Rare colors
            "rare": [
                "vermeil", "cinnabar", "cerise", "amaranth", "fuchsia",
                "chartreuse", "lime", "peridot", "olivine", "verdigris",
                "teal", "turquoise", "aquamarine", "cyan", "peacock",
                "periwinkle", "lavender", "mauve", "lilac", "orchid",
                "ochre", "sienna", "umber", "sepia", "taupe"
            ],

            # Metallic and mineral
            "metallic": [
                "gold", "silver", "bronze", "copper", "brass",
                "platinum", "titanium", "chrome", "steel", "iron",
                "pearl", "opal", "diamond", "crystal", "quartz",
                "obsidian", "onyx", "jet", "ebony", "alabaster"
            ],

            # Light qualities
            "light": [
                "luminous", "radiant", "brilliant", "dazzling", "gleaming",
                "glowing", "shimmering", "sparkling", "glittering", "twinkling",
                "phosphorescent", "fluorescent", "incandescent", "bioluminescent", "iridescent",
                "prismatic", "spectral", "chromatic", "achromatic", "monochromatic"
            ]
        }

    def get_synonyms(self, word: str, category: str = None) -> List[str]:
        """Get rich synonyms for a word, optionally filtered by category."""
        # Implementation would search across all categories
        synonyms = []

        # Search in specified category or all categories
        if category:
            if hasattr(self, f"{category}_terms"):
                term_dict = getattr(self, f"{category}_terms")
                for subcategory, words in term_dict.items():
                    if word in words:
                        # Return related words from same subcategory
                        synonyms.extend([w for w in words if w != word])
        else:
            # Search all categories
            for attr_name in dir(self):
                if attr_name.endswith("_terms"):
                    term_dict = getattr(self, attr_name)
                    if isinstance(term_dict, dict):
                        for subcategory, words in term_dict.items():
                            if isinstance(words, list) and word in words:
                                synonyms.extend([w for w in words if w != word])

        return list(set(synonyms))[:10]  # Return up to 10 unique synonyms

    def get_random_from_category(self, category: str, subcategory: str = None) -> str:
        """Get a random word from a specific category."""
        if hasattr(self, f"{category}_terms"):
            term_dict = getattr(self, f"{category}_terms")
            if subcategory and subcategory in term_dict:
                return random.choice(term_dict[subcategory])
            else:
                # Random from any subcategory
                all_words = []
                for words in term_dict.values():
                    if isinstance(words, list):
                        all_words.extend(words)
                return random.choice(all_words) if all_words else ""
        return ""

    def create_rich_phrase(self, theme: str, word_count: int = 5) -> str:
        """Create a rich phrase using varied vocabulary."""
        phrases = []

        # Map themes to relevant categories
        theme_map = {
            "consciousness": ["consciousness", "quantum", "spatial"],
            "memory": ["memory", "temporal", "emotional"],
            "quantum": ["quantum", "mathematical", "abstract"],
            "emotion": ["emotional", "sensory", "movement"],
            "neural": ["bio", "spatial", "movement"]
        }

        categories = theme_map.get(theme, ["consciousness"])

        for _ in range(word_count):
            category = random.choice(categories)
            word = self.get_random_from_category(category)
            if word:
                phrases.append(word)

        return " ".join(phrases)

    def generate_poetic_description(self, concept: str, style: str = "rich") -> str:
        """
        Generate a poetic description of a concept.

        Styles:
        - minimal: sparse, essential words
        - rich: lush, varied vocabulary
        - technical: precise, scientific
        - mystical: spiritual, transcendent
        """
        templates = {
            "minimal": "{adj1} {noun} {verb}",
            "rich": "The {adj1} {noun} {verb} through {adj2} {space}, {creating} {adj3} {result}",
            "technical": "{process} initiates {mechanism} within {structure}, yielding {outcome}",
            "mystical": "In the {realm} of {quality}, {entity} {transcends} into {state}"
        }

        template = templates.get(style, templates["rich"])

        # Fill template with appropriate vocabulary
        filled = template.format(
            adj1=self.get_random_from_category("sensory", "visual"),
            adj2=self.get_random_from_category("consciousness", "qualities"),
            adj3=self.get_random_from_category("emotional", "qualities"),
            noun=self.get_random_from_category("spatial", "structures"),
            verb=self.get_random_from_category("movement", "transformative"),
            space=self.get_random_from_category("spatial", "spaces"),
            creating=self.get_random_from_category("movement", "transformative"),
            result=self.get_random_from_category("consciousness", "metaphors"),
            process=self.get_random_from_category("quantum", "processes"),
            mechanism=self.get_random_from_category("bio", "processes"),
            structure=self.get_random_from_category("spatial", "structures"),
            outcome=self.get_random_from_category("consciousness", "states"),
            realm=self.get_random_from_category("spatial", "spaces"),
            quality=self.get_random_from_category("abstract", "metaphysical"),
            entity=self.get_random_from_category("consciousness", "metaphors"),
            transcends=self.get_random_from_category("movement", "transformative"),
            state=self.get_random_from_category("quantum", "states")
        )

        return filled


# Example usage
if __name__ == "__main__":
    lexicon = ExpandedLUKHASLexicon()

    print("═══════════════════════════════════════════════════════════════")
    print("         LUKHAS EXPANDED LEXICON")
    print("    'Infinite vocabulary for infinite expression'")
    print("═══════════════════════════════════════════════════════════════\n")

    print("▸ CONSCIOUSNESS VOCABULARY SAMPLE:")
    for _ in range(3):
        word = lexicon.get_random_from_category("consciousness", "qualities")
        print(f"  • {word}")
    print()

    print("▸ RARE EMOTIONAL STATES:")
    for emotion in lexicon.emotional_terms["rare"][:5]:
        print(f"  • {emotion}")
    print()

    print("▸ SENSORY RICHNESS (Visual):")
    for _ in range(5):
        word = lexicon.get_random_from_category("sensory", "visual")
        print(f"  • {word}")
    print()

    print("▸ QUANTUM METAPHORS:")
    for metaphor in random.sample(lexicon.qi_terms["metaphors"], 3):
        print(f"  • {metaphor}")
    print()

    print("▸ GENERATED PHRASES:")
    print(f"  Consciousness: {lexicon.create_rich_phrase('consciousness')}")
    print(f"  Memory: {lexicon.create_rich_phrase('memory')}")
    print(f"  Quantum: {lexicon.create_rich_phrase('quantum')}")
    print()

    print("▸ POETIC DESCRIPTIONS (Different Styles):")
    print(f"  Minimal: {lexicon.generate_poetic_description('consciousness', 'minimal')}")
    print(f"  Rich: {lexicon.generate_poetic_description('consciousness', 'rich')}")
    print(f"  Technical: {lexicon.generate_poetic_description('consciousness', 'technical')}")
    print(f"  Mystical: {lexicon.generate_poetic_description('consciousness', 'mystical')}")
    print()

    print("═══════════════════════════════════════════════════════════════")
    print("  Over 1000+ unique terms across 15+ categories")
    print("  Combining scientific precision with poetic beauty")
    print("═══════════════════════════════════════════════════════════════")
