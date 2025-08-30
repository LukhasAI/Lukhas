#!/usr/bin/env python3
"""
Andaluz Voice Engine for Healthcare Guardian
Specialized voice processing for elderly Andalusian Spanish speakers
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AndaluzPhonetics:
    """Andalusian Spanish phonetic patterns"""

    # Seseo: s/c/z all pronounced as 's'
    seseo_replacements = {
        "gracias": "grasia",
        "hacer": "haser",
        "medicina": "medisina",
        "corazón": "corasón",
    }

    # Aspiration of final consonants
    aspiration_patterns = {"los ": "loh ", "más ": "mah ", "después": "dehpué"}

    # Common Andalusian expressions
    expressions = {
        "greeting": ["mi niño", "mi niña", "mi arma"],
        "concern": ["¿qué le pasa?", "¿está malito?"],
        "comfort": ["no se preocupe", "tranquilo", "ya verá como se mejora"],
    }


class AndaluzVoiceEngine:
    """
    Voice engine specialized for Andalusian elderly users
    Handles dialect recognition and synthesis with medical context
    """

    def __init__(self, config: dict[str, Any] = None, consciousness=None):
        """
        Initialize Andaluz voice engine

        Args:
            config: Voice configuration
            consciousness: Optional LUKHAS consciousness integration
        """
        self.config = config or {}
        self.consciousness = consciousness
        self.phonetics = AndaluzPhonetics()

        # Voice settings for elderly users
        self.voice_settings = {
            "speed": self.config.get("speed", "slow"),  # Slower for elderly
            "pitch": self.config.get("pitch", "medium"),
            "volume": self.config.get("volume", "loud"),
            "clarity": self.config.get("clarity", "high"),
            "elder_mode": self.config.get("elder_mode", True),
        }

        # Medical vocabulary in simplified Andalusian Spanish
        self._load_medical_vocabulary()

        # Initialize voice components
        self._init_voice_components()

        logger.info("🗣️ Andaluz voice engine initialized")
        logger.info(f"Elder mode: {self.voice_settings['elder_mode']}")

    def _load_medical_vocabulary(self):
        """Load medical vocabulary with Andalusian adaptations"""
        vocab_path = Path(__file__).parent / "medical_vocabulary.json"

        # Default medical vocabulary
        self.medical_vocab = {
            # Medical terms -> Simple Andalusian
            "hipertensión": "tensión alta",
            "diabetes": "el azúcar",
            "medicamento": "medicina",
            "prescripción": "receta",
            "síntomas": "lo que siente",
            "diagnóstico": "lo que tiene",
            "tratamiento": "lo que hay que hacer",
            "efectos secundarios": "lo malo de la medicina",
            "contraindicaciones": "cuando no se puede tomar",
            "posología": "cuántas pastillas y cuándo",
            # Body parts in familiar terms
            "cardiovascular": "del corazón",
            "respiratorio": "de los pulmones",
            "gastrointestinal": "del estómago",
            "neurológico": "de la cabeza",
            # Common medications
            "enalapril": "la pastilla del corazón",
            "metformina": "la pastilla del azúcar",
            "omeprazol": "la pastilla del estómago",
            "paracetamol": "la pastilla del dolor",
            "ibuprofeno": "la pastilla de la inflamación",
        }

        # Load custom vocabulary if exists
        if vocab_path.exists():
            try:
                with open(vocab_path, encoding="utf-8") as f:
                    custom_vocab = json.load(f)
                    self.medical_vocab.update(custom_vocab)
            except Exception as e:
                logger.warning(f"Could not load custom vocabulary: {e}")

    def _init_voice_components(self):
        """Initialize STT and TTS components"""
        try:
            # Import voice libraries
            import pygame
            import speech_recognition as sr
            from gtts import gTTS

            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # Adjust for elderly speech patterns
            if self.voice_settings["elder_mode"]:
                self.recognizer.pause_threshold = 1.5  # Longer pauses
                self.recognizer.energy_threshold = 300  # Lower voice energy

            # Initialize audio player
            pygame.mixer.init()

            self.voice_ready = True
            logger.info("Voice components initialized successfully")

        except ImportError as e:
            logger.warning(f"Voice libraries not installed: {e}")
            logger.warning("Install with: pip install SpeechRecognition gtts pygame")
            self.voice_ready = False
        except Exception as e:
            logger.error(f"Error initializing voice components: {e}")
            self.voice_ready = False

    async def listen(self) -> Optional[str]:
        """
        Listen for voice input from the user

        Returns:
            Recognized text in Andalusian Spanish or None
        """
        if not self.voice_ready:
            logger.warning("Voice components not ready")
            return None

        try:
            import speech_recognition as sr

            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

                # Provide audio feedback that we're listening
                logger.info("Listening for Andalusian Spanish...")

                # Listen with extended timeout for elderly users
                audio = self.recognizer.listen(
                    source,
                    timeout=5,  # Wait up to 5 seconds
                    phrase_time_limit=10,  # Allow up to 10 seconds of speech
                )

            # Recognize speech using Google (supports Spanish)
            text = self.recognizer.recognize_google(
                audio,
                language="es-ES",  # Spanish (Spain)
            )

            # Apply Andalusian dialect processing
            text = self._process_andaluz_input(text)

            logger.info(f"Recognized: {text}")
            return text

        except sr.WaitTimeoutError:
            logger.debug("No speech detected - timeout")
            return None
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None

    async def speak(self, text: str, emotion: str = "neutral"):
        """
        Speak text in Andalusian Spanish with appropriate emotion

        Args:
            text: Text to speak
            emotion: Emotional tone (neutral, caring, urgent, happy)
        """
        if not self.voice_ready:
            # Fallback to console output
            print(f"🗣️ LUKHAS dice: {text}")
            return

        try:
            import os
            import tempfile

            import pygame
            from gtts import gTTS

            # Apply Andalusian dialect to output
            andaluz_text = self._apply_andaluz_dialect(text)

            # Add emotional markers if integrated with consciousness
            if self.consciousness and emotion != "neutral":
                andaluz_text = self._add_emotional_context(andaluz_text, emotion)

            # Create TTS with Spanish voice
            tts = gTTS(text=andaluz_text, lang="es", slow=self.voice_settings["speed"] == "slow")

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                temp_file = f.name
                tts.save(temp_file)

            # Play the audio
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.set_volume(1.0 if self.voice_settings["volume"] == "loud" else 0.7)
            pygame.mixer.music.play()

            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)

            # Clean up temp file
            os.unlink(temp_file)

            logger.debug(f"Spoke: {andaluz_text}")

        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            print(f"🗣️ LUKHAS dice: {text}")

    def _process_andaluz_input(self, text: str) -> str:
        """
        Process recognized text for Andalusian dialect patterns

        Args:
            text: Raw recognized text

        Returns:
            Processed text normalized from Andalusian
        """
        if not text:
            return ""

        text = text.lower()

        # Reverse common Andalusian phonetic changes for better understanding
        # Convert seseo back to standard Spanish
        reverse_seseo = {
            "grasia": "gracias",
            "haser": "hacer",
            "medisina": "medicina",
            "corasón": "corazón",
        }

        for andaluz, standard in reverse_seseo.items():
            text = text.replace(andaluz, standard)

        # Handle aspirated consonants
        text = re.sub(r"loh\s", "los ", text)
        text = re.sub(r"mah\s", "más ", text)
        text = re.sub(r"dehpué", "después", text)

        return text.strip()

    def _apply_andaluz_dialect(self, text: str) -> str:
        """
        Apply Andalusian dialect to output text

        Args:
            text: Standard Spanish text

        Returns:
            Text with Andalusian dialect applied
        """
        # Apply seseo
        for standard, andaluz in self.phonetics.seseo_replacements.items():
            text = text.replace(standard, andaluz)

        # Apply aspiration
        for standard, andaluz in self.phonetics.aspiration_patterns.items():
            text = text.replace(standard, andaluz)

        # Add warm Andalusian expressions
        if text.startswith("Buenos días"):
            text = text.replace("Buenos días", "Buenos días, mi niño")

        return text

    def _add_emotional_context(self, text: str, emotion: str) -> str:
        """
        Add emotional context to the speech

        Args:
            text: Text to speak
            emotion: Emotional tone

        Returns:
            Text with emotional markers
        """
        emotional_prefixes = {
            "caring": "Con cariño, ",
            "urgent": "¡Importante! ",
            "happy": "¡Qué bien! ",
            "concerned": "Me preocupa que ",
        }

        emotional_suffixes = {
            "caring": ", mi niño.",
            "urgent": " ¡Es urgente!",
            "happy": " ¡Qué alegría!",
            "concerned": ". ¿Está usted bien?",
        }

        prefix = emotional_prefixes.get(emotion, "")
        suffix = emotional_suffixes.get(emotion, "")

        # Add prefix/suffix if not already present
        if prefix and not text.startswith(prefix):
            text = prefix + text
        if suffix and not text.endswith(suffix):
            text = text + suffix

        return text

    def simplify_medical_term(self, term: str) -> str:
        """
        Convert medical term to simple Andalusian Spanish

        Args:
            term: Medical term

        Returns:
            Simplified term for elderly understanding
        """
        # Direct vocabulary lookup
        simplified = self.medical_vocab.get(term.lower(), term)

        # Further simplification patterns
        if "itis" in simplified:  # Inflammation conditions
            simplified = simplified.replace("itis", " inflamado")
        if "hiper" in simplified:  # Hyper conditions
            simplified = simplified.replace("hiper", "muy alto el ")
        if "hipo" in simplified:  # Hypo conditions
            simplified = simplified.replace("hipo", "muy bajo el ")

        return simplified

    async def explain_medication(self, medication_name: str) -> str:
        """
        Explain medication in simple Andalusian terms

        Args:
            medication_name: Name of the medication

        Returns:
            Simple explanation
        """
        # Look up simplified name
        simple_name = self.medical_vocab.get(medication_name.lower(), medication_name)

        # Create explanation
        explanation = f"Esa es {simple_name}. "

        # Add purpose based on medication type
        medication_purposes = {
            "enalapril": "Es para que el corazón funcione mejor y no suba la tensión.",
            "metformina": "Es para controlar el azúcar en la sangre.",
            "omeprazol": "Es para proteger el estómago y que no le duela.",
            "paracetamol": "Es para quitar el dolor y la fiebre.",
            "ibuprofeno": "Es para el dolor y la inflamación.",
        }

        purpose = medication_purposes.get(
            medication_name.lower(), "Es una medicina importante para su salud."
        )

        explanation += purpose
        explanation += " Tómela como le dijo el médico."

        return explanation

    def create_voice_reminder(self, medication: str, time: str) -> str:
        """
        Create a medication reminder in Andalusian Spanish

        Args:
            medication: Medication name
            time: Time to take medication

        Returns:
            Reminder message
        """
        simple_med = self.simplify_medical_term(medication)

        reminders = [
            f"Mi niño, son las {time}. Es hora de tomar {simple_med}.",
            f"No se olvide, ahora toca {simple_med}.",
            f"Venga, que es la hora de la medicina. {simple_med} le toca ahora.",
        ]

        # Select reminder based on time of day
        import random

        reminder = random.choice(reminders)

        # Add caring suffix
        reminder += " ¿La tiene a mano o necesita ayuda?"

        return reminder


class AndaluzMedicalPhrases:
    """Common medical phrases in Andalusian Spanish"""

    GREETINGS = {
        "morning": "Buenos días, mi niño. ¿Cómo ha amanecido hoy?",
        "afternoon": "Buenas tardes, mi alma. ¿Qué tal se encuentra?",
        "evening": "Buenas noches, mi niño. ¿Cómo ha pasado el día?",
        "check_in": "¿Cómo está usted? ¿Se encuentra bien?",
    }

    MEDICATION = {
        "reminder": "Es hora de su medicina, mi niño.",
        "taken": "Muy bien, ya ha tomado su medicina.",
        "missed": "Ay, se le ha pasado la medicina. Tómela ahora.",
        "question": "¿Ha tomado ya su medicina?",
        "explain": "Esta medicina es para {purpose}. Es importante tomarla.",
    }

    EMERGENCY = {
        "assess": "¿Qué le pasa? ¿Dónde le duele?",
        "calm": "Tranquilo, tranquilo. Ya viene la ayuda.",
        "calling": "Estoy llamando al 112. No se preocupe.",
        "family": "Voy a avisar a su familia también.",
        "stay": "Quédese sentado y respire tranquilo.",
    }

    APPOINTMENTS = {
        "next": "Su próxima cita es {date} a las {time}.",
        "reminder": "Mañana tiene cita con el médico.",
        "booking": "Voy a buscarle una cita. ¿Cuándo le viene bien?",
        "confirmed": "Ya tiene la cita confirmada.",
        "cancelled": "La cita se ha cancelado. ¿Quiere otra?",
    }

    COMFORT = {
        "dont_worry": "No se preocupe, todo va a salir bien.",
        "im_here": "Estoy aquí para ayudarle.",
        "take_time": "Tómese su tiempo, no hay prisa.",
        "well_done": "Muy bien, lo está haciendo fenomenal.",
        "rest": "Descanse un poquito, se lo merece.",
    }
