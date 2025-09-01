#!/usr/bin/env python3
"""
GPT-5 Healthcare Integration for LUKHAS Healthcare Guardian
Advanced medical AI capabilities for Spanish elderly care
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MedicationSchedule:
    """Medication schedule entry"""

    name: str
    dosage: str
    frequency: str
    times: list[str]
    purpose: str
    warnings: list[str]
    interactions: list[str]
    taken_today: list[bool]


@dataclass
class HealthQuery:
    """Health query with context"""

    query: str
    user_age: int
    medical_history: list[str]
    current_medications: list[str]
    language: str = "andaluz_spanish"
    urgency: str = "normal"  # normal, urgent, emergency


class GPT5HealthcareClient:
    """
    GPT-5 Healthcare Integration Client
    Provides medical AI capabilities with Spanish localization
    """

    def __init__(self, config: dict[str, Any] = None):
        """
        Initialize GPT-5 healthcare client

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.api_key = os.getenv("OPENAI_API_KEY") or self.config.get("api_key")

        # Healthcare-specific settings
        self.medical_config = {
            "model": "gpt-5-healthcare",  # Future GPT-5 healthcare model
            "temperature": 0.3,  # Lower temperature for medical accuracy
            "max_tokens": 500,
            "language": "spanish",
            "dialect": "andalusian",
            "user_profile": "elderly",
            "safety_mode": "maximum",
        }

        # Initialize medication database
        self._init_medication_database()

        # Initialize symptom checker
        self._init_symptom_checker()

        # User context storage
        self.user_context = {}

        logger.info("🤖 GPT-5 Healthcare client initialized")
        logger.info(f"Safety mode: {self.medical_config['safety_mode']}")

    def _init_medication_database(self):
        """Initialize Spanish medication database"""
        self.medications = {
            # Common elderly medications in Spain
            "enalapril": {
                "type": "ACE inhibitor",
                "purpose": "control de la tensión arterial",
                "common_dosage": "5-20mg",
                "side_effects": ["tos seca", "mareo", "cansancio"],
                "interactions": ["potasio", "AINE", "litio"],
                "warnings": ["No tome con alimentos ricos en potasio"],
            },
            "metformina": {
                "type": "antidiabético",
                "purpose": "control del azúcar en sangre",
                "common_dosage": "500-1000mg",
                "side_effects": ["náuseas", "diarrea", "dolor abdominal"],
                "interactions": ["alcohol", "contraste yodado"],
                "warnings": ["Tome con las comidas"],
            },
            "omeprazol": {
                "type": "inhibidor de bomba de protones",
                "purpose": "protección del estómago",
                "common_dosage": "20-40mg",
                "side_effects": ["dolor de cabeza", "náuseas"],
                "interactions": ["clopidogrel", "vitamina B12"],
                "warnings": ["Tome 30 minutos antes del desayuno"],
            },
            "simvastatina": {
                "type": "estatina",
                "purpose": "control del colesterol",
                "common_dosage": "20-40mg",
                "side_effects": ["dolor muscular", "cansancio"],
                "interactions": ["pomelo", "amiodarona"],
                "warnings": ["Tome por la noche"],
            },
            "paracetamol": {
                "type": "analgésico",
                "purpose": "alivio del dolor y fiebre",
                "common_dosage": "500-1000mg",
                "side_effects": ["raros con dosis normales"],
                "interactions": ["warfarina", "alcohol"],
                "warnings": ["Máximo 4g al día"],
            },
        }

    def _init_symptom_checker(self):
        """Initialize symptom checking patterns"""
        self.symptom_patterns = {
            "emergency": {
                "keywords": [
                    "dolor pecho",
                    "no puedo respirar",
                    "mareo fuerte",
                    "confusión",
                    "desmayo",
                    "sangre",
                    "caída",
                ],
                "action": "call_emergency",
                "message": "Síntomas de emergencia detectados. Llamando al 112.",
            },
            "urgent": {
                "keywords": ["fiebre alta", "dolor fuerte", "vómitos", "diarrea severa"],
                "action": "urgent_care",
                "message": "Necesita atención médica pronto. Contacte con su centro de salud.",
            },
            "routine": {
                "keywords": ["dolor leve", "cansancio", "tos", "resfriado"],
                "action": "schedule_appointment",
                "message": "Síntomas leves. Considere pedir cita con su médico.",
            },
        }

    async def process_health_query(self, query: str, user_context: dict = None) -> str:
        """
        Process a health query using GPT-5 healthcare capabilities

        Args:
            query: User's health question in Spanish
            user_context: Optional user medical context

        Returns:
            Medical response in simplified Spanish
        """
        try:
            # Check for emergency keywords first
            urgency = self._assess_urgency(query)
            if urgency == "emergency":
                return await self._handle_emergency_query(query)

            # Prepare context for GPT-5
            context = self._prepare_medical_context(query, user_context)

            # Simulate GPT-5 API call (replace with actual API when available)
            response = await self._call_gpt5_healthcare(context)

            # Simplify medical language for elderly user
            simplified = await self.simplify_medical_language(response)

            # Add safety disclaimers
            simplified = self._add_safety_disclaimers(simplified, urgency)

            return simplified

        except Exception as e:
            logger.error(f"Error processing health query: {e}")
            return "Perdone, no he podido procesar su consulta. Si es urgente, contacte con su médico o llame al 112."

    def _assess_urgency(self, query: str) -> str:
        """
        Assess the urgency level of a health query

        Args:
            query: Health query text

        Returns:
            Urgency level: emergency, urgent, or routine
        """
        query_lower = query.lower()

        # Check emergency patterns
        for keyword in self.symptom_patterns["emergency"]["keywords"]:
            if keyword in query_lower:
                return "emergency"

        # Check urgent patterns
        for keyword in self.symptom_patterns["urgent"]["keywords"]:
            if keyword in query_lower:
                return "urgent"

        return "routine"

    async def _handle_emergency_query(self, query: str) -> str:
        """Handle emergency health queries"""
        return (
            "⚠️ ATENCIÓN: Ha descrito síntomas que pueden ser graves. "
            "Debe llamar al 112 inmediatamente o pedir a alguien que lo haga. "
            "Mientras llega la ayuda:\n"
            "1. Siéntese o acuéstese\n"
            "2. Respire tranquilo\n"
            "3. No tome medicinas sin indicación médica\n"
            "4. Tenga su lista de medicamentos a mano"
        )

    def _prepare_medical_context(self, query: str, user_context: dict = None) -> dict:
        """Prepare context for GPT-5 medical query"""
        context = {
            "query": query,
            "language": "Spanish (Andalusian dialect)",
            "user_profile": "elderly (65+ years)",
            "safety_level": "maximum",
            "response_style": "simple, caring, non-technical",
            "medical_context": user_context or {},
            "timestamp": datetime.now().isoformat(),
        }

        # Add user's medication list if available
        if user_context and "medications" in user_context:
            context["current_medications"] = user_context["medications"]

        # Add medical history if available
        if user_context and "conditions" in user_context:
            context["medical_conditions"] = user_context["conditions"]

        return context

    async def _call_gpt5_healthcare(self, context: dict) -> str:
        """
        Call GPT-5 Healthcare API (simulated for now)

        In production, this would make actual API calls to GPT-5
        """
        # Simulate GPT-5 response based on context
        query = context["query"].lower()

        # Simulated responses for common queries
        if "dolor cabeza" in query:
            return (
                "El dolor de cabeza puede tener muchas causas. "
                "Asegúrese de estar bien hidratado y haber descansado. "
                "Si toma paracetamol, no exceda 1 gramo cada 8 horas. "
                "Si el dolor es muy fuerte, repentino o con otros síntomas, "
                "contacte con su médico."
            )
        elif "presión alta" in query or "tensión alta" in query:
            return (
                "La presión alta es importante controlarla. "
                "Tome su medicación como le indicó el médico. "
                "Reduzca la sal en las comidas, manténgase activo, "
                "y mida su tensión regularmente. "
                "Si tiene mareos o dolor de pecho, busque atención médica."
            )
        elif "diabetes" in query or "azúcar" in query:
            return (
                "Para controlar el azúcar en sangre: "
                "Tome su medicación regularmente, siga la dieta recomendada, "
                "haga ejercicio suave como caminar, y mida su azúcar según indicado. "
                "Si se siente muy mal, sudoroso o confuso, puede ser una bajada de azúcar."
            )
        else:
            return (
                "Entiendo su consulta sobre salud. "
                "Le recomiendo hablar con su médico para un consejo personalizado. "
                "Mientras tanto, mantenga sus medicamentos al día y "
                "siga las indicaciones médicas que ya tiene."
            )

    async def simplify_medical_language(self, text: str) -> str:
        """
        Simplify medical language for elderly understanding

        Args:
            text: Medical text to simplify

        Returns:
            Simplified text in Andalusian Spanish
        """
        # Medical term replacements
        replacements = {
            "hipertensión": "tensión alta",
            "hipotensión": "tensión baja",
            "diabetes mellitus": "el azúcar",
            "insuficiencia cardíaca": "el corazón débil",
            "arritmia": "latidos irregulares",
            "medicamento": "medicina",
            "efectos adversos": "cosas malas que puede causar",
            "contraindicaciones": "cuando no se debe tomar",
            "interacciones": "problemas con otras medicinas",
            "dosis": "cantidad",
            "administrar": "tomar",
            "vía oral": "por la boca",
            "en ayunas": "sin haber comido",
            "síntomas": "lo que siente",
            "diagnóstico": "lo que tiene",
            "pronóstico": "cómo va a evolucionar",
            "patología": "enfermedad",
            "crónico": "para siempre",
            "agudo": "de repente",
        }

        simplified = text
        for medical, simple in replacements.items():
            simplified = simplified.replace(medical, simple)

        # Make sentences shorter and clearer
        sentences = simplified.split(".")
        short_sentences = []
        for sentence in sentences:
            if len(sentence) > 100:  # Long sentence
                # Try to break it down
                parts = sentence.split(",")
                for part in parts:
                    if part.strip():
                        short_sentences.append(part.strip() + ".")
            else:
                if sentence.strip():
                    short_sentences.append(sentence.strip() + ".")

        return " ".join(short_sentences)

    def _add_safety_disclaimers(self, response: str, urgency: str) -> str:
        """Add appropriate safety disclaimers"""
        disclaimers = {
            "emergency": ("\n\n⚠️ IMPORTANTE: Si es una emergencia, llame al 112 ahora."),
            "urgent": ("\n\n📞 Recomendación: Contacte con su centro de salud hoy."),
            "routine": ("\n\n💡 Consejo: Hable con su médico en la próxima cita."),
        }

        disclaimer = disclaimers.get(urgency, "")
        return response + disclaimer

    async def check_drug_interactions(self, medications: list[str]) -> dict[str, Any]:
        """
        Check for drug interactions between medications

        Args:
            medications: List of medication names

        Returns:
            Dictionary with interaction information
        """
        interactions = {"safe": [], "caution": [], "dangerous": [], "recommendations": []}

        # Check each pair of medications
        for i, med1 in enumerate(medications):
            for med2 in medications[i + 1 :]:
                interaction = self._check_interaction_pair(med1, med2)
                if interaction:
                    interactions[interaction["severity"]].append(
                        {
                            "medications": [med1, med2],
                            "description": interaction["description"],
                            "action": interaction["action"],
                        }
                    )

        # Add general recommendations
        if interactions["dangerous"]:
            interactions["recommendations"].append(
                "⚠️ Hay interacciones peligrosas. Consulte con su médico urgentemente."
            )
        elif interactions["caution"]:
            interactions["recommendations"].append("⚡ Hay algunas interacciones. Coméntelo con su médico.")
        else:
            interactions["recommendations"].append("✅ No hay interacciones peligrosas conocidas.")

        return interactions

    def _check_interaction_pair(self, med1: str, med2: str) -> Optional[dict]:
        """Check interaction between two medications"""
        # Known dangerous interactions
        dangerous_pairs = {
            ("warfarina", "aspirina"): "Riesgo de sangrado",
            ("metformina", "alcohol"): "Riesgo de acidosis láctica",
            ("simvastatina", "amiodarona"): "Riesgo de daño muscular",
        }

        # Known caution interactions
        caution_pairs = {
            ("enalapril", "ibuprofeno"): "Puede reducir efecto antihipertensivo",
            ("omeprazol", "clopidogrel"): "Puede reducir efecto antiagregante",
            ("metformina", "furosemida"): "Vigilar función renal",
        }

        # Check dangerous interactions
        for pair, description in dangerous_pairs.items():
            if med1.lower() in pair and med2.lower() in pair:
                return {
                    "severity": "dangerous",
                    "description": description,
                    "action": "Contacte con su médico inmediatamente",
                }

        # Check caution interactions
        for pair, description in caution_pairs.items():
            if med1.lower() in pair and med2.lower() in pair:
                return {
                    "severity": "caution",
                    "description": description,
                    "action": "Coméntelo en su próxima cita",
                }

        return None

    async def get_medication_schedule(self, user_id: str = None) -> str:
        """
        Get user's medication schedule

        Args:
            user_id: User identifier

        Returns:
            Formatted schedule in Spanish
        """
        # Example schedule (would be loaded from database)
        schedule = [
            MedicationSchedule(
                name="Enalapril",
                dosage="10mg",
                frequency="1 vez al día",
                times=["08:00"],
                purpose="para la tensión",
                warnings=["No tome con mucho potasio"],
                interactions=[],
                taken_today=[False],
            ),
            MedicationSchedule(
                name="Metformina",
                dosage="500mg",
                frequency="2 veces al día",
                times=["08:00", "20:00"],
                purpose="para el azúcar",
                warnings=["Tome con las comidas"],
                interactions=[],
                taken_today=[False, False],
            ),
            MedicationSchedule(
                name="Omeprazol",
                dosage="20mg",
                frequency="1 vez al día",
                times=["07:30"],
                purpose="para el estómago",
                warnings=["Media hora antes del desayuno"],
                interactions=[],
                taken_today=[False],
            ),
        ]

        # Format schedule for voice output
        current_hour = datetime.now().hour

        if current_hour < 12 or current_hour < 20:
            pass
        else:
            pass

        # Find next medication
        next_med = None
        for med in schedule:
            for time_str in med.times:
                hour = int(time_str.split(":")[0])
                if hour > current_hour:
                    next_med = (med, time_str)
                    break
            if next_med:
                break

        if next_med:
            med, time = next_med
            return (
                f"Su próxima medicina es {med.name} a las {time}. "
                f"Es {med.purpose}. {med.warnings[0] if med.warnings else ''}"
            )
        else:
            return "Ya ha tomado todas las medicinas de hoy. Muy bien hecho."

    async def explain_medication(self, query: str) -> str:
        """
        Explain a medication in simple terms

        Args:
            query: Query about medication

        Returns:
            Simple explanation in Spanish
        """
        # Extract medication name from query
        med_name = None
        for med in self.medications:
            if med in query.lower():
                med_name = med
                break

        if not med_name:
            return "No he reconocido el nombre de la medicina. ¿Puede decirme cómo se llama exactamente?"

        med_info = self.medications[med_name]

        explanation = f"{med_name.capitalize()} es una medicina {med_info['purpose']}. "
        explanation += f"Normalmente se toma {med_info['common_dosage']}. "

        if med_info["warnings"]:
            explanation += f"Recuerde: {med_info['warnings'][0]}. "

        if med_info["side_effects"]:
            explanation += f"Puede causar {', '.join(med_info['side_effects'][:2])}, pero no siempre pasa. "

        explanation += "Si tiene dudas, pregunte a su médico o farmacéutico."

        return explanation

    async def generate_health_advice(self, condition: str) -> str:
        """
        Generate health advice for a condition

        Args:
            condition: Health condition

        Returns:
            Personalized advice in Spanish
        """
        advice_templates = {
            "hipertensión": (
                "Para controlar la tensión alta:\n"
                "1. Tome su medicina todos los días\n"
                "2. Reduzca la sal en las comidas\n"
                "3. Camine 30 minutos al día si puede\n"
                "4. Mida su tensión regularmente\n"
                "5. No fume y limite el alcohol"
            ),
            "diabetes": (
                "Para controlar el azúcar:\n"
                "1. Tome su medicina como le indicaron\n"
                "2. Coma a horas regulares\n"
                "3. Evite dulces y refrescos\n"
                "4. Haga ejercicio suave\n"
                "5. Revise sus pies cada día"
            ),
            "artritis": (
                "Para mejorar con la artritis:\n"
                "1. Manténgase activo con ejercicio suave\n"
                "2. Aplique calor o frío según le alivie\n"
                "3. Mantenga un peso saludable\n"
                "4. Use ayudas si las necesita\n"
                "5. Tome su medicina para el dolor"
            ),
        }

        advice = advice_templates.get(
            condition.lower(),
            "Siga las recomendaciones de su médico y mantenga hábitos saludables.",
        )

        return advice + "\n\nRecuerde: Estos son consejos generales. Siempre siga las indicaciones de su médico."
