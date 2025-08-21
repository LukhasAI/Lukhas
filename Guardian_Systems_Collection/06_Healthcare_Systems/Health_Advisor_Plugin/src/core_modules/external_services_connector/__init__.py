"""
External Services Connector for Health Advisor Plugin

This module manages all external service integrations with strict security
and HIPAA compliance. It handles:
- Electronic Health Record (EHR) system integration
- Telemedicine service connections
- Pharmacy system integration
- Emergency services coordination
- Appointment scheduling systems
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json
import ssl

from .ehr_connector import EHRConnector
from .telemedicine import TelemedicineConnector
from .pharmacy import PharmacyConnector
from .emergency import EmergencyServicesConnector
from .scheduling import AppointmentScheduler

logger = logging.getLogger(__name__)

class ExternalServicesConnector:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize external services connector with configuration"""
        self.config = config or {}
        
        # Initialize service connectors
        self.ehr = EHRConnector(config.get('ehr', {}))
        self.telemedicine = TelemedicineConnector(config.get('telemedicine', {}))
        self.pharmacy = PharmacyConnector(config.get('pharmacy', {}))
        self.emergency = EmergencyServicesConnector(config.get('emergency', {}))
        self.scheduler = AppointmentScheduler(config.get('scheduling', {}))
        
        # Initialize secure HTTP session
        self._init_secure_session()
        logger.info("ExternalServicesConnector initialized")

    def _init_secure_session(self):
        """Initialize secure HTTP session with HIPAA-compliant settings"""
        ssl_context = ssl.create_default_context()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context),
            headers={
                "User-Agent": "HealthAdvisorPlugin/1.0",
                "X-HIPAA-Compliance": "strict"
            }
        )

    async def schedule_appointment(
        self,
        user_id: str,
        provider_id: str,
        appointment_type: str,
        preferred_time: datetime,
        symptoms: Optional[List[str]] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Schedule an appointment with a healthcare provider

        Args:
            user_id: ID of the user
            provider_id: ID of the healthcare provider
            appointment_type: Type of appointment (e.g., "consultation", "follow-up")
            preferred_time: Preferred appointment time
            symptoms: List of symptoms for context
            priority: Appointment priority ("normal", "urgent", "emergency")

        Returns:
            Dictionary with appointment details
        """
        try:
            appointment = await self.scheduler.schedule_appointment(
                user_id=user_id,
                provider_id=provider_id,
                appointment_type=appointment_type,
                preferred_time=preferred_time,
                symptoms=symptoms,
                priority=priority
            )

            # Log the scheduling attempt
            logger.info(
                f"Appointment scheduled for user {user_id} with provider {provider_id}"
            )

            return appointment

        except Exception as e:
            logger.error(f"Error scheduling appointment: {str(e)}")
            raise

    async def get_ehr_summary(
        self,
        user_id: str,
        requester_id: str,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a summary of patient's Electronic Health Record

        Args:
            user_id: ID of the user
            requester_id: ID of the entity requesting the EHR
            include_sections: Optional list of specific sections to include

        Returns:
            Dictionary containing EHR summary
        """
        try:
            return await self.ehr.get_patient_summary(
                user_id,
                requester_id,
                include_sections
            )

        except Exception as e:
            logger.error(f"Error retrieving EHR summary: {str(e)}")
            raise

    async def initiate_telemedicine_session(
        self,
        user_id: str,
        provider_id: str,
        session_type: str,
        symptoms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a telemedicine session

        Args:
            user_id: ID of the user
            provider_id: ID of the healthcare provider
            session_type: Type of telemedicine session
            symptoms: Optional list of symptoms

        Returns:
            Dictionary with session details and connection information
        """
        try:
            return await self.telemedicine.create_session(
                user_id,
                provider_id,
                session_type,
                symptoms
            )

        except Exception as e:
            logger.error(f"Error initiating telemedicine session: {str(e)}")
            raise

    async def check_medication_availability(
        self,
        medication_id: str,
        pharmacy_id: Optional[str] = None,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Check medication availability at pharmacies

        Args:
            medication_id: ID of the medication
            pharmacy_id: Optional specific pharmacy to check
            location: Optional location coordinates

        Returns:
            Dictionary with availability information
        """
        try:
            return await self.pharmacy.check_availability(
                medication_id,
                pharmacy_id,
                location
            )

        except Exception as e:
            logger.error(f"Error checking medication availability: {str(e)}")
            raise

    async def notify_emergency_services(
        self,
        user_id: str,
        location: Dict[str, float],
        symptoms: List[str],
        severity: str
    ) -> Dict[str, Any]:
        """
        Notify emergency services in critical situations

        Args:
            user_id: ID of the user
            location: User's location coordinates
            symptoms: List of symptoms
            severity: Severity level of the emergency

        Returns:
            Dictionary with emergency response details
        """
        try:
            return await self.emergency.notify_services(
                user_id,
                location,
                symptoms,
                severity
            )

        except Exception as e:
            logger.error(f"Error notifying emergency services: {str(e)}")
            raise

    async def close(self):
        """Clean up resources and close connections"""
        await self.session.close()
        await self.ehr.close()
        await self.telemedicine.close()
        await self.pharmacy.close()
        await self.emergency.close()
        await self.scheduler.close()
