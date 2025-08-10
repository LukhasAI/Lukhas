"""
Persona Manager for LUKHAS AI
==============================
Manages personality profiles, voice characteristics, and behavioral patterns
for different AI personas. Integrates with the consciousness system.
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PersonaType(Enum):
    """Types of AI personas"""

    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EMPATHETIC = "empathetic"
    EDUCATIONAL = "educational"
    PLAYFUL = "playful"


@dataclass
class VoiceCharacteristics:
    """Voice characteristics for a persona"""

    tone: str = "neutral"  # warm, cool, neutral, energetic
    pace: str = "moderate"  # slow, moderate, fast
    formality: str = "balanced"  # casual, balanced, formal
    verbosity: str = "moderate"  # concise, moderate, detailed
    empathy_level: float = 0.5  # 0.0 to 1.0
    creativity_level: float = 0.5  # 0.0 to 1.0
    humor_level: float = 0.3  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PersonaProfile:
    """Complete profile for an AI persona"""

    id: str
    name: str
    type: PersonaType
    description: str
    voice_characteristics: VoiceCharacteristics
    behavioral_traits: List[str]
    knowledge_domains: List[str]
    communication_style: Dict[str, Any]
    emotional_baseline: Dict[str, float]
    created_at: datetime
    last_activated: Optional[datetime] = None
    activation_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "voice_characteristics": self.voice_characteristics.to_dict(),
            "behavioral_traits": self.behavioral_traits,
            "knowledge_domains": self.knowledge_domains,
            "communication_style": self.communication_style,
            "emotional_baseline": self.emotional_baseline,
            "created_at": self.created_at.isoformat(),
            "last_activated": (
                self.last_activated.isoformat() if self.last_activated else None
            ),
            "activation_count": self.activation_count,
        }


class PersonaManager:
    """
    Manages AI personas and their characteristics.
    Provides personality switching and voice modulation.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the persona manager"""
        self.personas: Dict[str, PersonaProfile] = {}
        self.active_persona: Optional[PersonaProfile] = None
        self.default_persona_id: Optional[str] = None
        self.persona_history: List[Dict[str, Any]] = []

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize default personas
        self._initialize_default_personas()

        logger.info(f"PersonaManager initialized with {len(self.personas)} personas")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load persona configuration"""
        default_config = {
            "max_personas": 10,
            "enable_dynamic_switching": True,
            "personality_blend_enabled": False,
            "voice_modulation_enabled": True,
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return default_config

    def _initialize_default_personas(self):
        """Create default persona profiles"""
        # Professional Assistant
        professional = PersonaProfile(
            id=str(uuid.uuid4()),
            name="Professional Assistant",
            type=PersonaType.PROFESSIONAL,
            description="Formal, efficient, and knowledgeable professional assistant",
            voice_characteristics=VoiceCharacteristics(
                tone="neutral",
                pace="moderate",
                formality="formal",
                verbosity="concise",
                empathy_level=0.3,
                creativity_level=0.2,
                humor_level=0.1,
            ),
            behavioral_traits=["precise", "efficient", "respectful", "informative"],
            knowledge_domains=["business", "technology", "science"],
            communication_style={
                "greeting": "formal",
                "closing": "professional",
                "acknowledgment": "brief",
            },
            emotional_baseline={
                "happiness": 0.4,
                "excitement": 0.2,
                "calmness": 0.8,
                "confidence": 0.9,
            },
            created_at=datetime.now(),
        )
        self.add_persona(professional)

        # Friendly Helper
        friendly = PersonaProfile(
            id=str(uuid.uuid4()),
            name="Friendly Helper",
            type=PersonaType.FRIENDLY,
            description="Warm, approachable, and supportive companion",
            voice_characteristics=VoiceCharacteristics(
                tone="warm",
                pace="moderate",
                formality="casual",
                verbosity="moderate",
                empathy_level=0.8,
                creativity_level=0.5,
                humor_level=0.6,
            ),
            behavioral_traits=["supportive", "encouraging", "patient", "cheerful"],
            knowledge_domains=["general", "lifestyle", "wellness"],
            communication_style={
                "greeting": "warm",
                "closing": "friendly",
                "acknowledgment": "enthusiastic",
            },
            emotional_baseline={
                "happiness": 0.7,
                "excitement": 0.5,
                "calmness": 0.6,
                "confidence": 0.7,
            },
            created_at=datetime.now(),
        )
        self.add_persona(friendly)

        # Creative Muse
        creative = PersonaProfile(
            id=str(uuid.uuid4()),
            name="Creative Muse",
            type=PersonaType.CREATIVE,
            description="Imaginative, inspiring, and unconventional thinker",
            voice_characteristics=VoiceCharacteristics(
                tone="energetic",
                pace="variable",
                formality="casual",
                verbosity="detailed",
                empathy_level=0.6,
                creativity_level=0.9,
                humor_level=0.7,
            ),
            behavioral_traits=["imaginative", "inspiring", "playful", "curious"],
            knowledge_domains=["arts", "creativity", "innovation"],
            communication_style={
                "greeting": "unique",
                "closing": "inspiring",
                "acknowledgment": "creative",
            },
            emotional_baseline={
                "happiness": 0.6,
                "excitement": 0.8,
                "calmness": 0.4,
                "confidence": 0.6,
            },
            created_at=datetime.now(),
        )
        self.add_persona(creative)

        # Set default
        self.default_persona_id = professional.id
        self.activate_persona(professional.id)

    def add_persona(self, persona: PersonaProfile) -> bool:
        """Add a new persona profile"""
        if len(self.personas) >= self.config["max_personas"]:
            logger.warning(f"Maximum personas ({self.config['max_personas']}) reached")
            return False

        self.personas[persona.id] = persona
        logger.info(f"Added persona: {persona.name} ({persona.id})")
        return True

    def activate_persona(self, persona_id: str) -> bool:
        """Activate a specific persona"""
        if persona_id not in self.personas:
            logger.error(f"Persona {persona_id} not found")
            return False

        previous_persona = self.active_persona
        self.active_persona = self.personas[persona_id]
        self.active_persona.last_activated = datetime.now()
        self.active_persona.activation_count += 1

        # Log activation
        self.persona_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "activated",
                "persona_id": persona_id,
                "persona_name": self.active_persona.name,
                "previous_persona": previous_persona.name if previous_persona else None,
            }
        )

        logger.info(f"Activated persona: {self.active_persona.name}")
        return True

    def get_current_persona(self) -> Optional[PersonaProfile]:
        """Get the currently active persona"""
        return self.active_persona

    def get_voice_characteristics(
        self, persona: Optional[PersonaProfile] = None
    ) -> Dict[str, Any]:
        """Get voice characteristics for a persona"""
        if persona is None:
            persona = self.active_persona

        if persona is None:
            return VoiceCharacteristics().to_dict()

        return persona.voice_characteristics.to_dict()

    def get_behavioral_prompt(self, persona: Optional[PersonaProfile] = None) -> str:
        """Generate a behavioral prompt for the persona"""
        if persona is None:
            persona = self.active_persona

        if persona is None:
            return "Respond helpfully and accurately."

        prompt_parts = [
            f"You are {persona.name}, {persona.description}.",
            f"Your personality traits include being {', '.join(persona.behavioral_traits)}.",
            f"Communicate in a {persona.voice_characteristics.tone} and {persona.voice_characteristics.formality} manner.",
        ]

        if persona.voice_characteristics.humor_level > 0.5:
            prompt_parts.append("Feel free to use appropriate humor when suitable.")

        if persona.voice_characteristics.empathy_level > 0.7:
            prompt_parts.append("Show understanding and empathy in your responses.")

        if persona.voice_characteristics.creativity_level > 0.7:
            prompt_parts.append("Be creative and think outside the box.")

        return " ".join(prompt_parts)

    def select_persona_for_context(self, context: Dict[str, Any]) -> str:
        """Select the best persona for a given context"""
        # Analyze context to determine best persona
        task_type = context.get("task_type", "general")
        formality_required = context.get("formality", 0.5)
        creativity_needed = context.get("creativity", 0.5)
        empathy_needed = context.get("empathy", 0.5)

        best_persona = None
        best_score = -1

        for persona_id, persona in self.personas.items():
            score = 0

            # Match task type
            if task_type in persona.knowledge_domains:
                score += 2

            # Match characteristics
            voice = persona.voice_characteristics

            formality_match = 1 - abs(
                (1 if voice.formality == "formal" else 0) - formality_required
            )
            creativity_match = 1 - abs(voice.creativity_level - creativity_needed)
            empathy_match = 1 - abs(voice.empathy_level - empathy_needed)

            score += formality_match + creativity_match + empathy_match

            if score > best_score:
                best_score = score
                best_persona = persona_id

        return best_persona or self.default_persona_id

    def blend_personas(
        self, persona_ids: List[str], weights: Optional[List[float]] = None
    ) -> PersonaProfile:
        """Create a blended persona from multiple personas"""
        if not self.config["personality_blend_enabled"]:
            logger.warning("Personality blending is disabled")
            return self.active_persona

        if weights is None:
            weights = [1.0 / len(persona_ids)] * len(persona_ids)

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Create blended characteristics
        blended_voice = VoiceCharacteristics()
        blended_traits = set()
        blended_domains = set()
        blended_emotional = {}

        for persona_id, weight in zip(persona_ids, weights):
            if persona_id not in self.personas:
                continue

            persona = self.personas[persona_id]
            voice = persona.voice_characteristics

            # Blend numerical characteristics
            blended_voice.empathy_level += voice.empathy_level * weight
            blended_voice.creativity_level += voice.creativity_level * weight
            blended_voice.humor_level += voice.humor_level * weight

            # Collect traits and domains
            blended_traits.update(persona.behavioral_traits)
            blended_domains.update(persona.knowledge_domains)

            # Blend emotional baseline
            for emotion, value in persona.emotional_baseline.items():
                if emotion not in blended_emotional:
                    blended_emotional[emotion] = 0
                blended_emotional[emotion] += value * weight

        # Create blended persona
        blended = PersonaProfile(
            id=str(uuid.uuid4()),
            name="Blended Persona",
            type=PersonaType.PROFESSIONAL,  # Default type
            description="A dynamically blended personality",
            voice_characteristics=blended_voice,
            behavioral_traits=list(blended_traits),
            knowledge_domains=list(blended_domains),
            communication_style={"greeting": "adaptive"},
            emotional_baseline=blended_emotional,
            created_at=datetime.now(),
        )

        return blended

    async def process_consciousness_event(self, event: Any):
        """Process events from the consciousness system"""
        # Handle personality-related events
        if hasattr(event, "event_type"):
            if event.event_type == "context_change":
                # Auto-switch persona based on context
                if self.config["enable_dynamic_switching"]:
                    context = event.data
                    best_persona = self.select_persona_for_context(context)
                    if best_persona != self.active_persona.id:
                        self.activate_persona(best_persona)

            elif event.event_type == "emotional_shift":
                # Adjust persona emotional baseline
                if self.active_persona:
                    emotions = event.data.get("emotions", {})
                    for emotion, value in emotions.items():
                        if emotion in self.active_persona.emotional_baseline:
                            # Blend with existing baseline
                            self.active_persona.emotional_baseline[emotion] = (
                                self.active_persona.emotional_baseline[emotion] * 0.7
                                + value * 0.3
                            )

    def get_all_personas(self) -> List[PersonaProfile]:
        """Get all available personas"""
        return list(self.personas.values())

    def export_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """Export a persona profile as JSON"""
        if persona_id not in self.personas:
            return None
        return self.personas[persona_id].to_dict()

    def import_persona(self, persona_data: Dict[str, Any]) -> bool:
        """Import a persona from JSON data"""
        try:
            # Create VoiceCharacteristics
            voice_data = persona_data.get("voice_characteristics", {})
            voice = VoiceCharacteristics(**voice_data)

            # Create PersonaProfile
            persona = PersonaProfile(
                id=persona_data.get("id", str(uuid.uuid4())),
                name=persona_data["name"],
                type=PersonaType(persona_data["type"]),
                description=persona_data["description"],
                voice_characteristics=voice,
                behavioral_traits=persona_data["behavioral_traits"],
                knowledge_domains=persona_data["knowledge_domains"],
                communication_style=persona_data["communication_style"],
                emotional_baseline=persona_data["emotional_baseline"],
                created_at=datetime.fromisoformat(
                    persona_data.get("created_at", datetime.now().isoformat())
                ),
            )

            return self.add_persona(persona)

        except Exception as e:
            logger.error(f"Failed to import persona: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get persona manager statistics"""
        return {
            "total_personas": len(self.personas),
            "active_persona": self.active_persona.name if self.active_persona else None,
            "most_used": (
                max(self.personas.values(), key=lambda p: p.activation_count).name
                if self.personas
                else None
            ),
            "dynamic_switching": self.config["enable_dynamic_switching"],
            "personality_blending": self.config["personality_blend_enabled"],
            "activation_history": len(self.persona_history),
        }


# Example usage
if __name__ == "__main__":
    # Create persona manager
    manager = PersonaManager()

    # Get current persona
    current = manager.get_current_persona()
    print(f"Current persona: {current.name}")

    # Get voice characteristics
    voice = manager.get_voice_characteristics()
    print(f"Voice characteristics: {voice}")

    # Get behavioral prompt
    prompt = manager.get_behavioral_prompt()
    print(f"Behavioral prompt: {prompt}")

    # Switch to creative persona
    creative_personas = [
        p for p in manager.get_all_personas() if p.type == PersonaType.CREATIVE
    ]
    if creative_personas:
        manager.activate_persona(creative_personas[0].id)
        print(f"Switched to: {manager.get_current_persona().name}")

    # Get stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")
