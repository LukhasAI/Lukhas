"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

Service Discovery System
Enables cross-system service discovery and communication
"""
from typing import List
import streamlit as st

import logging
from typing import Any, Optional

from lukhas.core.integration.hub_registry import get_hub_registry

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """Central service discovery system"""

    def __init__(self):
        self.hub_registry = get_hub_registry()

    def find_service(self, service_name: str, preferred_hub: Optional[str] = None) -> Optional[Any]:
        """Find a service across all hubs"""

        # Try preferred hub first
        if preferred_hub:
            hub = self.hub_registry.get_hub(preferred_hub)
            if hub:
                service = hub.get_service(service_name)
                if service:
                    logger.debug(f"Found {service_name} in preferred hub {preferred_hub}")
                    return service

        # Search all hubs
        for hub_name, hub_factory in self.hub_registry.hubs.items():
            if hub_name == preferred_hub:
                continue  # Already checked

            try:
                hub = hub_factory()
                service = hub.get_service(service_name)
                if service:
                    logger.debug(f"Found {service_name} in hub {hub_name}")
                    return service
            except Exception as e:
                logger.warning(f"Error searching hub {hub_name}: {e}")

        logger.warning(f"Service {service_name} not found in any hub")
        return None

    def register_service_globally(self, service_name: str, service: Any, hub_name: str) -> bool:
        """Register a service in a specific hub"""
        hub = self.hub_registry.get_hub(hub_name)
        if hub:
            hub.register_service(service_name, service)
            logger.info(f"Registered {service_name} in {hub_name} hub")
            return True
        return False

    def list_all_services(self) -> dict[str, list[str]]:
        """List all services across all hubs"""
        all_services = {}

        for hub_name, hub_factory in self.hub_registry.hubs.items():
            try:
                hub = hub_factory()
                if hasattr(hub, "services"):
                    all_services[hub_name] = list(hub.services.keys())
                else:
                    all_services[hub_name] = []
            except Exception as e:
                logger.warning(f"Error listing services in {hub_name}: {e}")
                all_services[hub_name] = []

        return all_services

    async def health_check_service(self, service_name: str) -> dict[str, Any]:
        """Health check a specific service across all hubs"""
        service = self.find_service(service_name)

        if not service:
            return {"status": "not_found", "service": service_name}

        try:
            if hasattr(service, "health_check"):
                health = await service.health_check()
                return {
                    "status": "healthy",
                    "service": service_name,
                    "health": health,
                }
            else:
                return {"status": "available", "service": service_name}
        except Exception as e:
            return {
                "status": "error",
                "service": service_name,
                "error": str(e),
            }


# Singleton
_service_discovery = None


def get_service_discovery() -> ServiceDiscovery:
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery
