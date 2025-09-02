#!/usr/bin/env python3
"""
LUKHAS Healthcare Guardian - Main Entry Point
Spanish Eldercare AI System with Andalusian Voice Support
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for LUKHAS imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import healthcare guardian components
try:
    from .emergency_systems.emergency_handler import EmergencyResponseSystem
    from .medical_ai.gpt5_integration import GPT5HealthcareClient
    from .sas_integration.sas_connector import SASHealthcareConnector
    from .vision_systems.medication_ocr import MedicationOCRSystem
    from .voice_andaluz.voice_engine import AndaluzVoiceEngine
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from emergency_systems.emergency_handler import EmergencyResponseSystem
    from medical_ai.gpt5_integration import GPT5HealthcareClient
    from sas_integration.sas_connector import SASHealthcareConnector
    from vision_systems.medication_ocr import MedicationOCRSystem
    from voice_andaluz.voice_engine import AndaluzVoiceEngine

# Try to import lukhas_components (will be available when integrated)
try:
    from lukhas.consciousness import ConsciousnessEngine
    from lukhas.guardian import GuardianSystem
    from lukhas.identity import IdentityManager

    LUKHAS_AVAILABLE = True
except ImportError:
    logger.warning("LUKHAS core components not found. Running in standalone mode.")
    LUKHAS_AVAILABLE = False


class HealthcareGuardian:
    """
    Main Healthcare Guardian System for Spanish Elders
    Integrates with LUKHAS Trinity Framework when available
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Healthcare Guardian system

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.components = {}

        # Initialize Trinity Framework if available
        if LUKHAS_AVAILABLE:
            self._init_lukhas_integration()

        # Initialize healthcare components
        self._init_healthcare_components()

        logger.info("🏥 Healthcare Guardian initialized successfully")
        logger.info("🗣️ Andalusian voice support: ENABLED")
        logger.info("🚨 Emergency response: READY")
        logger.info("💊 Medication management: ACTIVE")

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load configuration from file or use defaults"""
        import yaml

        if not config_path:
            config_path = Path(__file__).parent / "config" / "healthcare_config.yaml"

        if Path(config_path).exists():
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration
            return {
                "language": "andaluz_spanish",
                "voice": {"enabled": True, "speed": "slow", "elder_mode": True},
                "medical": {"gpt5_enabled": True, "local_fallback": True},
                "emergency": {"number": "112", "auto_dispatch": False},
                "sas": {"enabled": True, "region": "andalucia"},
            }

    def _init_lukhas_integration(self):
        """Initialize LUKHAS Trinity Framework integration"""
        try:
            # ⚛️ Identity Layer
            self.identity = IdentityManager()
            logger.info("⚛️ LUKHAS Identity layer connected")

            # 🧠 Consciousness Layer
            self.consciousness = ConsciousnessEngine()
            logger.info("🧠 LUKHAS Consciousness layer connected")

            # 🛡️ Guardian Layer
            self.guardian = GuardianSystem()
            logger.info("🛡️ LUKHAS Guardian layer connected")

            self.lukhas_integrated = True
        except Exception as e:
            logger.warning(f"Could not fully integrate LUKHAS: {e}")
            self.lukhas_integrated = False

    def _init_healthcare_components(self):
        """Initialize healthcare-specific components"""

        # Voice Engine for Andalusian Spanish
        self.components["voice"] = AndaluzVoiceEngine(
            config=self.config.get("voice", {}), consciousness=getattr(self, "consciousness", None)
        )
        logger.info("🗣️ Andaluz voice engine initialized")

        # GPT-5 Healthcare Integration
        self.components["medical_ai"] = GPT5HealthcareClient(config=self.config.get("medical", {}))
        logger.info("🤖 GPT-5 healthcare AI connected")

        # SAS Healthcare System Integration
        if self.config.get("sas", {}).get("enabled"):
            self.components["sas"] = SASHealthcareConnector(config=self.config.get("sas", {}))
            logger.info("🏥 SAS healthcare system connected")

        # Emergency Response System
        self.components["emergency"] = EmergencyResponseSystem(
            config=self.config.get("emergency", {}), guardian=getattr(self, "guardian", None)
        )
        logger.info("🚨 Emergency response system ready")

        # Medication OCR System
        self.components["vision"] = MedicationOCRSystem(config=self.config.get("vision", {}))
        logger.info("📸 Medication OCR system initialized")

    async def start(self):
        """Start the Healthcare Guardian system"""
        logger.info("Starting Healthcare Guardian...")

        # Start voice interaction loop
        if self.config.get("voice", {}).get("enabled"):
            await self.start_voice_assistant()
        else:
            await self.start_text_interface()

    async def start_voice_assistant(self):
        """Start the voice-based assistant for elderly users"""
        voice_engine = self.components["voice"]

        # Initial greeting in Andaluz Spanish
        greeting = (
            "Buenos días, mi niño. Soy LUKHAS, su compañero de salud. "
            "Estoy aquí para ayudarle con sus medicinas y su salud. "
            "¿Cómo se encuentra hoy?"
        )

        await voice_engine.speak(greeting)
        logger.info("Voice assistant started - listening for commands...")

        while True:
            try:
                # Listen for voice command
                command = await voice_engine.listen()

                if command:
                    # Process command with consciousness integration if available
                    response = await self.process_command(command)

                    # Speak response
                    await voice_engine.speak(response)

                # Check for emergency conditions
                if await self._check_emergency_conditions():
                    await self.handle_emergency()

            except KeyboardInterrupt:
                farewell = "Hasta luego, que tenga un buen día. Cuídese mucho."
                await voice_engine.speak(farewell)
                break
            except Exception as e:
                logger.error(f"Error in voice assistant: {e}")
                error_message = "Perdone, no le he entendido bien. ¿Puede repetir?"
                await voice_engine.speak(error_message)

    async def start_text_interface(self):
        """Fallback text interface for testing"""
        print("🏥 Healthcare Guardian - Text Interface")
        print("Type 'help' for commands or 'exit' to quit")

        while True:
            try:
                command = input("\n> ").strip()

                if command.lower() == "exit":
                    break
                elif command.lower() == "help":
                    self.print_help()
                else:
                    response = await self.process_command(command)
                    print(f"\n{response}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                print("Error processing command. Please try again.")

    async def process_command(self, command: str) -> str:
        """
        Process user command and return response

        Args:
            command: User's voice or text command

        Returns:
            Response string in appropriate language
        """
        command_lower = command.lower()

        # Emergency detection
        if any(word in command_lower for word in ["socorro", "ayuda", "emergencia", "dolor"]):
            return await self.handle_emergency_command(command)

        # Medication queries
        elif any(word in command_lower for word in ["medicina", "pastilla", "medicamento"]):
            return await self.handle_medication_query(command)

        # Appointment queries
        elif any(word in command_lower for word in ["cita", "médico", "doctor"]):
            return await self.handle_appointment_query(command)

        # Health questions
        else:
            return await self.handle_health_query(command)

    async def handle_emergency_command(self, command: str) -> str:
        """Handle emergency-related commands"""
        emergency_system = self.components["emergency"]

        # Analyze severity
        severity = await emergency_system.assess_severity(command)

        if severity == "critical":
            await emergency_system.dispatch_emergency()
            return (
                "He detectado una emergencia. Estoy llamando al 112 ahora mismo. "
                "Manténgase tranquilo, la ayuda está en camino."
            )
        else:
            return "Entiendo que necesita ayuda. ¿Es una emergencia médica? Diga 'sí' si necesita que llame al 112."

    async def handle_medication_query(self, command: str) -> str:
        """Handle medication-related queries"""
        medical_ai = self.components["medical_ai"]

        # Check medication schedule
        if "hora" in command.lower() or "cuándo" in command.lower():
            schedule = await medical_ai.get_medication_schedule()
            return f"Su próxima medicina es {schedule}"

        # Check medication information
        elif "para qué" in command.lower():
            info = await medical_ai.explain_medication(command)
            return info

        else:
            return (
                "¿Qué necesita saber sobre sus medicinas? "
                "Puedo recordarle cuándo tomarlas o explicarle para qué sirven."
            )

    async def handle_appointment_query(self, command: str) -> str:
        """Handle appointment-related queries"""
        if "sas" in self.components:
            sas_connector = self.components["sas"]

            if "próxima" in command.lower() or "cuándo" in command.lower():
                appointment = await sas_connector.get_next_appointment()
                if appointment:
                    return f"Su próxima cita es {appointment}"
                else:
                    return "No tiene citas programadas próximamente."

            elif "pedir" in command.lower() or "nueva" in command.lower():
                return "Voy a buscar citas disponibles para usted. ¿Prefiere por la mañana o por la tarde?"

        return "El sistema de citas no está disponible en este momento."

    async def handle_health_query(self, command: str) -> str:
        """Handle general health queries using GPT-5"""
        medical_ai = self.components["medical_ai"]

        # Get response from GPT-5 healthcare
        response = await medical_ai.process_health_query(command)

        # Simplify medical terminology for elderly user
        simplified = await medical_ai.simplify_medical_language(response)

        return simplified

    async def _check_emergency_conditions(self) -> bool:
        """Check for automatic emergency conditions"""
        # This would integrate with sensors, fall detection, etc.
        return False

    async def handle_emergency(self):
        """Handle detected emergency"""
        emergency_system = self.components["emergency"]
        await emergency_system.activate_emergency_protocol()

    def print_help(self):
        """Print help information"""
        help_text = """
        🏥 Healthcare Guardian Commands:

        MEDICATION:
        - "¿Qué medicina me toca?" - Check medication schedule
        - "¿Para qué es esta pastilla?" - Medication information

        APPOINTMENTS:
        - "¿Cuándo tengo cita?" - Check appointments
        - "Quiero pedir cita" - Book new appointment

        EMERGENCY:
        - "Socorro" / "Ayuda" - Emergency assistance
        - "Me duele..." - Report symptoms

        GENERAL:
        - "help" - Show this help
        - "exit" - Exit the program
        """
        print(help_text)


async def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     🏥 LUKHAS Healthcare Guardian                    ║
    ║     Sistema de Salud para Mayores Andaluces         ║
    ║     ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian      ║
    ╚══════════════════════════════════════════════════════╝
    """)

    # Create and start the guardian
    guardian = HealthcareGuardian()
    await guardian.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Hasta luego, cuídese mucho!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more information.")
