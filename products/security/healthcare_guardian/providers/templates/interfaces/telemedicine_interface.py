"""
Telemedicine Interface Template for Health Advisor Provider Plugin

This module defines the required interfaces for telemedicine integration.
Providers must implement these interfaces to enable virtual consultations.
"""
import streamlit as st

from abc import ABC, abstractmethod
from typing import Any, Optional


class TelemedicineInterface(ABC):
    """Abstract base class for telemedicine platform integration"""

    @abstractmethod
    async def initialize_session(self, provider_id: str, patient_id: str, session_type: str) -> dict[str, Any]:
        """Initialize a new telemedicine session"""
        pass

    @abstractmethod
    async def generate_session_link(self, session_id: str, participant_type: str) -> str:
        """Generate secure session link for participant"""
        pass

    @abstractmethod
    async def end_session(self, session_id: str, summary: Optional[dict[str, Any]] = None) -> bool:
        """End an active telemedicine session"""
        pass

    @abstractmethod
    async def record_session(self, session_id: str, record_type: str = "audio") -> str:
        """Start/Stop session recording (if permitted)"""
        pass

    @abstractmethod
    async def share_screen(self, session_id: str, content_type: str, content: Any) -> bool:
        """Share screen or content during session"""
        pass

    @abstractmethod
    async def get_session_metrics(self, session_id: str) -> dict[str, Any]:
        """Get session quality and engagement metrics"""
        pass


class TelemedicineSecurityHandler(ABC):
    """Handler for telemedicine security requirements"""

    @abstractmethod
    async def verify_participant(self, session_id: str, participant_id: str, verification_type: str) -> bool:
        """Verify participant identity"""
        pass

    @abstractmethod
    async def encrypt_stream(self, session_id: str, stream_type: str) -> None:
        """Set up encrypted streaming"""
        pass

    @abstractmethod
    async def log_security_event(self, session_id: str, event_type: str, event_data: dict[str, Any]) -> None:
        """Log security-related events"""
        pass
