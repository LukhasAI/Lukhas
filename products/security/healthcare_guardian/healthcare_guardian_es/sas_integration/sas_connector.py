#!/usr/bin/env python3
"""
SAS (Servicio Andaluz de Salud) Healthcare Connector
Integrates with Andalusian healthcare system for appointments, prescriptions, and records
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class SASAppointment:
    """SAS appointment data structure"""

    appointment_id: str
    patient_nuhsa: str  # Número Único de Historia de Salud de Andalucía
    doctor_name: str
    specialty: str
    date: datetime
    time: str
    location: str
    centro_salud: str
    status: str  # scheduled, confirmed, cancelled
    notes: Optional[str] = None


@dataclass
class SASPrescription:
    """Electronic prescription data"""

    prescription_id: str
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    prescriber: str
    date_prescribed: datetime
    date_expires: datetime
    dispensed: bool
    refills_remaining: int


@dataclass
class SASPatientRecord:
    """Patient medical record"""

    nuhsa: str
    name: str
    birth_date: datetime
    medical_conditions: list[str]
    allergies: list[str]
    current_medications: list[str]
    recent_visits: list[dict]
    emergency_contacts: list[dict]


class SASHealthcareConnector:
    """
    Connector for Servicio Andaluz de Salud (SAS) healthcare system
    Provides appointment booking, prescription management, and medical records access
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize SAS connector with configuration

        Args:
            config: SAS configuration including credentials and endpoints
        """
        self.config = config or {}

        # Load SAS configuration
        self._load_sas_config()

        # Initialize connection status
        self.connected = False
        self.last_sync = None

        # Cache for user data
        self.appointment_cache = {}
        self.prescription_cache = {}
        self.record_cache = {}

        logger.info("🏥 SAS Healthcare Connector initialized")
        logger.info(f"Region: {self.sas_config.get('region', 'Andalucía')}")
        logger.info(f"Centro: {self.sas_config.get('centro_salud', 'Not configured')}")

    def _load_sas_config(self):
        """Load SAS configuration from file or defaults"""
        config_path = Path(__file__).parent.parent / "config" / "sas_settings.yaml"

        # Default configuration based on existing template
        self.sas_config = {
            "environment": self.config.get("environment", "production"),
            "region": "andalucia",
            "api_endpoints": {
                "base_url": "https://api.sas.junta-andalucia.es",
                "appointments": "/api/v1/citas",
                "prescriptions": "/api/v1/recetas",
                "medical_records": "/api/v1/historia",
                "emergency": "/api/v1/urgencias",
            },
            "centro_salud": self.config.get("centro_salud", ""),
            "provincia": self.config.get("provincia", "SEVILLA"),
            "timeout": 30,
            "retry_attempts": 3,
        }

        # Load custom config if exists
        if config_path.exists():
            try:
                import yaml

                with open(config_path, encoding="utf-8") as f:
                    custom_config = yaml.safe_load(f)
                    self.sas_config.update(custom_config)
            except Exception as e:
                logger.warning(f"Could not load SAS config: {e}")

    async def connect(self, nuhsa: str, credentials: Optional[dict] = None) -> bool:
        """
        Connect to SAS system with patient NUHSA

        Args:
            nuhsa: Patient's NUHSA number
            credentials: Optional authentication credentials

        Returns:
            Success status
        """
        try:
            # Validate NUHSA format (AN + 10 digits)
            if not self._validate_nuhsa(nuhsa):
                logger.error(f"Invalid NUHSA format: {nuhsa}")
                return False

            # In production, this would authenticate with SAS
            # For now, simulate connection
            self.current_nuhsa = nuhsa
            self.connected = True
            self.last_sync = datetime.now(timezone.utc)

            # Load cached data if available
            await self._load_cached_data(nuhsa)

            logger.info(f"Connected to SAS for patient NUHSA: {nuhsa}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to SAS: {e}")
            return False

    def _validate_nuhsa(self, nuhsa: str) -> bool:
        """Validate NUHSA format (AN + 10 digits)"""
        if not nuhsa:
            return False

        # NUHSA format: AN followed by 10 digits
        if len(nuhsa) != 12:
            return False

        if not nuhsa.startswith("AN"):
            return False

        # Check if rest are digits
        return nuhsa[2:].isdigit()

    async def _load_cached_data(self, nuhsa: str):
        """Load cached patient data"""
        # In production, this would load from secure local storage
        # For demo, create sample data

        # Sample appointments
        self.appointment_cache[nuhsa] = [
            SASAppointment(
                appointment_id="CIT-2024-001",
                patient_nuhsa=nuhsa,
                doctor_name="Dr. García Martínez",
                specialty="Cardiología",
                date=datetime.now(timezone.utc) + timedelta(days=7),
                time="10:30",
                location="Consulta 5, Planta 2",
                centro_salud="Centro de Salud Alameda",
                status="confirmed",
                notes="Control rutinario",
            ),
            SASAppointment(
                appointment_id="CIT-2024-002",
                patient_nuhsa=nuhsa,
                doctor_name="Dra. López Ruiz",
                specialty="Medicina Familiar",
                date=datetime.now(timezone.utc) + timedelta(days=30),
                time="09:00",
                location="Consulta 2",
                centro_salud="Centro de Salud Alameda",
                status="scheduled",
                notes="Revisión anual",
            ),
        ]

        # Sample prescriptions
        self.prescription_cache[nuhsa] = [
            SASPrescription(
                prescription_id="REC-2024-001",
                medication_name="Enalapril",
                dosage="10mg",
                frequency="1 vez al día",
                duration="Crónico",
                prescriber="Dr. García Martínez",
                date_prescribed=datetime.now(timezone.utc) - timedelta(days=30),
                date_expires=datetime.now(timezone.utc) + timedelta(days=60),
                dispensed=True,
                refills_remaining=3,
            ),
            SASPrescription(
                prescription_id="REC-2024-002",
                medication_name="Metformina",
                dosage="500mg",
                frequency="2 veces al día",
                duration="Crónico",
                prescriber="Dr. García Martínez",
                date_prescribed=datetime.now(timezone.utc) - timedelta(days=30),
                date_expires=datetime.now(timezone.utc) + timedelta(days=60),
                dispensed=True,
                refills_remaining=3,
            ),
        ]

        # Sample patient record
        self.record_cache[nuhsa] = SASPatientRecord(
            nuhsa=nuhsa,
            name="María García López",
            birth_date=datetime(1945, 3, 15),
            medical_conditions=["Hipertensión", "Diabetes Tipo 2", "Artrosis"],
            allergies=["Penicilina"],
            current_medications=["Enalapril 10mg", "Metformina 500mg", "Omeprazol 20mg"],
            recent_visits=[
                {
                    "date": "2024-01-15",
                    "doctor": "Dr. García",
                    "reason": "Control tensión",
                    "notes": "Tensión controlada",
                }
            ],
            emergency_contacts=[{"name": "Juan García", "relationship": "Hijo", "phone": "600123456"}],
        )

    async def get_next_appointment(self) -> Optional[str]:
        """
        Get the next scheduled appointment

        Returns:
            Formatted appointment string or None
        """
        if not self.connected or not self.current_nuhsa:
            return None

        appointments = self.appointment_cache.get(self.current_nuhsa, [])

        # Find next future appointment
        future_appointments = [apt for apt in appointments if apt.date > datetime.now(timezone.utc) and apt.status != "cancelled"]

        if not future_appointments:
            return None

        # Sort by date and get first
        next_apt = sorted(future_appointments, key=lambda x: x.date)[0]

        # Format for voice output
        date_str = next_apt.date.strftime("%d de %B")
        response = (
            f"el {date_str} a las {next_apt.time} "
            f"con {next_apt.doctor_name} de {next_apt.specialty}. "
            f"En {next_apt.centro_salud}"
        )

        return response

    async def get_all_appointments(self) -> list[SASAppointment]:
        """Get all appointments for current patient"""
        if not self.connected or not self.current_nuhsa:
            return []

        return self.appointment_cache.get(self.current_nuhsa, [])

    async def book_appointment(
        self, specialty: str, preferred_time: Optional[str] = None, urgency: str = "normal"
    ) -> Optional[SASAppointment]:
        """
        Book a new appointment

        Args:
            specialty: Medical specialty needed
            preferred_time: Preferred time (morning/afternoon)
            urgency: Urgency level (normal/preferente/urgente)

        Returns:
            New appointment or None if not available
        """
        if not self.connected:
            logger.error("Not connected to SAS")
            return None

        try:
            # In production, this would call SAS API
            # For demo, create simulated appointment

            # Calculate next available date
            if urgency == "urgente":
                apt_date = datetime.now(timezone.utc) + timedelta(days=1)
            elif urgency == "preferente":
                apt_date = datetime.now(timezone.utc) + timedelta(days=7)
            else:
                apt_date = datetime.now(timezone.utc) + timedelta(days=14)

            # Determine time based on preference
            if preferred_time == "mañana":
                apt_time = "09:30"
            elif preferred_time == "tarde":
                apt_time = "16:00"
            else:
                apt_time = "11:00"

            # Create new appointment
            new_appointment = SASAppointment(
                appointment_id=f"CIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
                patient_nuhsa=self.current_nuhsa,
                doctor_name="Por asignar",
                specialty=specialty,
                date=apt_date,
                time=apt_time,
                location="Por determinar",
                centro_salud=self.sas_config["centro_salud"],
                status="scheduled",
                notes=f"Cita {urgency}",
            )

            # Add to cache
            if self.current_nuhsa not in self.appointment_cache:
                self.appointment_cache[self.current_nuhsa] = []
            self.appointment_cache[self.current_nuhsa].append(new_appointment)

            logger.info(f"Appointment booked: {new_appointment.appointment_id}")
            return new_appointment

        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return None

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Cancel an appointment

        Args:
            appointment_id: Appointment identifier

        Returns:
            Success status
        """
        if not self.connected or not self.current_nuhsa:
            return False

        appointments = self.appointment_cache.get(self.current_nuhsa, [])

        for apt in appointments:
            if apt.appointment_id == appointment_id:
                apt.status = "cancelled"
                logger.info(f"Appointment cancelled: {appointment_id}")
                return True

        return False

    async def get_active_prescriptions(self) -> list[SASPrescription]:
        """Get active prescriptions for current patient"""
        if not self.connected or not self.current_nuhsa:
            return []

        prescriptions = self.prescription_cache.get(self.current_nuhsa, [])

        # Filter active prescriptions
        active = [presc for presc in prescriptions if presc.date_expires > datetime.now(timezone.utc)]

        return active

    async def request_prescription_renewal(self, prescription_id: str) -> bool:
        """
        Request prescription renewal

        Args:
            prescription_id: Prescription identifier

        Returns:
            Success status
        """
        if not self.connected or not self.current_nuhsa:
            return False

        prescriptions = self.prescription_cache.get(self.current_nuhsa, [])

        for presc in prescriptions:
            if presc.prescription_id == prescription_id:
                # Extend expiration date
                presc.date_expires = datetime.now(timezone.utc) + timedelta(days=90)
                presc.refills_remaining += 3
                logger.info(f"Prescription renewed: {prescription_id}")
                return True

        return False

    async def get_medical_history(self) -> Optional[SASPatientRecord]:
        """Get patient medical history"""
        if not self.connected or not self.current_nuhsa:
            return None

        return self.record_cache.get(self.current_nuhsa)

    async def get_emergency_info(self) -> dict[str, Any]:
        """
        Get emergency information for current patient

        Returns:
            Emergency information including contacts and medical alerts
        """
        if not self.connected or not self.current_nuhsa:
            return {}

        record = self.record_cache.get(self.current_nuhsa)
        if not record:
            return {}

        emergency_info = {
            "patient_name": record.name,
            "nuhsa": record.nuhsa,
            "birth_date": record.birth_date.strftime("%d/%m/%Y"),
            "allergies": record.allergies,
            "medical_conditions": record.medical_conditions,
            "current_medications": record.current_medications,
            "emergency_contacts": record.emergency_contacts,
            "centro_salud": self.sas_config["centro_salud"],
            "emergency_number": "112",
        }

        return emergency_info

    async def find_nearest_pharmacy(self, location: Optional[tuple[float, float]] = None) -> dict:
        """
        Find nearest pharmacy for prescriptions

        Args:
            location: GPS coordinates (latitude, longitude)

        Returns:
            Pharmacy information
        """
        # In production, this would use SAS pharmacy database
        # For demo, return sample pharmacy

        pharmacy = {
            "name": "Farmacia García López",
            "address": "Calle Real 23, Sevilla",
            "phone": "954123456",
            "hours": "Lunes-Viernes 9:00-21:00, Sábado 9:00-14:00",
            "distance": "500 metros",
            "has_emergency_service": True,
        }

        return pharmacy

    def format_appointment_for_voice(self, appointment: SASAppointment) -> str:
        """
        Format appointment for voice output in Andalusian Spanish

        Args:
            appointment: Appointment to format

        Returns:
            Formatted string for voice
        """
        # Convert date to Spanish format
        months = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }

        day = appointment.date.day
        month = months[appointment.date.month]

        response = f"Tiene cita el {day} de {month} a las {appointment.time} con {appointment.doctor_name}. "

        if appointment.specialty:
            response += f"Es de {appointment.specialty}. "

        response += f"En {appointment.centro_salud}."

        if appointment.notes:
            response += f" {appointment.notes}."

        return response

    def format_prescription_for_voice(self, prescription: SASPrescription) -> str:
        """
        Format prescription for voice output

        Args:
            prescription: Prescription to format

        Returns:
            Formatted string for voice
        """
        response = f"{prescription.medication_name}, {prescription.dosage}, {prescription.frequency}. "

        if prescription.refills_remaining > 0:
            response += f"Le quedan {prescription.refills_remaining} repeticiones. "
        else:
            response += "Necesita renovar la receta. "

        return response