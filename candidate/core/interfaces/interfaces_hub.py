#!/usr/bin/env python3
"""
Core Interfaces Integration Hub
Connects all agent interfaces, APIs, and external communication points.
"""
import logging

# API interfaces
from lukhas.core.api.api_server import APIServer
from lukhas.core.api.endpoints import EndpointsManager
from lukhas.core.api.external_api_handler import ExternalAPIHandler

# Agent interfaces
from lukhas.core.interfaces.as_agent.core.agent_handoff import AgentHandoff
from lukhas.core.interfaces.as_agent.core.gatekeeper import Gatekeeper
from lukhas.core.interfaces.as_agent.sys.dast.dast_logger import DASTLogger

logger = logging.getLogger(__name__)


class CoreInterfacesHub:
    """Hub for all core interfaces and APIs"""

    def __init__(self):
        logger.info("Initializing Core Interfaces Hub...")

        # API components
        self.api_server = APIServer()
        self.endpoints_manager = EndpointsManager()
        self.external_api_handler = ExternalAPIHandler()

        # Agent interface components
        self.agent_handoff = AgentHandoff()
        self.gatekeeper = Gatekeeper()
        self.dast_logger = DASTLogger()

        self._establish_connections()

    def _establish_connections(self):
        """Connect interface components"""
        # API server uses endpoints manager
        self.api_server.register_endpoints_manager = lambda em: None  # Placeholder

        # Gatekeeper protects all interfaces
        self.api_server.register_security_layer = lambda sl: None  # Placeholder

        # DAST logger records all interface activity
        self.api_server.register_logger = lambda lg: None  # Placeholder


# Global instance
_interfaces_hub_instance = None


def get_interfaces_hub() -> CoreInterfacesHub:
    global _interfaces_hub_instance
    if _interfaces_hub_instance is None:
        _interfaces_hub_instance = CoreInterfacesHub()
    return _interfaces_hub_instance
