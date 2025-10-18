"""
LUKHAS Creativity Service - Module API Interface

This service provides creative generation capabilities for the Cognitive system.
All operations are logged via ΛTRACE and respect user consent and tier access.

Key functions:
- generate_content: Create creative content (stories, poems, ideas)
- dream_synthesis: Process and synthesize dream content
- emotional_expression: Generate emotionally-aware content
- creative_collaboration: Multi-user creative projects

Integration with lukhas-id:
- Creative generation requires valid user identity and consent
- All creative activities are logged for attribution and audit
- Tier-based access to different creative capabilities
- Respect user preferences and ethical boundaries
"""
import os
import random
import sys
from datetime import datetime, timezone
from typing import Any, Optional

# Add parent directory to path for identity interface
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from governance.identity.interface import IdentityClient
except ImportError:
    # Fallback for development
    class IdentityClient:
        def verify_user_access(self, user_id: str, required_tier: str = "LAMBDA_TIER_1") -> bool:
            return True

        def check_consent(self, user_id: str, action: str) -> bool:
            return True

        def log_activity(self, activity_type: str, user_id: str, metadata: dict[str, Any]) -> None:
            print(f"CREATIVITY_LOG: {activity_type} by {user_id}: {metadata}")


class CreativityService:
    """
    Main creativity service for the LUKHAS Cognitive system.

    Provides creative content generation with full integration to
    the identity system for access control and audit logging.
    """

    def __init__(self):
        """Initialize the creativity service with identity integration."""
        self.identity_client = IdentityClient()
        self.creative_models = {
            "story": {"min_tier": "LAMBDA_TIER_1", "consent": "creative_content"},
            "poetry": {"min_tier": "LAMBDA_TIER_1", "consent": "creative_content"},
            "music": {"min_tier": "LAMBDA_TIER_2", "consent": "creative_content"},
            "visual": {"min_tier": "LAMBDA_TIER_2", "consent": "visual_generation"},
            "dream": {"min_tier": "LAMBDA_TIER_3", "consent": "dream_synthesis"},
            "emotion": {"min_tier": "LAMBDA_TIER_2", "consent": "emotional_processing"},
        }

    def generate_content(
        self,
        user_id: str,
        content_type: str,
        prompt: str,
        style: Optional[str] = None,
        parameters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Generate creative content based on user prompt and preferences.

        Args:
            user_id: The user requesting content generation
            content_type: Type of content (story, poetry, music, visual, etc.)
            prompt: Creative prompt or description
            style: Optional style preference
            parameters: Additional generation parameters

        Returns:
            Dict: Generated content and metadata
        """
        parameters = parameters or {}

        # Check if content type is supported
        if content_type not in self.creative_models:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}",
            }

        model_config = self.creative_models[content_type]

        # Verify user access for this content type
        if not self.identity_client.verify_user_access(user_id, model_config["min_tier"]):
            return {
                "success": False,
                "error": f"Insufficient tier for {content_type} generation",
            }

        # Check consent for content generation
        if not self.identity_client.check_consent(user_id, model_config["consent"]):
            return {
                "success": False,
                "error": f"User consent required for {content_type} generation",
            }

        try:
            # Generate content (placeholder implementation)
            generated_content = self._generate_creative_content(content_type, prompt, style, parameters)

            # Create content metadata
            content_id = f"creative_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            content_metadata = {
                "content_id": content_id,
                "type": content_type,
                "prompt": prompt,
                "style": style,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "parameters": parameters,
                "word_count": (len(generated_content.get("text", "").split()) if "text" in generated_content else 0),
            }

            # Log content generation
            self.identity_client.log_activity(
                "creative_content_generated",
                user_id,
                {
                    "content_id": content_id,
                    "content_type": content_type,
                    "prompt_length": len(prompt),
                    "style": style,
                    "success": True,
                    "word_count": content_metadata["word_count"],
                },
            )

            return {
                "success": True,
                "content_id": content_id,
                "content": generated_content,
                "metadata": content_metadata,
                "attribution": f"Generated by LUKHAS Cognitive AI for user {user_id}",
            }

        except Exception as e:
            error_msg = f"Content generation error: {e!s}"
            self.identity_client.log_activity(
                "creative_generation_error",
                user_id,
                {"content_type": content_type, "prompt": prompt, "error": error_msg},
            )
            return {"success": False, "error": error_msg}

    def synthesize_dream(
        self,
        user_id: str,
        dream_data: dict[str, Any],
        synthesis_type: str = "narrative",
    ) -> dict[str, Any]:
        """
        Process and synthesize dream content into coherent narratives.

        Args:
            user_id: The user requesting dream synthesis
            dream_data: Raw dream data to process
            synthesis_type: Type of synthesis (narrative, visual, emotional)

        Returns:
            Dict: Synthesized dream content
        """
        # Verify user access for dream synthesis
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_3"):
            return {"success": False, "error": "Insufficient tier for dream synthesis"}

        # Check consent for dream processing
        if not self.identity_client.check_consent(user_id, "dream_synthesis"):
            return {
                "success": False,
                "error": "User consent required for dream synthesis",
            }

        try:
            # Process dream data
            synthesized_dream = self._process_dream_content(dream_data, synthesis_type)

            dream_id = f"dream_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{user_id}"

            # Log dream synthesis
            self.identity_client.log_activity(
                "dream_synthesized",
                user_id,
                {
                    "dream_id": dream_id,
                    "synthesis_type": synthesis_type,
                    "data_elements": len(dream_data.get("elements", [])),
                    "coherence_score": synthesized_dream.get("coherence", 0.0),
                },
            )

            return {
                "success": True,
                "dream_id": dream_id,
                "synthesized_content": synthesized_dream,
                "synthesis_type": synthesis_type,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            error_msg = f"Dream synthesis error: {e!s}"
            self.identity_client.log_activity(
                "dream_synthesis_error",
                user_id,
                {"synthesis_type": synthesis_type, "error": error_msg},
            )
            return {"success": False, "error": error_msg}

    def generate_emotional_content(
        self,
        user_id: str,
        emotion: str,
        context: dict[str, Any],
        output_format: str = "text",
    ) -> dict[str, Any]:
        """
        Generate content with specific emotional resonance.

        Args:
            user_id: The user requesting emotional content
            emotion: Target emotion (joy, melancholy, excitement, etc.)
            context: Contextual information for emotion generation
            output_format: Format of output (text, music, visual)

        Returns:
            Dict: Emotionally-resonant content
        """
        # Verify user access for emotional content generation
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
            return {
                "success": False,
                "error": "Insufficient tier for emotional content generation",
            }

        # Check consent for emotional processing
        if not self.identity_client.check_consent(user_id, "emotional_processing"):
            return {
                "success": False,
                "error": "User consent required for emotional content generation",
            }

        try:
            # Generate emotionally-aware content
            emotional_content = self._generate_emotional_content(emotion, context, output_format)

            content_id = f"emotional_{emotion}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

            # Log emotional content generation
            self.identity_client.log_activity(
                "emotional_content_generated",
                user_id,
                {
                    "content_id": content_id,
                    "target_emotion": emotion,
                    "output_format": output_format,
                    "emotional_intensity": emotional_content.get("intensity", 0.5),
                    "resonance_score": emotional_content.get("resonance", 0.0),
                },
            )

            return {
                "success": True,
                "content_id": content_id,
                "emotional_content": emotional_content,
                "target_emotion": emotion,
                "output_format": output_format,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            error_msg = f"Emotional content generation error: {e!s}"
            self.identity_client.log_activity(
                "emotional_generation_error",
                user_id,
                {
                    "target_emotion": emotion,
                    "output_format": output_format,
                    "error": error_msg,
                },
            )
            return {"success": False, "error": error_msg}

    def collaborate_creatively(
        self,
        user_id: str,
        project_id: str,
        contribution: dict[str, Any],
        collaboration_type: str = "additive",
    ) -> dict[str, Any]:
        """
        Enable multi-user creative collaboration.

        Args:
            user_id: The user making the contribution
            project_id: ID of the collaborative project
            contribution: The user's creative contribution
            collaboration_type: Type of collaboration (additive, iterative, harmonic)

        Returns:
            Dict: Collaboration result and updated project state
        """
        # Verify user access for collaboration
        if not self.identity_client.verify_user_access(user_id, "LAMBDA_TIER_2"):
            return {
                "success": False,
                "error": "Insufficient tier for creative collaboration",
            }

        # Check consent for collaboration
        if not self.identity_client.check_consent(user_id, "creative_collaboration"):
            return {
                "success": False,
                "error": "User consent required for creative collaboration",
            }

        try:
            # Process collaborative contribution
            collaboration_result = self._process_collaboration(project_id, user_id, contribution, collaboration_type)

            # Log collaboration
            self.identity_client.log_activity(
                "creative_collaboration",
                user_id,
                {
                    "project_id": project_id,
                    "collaboration_type": collaboration_type,
                    "contribution_type": contribution.get("type", "unknown"),
                    "harmony_score": collaboration_result.get("harmony", 0.0),
                },
            )

            return {
                "success": True,
                "project_id": project_id,
                "collaboration_result": collaboration_result,
                "user_contribution": contribution,
                "collaborated_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            error_msg = f"Creative collaboration error: {e!s}"
            self.identity_client.log_activity(
                "collaboration_error",
                user_id,
                {"project_id": project_id, "error": error_msg},
            )
            return {"success": False, "error": error_msg}

    def _generate_creative_content(
        self,
        content_type: str,
        prompt: str,
        style: Optional[str],
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Core creative content generation logic."""
        if content_type == "story":
            return {
                "text": f"Once upon a time, inspired by '{prompt}', a story unfolded...",
                "genre": style or "general",
                "themes": ["creativity", "imagination"],
                "estimated_reading_time": "5 minutes",
            }
        elif content_type == "poetry":
            return {
                "text": f"In verses bright and words so true,\nInspired by '{prompt}' I write for you...",
                "form": style or "free verse",
                "meter": "iambic",
                "stanzas": 2,
            }
        elif content_type == "music":
            return {
                "composition": f"Musical piece inspired by '{prompt}'",
                "key": "C major",
                "tempo": "moderato",
                "style": style or "classical",
                "duration": "3:30",
            }
        else:
            return {"content": f"Creative {content_type} inspired by: {prompt}"}

    def _process_dream_content(self, dream_data: dict[str, Any], synthesis_type: str) -> dict[str, Any]:
        """Process dream data into coherent content."""
        return {
            "narrative": f"Dream synthesis of {len(dream_data.get('elements', []))} dream elements",
            "coherence": 0.8,
            "emotional_tone": "contemplative",
            "symbolic_elements": dream_data.get("symbols", []),
            "synthesis_type": synthesis_type,
        }

    def _generate_emotional_content(self, emotion: str, context: dict[str, Any], output_format: str) -> dict[str, Any]:
        """Generate content with specific emotional resonance."""
        return {
            "content": f"Content resonating with {emotion}",
            "intensity": 0.7,
            "resonance": 0.85,
            "emotional_markers": [emotion, "authentic", "expressive"],
            "format": output_format,
            "context_integration": len(context.keys()),
        }

    def _process_collaboration(
        self,
        project_id: str,
        user_id: str,
        contribution: dict[str, Any],
        collaboration_type: str,
    ) -> dict[str, Any]:
        """Process collaborative creative contribution."""
        return {
            "integration_success": True,
            "harmony": 0.9,
            "contribution_impact": "positive",
            "project_evolution": "enhanced",
            "collaboration_type": collaboration_type,
        }


# Module API functions for easy import
def generate_content(user_id: str, content_type: str, prompt: str, style: Optional[str] = None) -> dict[str, Any]:
    """Simplified API for content generation."""
    service = CreativityService()
    return service.generate_content(user_id, content_type, prompt, style)


def synthesize_dream(user_id: str, dream_data: dict[str, Any]) -> dict[str, Any]:
    """Simplified API for dream synthesis."""
    service = CreativityService()
    return service.synthesize_dream(user_id, dream_data)


def generate_emotional_content(user_id: str, emotion: str, context: dict[str, Any]) -> dict[str, Any]:
    """Simplified API for emotional content generation."""
    service = CreativityService()
    return service.generate_emotional_content(user_id, emotion, context)


if __name__ == "__main__":
    # Example usage
    creativity = CreativityService()

    test_user = "test_lambda_user_001"

    # Test story generation
    story_result = creativity.generate_content(test_user, "story", "A robot learning to dream", "science fiction")
    print(f"Story generation: {story_result.get('success', False)}")

    # Test dream synthesis
    dream_result = creativity.synthesize_dream(
        test_user,
        {"elements": ["flying", "ocean", "music"], "symbols": ["freedom", "depth"]},
    )
    print(f"Dream synthesis: {dream_result.get('success', False)}")

    # Test emotional content
    emotional_result = creativity.generate_emotional_content(
        test_user, "joy", {"occasion": "celebration", "audience": "family"}
    )
    print(f"Emotional content: {emotional_result.get('success', False)}")
