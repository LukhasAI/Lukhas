"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: accent_adapter.py
Advanced: accent_adapter.py
Integration Date: 2025-05-31T07:55:28.109160
"""

"""
╔═══════════════════════════════════════════════════════════════════════════╗
║ MODULE        : accent_adapter.py                                         ║
║ DESCRIPTION   : Ethically handles accent detection, adaptation, and       ║
║                 cultural sensitivity for voice interactions. Ensures      ║
║                 respectful linguistic curiosity and cultural awareness.   ║
║ TYPE          : Accent Adaptation Module     VERSION: v1.0.0              ║
║ AUTHOR        : LUKHAS SYSTEMS                  CREATED: 2025-05-09        ║
╚═══════════════════════════════════════════════════════════════════════════╝
DEPENDENCIES:
- lukhas_emotion_log_alt.py
- emotion_mapper_alt.py
- voice_memory_helix.py
"""

import base64
import hashlib
import logging
import random
import re
from datetime import datetime, timezone
from typing import Any, Optional

from cryptography.fernet import Fernet

from lukhas.core.identity.vault.lukhas_id import (get_encryption_key,
                                                  has_access, log_access)

# Initialize logger
logger = logging.getLogger("accent_adapter")


class AccentAdapter:
    """
    Provides ethical and respectful accent awareness and adaptation capabilities.
    Enables culturally sensitive linguistic curiosity and appropriate responses.
    Tracks trust_score per region, memory decay fields, and emotional tagging.
    """

    def __init__(
        self,
        emotion_mapper=None,
        memory_helix=None,
        config: dict[str, Any] = None,
        user_id: str = None,
        tier: str = "T3"
    ):
        """
        Initialize the accent adapter with Lukhas_ID-based encryption and access control.

        Args:
            emotion_mapper: Reference to emotion mapping system
            memory_helix: Reference to voice memory helix for pronunciation patterns
            config: Configuration dictionary
            user_id: User ID for Lukhas_ID integration
            tier: Access tier for encryption and access control
        """
        self.emotion_mapper = emotion_mapper
        self.memory_helix = memory_helix
        self.config = config or {}
        self.user_id = user_id
        self.tier = tier
        self.trust_score = {}

        # Get encryption key from Lukhas_ID
        self.encryption_key = get_encryption_key(user_id=self.user_id, tier=self.tier)
        self.cipher = Fernet(self.encryption_key)

        # DNA-like, append-only, encrypted memory chain per user
        self.cultural_memory = {}  # user_id: list of encrypted, hash-chained records

        # Cultural context awareness settings
        self.cultural_contexts = {
            "formal": {
                "curiosity_threshold": 0.05,  # Very low chance of asking about unfamiliar words
                "phrasing_style": "respectful",
                "voice_mode": "cultural_bridge",
            },
            "educational": {
                "curiosity_threshold": 0.4,  # Higher chance to ask about language
                "phrasing_style": "curious",
                "voice_mode": "cultural_explorer",
            },
            "casual": {
                "curiosity_threshold": 0.2,  # Moderate chance to ask
                "phrasing_style": "casual",
                "voice_mode": "accent_learner",
            },
            "professional": {
                "curiosity_threshold": 0.1,  # Low chance of asking
                "phrasing_style": "professional",
                "voice_mode": "respectful",
            },
        }

        # Respectful curiosity phrases for asking about unfamiliar words
        self.curiosity_phrases = {
            "respectful": [
                "If you don't mind me asking, what does {word} mean in this context?",
                "I'm not familiar with the term {word}. Would you be comfortable explaining it?",
                "I'd like to learn more about the word {word}, if you're open to sharing.",
                "May I ask about the meaning of {word} in your cultural context?",
            ],
            "curious": [
                "I'm curious about the word {word} - could you tell me more about it?",
                "The word {word} is new to me. What does it mean?",
                "I'm learning about different expressions - what does {word} mean?",
                "I'd love to understand what {word} means in this context.",
            ],
            "casual": [
                "That's an interesting word - {word}. What does it mean?",
                "I haven't heard {word} before. Can you explain?",
                "What does {word} mean? I'd love to add it to my vocabulary.",
                "I'm still learning about different expressions - what's {word} mean?",
            ],
            "professional": [
                "For clarity, could you explain the term {word}?",
                "To ensure understanding, would you mind explaining what {word} means?",
                "I'd like to confirm the meaning of {word} in this professional context.",
                "For my understanding, could you elaborate on the term {word}?",
            ],
        }

        # Cultural context patterns
        self.cultural_patterns = {
            "honorifics_used": re.compile(r"\b(Mr|Mrs|Ms|Dr|Prof|Sir|Madam|Your)\b"),
            "formal_language": re.compile(
                r"\b(would you|could you|may I|shall we|kindly)\b"
            ),
            "educational_setting": re.compile(
                r"\b(learn|teach|study|explain|understand|course|class)\b"
            ),
            "business_context": re.compile(
                r"\b(meeting|client|project|business|company|report|deadline)\b"
            ),
        }

        logger.info("Accent Adapter initialized with Lukhas_ID integration")

    def _encrypt_record(self, record: dict, prev_hash: Optional[str] = None) -> dict:
        """
        Encrypts a memory record and links it to the previous via hash (DNA chain).
        Hash is computed over the raw JSON and previous hash (before encryption) for auditability.
        Adds optional fields for memory decay and type tagging.
        """
        import json

        # Ensure recall_count and last_rehearsed fields are present
        record.setdefault("recall_count", 0)
        record.setdefault("last_rehearsed", datetime.now(timezone.utc).isoformat())
        # Add support for new type tags if provided
        valid_types = {
            "general",
            "location",
            "curiosity",
            "cultural_trigger",
            "emotional_response",
        }
        record_type = record.get("type", "general")
        if record_type not in valid_types:
            record_type = "general"
        record["type"] = record_type
        # Compute hash input using raw JSON and previous hash (before encryption)
        hash_input = f"{prev_hash or ''}|{json.dumps(record, sort_keys=True)}"
        record_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        # Add previous hash for chain integrity
        record_copy = dict(record)
        record_copy["prev_hash"] = prev_hash or ""
        # Encrypt the record (with prev_hash included)
        record_bytes = json.dumps(record_copy, sort_keys=True).encode()
        encrypted = self.cipher.encrypt(record_bytes)
        return {
            "encrypted": base64.b64encode(encrypted).decode(),
            "hash": record_hash,
            "prev_hash": prev_hash or "",
        }

    def _decrypt_record(self, encrypted_record: dict) -> dict:
        """
        Decrypts an encrypted memory record with access control.
        """
        import json

        if not has_access(:  # noqa: invalid-syntax
            user_id=self.user_id,
            memory_id=encrypted_record["hash"],
            required_tier=self.tier
        ):
            raise PermissionError("Access denied for this memory.")

        encrypted = base64.b64decode(encrypted_record["encrypted"])
        decrypted = self.cipher.decrypt(encrypted)
        record = json.loads(decrypted.decode())
        return record

    def log_cultural_interaction(
        self,
        user_id: str,
        word: str,
        cultural_context: str,
        response: Optional[str] = None,
    ) -> None:
        """
            Log a cultural interaction for future reference (DNA chain, encrypted,
        immutable).
        """
        if user_id not in self.cultural_memory:
            self.cultural_memory[user_id] = []
        prev_hash = (
            self.cultural_memory[user_id][-1]["hash"]
            if self.cultural_memory[user_id]:  # noqa: invalid-syntax
            else "":  # noqa: invalid-syntax
        )  # noqa: invalid-syntax
        interaction = {
            "word": word,
            "cultural_context": cultural_context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response": response,
        }
        encrypted_record = self._encrypt_record(interaction, prev_hash)
        self.cultural_memory[user_id].append(encrypted_record)

        # Log the action
        log_access(
            user_id=self.user_id,
            action="log_cultural_interaction",
            memory_id=encrypted_record["hash"],
            tier=self.tier,
        )

    def get_user_memory_chain(self, user_id: str) -> list:
        """
        Retrieve and decrypt the full memory DNA chain for a user.
        """
        if user_id not in self.cultural_memory:
            return []
        return [self._decrypt_record(r) for r in self.cultural_memory[user_id]]

    def remember_location(
        self,
        user_id: str,
        location: str,
        accent_detected: Optional[str] = None,
        words_learned: Optional[list[str]] = None,
    ) -> None:
        """
            Remember a location associated with linguistic experiences (DNA chain,
        encrypted, immutable).
        """
        if user_id not in self.cultural_memory:
            self.cultural_memory[user_id] = []
        prev_hash = (
            self.cultural_memory[user_id][-1]["hash"]
            if self.cultural_memory[user_id]:  # noqa: invalid-syntax
            else "":  # noqa: invalid-syntax
        )  # noqa: invalid-syntax
        location_memory = {
            "type": "location",
            "location": location,
            "first_visited": datetime.now(timezone.utc).isoformat(),
            "last_visited": datetime.now(timezone.utc).isoformat(),
            "visit_count": 1,
            "accents": [accent_detected] if accent_detected else [],
            "words": words_learned or [],
        }
        encrypted_record = self._encrypt_record(location_memory, prev_hash)
        self.cultural_memory[user_id].append(encrypted_record)

        # Log the action
        log_access(
            user_id=self.user_id,
            action="remember_location",
            memory_id=encrypted_record["hash"],
            tier=self.tier,
        )

    def generate_reminiscence(
        self, user_id: str, current_context: dict[str, Any]
    ) -> Optional[str]:
        """
        Generate a reminiscence about a past linguistic or cultural experience (from DNA chain).
        Includes optional emotional tone if emotion_mapper is available.
        """
        if user_id not in self.cultural_memory or not self.cultural_memory[user_id]:
            return None
        # Decrypt all records for this user
        records = [self._decrypt_record(r) for r in self.cultural_memory[user_id]]
        # Check for location mention in current context
        mentioned_location = None
        if "text" in current_context:
            locations = [
                m["location"]
                for m in records:  # noqa: invalid-syntax
                if "type" in m and m["type"] == "location":
            ]  # noqa: invalid-syntax
            for location in locations:
                if location.lower() in current_context["text"].lower():
                    mentioned_location = location
                    break
        if mentioned_location:
            location_memories = [
                m
                for m in records:  # noqa: invalid-syntax
                if m.get("type") == "location":
                and m.get("location") == mentioned_location  # noqa: invalid-syntax
            ]  # noqa: invalid-syntax
            if location_memories:
                memory = location_memories[0]
                templates = [
                    "I remember when we were in {location}. {accent_phrase} {word_phrase}",
                    "That reminds me of our time in {location}. {word_phrase}",
                    "When we visited {location}, {accent_phrase}",
                    "Oh, {location}! {memory_phrase}",]
                accent_phrase = ""
                if memory.get("accents"):
                    accent_phrase = (
                        f"I noticed the {memory['accents'][0]} accent there."
                    )
                word_phrase = ""
                if memory.get("words") and len(memory["words"]) > 0:
                    word = random.choice(memory["words"])
                    word_phrase = f"I learned the word '{word}' there."
                memory_phrase = f"We visited {memory.get('visit_count',")}  # noqa: invalid-syntax
                                                         1)} times. The last time was quite memorable."
                template = random.choice(templates)
                reminiscence = template.format(
                    location=mentioned_location,
                    accent_phrase=accent_phrase,
                    word_phrase=word_phrase,
                    memory_phrase=memory_phrase,
                )
                # Add fallback phrases if no accent or word phrase
                if not accent_phrase and not word_phrase:
                    reminiscence = f"I have fond memories of {mentioned_location} from our past interactions."
                # Add emotional tone with replay awareness if emotion_mapper is
                # available
                if self.emotion_mapper:
                    tone = self.emotion_mapper.suggest_tone("nostalgia", memory)
                    reminiscence = (
                        f"{reminiscence} I remember it softly—it made me feel {tone}."
                    )
                    if self.config.get("speak_reminiscence", False) and hasattr(:  # noqa: invalid-syntax
                        self.memory_helix, "speak"
                    ):
                        self.memory_helix.speak(reminiscence, tone=tone)
                return re.sub(r"\s{2,}", " ", reminiscence).strip()
        # Random chance to reminisce about a past interaction if we have enough memories
        if len(records) > 10 and random.random() < 0.15:
            word_memories = [m for m in records if "word" in m]
            if word_memories:
                memory = random.choice(word_memories)
                reminiscence = f"By the way, I remember learning the word '{memory['word']}' in our previous conversation. That was interesting to me."
                if self.emotion_mapper:
                    tone = self.emotion_mapper.suggest_tone("nostalgia", memory)
                    reminiscence = (
                        f"{reminiscence} I remember it softly—it made me feel {tone}."
                    )
                    if self.config.get("speak_reminiscence", False) and hasattr(:  # noqa: invalid-syntax
                        self.memory_helix, "speak"
                    ):
                        self.memory_helix.speak(reminiscence, tone=tone)
                return reminiscence
        return None

    def boost_memory(self, memory: dict) -> dict:
        """
        Simulate memory rehearsal by incrementing recall count and updating timestamp.
        """
        memory["recall_count"] += 1
        memory["last_rehearsed"] = datetime.now(timezone.utc).isoformat()
        return memory

    # Other methods remain unchanged
    # ...
