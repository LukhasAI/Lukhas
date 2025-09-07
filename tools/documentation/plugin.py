"""
DocuTutor Plugin Integration with Lukhas AGI
Implements core integration patterns for connecting with Lukhas's systems.
"""
import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

# Import Lukhas interfaces (these would be provided by Lukhas AGI)
from core import (
    LUKHASBioOscillatorInterface,
    LUKHASComplianceInterface,
    LUKHASIdentityInterface,
    LUKHASMemoryInterface,
    LUKHASPlugin,
    LUKHASVoiceInterface,
)

from .content_generation_engine.doc_generator import DocGenerator
from .symbolic_knowledge_core.knowledge_graph import SystemKnowledgeGraph
from .tutoring_engine.tutor import TutorEngine

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    EXPLANATION = "explanation"
    REFERENCE = "reference"


class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GenerationConfig(BaseModel):
    content_type: ContentType
    user_level: UserLevel
    voice_enabled: bool = False
    bio_oscillator_aware: bool = True
    max_complexity: Optional[int] = None
    cultural_context: Optional[str] = None


class DocuTutorPlugin(LUKHASPlugin):
    """
    Main plugin class for integrating DocuTutor with Lukhas AGI.
    Implements Lukhas's core patterns for perfect UX and safe AI.
    """

    def __init__(self, plugin_config: Optional[dict[str, Any]] = None):
        """Initialize plugin with Lukhas AGI systems."""
        super().__init__(name="DocuTutor", version="1.0.0")

        # Initialize Lukhas system interfaces
        self.memory = LUKHASMemoryInterface()
        self.voice = LUKHASVoiceInterface()
        self.identity = LUKHASIdentityInterface()
        self.bio = LUKHASBioOscillatorInterface()
        self.compliance = LUKHASComplianceInterface()

        # Initialize DocuTutor components
        self.skg = SystemKnowledgeGraph()
        self.doc_generator = DocGenerator(self.skg)
        self.tutor = TutorEngine(self.skg)

        # Create memory helix for documentation
        self.doc_helix = self.memory.create_helix(
            name="documentation",
            description="Documentation knowledge evolution",
            schema={
                "type": "documentation",
                "version": "1.0",
                "fields": ["content", "context", "timestamp"],
            },
        )

        logger.info("DocuTutor plugin initialized and connected to Lukhas systems")

    async def generate_documentation(self, source_path: str, config: GenerationConfig) -> str:
        """
        Generate documentation using Lukhas's advanced capabilities.
        """
        # Verify user permissions through Lukhas_ID
        user = self.identity.get_current_user()
        if not self.compliance.can_access_content(user, source_path):
            raise PermissionError("User does not have access to this content")

        # Get optimal timing from bio-oscillator if enabled
        if config.bio_oscillator_aware:
            timing = self.bio.get_optimal_timing()
            if not timing.is_optimal():
                logger.warning("Sub-optimal timing for documentation generation")

        # Generate base documentation
        docs = self.doc_generator.generate(source_path)

        # Enhance with voice if enabled
        if config.voice_enabled:
            voice_config = self.voice.create_config(
                emotional_style="educational", cultural_context=config.cultural_context
            )
            docs = self.voice.enhance_content(docs, voice_config)

        # Store in memory helix
        await self.doc_helix.store_memory(
            {
                "content": docs,
                "context": {
                    "source": source_path,
                    "config": config.dict(),
                    "user": user.id,
                },
                "timestamp": self.memory.get_current_timestamp(),
            }
        )

        return docs

    async def start_learning_session(self, topic: str, config: GenerationConfig) -> Any:
        """
        Start an interactive learning session using Lukhas's tutoring capabilities.
        """
        # Verify user and get profile
        user = self.identity.get_current_user()
        profile = await self.memory.get_user_knowledge_profile(user.id)

        # Create personalized session
        session = self.tutor.create_session(topic=topic, user_level=config.user_level, knowledge_profile=profile)

        # Enable voice interaction if requested
        if config.voice_enabled:
            voice_personality = self.voice.create_tutor_personality(
                style="encouraging", cultural_context=config.cultural_context
            )
            session.enable_voice(voice_personality)

        # Monitor bio-oscillator patterns if enabled
        if config.bio_oscillator_aware:
            session.set_bio_monitor(self.bio.create_session_monitor(session_type="learning", user_id=user.id))

        return session

    async def update_knowledge(self, content_id: str, feedback: dict[str, Any]):
        """
        Update documentation/tutorial content based on user feedback.
        Uses Lukhas's memory evolution patterns.
        """
        # Verify update permission
        user = self.identity.get_current_user()
        if not self.compliance.can_modify_content(user, content_id):
            raise PermissionError("User cannot modify this content")

        # Get existing content
        content = await self.doc_helix.get_memory(content_id)

        # Apply feedback using Lukhas's learning patterns
        updated_content = self.doc_generator.apply_feedback(
            content=content, feedback=feedback, user_profile=user.profile
        )

        # Store updated version in memory helix
        await self.doc_helix.evolve_memory(
            memory_id=content_id,
            new_content=updated_content,
            evolution_context={
                "feedback": feedback,
                "user": user.id,
                "timestamp": self.memory.get_current_timestamp(),
            },
        )

        return updated_content

    def get_optimal_complexity(self, user_id: str, topic: str) -> int:
        """
        Use Lukhas's bio-oscillator to determine optimal complexity level.
        """
        user_state = self.bio.get_current_state(user_id)
        knowledge_level = self.memory.get_topic_knowledge_level(user_id, topic)

        return self.tutor.calculate_optimal_complexity(bio_state=user_state, knowledge_level=knowledge_level)

    async def cleanup(self):
        """Clean up plugin resources properly."""
        await self.doc_helix.close()
        self.skg.clear()
        logger.info("DocuTutor plugin cleaned up")
