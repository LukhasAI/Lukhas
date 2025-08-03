import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DiagnosticEngine:
    """
    Core diagnostic logic engine.
    Altman-inspired focus on safety and responsible AI.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.red_flag_symptoms = {
            "chest pain",
            "difficulty breathing",
            "severe bleeding",
            "unconsciousness",
            "severe head injury"
        }
        logger.info("DiagnosticEngine initialized")

    def process_user_response(
        self,
        user_input: str,
        current_symptoms: List[str]
    ) -> Tuple[bool, List[str], bool, bool, float]:
        """
        Processes user's symptom description.
        Returns: (is_critical, new_symptoms, needs_media, needs_questions, confidence)
        """
        # Simple keyword-based processing for now
        user_input_lower = user_input.lower()

        # Check for critical symptoms (Altman's safety emphasis)
        is_critical = any(
            symptom in user_input_lower
            for symptom in self.red_flag_symptoms
        )

        # Extract symptoms (simplified)
        new_symptoms = [
            word.strip()
            for word in user_input_lower.split()
            if len(word) > 3  # Simple filter for meaningful words
        ]

        # Determine if we need media (e.g., for visual symptoms)
        needs_media = "rash" in user_input_lower or "swelling" in user_input_lower

        # Calculate confidence (simplified)
        confidence = min(0.3 + (len(current_symptoms) + len(new_symptoms)) * 0.1, 0.9)

        # Determine if we need more questions
        needs_questions = confidence < 0.8

        return is_critical, new_symptoms, needs_media, needs_questions, confidence

    def get_next_question(self, symptoms: List[str], user_profile: Dict) -> str:
        """Determines the next question to ask based on reported symptoms"""
        if not symptoms:
            return "What symptoms are you experiencing?"

        # Simple decision tree (would be much more sophisticated in reality)
        if "headache" in symptoms and "fever" not in symptoms:
            return "Do you also have a fever?"
        if "cough" in symptoms and "chest pain" not in symptoms:
            return "Is the cough accompanied by chest pain?"

        return "Could you tell me about any other symptoms you're experiencing?"

    def get_critical_alert_message(self, symptoms: List[str]) -> str:
        """Generates an alert message for critical symptoms"""
        return (
            "Based on your symptoms, you should seek immediate medical attention. "
            "Please call emergency services or go to the nearest emergency room."
        )