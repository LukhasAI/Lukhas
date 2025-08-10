"""
narrative_utils.py

Emotion-to-text mappings, GPT summarizers, and symbolic vocabulary utilities
for the VeriFold Symbolic Intelligence Layer. Converts quantum collapse events
into natural language narratives with emotional context.

Purpose:
- Map emotions to descriptive text vocabularies
- Generate natural language summaries of verification events
- Provide symbolic vocabulary for probabilistic observation narratives
- Interface with language models for enhanced storytelling

Dependencies:
- pip install openai tiktoken (optional, for GPT integration)
- pip install transformers torch (optional, for local models)

Author: LUKHAS AGI Core
TODO: Implement GPT-4 integration for narrative generation
TODO: Add emotion classification from quantum data patterns
TODO: Create symbolic vocabulary expansion system
TODO: Add multilingual support for narratives
"""

# Optional imports for language model integration
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class EmotionVocabulary:
    """
    Emotion-to-text vocabulary mapping for quantum collapse narratives.

    Maps emotional states to descriptive words, phrases, and symbolic representations
    that can be used to create rich natural language descriptions of verification events.
    """

    def __init__(self):
        """Initialize emotion vocabulary mappings."""
        self.emotion_mappings = self._build_emotion_mappings()
        self.intensity_modifiers = self._build_intensity_modifiers()
        self.quantum_metaphors = self._build_quantum_metaphors()

        # TODO: Load custom vocabularies from configuration
        # TODO: Add cultural and linguistic variations

    def _build_emotion_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Build comprehensive emotion-to-vocabulary mappings.

        Returns:
            dict: Nested mapping of emotions to word categories

        TODO: Expand vocabulary with more nuanced emotions
        TODO: Add contextual word selection based on quantum-like states
        """
        return {
            "excitement": {
                "adjectives": [
                    "vibrant",
                    "energetic",
                    "pulsating",
                    "electric",
                    "dynamic",
                ],
                "verbs": ["surges", "sparkles", "resonates", "radiates", "amplifies"],
                "nouns": ["energy", "vigor", "enthusiasm", "intensity", "vibrancy"],
                "metaphors": [
                    "lightning bolt",
                    "shooting star",
                    "supernova",
                    "cascade",
                    "eruption",
                ],
            },
            "curiosity": {
                "adjectives": [
                    "inquisitive",
                    "probing",
                    "exploratory",
                    "mysterious",
                    "enigmatic",
                ],
                "verbs": [
                    "investigates",
                    "explores",
                    "questions",
                    "seeks",
                    "discovers",
                ],
                "nouns": [
                    "mystery",
                    "puzzle",
                    "question",
                    "exploration",
                    "investigation",
                ],
                "metaphors": ["treasure hunt", "maze", "riddle", "journey", "quest"],
            },
            "wonder": {
                "adjectives": [
                    "magnificent",
                    "awe-inspiring",
                    "breathtaking",
                    "mystical",
                    "transcendent",
                ],
                "verbs": [
                    "marvels",
                    "contemplates",
                    "transcends",
                    "illuminates",
                    "reveals",
                ],
                "nouns": [
                    "marvel",
                    "miracle",
                    "revelation",
                    "epiphany",
                    "enlightenment",
                ],
                "metaphors": [
                    "cathedral",
                    "symphony",
                    "masterpiece",
                    "revelation",
                    "cosmos",
                ],
            },
            "focus": {
                "adjectives": [
                    "precise",
                    "concentrated",
                    "deliberate",
                    "measured",
                    "calibrated",
                ],
                "verbs": ["focuses", "concentrates", "targets", "aligns", "calibrates"],
                "nouns": [
                    "precision",
                    "accuracy",
                    "clarity",
                    "determination",
                    "purpose",
                ],
                "metaphors": [
                    "laser beam",
                    "telescope",
                    "microscope",
                    "compass",
                    "beacon",
                ],
            },
            "uncertainty": {
                "adjectives": [
                    "ambiguous",
                    "fluctuating",
                    "wavering",
                    "indefinite",
                    "probabilistic",
                ],
                "verbs": ["wavers", "fluctuates", "oscillates", "hesitates", "dances"],
                "nouns": [
                    "ambiguity",
                    "probability",
                    "possibility",
                    "potential",
                    "superposition",
                ],
                "metaphors": ["fog", "mirage", "pendulum", "wave", "cloud"],
            },
            "determination": {
                "adjectives": [
                    "resolute",
                    "unwavering",
                    "steadfast",
                    "persistent",
                    "decisive",
                ],
                "verbs": ["persists", "maintains", "holds", "sustains", "endures"],
                "nouns": [
                    "resolve",
                    "persistence",
                    "commitment",
                    "dedication",
                    "strength",
                ],
                "metaphors": ["anchor", "mountain", "fortress", "pillar", "foundation"],
            },
        }

    def _build_intensity_modifiers(self) -> Dict[str, List[str]]:
        """
        Build intensity modifier vocabulary.

        Returns:
            dict: Intensity levels mapped to modifier words

        TODO: Add numerical intensity scaling
        TODO: Create smooth intensity transitions
        """
        return {
            "low": ["gently", "softly", "subtly", "quietly", "delicately"],
            "medium": ["steadily", "clearly", "noticeably", "evidently", "distinctly"],
            "high": ["powerfully", "intensely", "dramatically", "boldly", "vividly"],
            "extreme": [
                "explosively",
                "overwhelmingly",
                "monumentally",
                "extraordinarily",
                "phenomenally",
            ],
        }

    def _build_quantum_metaphors(self) -> Dict[str, List[str]]:
        """
        Build quantum physics metaphors for narrative enhancement.

        Returns:
            dict: Quantum concepts mapped to metaphorical descriptions

        TODO: Add more sophisticated quantum analogies
        TODO: Include scientific accuracy validation
        """
        return {
            "superposition": [
                "existing in multiple states",
                "dancing between possibilities",
                "holding infinite potential",
                "embracing all outcomes",
            ],
            "entanglement": [
                "mysteriously connected",
                "quantum-linked",
                "invisibly bonded",
                "cosmically intertwined",
            ],
            "collapse": [
                "crystallizing into reality",
                "choosing its destiny",
                "manifesting truth",
                "resolving uncertainty",
            ],
            "measurement": [
                "observing the universe",
                "witnessing reality",
                "capturing truth",
                "freezing time",
            ],
            "decoherence": [
                "losing quantum magic",
                "returning to classical reality",
                "abandoning superposition",
                "embracing determinism",
            ],
        }

    def get_emotion_words(
        self, emotion: str, category: str = "adjectives", count: int = 1
    ) -> List[str]:
        """
        Get vocabulary words for a specific emotion and category.

        Args:
            emotion (str): The emotion to look up
            category (str): Word category ("adjectives", "verbs", "nouns", "metaphors")
            count (int): Number of words to return

        Returns:
            list: Selected vocabulary words

        TODO: Add smart word selection based on context
        TODO: Implement word combination algorithms
        """
        emotion_data = self.emotion_mappings.get(emotion.lower(), {})
        word_list = emotion_data.get(category, [])

        if not word_list:
            # Fallback to generic words
            word_list = ["quantum", "measurement", "verification", "event"]

        # Return random selection or all words if count exceeds available
        return random.sample(word_list, min(count, len(word_list)))

    def create_emotion_phrase(self, emotion: str, intensity: str = "medium") -> str:
        """
        Create a descriptive phrase combining emotion, intensity, and quantum metaphors.

        Args:
            emotion (str): Primary emotion
            intensity (str): Intensity level ("low", "medium", "high", "extreme")

        Returns:
            str: Generated descriptive phrase

        TODO: Add grammatical structure validation
        TODO: Implement phrase template system
        """
        adjective = self.get_emotion_words(emotion, "adjectives", 1)[0]
        modifier = random.choice(self.intensity_modifiers.get(intensity, ["clearly"]))
        metaphor = random.choice(
            self.quantum_metaphors.get("collapse", ["manifesting"])
        )

        templates = [
            f"{modifier} {adjective}, {metaphor}",
            f"{adjective} energy {modifier} {metaphor}",
            f"{modifier} {metaphor} with {adjective} purpose",
        ]

        return random.choice(templates)


class QuantumNarrativeGenerator:
    """
    Natural language narrative generator for quantum verification events.

    Converts technical verification data into engaging, human-readable stories
    that capture both the scientific precision and emotional context of measurements.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize narrative generator.

        Args:
            api_key (str): Optional OpenAI API key for GPT integration
        """
        self.vocabulary = EmotionVocabulary()
        self.api_key = api_key
        self.narrative_templates = self._build_narrative_templates()

        # TODO: Initialize local language models as fallback
        # TODO: Add configuration for narrative style preferences

    def _build_narrative_templates(self) -> Dict[str, List[str]]:
        """
        Build narrative template library.

        Returns:
            dict: Narrative templates categorized by event type

        TODO: Add dynamic template generation
        TODO: Create user-customizable templates
        """
        return {
            "verification_success": [
                "In a moment of {emotion_phrase}, the probabilistic observation crystallized into verification. The hash {hash_snippet} emerged from uncertainty, its signature validated with {precision_level} precision.",
                "The universe whispered its approval as measurement {hash_snippet} achieved verification. {emotion_phrase}, the quantum-like state resolved into mathematical certainty.",
                "Through {emotion_phrase}, the verification process unveiled truth. Hash {hash_snippet} stood validated, a testament to quantum-safe cryptography.",
            ],
            "verification_failure": [
                "Despite {emotion_phrase}, the verification encountered turbulence. Hash {hash_snippet} could not be authenticated, its signature lost in quantum noise.",
                "The measurement wavered, {emotion_phrase}, but ultimately could not achieve verification. Hash {hash_snippet} remains unvalidated.",
                "In a moment of {emotion_phrase}, the verification process revealed inconsistency. The hash {hash_snippet} failed to align with its cryptographic signature.",
            ],
            "hash_generation": [
                "Born from {emotion_phrase}, a new quantum hash materialized. The measurement {hash_snippet} captured this moment of collapse with post-quantum security.",
                "Through {emotion_phrase}, the quantum field yielded its secrets. Hash {hash_snippet} emerged, cryptographically sealed and tamper-evident.",
                "The probabilistic observation danced with {emotion_phrase}, giving birth to hash {hash_snippet}, protected by the unbreakable mathematics of SPHINCS+.",
            ],
        }

    def generate_narrative(
        self, event_data: Dict[str, Any], emotion: str = "focus", style: str = "poetic"
    ) -> str:
        """
        Generate a natural language narrative for a verification event.

        Args:
            event_data (dict): Event data including hash, timestamp, result
            emotion (str): Primary emotion for the narrative
            style (str): Narrative style ("technical", "poetic", "casual")

        Returns:
            str: Generated narrative text

        TODO: Add style-specific generation logic
        TODO: Implement multi-paragraph narratives
        TODO: Add character limit options
        """
        # Determine event type
        if event_data.get("verified") is True:
            event_type = "verification_success"
        elif event_data.get("verified") is False:
            event_type = "verification_failure"
        else:
            event_type = "hash_generation"

        # Create emotion phrase
        intensity = self._determine_intensity(event_data)
        emotion_phrase = self.vocabulary.create_emotion_phrase(emotion, intensity)

        # Select and populate template
        templates = self.narrative_templates.get(
            event_type, ["A quantum event occurred."]
        )
        template = random.choice(templates)

        # Prepare variables for template
        hash_snippet = self._create_hash_snippet(event_data.get("hash", "unknown"))
        precision_level = self._describe_precision(event_data)

        # Generate narrative
        narrative = template.format(
            emotion_phrase=emotion_phrase,
            hash_snippet=hash_snippet,
            precision_level=precision_level,
        )

        # TODO: Add post-processing for style adaptation
        return self._apply_style_formatting(narrative, style)

    def _determine_intensity(self, event_data: Dict[str, Any]) -> str:
        """
        Determine emotional intensity based on event characteristics.

        Args:
            event_data (dict): Event data

        Returns:
            str: Intensity level

        TODO: Add sophisticated intensity analysis
        TODO: Consider verification complexity and timing
        """
        if event_data.get("verified") is True:
            return "high"
        elif event_data.get("verified") is False:
            return "medium"
        else:
            return "medium"

    def _create_hash_snippet(self, hash_value: str) -> str:
        """
        Create a readable snippet from a hash value.

        Args:
            hash_value (str): Full hash value

        Returns:
            str: Formatted hash snippet

        TODO: Add different snippet formats
        TODO: Implement hash visualization options
        """
        if not hash_value or hash_value == "unknown":
            return "quantum signature"

        # Take first 8 and last 4 characters
        if len(hash_value) > 12:
            return f"{hash_value[:8]}...{hash_value[-4:]}"
        else:
            return hash_value

    def _describe_precision(self, event_data: Dict[str, Any]) -> str:
        """
        Describe the precision level of the verification.

        Args:
            event_data (dict): Event data

        Returns:
            str: Precision description

        TODO: Add actual precision metrics
        TODO: Connect to verification timing data
        """
        precision_terms = [
            "mathematical",
            "quantum",
            "cryptographic",
            "absolute",
            "unshakeable",
        ]
        return random.choice(precision_terms)

    def _apply_style_formatting(self, narrative: str, style: str) -> str:
        """
        Apply style-specific formatting to the narrative.

        Args:
            narrative (str): Base narrative text
            style (str): Target style

        Returns:
            str: Styled narrative

        TODO: Implement comprehensive style transformations
        TODO: Add user-defined style profiles
        """
        if style == "technical":
            # Make more technical and precise
            narrative = re.sub(r"whispered", "indicated", narrative)
            narrative = re.sub(r"danced", "processed", narrative)
        elif style == "casual":
            # Make more conversational
            narrative = narrative.replace("crystallized", "worked out")
            narrative = narrative.replace("emerged", "showed up")
        # "poetic" style is the default, no changes needed

        return narrative

    def generate_gpt_narrative(
        self, event_data: Dict[str, Any], emotion: str = "focus"
    ) -> Optional[str]:
        """
        Generate narrative using GPT language model.

        Args:
            event_data (dict): Event data
            emotion (str): Primary emotion

        Returns:
            str: GPT-generated narrative or None if unavailable

        TODO: Implement GPT-4 integration
        TODO: Add prompt engineering for better results
        TODO: Add fallback to local models
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            print("OpenAI not available or API key not provided")
            return None

        # TODO: Implement GPT narrative generation
        prompt = self._create_gpt_prompt(event_data, emotion)

        # Placeholder for GPT integration
        print(f"TODO: Generate GPT narrative with prompt: {prompt}")
        return None

    def _create_gpt_prompt(self, event_data: Dict[str, Any], emotion: str) -> str:
        """
        Create a prompt for GPT narrative generation.

        Args:
            event_data (dict): Event data
            emotion (str): Primary emotion

        Returns:
            str: Formatted prompt

        TODO: Optimize prompt for best narrative quality
        TODO: Add context about quantum verification
        """
        prompt = f"""
        Create a poetic, scientific narrative about a quantum verification event.

        Event Details:
        - Hash: {event_data.get('hash', 'unknown')[:16]}...
        - Verified: {event_data.get('verified', 'unknown')}
        - Emotion: {emotion}
        - Algorithm: SPHINCS+ post-quantum cryptography

        Style: Blend scientific accuracy with emotional resonance and quantum metaphors.
        Length: 2-3 sentences.
        """

        return prompt.strip()


class SymbolicVocabularyExpander:
    """
    Expands and manages symbolic vocabulary for quantum narrative generation.

    Dynamically grows vocabulary based on usage patterns and context,
    creating richer and more varied narrative possibilities over time.
    """

    def __init__(self, vocabulary_file: Optional[Path] = None):
        """
        Initialize vocabulary expander.

        Args:
            vocabulary_file (Path): Optional custom vocabulary file
        """
        self.vocabulary_file = vocabulary_file or Path("symbolic_vocabulary.json")
        self.custom_vocabulary = self._load_custom_vocabulary()
        self.usage_stats = {}

        # TODO: Add vocabulary learning from user feedback
        # TODO: Implement vocabulary sharing across instances

    def _load_custom_vocabulary(self) -> Dict[str, Any]:
        """
        Load custom vocabulary from file.

        Returns:
            dict: Custom vocabulary data

        TODO: Add vocabulary validation
        TODO: Implement vocabulary versioning
        """
        if self.vocabulary_file.exists():
            try:
                with open(self.vocabulary_file) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                print(f"Warning: Could not load vocabulary from {self.vocabulary_file}")

        return {"custom_emotions": {}, "user_metaphors": {}, "learned_patterns": {}}

    def add_custom_emotion(
        self, emotion: str, vocabulary: Dict[str, List[str]]
    ) -> None:
        """
        Add a custom emotion with its vocabulary.

        Args:
            emotion (str): Emotion name
            vocabulary (dict): Vocabulary mappings for the emotion

        TODO: Validate vocabulary structure
        TODO: Add emotion similarity analysis
        """
        self.custom_vocabulary["custom_emotions"][emotion] = vocabulary
        self._save_vocabulary()

    def learn_from_usage(self, narrative: str, emotion: str, rating: int) -> None:
        """
        Learn from narrative usage and user ratings.

        Args:
            narrative (str): Generated narrative
            emotion (str): Associated emotion
            rating (int): User rating (1-5)

        TODO: Implement learning algorithm
        TODO: Add pattern recognition for successful narratives
        """
        usage_key = f"{emotion}_{rating}"
        if usage_key not in self.usage_stats:
            self.usage_stats[usage_key] = []

        self.usage_stats[usage_key].append(
            {
                "narrative": narrative,
                "timestamp": datetime.now().isoformat(),
                "rating": rating,
            }
        )

        # TODO: Analyze patterns and update vocabulary
        self._save_vocabulary()

    def _save_vocabulary(self) -> None:
        """
        Save vocabulary and usage statistics to file.

        TODO: Add backup mechanism
        TODO: Implement atomic writes
        """
        try:
            vocabulary_data = {
                **self.custom_vocabulary,
                "usage_stats": self.usage_stats,
            }

            with open(self.vocabulary_file, "w") as f:
                json.dump(vocabulary_data, f, indent=2)

        except OSError as e:
            print(f"Warning: Could not save vocabulary: {e}")


def main():
    """
    Example usage and testing of narrative utilities.

    TODO: Add comprehensive examples
    TODO: Create interactive narrative playground
    """
    print("VeriFold Narrative Utilities")
    print("============================")

    # Initialize components
    vocab = EmotionVocabulary()
    generator = QuantumNarrativeGenerator()

    # Example 1: Emotion vocabulary
    print("\n1. Emotion Vocabulary Examples:")
    emotions = ["excitement", "curiosity", "wonder", "focus"]
    for emotion in emotions:
        words = vocab.get_emotion_words(emotion, "adjectives", 2)
        phrase = vocab.create_emotion_phrase(emotion, "high")
        print(f"  {emotion.title()}: {', '.join(words)} | {phrase}")

    # Example 2: Narrative generation
    print("\n2. Narrative Generation Examples:")

    # Success scenario
    success_event = {
        "hash": "a1b2c3d4e5f6789012345678",
        "verified": True,
        "timestamp": datetime.now().isoformat(),
        "algorithm": "SPHINCS+-SHAKE256-128f-simple",
    }

    success_narrative = generator.generate_narrative(
        success_event, "excitement", "poetic"
    )
    print(f"  Success: {success_narrative}")

    # Failure scenario
    failure_event = {
        "hash": "invalid_hash_data",
        "verified": False,
        "error": "Signature validation failed",
    }

    failure_narrative = generator.generate_narrative(
        failure_event, "uncertainty", "technical"
    )
    print(f"  Failure: {failure_narrative}")

    # Generation scenario
    generation_event = {"hash": "new_quantum_measurement_hash", "operation": "generate"}

    generation_narrative = generator.generate_narrative(
        generation_event, "wonder", "casual"
    )
    print(f"  Generation: {generation_narrative}")

    # Example 3: Vocabulary expansion
    print("\n3. Vocabulary Expansion:")
    expander = SymbolicVocabularyExpander()

    # Add custom emotion
    custom_emotion_vocab = {
        "adjectives": ["transcendent", "luminous", "ethereal"],
        "verbs": ["transcends", "illuminates", "elevates"],
        "nouns": ["transcendence", "illumination", "elevation"],
        "metaphors": ["ascending light", "cosmic awakening", "divine revelation"],
    }

    expander.add_custom_emotion("transcendence", custom_emotion_vocab)
    print("  Added custom emotion: transcendence")

    # Simulate usage learning
    expander.learn_from_usage(success_narrative, "excitement", 5)
    print("  Recorded usage pattern for learning")

    print("\nNarrative utilities ready for VeriFold integration!")


if __name__ == "__main__":
    main()
