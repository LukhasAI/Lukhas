"""
EHR (Electronic Health Record) Connector for Health Advisor Plugin

Manages secure integration with Electronic Health Record systems,
ensuring HIPAA compliance and data security.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)

class EHRConnector:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize EHR connector with configuration"""
        self.config = config or {}
        self._init_api_config()
        logger.info("EHRConnector initialized")

    def _init_api_config(self):
        """Initialize API configuration and authentication"""
        self.api_base_url = self.config.get('api_base_url', 'https://api.ehr-system.com')
        self.api_version = self.config.get('api_version', 'v1')
        self.auth_token = self.config.get('auth_token')
        
        if not self.auth_token:
            logger.warning("No EHR auth token provided")

    async def get_patient_summary(
        self,
        user_id: str,
        requester_id: str,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve patient's EHR summary

        Args:
            user_id: ID of the user
            requester_id: ID of the entity requesting the EHR
            include_sections: Optional list of specific sections to include

        Returns:
            Dictionary containing EHR summary
        """
        try:
            # Construct API endpoint
            endpoint = f"{self.api_base_url}/{self.api_version}/patients/{user_id}/summary"
            
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "X-Requester-ID": requester_id,
                "X-Request-Time": datetime.utcnow().isoformat()
            }
            
            # Prepare query parameters
            params = {}
            if include_sections:
                params['sections'] = ','.join(include_sections)

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.text()
                        raise Exception(f"EHR API error: {error_data}")

        except Exception as e:
            logger.error(f"Error retrieving patient summary: {str(e)}")
            raise

    async def update_patient_record(
        self,
        user_id: str,
        updates: Dict[str, Any],
        requester_id: str
    ) -> Dict[str, Any]:
        """
        Update patient's EHR

        Args:
            user_id: ID of the user
            updates: Dictionary of updates to apply
            requester_id: ID of the entity making the update

        Returns:
            Dictionary with update confirmation
        """
        try:
            endpoint = f"{self.api_base_url}/{self.api_version}/patients/{user_id}/record"
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "X-Requester-ID": requester_id,
                "X-Request-Time": datetime.utcnow().isoformat(),
                "Content-Type": "application/json"
            }

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
                        raise Exception(f"EHR API error: {error_data}")

        except Exception as e:
            logger.error(f"Error updating patient record: {str(e)}")
            raise

    async def get_medical_history(
        self,
        user_id: str,
        requester_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Retrieve patient's medical history

        Args:
            user_id: ID of the user
            requester_id: ID of the entity requesting the history
            start_date: Optional start date for history
            end_date: Optional end date for history

        Returns:
            Dictionary containing medical history
        """
        try:
            endpoint = f"{self.api_base_url}/{self.api_version}/patients/{user_id}/history"
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "X-Requester-ID": requester_id,
                "X-Request-Time": datetime.utcnow().isoformat()
            }

            params = {}
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()

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
                        raise Exception(f"EHR API error: {error_data}")

        except Exception as e:
            logger.error(f"Error retrieving medical history: {str(e)}")
            raise

    async def close(self):
        """Clean up resources"""
        # Nothing to clean up for now
        pass
