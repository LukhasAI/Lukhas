"""
Pharmacy Connector for Health Advisor Plugin

Manages integration with pharmacy systems for medication
availability checks and prescription services.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)

class PharmacyConnector:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize pharmacy connector with configuration"""
        self.config = config or {}
        self._init_pharmacy_config()
        logger.info("PharmacyConnector initialized")

    def _init_pharmacy_config(self):
        """Initialize pharmacy system configuration"""
        self.api_base_url = self.config.get(
            'api_base_url',
            'https://api.pharmacy-network.com'
        )
        self.api_key = self.config.get('api_key')
        self.network_id = self.config.get('network_id')
        
        if not self.api_key:
            logger.warning("No pharmacy API key provided")

    async def check_availability(
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
            endpoint = f"{self.api_base_url}/v1/medications/{medication_id}/availability"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Network-ID": self.network_id,
                "Content-Type": "application/json"
            }

            params = {}
            if pharmacy_id:
                params['pharmacy_id'] = pharmacy_id
            if location:
                params.update({
                    'latitude': location['latitude'],
                    'longitude': location['longitude']
                })

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
                        raise Exception(f"Pharmacy API error: {error_data}")

        except Exception as e:
            logger.error(f"Error checking medication availability: {str(e)}")
            raise

    async def get_prescription_status(
        self,
        prescription_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a prescription

        Args:
            prescription_id: ID of the prescription
            user_id: ID of the user

        Returns:
            Dictionary with prescription status
        """
        try:
            endpoint = f"{self.api_base_url}/v1/prescriptions/{prescription_id}/status"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Network-ID": self.network_id,
                "X-User-ID": user_id
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"Pharmacy API error: {error_data}")

        except Exception as e:
            logger.error(f"Error checking prescription status: {str(e)}")
            raise

    async def find_nearby_pharmacies(
        self,
        location: Dict[str, float],
        radius_km: float = 5.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find pharmacies near a location

        Args:
            location: Dictionary with latitude and longitude
            radius_km: Search radius in kilometers
            filters: Optional filters (e.g., "24_hour", "drive_thru")

        Returns:
            List of pharmacy information dictionaries
        """
        try:
            endpoint = f"{self.api_base_url}/v1/pharmacies/search"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Network-ID": self.network_id,
                "Content-Type": "application/json"
            }

            params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "radius_km": radius_km
            }
            if filters:
                params.update(filters)

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
                        raise Exception(f"Pharmacy API error: {error_data}")

        except Exception as e:
            logger.error(f"Error finding nearby pharmacies: {str(e)}")
            raise

    async def request_refill(
        self,
        prescription_id: str,
        user_id: str,
        pharmacy_id: str
    ) -> Dict[str, Any]:
        """
        Request a prescription refill

        Args:
            prescription_id: ID of the prescription
            user_id: ID of the user
            pharmacy_id: ID of the pharmacy

        Returns:
            Dictionary with refill request confirmation
        """
        try:
            endpoint = f"{self.api_base_url}/v1/prescriptions/{prescription_id}/refill"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Network-ID": self.network_id,
                "Content-Type": "application/json",
                "X-User-ID": user_id
            }

            payload = {
                "pharmacy_id": pharmacy_id,
                "request_time": datetime.utcnow().isoformat()
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
                        raise Exception(f"Pharmacy API error: {error_data}")

        except Exception as e:
            logger.error(f"Error requesting prescription refill: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        # Nothing to clean up for now
        pass
