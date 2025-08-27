#!/usr/bin/env python3
"""
Emergency Response System for Healthcare Guardian
Handles medical emergencies, fall detection, and automatic dispatch for elderly users
Consolidated from Enhanced Guardian Medical emergency_aid.py
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Types of emergencies - from original Guardian system"""
    MEDICAL = "medical"
    FALL = "fall"
    PSYCHOLOGICAL = "psychological"
    SECURITY = "security"
    FIRE = "fire"
    UNKNOWN = "unknown"


class EmergencySeverity(Enum):
    """Emergency severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    LIFE_THREATENING = 5


@dataclass
class EmergencyContact:
    """Emergency contact information"""
    name: str
    phone: str
    relationship: str
    priority: int
    languages: list[str]
    notify_automatically: bool


@dataclass
class EmergencyIncident:
    """Emergency incident record"""
    incident_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    timestamp: datetime
    location: Optional[tuple[float, float]]  # GPS coordinates
    location_address: Optional[str]
    description: str
    symptoms: list[str]
    user_vitals: Optional[dict]
    actions_taken: list[str]
    contacts_notified: list[str]
    response_time: Optional[float]
    status: str  # active, resolved, dispatched


class EmergencyResponseSystem:
    """
    Emergency Response System specialized for elderly Spanish users
    Integrates with 112 emergency services and family notification
    """

    # Emergency keywords in Spanish/Andalusian
    EMERGENCY_KEYWORDS = {
        EmergencyType.MEDICAL: [
            "dolor pecho", "no puedo respirar", "mareo", "desmayo",
            "infarto", "corazón", "sangre", "caída", "golpe cabeza",
            "no me encuentro bien", "me duele mucho", "ayuda"
        ],
        EmergencyType.FALL: [
            "me he caído", "me caí", "no puedo levantarme",
            "estoy en el suelo", "tropezado", "resbalado"
        ],
        EmergencyType.PSYCHOLOGICAL: [
            "ansiedad", "pánico", "confundido", "no sé dónde estoy",
            "tengo miedo", "estoy solo", "deprimido"
        ],
        EmergencyType.SECURITY: [
            "alguien en casa", "ruido", "ladrón", "puerta abierta"
        ]
    }

    # Emergency phrases for different severities
    EMERGENCY_RESPONSES = {
        EmergencySeverity.LIFE_THREATENING: {
            "message": "🚨 EMERGENCIA CRÍTICA DETECTADA",
            "voice": "Emergencia detectada. Llamando al 112 inmediatamente. Manténgase tranquilo.",
            "action": "dispatch_immediate"
        },
        EmergencySeverity.CRITICAL: {
            "message": "⚠️ SITUACIÓN CRÍTICA",
            "voice": "Necesita ayuda urgente. Voy a llamar a emergencias. ¿Está consciente?",
            "action": "dispatch_urgent"
        },
        EmergencySeverity.HIGH: {
            "message": "⚡ ATENCIÓN NECESARIA",
            "voice": "Parece que necesita ayuda. ¿Quiere que llame a alguien?",
            "action": "confirm_dispatch"
        },
        EmergencySeverity.MEDIUM: {
            "message": "📞 ASISTENCIA RECOMENDADA",
            "voice": "Le recomiendo contactar con su médico. ¿Le ayudo a llamar?",
            "action": "offer_assistance"
        },
        EmergencySeverity.LOW: {
            "message": "ℹ️ SUPERVISIÓN",
            "voice": "Voy a estar pendiente de usted. Avíseme si empeora.",
            "action": "monitor"
        }
    }

    def __init__(self, config: dict[str, Any] = None, guardian=None):
        """
        Initialize Emergency Response System

        Args:
            config: Emergency configuration
            guardian: Optional LUKHAS Guardian integration
        """
        self.config = config or {}
        self.guardian = guardian

        # Emergency settings
        self.emergency_number = self.config.get("number", "112")
        self.auto_dispatch = self.config.get("auto_dispatch", False)
        self.location_tracking = self.config.get("location_tracking", True)

        # Initialize emergency contacts
        self._load_emergency_contacts()

        # Active incidents tracking
        self.active_incidents = {}

        # Location service
        self.last_known_location = None

        # Fall detection state
        self.fall_detection_enabled = self.config.get("fall_detection", True)
        self.fall_sensitivity = self.config.get("fall_sensitivity", "medium")

        logger.info("🚨 Emergency Response System initialized")
        logger.info(f"Emergency number: {self.emergency_number}")
        logger.info(f"Auto-dispatch: {self.auto_dispatch}")
        logger.info(f"Fall detection: {self.fall_detection_enabled}")

    def _load_emergency_contacts(self):
        """Load emergency contacts from configuration"""
        self.emergency_contacts = []

        # Default emergency contacts
        default_contacts = [
            EmergencyContact(
                name="112 Andalucía",
                phone="112",
                relationship="emergency_services",
                priority=1,
                languages=["es"],
                notify_automatically=True
            ),
            EmergencyContact(
                name="Emergencias Sanitarias",
                phone="061",
                relationship="medical_emergency",
                priority=2,
                languages=["es"],
                notify_automatically=True
            )
        ]

        # Load user's family contacts from config
        family_contacts = self.config.get("family_contacts", [])
        for contact in family_contacts:
            self.emergency_contacts.append(EmergencyContact(
                name=contact.get("name"),
                phone=contact.get("phone"),
                relationship=contact.get("relationship", "family"),
                priority=contact.get("priority", 3),
                languages=contact.get("languages", ["es"]),
                notify_automatically=contact.get("auto_notify", False)
            ))

        # Add default contacts if not already present
        for default in default_contacts:
            if not any(c.phone == default.phone for c in self.emergency_contacts):
                self.emergency_contacts.append(default)

        # Sort by priority
        self.emergency_contacts.sort(key=lambda x: x.priority)

    async def assess_severity(self, input_text: str, vitals: dict = None) -> str:
        """
        Assess the severity of an emergency from user input

        Args:
            input_text: User's description of emergency
            vitals: Optional vital signs data

        Returns:
            Severity level string
        """
        input_lower = input_text.lower()

        # Check for life-threatening keywords
        life_threatening = [
            "no puedo respirar", "dolor pecho fuerte", "infarto",
            "mucha sangre", "inconsciente", "no responde"
        ]

        for keyword in life_threatening:
            if keyword in input_lower:
                return "critical"

        # Check for high severity
        high_severity = [
            "me he caído", "dolor fuerte", "mareo", "confundido",
            "no puedo moverme"
        ]

        for keyword in high_severity:
            if keyword in input_lower:
                return "high"

        # Check vitals if available
        if vitals:
            if vitals.get("heart_rate", 70) > 120 or vitals.get("heart_rate", 70) < 50:
                return "critical"
            if vitals.get("blood_pressure_systolic", 120) > 180:
                return "critical"

        # Default to medium for any emergency keyword
        for keywords in self.EMERGENCY_KEYWORDS.values():
            if any(kw in input_lower for kw in keywords):
                return "medium"

        return "low"

    async def handle_emergency(self,
                             description: str,
                             emergency_type: EmergencyType = EmergencyType.UNKNOWN,
                             location: tuple[float, float] = None) -> EmergencyIncident:
        """
        Handle an emergency situation

        Args:
            description: Description of the emergency
            emergency_type: Type of emergency
            location: GPS coordinates

        Returns:
            Emergency incident record
        """
        # Create incident
        incident = EmergencyIncident(
            incident_id=str(uuid.uuid4()),
            emergency_type=emergency_type,
            severity=EmergencySeverity.HIGH,
            timestamp=datetime.now(),
            location=location or self.last_known_location,
            location_address=await self._get_address_from_location(location),
            description=description,
            symptoms=self._extract_symptoms(description),
            user_vitals=None,
            actions_taken=[],
            contacts_notified=[],
            response_time=None,
            status="active"
        )

        # Store incident
        self.active_incidents[incident.incident_id] = incident

        # Determine severity
        severity_str = await self.assess_severity(description)
        incident.severity = self._get_severity_enum(severity_str)

        # Take appropriate action based on severity
        if incident.severity in [EmergencySeverity.CRITICAL, EmergencySeverity.LIFE_THREATENING]:
            await self.dispatch_emergency(incident)
        elif incident.severity == EmergencySeverity.HIGH:
            await self.prepare_emergency_dispatch(incident)
        else:
            await self.monitor_situation(incident)

        return incident

    def _get_severity_enum(self, severity_str: str) -> EmergencySeverity:
        """Convert severity string to enum"""
        mapping = {
            "low": EmergencySeverity.LOW,
            "medium": EmergencySeverity.MEDIUM,
            "high": EmergencySeverity.HIGH,
            "critical": EmergencySeverity.CRITICAL,
            "life_threatening": EmergencySeverity.LIFE_THREATENING
        }
        return mapping.get(severity_str, EmergencySeverity.MEDIUM)

    def _extract_symptoms(self, description: str) -> list[str]:
        """Extract symptoms from emergency description"""
        symptoms = []
        description_lower = description.lower()

        symptom_keywords = {
            "dolor": "dolor",
            "mareo": "mareo",
            "náuseas": "náuseas",
            "vómitos": "vómitos",
            "fiebre": "fiebre",
            "confusión": "confusión",
            "dificultad respirar": "dificultad respiratoria",
            "sangrado": "sangrado",
            "caída": "traumatismo por caída",
            "desmayo": "pérdida de consciencia"
        }

        for keyword, symptom in symptom_keywords.items():
            if keyword in description_lower:
                symptoms.append(symptom)

        return symptoms or ["síntomas no especificados"]

    async def dispatch_emergency(self, incident: EmergencyIncident):
        """
        Dispatch emergency services immediately

        Args:
            incident: Emergency incident
        """
        logger.critical(f"DISPATCHING EMERGENCY: {incident.incident_id}")

        incident.actions_taken.append(f"Emergency dispatch initiated at {datetime.now()}")

        # Call 112
        if self.auto_dispatch:
            await self._call_emergency_services(incident)

        # Notify family
        await self._notify_emergency_contacts(incident, urgent=True)

        # Update incident status
        incident.status = "dispatched"

        # If integrated with Guardian, activate protection
        if self.guardian:
            await self.guardian.activate_emergency_protocol(incident)

    async def prepare_emergency_dispatch(self, incident: EmergencyIncident):
        """Prepare for emergency dispatch but wait for confirmation"""
        logger.warning(f"Preparing emergency dispatch: {incident.incident_id}")

        incident.actions_taken.append("Emergency dispatch prepared, awaiting confirmation")

        # Notify family with high priority
        await self._notify_emergency_contacts(incident, urgent=False)

        # Set timeout for auto-dispatch if no response
        asyncio.create_task(self._auto_dispatch_timeout(incident))

    async def monitor_situation(self, incident: EmergencyIncident):
        """Monitor a non-critical situation"""
        logger.info(f"Monitoring situation: {incident.incident_id}")

        incident.actions_taken.append("Situation under monitoring")

        # Schedule check-ins
        asyncio.create_task(self._schedule_checkins(incident))

    async def _call_emergency_services(self, incident: EmergencyIncident):
        """
        Make actual emergency call (simulated)

        In production, this would interface with telephony API
        """
        logger.critical(f"CALLING {self.emergency_number}")

        # Prepare emergency information
        emergency_data = {
            "caller_id": "LUKHAS Healthcare Guardian",
            "patient_location": incident.location_address or "Unknown",
            "gps_coordinates": incident.location,
            "emergency_type": incident.emergency_type.value,
            "symptoms": incident.symptoms,
            "patient_info": {
                "age": "elderly",
                "conditions": self.config.get("medical_conditions", []),
                "medications": self.config.get("medications", [])
            }
        }

        # Log the call
        incident.actions_taken.append(
            f"Emergency services called at {datetime.now()}: {self.emergency_number}"
        )
        incident.contacts_notified.append(self.emergency_number)

        # In production, this would make actual call
        logger.info(f"Emergency data transmitted: {json.dumps(emergency_data, indent=2)}")

    async def _notify_emergency_contacts(self, incident: EmergencyIncident, urgent: bool = False):
        """Notify emergency contacts about incident"""
        for contact in self.emergency_contacts:
            if urgent or contact.notify_automatically:
                await self._send_emergency_notification(contact, incident)
                incident.contacts_notified.append(contact.name)

    async def _send_emergency_notification(self, contact: EmergencyContact, incident: EmergencyIncident):
        """Send notification to emergency contact"""
        message = self._create_emergency_message(incident, contact.languages[0])

        # In production, this would send SMS/call
        logger.info(f"Notifying {contact.name} ({contact.relationship}): {message}")

    def _create_emergency_message(self, incident: EmergencyIncident, language: str = "es") -> str:
        """Create emergency notification message"""
        if language == "es":
            message = (
                f"ALERTA EMERGENCIA LUKHAS:\n"
                f"Tipo: {incident.emergency_type.value}\n"
                f"Severidad: {incident.severity.name}\n"
                f"Descripción: {incident.description}\n"
            )

            if incident.location_address:
                message += f"Ubicación: {incident.location_address}\n"

            if incident.location:
                message += f"GPS: {incident.location[0]}, {incident.location[1]}\n"

            message += f"Hora: {incident.timestamp.strftime('%H:%M')}"
        else:
            # English fallback
            message = f"EMERGENCY ALERT: {incident.emergency_type.value} - {incident.description}"

        return message

    async def _auto_dispatch_timeout(self, incident: EmergencyIncident):
        """Auto-dispatch after timeout if no response"""
        await asyncio.sleep(60)  # Wait 1 minute

        if incident.status == "active" and incident.severity == EmergencySeverity.HIGH:
            logger.warning(f"Auto-dispatching due to no response: {incident.incident_id}")
            await self.dispatch_emergency(incident)

    async def _schedule_checkins(self, incident: EmergencyIncident):
        """Schedule periodic check-ins for monitored situations"""
        check_in_intervals = [5*60, 15*60, 30*60]  # 5, 15, 30 minutes

        for interval in check_in_intervals:
            await asyncio.sleep(interval)
            if incident.status == "active":
                # Would trigger voice check-in
                logger.info(f"Check-in for incident {incident.incident_id}")

    async def detect_fall(self, sensor_data: dict) -> bool:
        """
        Detect potential fall from sensor data

        Args:
            sensor_data: Accelerometer/gyroscope data

        Returns:
            True if fall detected
        """
        if not self.fall_detection_enabled:
            return False

        # Simple fall detection algorithm
        # In production, use more sophisticated ML model

        acceleration = sensor_data.get("acceleration", 0)
        orientation_change = sensor_data.get("orientation_change", 0)

        # Thresholds based on sensitivity
        thresholds = {
            "low": {"acceleration": 4.0, "orientation": 90},
            "medium": {"acceleration": 3.0, "orientation": 70},
            "high": {"acceleration": 2.0, "orientation": 50}
        }

        threshold = thresholds.get(self.fall_sensitivity, thresholds["medium"])

        if (acceleration > threshold["acceleration"] and
            orientation_change > threshold["orientation"]):
            logger.warning("Fall detected!")
            return True

        return False

    async def handle_fall_detection(self, sensor_data: dict):
        """Handle detected fall"""
        if await self.detect_fall(sensor_data):
            # Create fall emergency
            incident = await self.handle_emergency(
                description="Detección automática de caída",
                emergency_type=EmergencyType.FALL,
                location=self.last_known_location
            )

            # Voice check
            # In production, would ask user if they're okay
            return incident

        return None

    async def update_location(self, latitude: float, longitude: float):
        """Update user's location"""
        self.last_known_location = (latitude, longitude)
        logger.debug(f"Location updated: {latitude}, {longitude}")

    async def _get_address_from_location(self, location: tuple[float, float]) -> Optional[str]:
        """
        Convert GPS coordinates to address

        In production, would use geocoding service
        """
        if not location:
            return None

        # Simulated address
        return "Calle Ejemplo 123, Sevilla, Andalucía"

    async def activate_emergency_protocol(self):
        """Activate full emergency protocol"""
        incident = await self.handle_emergency(
            description="Protocolo de emergencia activado manualmente",
            emergency_type=EmergencyType.MEDICAL
        )

        return incident

    async def cancel_emergency(self, incident_id: str):
        """Cancel an active emergency"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.status = "cancelled"
            incident.actions_taken.append(f"Emergency cancelled at {datetime.now()}")

            # Notify contacts of cancellation
            for contact in self.emergency_contacts:
                if contact.name in incident.contacts_notified:
                    # Would send cancellation notice
                    logger.info(f"Cancellation sent to {contact.name}")

            return True

        return False

    def get_emergency_status(self) -> dict:
        """Get current emergency system status"""
        return {
            "system_active": True,
            "auto_dispatch": self.auto_dispatch,
            "fall_detection": self.fall_detection_enabled,
            "active_incidents": len(self.active_incidents),
            "emergency_number": self.emergency_number,
            "contacts_configured": len(self.emergency_contacts),
            "last_location": self.last_known_location is not None
        }
