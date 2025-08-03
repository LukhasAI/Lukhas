"""
LUKHAS Voice Memory Helix System
===============================

Golden transfer from LUKHAS-Portfolio Voice_Pack.
Advanced voice learning system with helix-pattern memory recursion.

╔═══════════════════════════════════════════════════════════════════════════╗
║ LUKHAS SYSTEM : voice_memory_helix.py                                     ║
║ DESCRIPTION   : Manages learning of accents, pronunciations, and curious  ║
║                 exploration of new words based on user interactions.      ║
║                 Implements a helix pattern for recursive self-improvement.║
║ TYPE          : Voice Learning System          VERSION: v2.0.0-LUKHAS     ║
║ AUTHOR        : LUKHAS SYSTEMS                 UPDATED: 2025-05-30        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- CORE.memory.helix_memory
- CORE.learn_to_learn
"""mory Helix System
"""
===============================

Golden transfer from LUKHAS Voice_Pack.
Advanced voice learning system with helix-pattern memory recursion.

# LUKHAS SYSTEM : voice_memory_helix.py
# DESCRIPTION   : Manages learning of accents, pronunciations, and curious
#                 exploration of new words based on user interactions.
#                 Implements a helix pattern for recursive self-improvement.
# TYPE          : Voice Learning System          VERSION: v2.0.0-LUKHAS
║ AUTHOR        : LUKHAS SYSTEMS                 UPDATED: 2025-05-30        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- CORE.memory.helix_memory
- CORE.learn_to_learn
"""

import logging
import asyncio
import json
import os
import re
import time
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import random

# Configure logging
logger = logging.getLogger(__name__)

class VoiceMemoryHelix:
    """
    Implements a memory helix for voice learning that enables LUKHAS AGI to:

    1. Learn and adapt to local accents
    2. Develop curiosity about new or unfamiliar words
    3. Practice pronunciation through guided feedback
    4. Remember user pronunciation preferences
    5. Self-improve through recursive learning loops
    6. Build cultural location memories and associations
    7. Ethically adapt to cultural contexts and expressions

    The helix pattern allows for continuous improvement by spiraling through:
    - Detection (identify new patterns)
    - Collection (gather examples)
    - Adaptation (modify speech patterns)
    - Verification (test improvements)
    - Refinement (optimize based on feedback)
    """

    def __init__(self, core_interface=None, config: Dict[str, Any] = None):
        """
        Initialize the voice memory helix.

        Args:
            core_interface: Interface to the LUKHAS core system
            config: Configuration dictionary
        """
        self.core = core_interface
        self.config = config or {}

        # Memory structures
        self.accent_memory = {}  # Map of accent patterns
        self.pronunciation_memory = {}  # Map of word pronunciations
        self.curiosity_list = set()  # Words to explore
        self.practice_history = []  # Record of practice sessions
        self.location_memories = {}  # Cultural location memories

        # Learning parameters
        self.curiosity_threshold = self.config.get("curiosity_threshold", 0.65)
        self.learning_rate = self.config.get("learning_rate", 0.2)
        self.practice_interval = self.config.get("practice_interval", 5)  # sessions
        self.retention_factor = self.config.get("retention_factor", 0.95)  # memory decay rate
        self.cultural_sensitivity = self.config.get("cultural_sensitivity", 0.8)  # How sensitive to cultural context

        # Statistics
        self.stats = {
            "words_learned": 0,
            "accent_patterns": 0,
            "practice_sessions": 0,
            "successful_adaptations": 0,
            "cultural_locations": 0,
            "cultural_interactions": 0
        }

        # Load saved memory if available
        self._load_memory()

        logger.info("Voice Memory Helix initialized")

    def _load_memory(self):
        """Load saved memory from disk"""
        memory_path = self.config.get("memory_path", "memory/voice_memory.json")
        try:
            if os.path.exists(memory_path):
                with open(memory_path, "r") as file:
                    memory_data = json.load(file)

                    self.accent_memory = memory_data.get("accent_memory", {})
                    self.pronunciation_memory = memory_data.get("pronunciation_memory", {})
                    self.curiosity_list = set(memory_data.get("curiosity_list", []))
                    self.location_memories = memory_data.get("location_memories", {})
                    self.stats = memory_data.get("stats", self.stats)

                    cultural_locations = len(self.location_memories)
                    logger.info(f"Loaded voice memory with {len(self.pronunciation_memory)} words, {len(self.accent_memory)} accent patterns, and {cultural_locations} cultural locations")
            else:
                logger.info("No saved voice memory found, starting fresh")
        except Exception as e:
            logger.warning(f"Failed to load voice memory: {e}")

    def save_memory(self):
        """Save memory to disk"""
        memory_path = self.config.get("memory_path", "memory/voice_memory.json")
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(memory_path), exist_ok=True)

            memory_data = {
                "accent_memory": self.accent_memory,
                "pronunciation_memory": self.pronunciation_memory,
                "curiosity_list": list(self.curiosity_list),
                "location_memories": self.location_memories,
                "stats": self.stats,
                "last_updated": datetime.now().isoformat()
            }

            with open(memory_path, "w") as file:
                json.dump(memory_data, file, indent=2)

            logger.info("Saved voice memory to disk")
        except Exception as e:
            logger.warning(f"Failed to save voice memory: {e}")

    async def detect_new_words(self, text: str) -> List[str]:
        """
        Detect new or unusual words in text that might need pronunciation learning.

        Args:
            text: The input text to analyze

        Returns:
            List of detected new words
        """
        if not text:
            return []

        # Extract words (basic implementation)
        words = re.findall(r'\b[a-zA-Z\']+\b', text)

        # Filter for unusual words not in our pronunciation memory
        new_words = []
        for word in words:
            word = word.lower()
            if len(word) > 4:  # Focus on longer words that might be more complex
                if word not in self.pronunciation_memory:
                    # Check if it's an unusual word (simplified check)
                    # In a real implementation, this would use more sophisticated methods
                    if await self._is_unusual_word(word):
                        new_words.append(word)
                        self.curiosity_list.add(word)

        if new_words:
            logger.debug(f"Detected {len(new_words)} potentially new words: {new_words}")

        return new_words

    async def _is_unusual_word(self, word: str) -> bool:
        """
        Check if a word is unusual and might need pronunciation learning.

        Args:
            word: The word to check

        Returns:
            True if the word is unusual, False otherwise
        """
        # In a real implementation, this would use a more sophisticated approach
        # For now, simulate with a simple heuristic

        # Try to use the core if available
        if self.core:
            try:
                result = await self.core.query_language_model({
                    "type": "word_familiarity",
                    "word": word,
                    "query": f"Is '{word}' an uncommon or difficult to pronounce word?"
                })

                if isinstance(result, dict) and "uncommon_score" in result:
                    return result["uncommon_score"] > self.curiosity_threshold
            except Exception as e:
                logger.warning(f"Failed to query language model: {e}")

        # Fallback to simple heuristic
        # Check for unusual letter patterns
        unusual_patterns = ["ph", "kn", "gn", "mn", "ps", "pt", "wr", "rh"]
        if any(pattern in word for pattern in unusual_patterns):
            return True

        # Check for consecutive vowels or consonants
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"

        vowel_count = 0
        consonant_count = 0

        for char in word:
            if char in vowels:
                vowel_count += 1
                consonant_count = 0
            elif char in consonants:
                consonant_count += 1
                vowel_count = 0

            if vowel_count >= 3 or consonant_count >= 3:
                return True

        return False

    async def learn_from_pronunciation(self,
                                       word: str,
                                       pronunciation: str,
                                       accent_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Learn from a pronunciation example.

        Args:
            word: The word that was pronounced
            pronunciation: The correct pronunciation (phonetic or audio reference)
            accent_info: Optional information about the accent

        Returns:
            Info about the learning result
        """
        word = word.lower()

        # Store the pronunciation
        if word not in self.pronunciation_memory:
            self.pronunciation_memory[word] = {
                "canonical": pronunciation,
                "variants": {},
                "practice_count": 0,
                "last_practiced": datetime.now().isoformat()
            }
            self.stats["words_learned"] += 1
        else:
            # Update existing pronunciation
            self.pronunciation_memory[word]["practice_count"] += 1
            self.pronunciation_memory[word]["last_practiced"] = datetime.now().isoformat()

        # If we have accent information, update accent memory
        if accent_info:
            accent_name = accent_info.get("name", "unknown")
            accent_region = accent_info.get("region", "unknown")

            if accent_name not in self.accent_memory:
                self.accent_memory[accent_name] = {
                    "region": accent_region,
                    "patterns": {},
                    "example_words": []
                }
                self.stats["accent_patterns"] += 1

            # Add this word as an example for this accent
            if word not in self.accent_memory[accent_name]["example_words"]:
                self.accent_memory[accent_name]["example_words"].append(word)

            # Add the pronunciation variant to the word
            self.pronunciation_memory[word]["variants"][accent_name] = pronunciation

        # Remove from curiosity list if present
        if word in self.curiosity_list:
            self.curiosity_list.remove(word)

        # Save updated memory
        self.save_memory()

        return {
            "word": word,
            "learned": True,
            "total_words_known": len(self.pronunciation_memory),
            "accent_patterns": self.stats["accent_patterns"]
        }

    def get_curious_word(self) -> Optional[str]:
        """
        Get a word to be curious about for pronunciation learning.

        Returns:
            A word to ask about, or None if no curiosity
        """
        if not self.curiosity_list:
            return None

        # Choose a random word from our curiosity list
        curious_words = list(self.curiosity_list)
        if curious_words:
            return random.choice(curious_words)

        return None

    async def practice_pronunciation(self,
                                     word: str,
                                     feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Practice pronunciation of a word and incorporate feedback.

        Args:
            word: The word being practiced
            feedback: Feedback on the pronunciation

        Returns:
            Results of the practice session
        """
        word = word.lower()
        success = feedback.get("success", False)
        correction = feedback.get("correction", None)
        accent = feedback.get("accent", "neutral")

        # Record practice history
        practice_entry = {
            "word": word,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "correction": correction,
            "accent": accent
        }

        self.practice_history.append(practice_entry)
        self.stats["practice_sessions"] += 1

        # Update pronunciation memory
        if word in self.pronunciation_memory:
            self.pronunciation_memory[word]["practice_count"] += 1
            self.pronunciation_memory[word]["last_practiced"] = datetime.now().isoformat()

            if success:
                # If successful, strengthen this pronunciation
                self.stats["successful_adaptations"] += 1
            elif correction:
                # If corrected, update with the correction
                if accent in self.pronunciation_memory[word]["variants"]:
                    # Blend the existing and new pronunciation
                    old_pron = self.pronunciation_memory[word]["variants"][accent]
                    self.pronunciation_memory[word]["variants"][accent] = self._blend_pronunciations(
                        old_pron, correction, self.learning_rate
                    )
                else:
                    # Add new variant
                    self.pronunciation_memory[word]["variants"][accent] = correction
        else:
            # New word, add it
            self.pronunciation_memory[word] = {
                "canonical": correction if correction else word,  # Fallback to word itself
                "variants": {accent: correction} if correction else {},
                "practice_count": 1,
                "last_practiced": datetime.now().isoformat()
            }
            self.stats["words_learned"] += 1

        # Save updated memory
        self.save_memory()

        return {
            "word": word,
            "success": success,
            "needs_more_practice": not success,
            "practice_count": self.pronunciation_memory.get(word, {}).get("practice_count", 1)
        }

    def _blend_pronunciations(self, old_pron: str, new_pron: str, learning_rate: float) -> str:
        """
        Blend old and new pronunciations according to learning rate.

        This is a placeholder implementation. In a real system, this would
        use phonetic representations and blend them appropriately.

        Args:
            old_pron: Old pronunciation
            new_pron: New pronunciation
            learning_rate: How much to weight the new pronunciation

        Returns:
            Blended pronunciation
        """
        # In a real system, this would use phonemes or other representations
        # For this example, we'll just return the new pronunciation
        # but in reality it would be a weighted blend
        return new_pron

    async def detect_accent(self, audio_sample) -> Dict[str, Any]:
        """
        Detect accent from an audio sample.

        Args:
            audio_sample: Audio data

        Returns:
            Detected accent information
        """
        # In a real implementation, this would use audio processing
        # For now, return a placeholder

        return {
            "name": "general_american",
            "confidence": 0.85,
            "region": "North America"
        }

    def get_due_practice_words(self, limit: int = 5) -> List[str]:
        """
        Get words that are due for practice.

        Args:
            limit: Maximum number of words to return

        Returns:
            List of words due for practice
        """
        # Calculate word priority based on:
        # 1. Time since last practice
        # 2. Number of previous practices (fewer is higher priority)
        # 3. Whether it's in the curiosity list

        now = datetime.now()
        word_priorities = []

        for word, data in self.pronunciation_memory.items():
            try:
                # Calculate days since last practice
                last_practiced = datetime.fromisoformat(data.get("last_practiced", "2000-01-01T00:00:00"))
                days_since = (now - last_practiced).days

                # Calculate priority score
                priority = days_since * 10
                priority -= data.get("practice_count", 0) * 2  # Lower priority if practiced a lot

                if word in self.curiosity_list:
                    priority += 50  # Boost curiosity words

                word_priorities.append((word, priority))
            except Exception as e:
                logger.warning(f"Error calculating priority for word {word}: {e}")

        # Sort by priority (highest first) and take the top 'limit' words
        word_priorities.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in word_priorities[:limit]]

    def get_pronunciation_for_word(self, word: str, accent: str = "neutral") -> Optional[str]:
        """
        Get the pronunciation for a word in a specific accent.

        Args:
            word: The word to get pronunciation for
            accent: The accent to use

        Returns:
            Pronunciation if available, None otherwise
        """
        word = word.lower()
        if word not in self.pronunciation_memory:
            return None

        # Check for accent-specific variant
        if accent in self.pronunciation_memory[word]["variants"]:
            return self.pronunciation_memory[word]["variants"][accent]

        # Fall back to canonical pronunciation
        return self.pronunciation_memory[word]["canonical"]

    def generate_accent_report(self) -> Dict[str, Any]:
        """
        Generate a report on accent learning progress.

        Returns:
            Report on accent learning
        """
        return {
            "accents_known": len(self.accent_memory),
            "words_learned": self.stats["words_learned"],
            "practice_sessions": self.stats["practice_sessions"],
            "successful_adaptations": self.stats["successful_adaptations"],
            "curious_words": len(self.curiosity_list),
            "accent_details": {
                name: {
                    "region": data.get("region", "unknown"),
                    "example_count": len(data.get("example_words", [])),
                    "examples": data.get("example_words", [])[:5]  # First 5 examples
                }
                for name, data in self.accent_memory.items()
            }
        }
