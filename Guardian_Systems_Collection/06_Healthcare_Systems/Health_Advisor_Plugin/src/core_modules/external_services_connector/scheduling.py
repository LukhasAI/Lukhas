"""
Appointment Scheduler for Health Advisor Plugin

Manages appointment scheduling with healthcare providers,
including availability checks and calendar integration.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
import json

logger = logging.getLogger(__name__)

class AppointmentScheduler:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize appointment scheduler with configuration"""
        self.config = config or {}
        self._init_scheduler_config()
        logger.info("AppointmentScheduler initialized")

    def _init_scheduler_config(self):
        """Initialize scheduler configuration"""
        self.api_base_url = self.config.get(
            'api_base_url',
            'https://api.appointment-system.com'
        )
        self.api_key = self.config.get('api_key')
        
        if not self.api_key:
            logger.warning("No appointment scheduler API key provided")

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
            appointment_type: Type of appointment
            preferred_time: Preferred appointment time
            symptoms: Optional list of symptoms
            priority: Appointment priority

        Returns:
            Dictionary with appointment details
        """
        try:
            # First check provider availability
            available_slots = await self.check_availability(
                provider_id,
                preferred_time.date(),
                appointment_type
            )

            # Find the best matching time slot
            chosen_slot = self._find_best_slot(
                available_slots,
                preferred_time,
                priority
            )

            if not chosen_slot:
                raise ValueError("No suitable appointment slots available")

            # Book the appointment
            return await self._book_appointment(
                user_id,
                provider_id,
                chosen_slot["slot_id"],
                appointment_type,
                symptoms,
                priority
            )

        except Exception as e:
            logger.error(f"Error scheduling appointment: {str(e)}")
            raise

    async def check_availability(
        self,
        provider_id: str,
        date: datetime,
        appointment_type: str
    ) -> List[Dict[str, Any]]:
        """
        Check provider's availability for a given date

        Args:
            provider_id: ID of the healthcare provider
            date: Date to check availability for
            appointment_type: Type of appointment

        Returns:
            List of available time slots
        """
        try:
            endpoint = f"{self.api_base_url}/v1/availability"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            params = {
                "provider_id": provider_id,
                "date": date.isoformat(),
                "appointment_type": appointment_type
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Scheduler API error: {error_data}")

        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            raise

    def _find_best_slot(
        self,
        available_slots: List[Dict[str, Any]],
        preferred_time: datetime,
        priority: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best available time slot

        Args:
            available_slots: List of available slots
            preferred_time: Preferred appointment time
            priority: Appointment priority

        Returns:
            Best matching time slot or None if no suitable slot found
        """
        if not available_slots:
            return None

        # Sort slots by proximity to preferred time
        slots = sorted(
            available_slots,
            key=lambda x: abs(
                datetime.fromisoformat(x["start_time"]) - preferred_time
            )
        )

        # For urgent priority, return first available slot
        if priority == "urgent":
            return slots[0]

        # For normal priority, find closest slot to preferred time
        # within reasonable time range (e.g., ±2 hours)
        max_diff = timedelta(hours=2)
        for slot in slots:
            slot_time = datetime.fromisoformat(slot["start_time"])
            if abs(slot_time - preferred_time) <= max_diff:
                return slot

        # If no slot found within preferred range, return closest available
        return slots[0]

    async def _book_appointment(
        self,
        user_id: str,
        provider_id: str,
        slot_id: str,
        appointment_type: str,
        symptoms: Optional[List[str]] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Book a specific appointment slot

        Args:
            user_id: ID of the user
            provider_id: ID of the healthcare provider
            slot_id: ID of the chosen time slot
            appointment_type: Type of appointment
            symptoms: Optional list of symptoms
            priority: Appointment priority

        Returns:
            Dictionary with booking confirmation
        """
        try:
            endpoint = f"{self.api_base_url}/v1/appointments"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "user_id": user_id,
                "provider_id": provider_id,
                "slot_id": slot_id,
                "appointment_type": appointment_type,
                "symptoms": symptoms or [],
                "priority": priority,
                "booking_time": datetime.utcnow().isoformat()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 201:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Scheduler API error: {error_data}")

        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            raise

    async def get_appointment_details(
        self,
        appointment_id: str
    ) -> Dict[str, Any]:
        """
        Get details of a scheduled appointment

        Args:
            appointment_id: ID of the appointment

        Returns:
            Dictionary with appointment details
        """
        try:
            endpoint = f"{self.api_base_url}/v1/appointments/{appointment_id}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Scheduler API error: {error_data}")

        except Exception as e:
            logger.error(f"Error getting appointment details: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        # Nothing to clean up for now
        pass
