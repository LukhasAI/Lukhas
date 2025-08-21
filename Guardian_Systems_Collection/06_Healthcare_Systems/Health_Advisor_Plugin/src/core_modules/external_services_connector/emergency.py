"""
Emergency Services Connector for Health Advisor Plugin

Manages integration with emergency services and coordinates
urgent medical response when needed.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)

class EmergencyServicesConnector:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize emergency services connector with configuration"""
        self.config = config or {}
        self._init_emergency_config()
        logger.info("EmergencyServicesConnector initialized")

    def _init_emergency_config(self):
        """Initialize emergency services configuration"""
        self.api_endpoint = self.config.get(
            'api_endpoint',
            'https://api.emergency-services.com'
        )
        self.api_key = self.config.get('api_key')
        self.emergency_numbers = self.config.get('emergency_numbers', {
            'default': '911',
            'police': '911',
            'ambulance': '911',
            'fire': '911'
        })
        
        if not self.api_key:
            logger.warning("No emergency services API key provided")

    async def notify_services(
        self,
        user_id: str,
        location: Dict[str, float],
        symptoms: List[str],
        severity: str
    ) -> Dict[str, Any]:
        """
        Notify emergency services about a medical emergency

        Args:
            user_id: ID of the user
            location: Dictionary with latitude and longitude
            symptoms: List of symptoms
            severity: Severity level of the emergency

        Returns:
            Dictionary with emergency response details
        """
        try:
            endpoint = f"{self.api_endpoint}/v1/emergency/notify"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Emergency-Priority": severity
            }

            payload = {
                "user_id": user_id,
                "location": location,
                "symptoms": symptoms,
                "severity": severity,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "health_advisor_plugin"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Emergency services API error: {error_data}")

        except Exception as e:
            logger.error(f"Error notifying emergency services: {str(e)}")
            # Fall back to providing emergency contact information
            return self._get_emergency_contact_info(location)

    async def check_response_status(
        self,
        emergency_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of an emergency response

        Args:
            emergency_id: ID of the emergency incident

        Returns:
            Dictionary with response status details
        """
        try:
            endpoint = f"{self.api_endpoint}/v1/emergency/{emergency_id}/status"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Emergency-ID": emergency_id
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Emergency services API error: {error_data}")

        except Exception as e:
            logger.error(f"Error checking emergency response status: {str(e)}")
            raise

    def _get_emergency_contact_info(
        self,
        location: Optional[Dict[str, float]] = None
    ) -> Dict[str, str]:
        """
        Get emergency contact information based on location

        Args:
            location: Optional dictionary with latitude and longitude

        Returns:
            Dictionary with emergency contact numbers
        """
        # TODO: Implement location-based emergency number lookup
        return {
            "message": "Please contact emergency services immediately",
            "emergency_numbers": self.emergency_numbers
        }

    async def update_emergency_info(
        self,
        emergency_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update information for an ongoing emergency

        Args:
            emergency_id: ID of the emergency incident
            updates: Dictionary with updates to apply

        Returns:
            Dictionary with update confirmation
        """
        try:
            endpoint = f"{self.api_endpoint}/v1/emergency/{emergency_id}/update"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Emergency-ID": emergency_id
            }

            updates["update_time"] = datetime.utcnow().isoformat()

            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    endpoint,
                    headers=headers,
                    json=updates
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Emergency services API error: {error_data}")

        except Exception as e:
            logger.error(f"Error updating emergency info: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        # Nothing to clean up for now
        pass
