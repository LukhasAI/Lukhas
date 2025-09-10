import logging
from datetime import datetime, timezone
from typing import Optional

from ..data_manager.crud_operations import DataManagerCRUD
from ..diagnostic_engine.engine import DiagnosticEngine
from ..user_interface_manager.text_handler import TextHandler
from ..user_interface_manager.voice_handler import VoiceHandler

logger = logging.getLogger(__name__)


class SymptomReporter:
    """
    Handles the initial symptom reporting interaction with users.
    Combines natural conversation flow with medical precision and safety.

    Design Philosophy:
    - Empathetic yet professional tone (Jobs' focus on user experience)
    - Multiple safety checks and validations (Altman's emphasis on safety)
    - Graceful fallbacks at every step (Jobs' attention to detail)
    - Clear documentation of decision paths (Altman's focus on transparency)
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

        # Core components
        self.voice_handler = VoiceHandler(self.config.get("voice_config"))
        self.text_handler = TextHandler(self.config.get("text_config"))
        self.diagnostic_engine = DiagnosticEngine(self.config.get("diagnostic_config"))
        self.data_manager = DataManagerCRUD(self.config.get("data_config"))

        # Conversation state
        self.max_interaction_turns = self.config.get("max_interaction_turns", 10)
        self.comfort_phrases = [
            "I understand that must be difficult.",
            "I'm here to help you through this.",
            "Thank you for sharing that with me.",
            "Let's work through this together.",
        ]

        logger.info("SymptomReporter initialized and ready for interactions")

    async def start_symptom_reporting(self, user_id: str, mode: str = "voice") -> dict:
        """
        Begins a symptom reporting session with the user.

        Jobs-inspired features:
        - Seamless mode switching if primary mode fails
        - Empathetic responses
        - Clear progression feedback

        Altman-inspired features:
        - Comprehensive logging
        - Safety checks
        - Responsible handling of medical data
        """
        logger.info(f"Starting symptom reporting for user {user_id} in {mode} mode")

        # Initialize session
        session_id = self.data_manager.create_diagnostic_session(user_id, {"status": "active", "mode": mode})
        if not session_id:
            return {"status": "error", "message": "Could not create session"}

        symptoms = []
        interaction_count = 0
        requires_immediate_attention = False

        # Initial greeting (Jobs: make it personal)
        greeting = (
            "Hello! I'm here to help you understand your symptoms. "
            "Please tell me what's bothering you, and take your time."
        )
        await self._communicate(greeting, user_id, mode)

        while interaction_count < self.max_interaction_turns:
            # Get user input
            user_input = await self._get_user_input(mode)
            if not user_input:
                return await self._handle_failed_interaction(session_id)

            # Process response with diagnostic engine
            # SYNTAX_ERROR_FIXED:             is_critical, new_symptoms, needs_media,
            # needs_questions, confidence = " +
            # "self.diagnostic_engine.process_user_response(user_input, symptoms)

            # Critical symptom check (Altman: safety first)
            if is_critical:
                requires_immediate_attention = True
                await self._handle_critical_situation(session_id, symptoms + new_symptoms)
                break

            # Update symptom list
            symptoms.extend(new_symptoms)

            # Request media if needed (Jobs: contextual feature introduction)
            if needs_media:
                media_result = await self._handle_media_request(session_id, mode)
                if media_result.get("status") == "success":
                    await self._communicate(
                        "Thank you for sharing that image. It will help with the assessment.",
                        user_id,
                        mode,
                    )

            # Determine next step
            if confidence >= 0.9 or not needs_questions:
                break

            # Get next question from diagnostic engine
            next_question = self.diagnostic_engine.get_next_question(symptoms, {})
            if next_question:
                # Add empathy if the conversation has gone on (Jobs: emotional
                # connection)
                if interaction_count > 2:
                    next_question = f"{self._get_comfort_phrase()} {next_question}"
                await self._communicate(next_question, user_id, mode)

            interaction_count += 1

            # Update session data (Altman: maintain state)
            self.data_manager.update_diagnostic_session(
                session_id,
                {
                    "symptoms_reported": symptoms,
                    "interaction_count": interaction_count,
                    "last_update": datetime.now(timezone.utc).isoformat(),
                },
            )

        # Session completion
        return await self._complete_session(session_id, symptoms, requires_immediate_attention)

    async def _communicate(self, message: str, user_id: str, mode: str) -> bool:
        """Handles communication in the specified mode with fallback"""
        try:
            if mode == "voice":
                self.voice_handler.speak(message)
            else:
                self.text_handler.send_message(user_id, message)
            return True
        except Exception as e:
            logger.error(f"Communication failed in {mode} mode: {e}")
            # Jobs: graceful fallback
            if mode == "voice":
                try:
                    self.text_handler.send_message(
                        user_id,
                        f"Voice communication failed. Message: {message}",
                    )
                    return True
                except BaseException:
                    pass
            return False

    async def _get_user_input(self, mode: str) -> Optional[str]:
        """Gets user input with error handling and validation"""
        try:
            if mode == "voice":
                return self.voice_handler.listen()
            else:
                return self.text_handler.get_message()
        except Exception as e:
            logger.error(f"Failed to get user input in {mode} mode: {e}")
            return None

    async def _handle_critical_situation(self, session_id: str, symptoms: list):
        """
        Handles detection of critical symptoms requiring immediate attention.
        Altman: Responsible AI principles in medical context
        """
        self.diagnostic_engine.get_critical_alert_message(symptoms)
        self.data_manager.update_diagnostic_session(
            session_id,
            {
                "status": "critical",
                "symptoms_reported": symptoms,
                "requires_immediate_attention": True,
            },
        )
        # In a real system, this would trigger emergency protocols
        logger.warning(f"Critical symptoms detected in session {session_id}")

    async def _handle_failed_interaction(self, session_id: str) -> dict:
        """Gracefully handles failed interactions (Jobs: never leave users stranded)"""
        self.data_manager.update_diagnostic_session(
            session_id,
            {"status": "failed", "end_time": datetime.now(timezone.utc).isoformat()},
        )
        return {
            "status": "error",
            "message": "Unable to complete symptom reporting. Please try again or seek direct medical assistance.",
        }

    def _get_comfort_phrase(self) -> str:
        """Returns a comforting phrase (Jobs: emotional design)"""
        from random import choice

        return choice(self.comfort_phrases)

    async def _complete_session(
        self,
        session_id: str,
        symptoms: list,
        requires_immediate_attention: bool,
    ) -> dict:
        """Completes the session and returns final statu"""
        status = "completed_critical" if requires_immediate_attention else "completed_normal"
        self.data_manager.update_diagnostic_session(
            session_id,
            {
                "status": status,
                "symptoms_reported": symptoms,
                "end_time": datetime.now(timezone.utc).isoformat(),
            },
        )

        return {
            "status": status,
            "session_id": session_id,
            "symptoms": symptoms,
            "requires_immediate_attention": requires_immediate_attention,
        }