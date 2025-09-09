#!/usr/bin/env python3
"""
Identity System Connector
Ensures all systems properly integrate with identity and safety checks.
"""
import functools
from typing import Callable

from candidate.orchestration.integration_hub import get_integration_hub
from identity.audit_logger import AuditLogger
from identity.safety_monitor import SafetyMonitor
from identity.tiered_access import TieredAccessControl


class IdentityConnector:
    """Connects identity and safety to all systems."""

    def __init__(self):
        self.access_control = TieredAccessControl()
        self.safety_monitor = SafetyMonitor()
        self.audit_logger = AuditLogger()

    def require_tier(self, min_tier: int):
        """Decorator to enforce tier requirements."""

        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(self, agent_id: str, *args, **kwargs):
                # Check tier access
                tier = await self.access_control.get_agent_tier(agent_id)
                if tier < min_tier:
                    self.audit_logger.log_access_denied(agent_id, func.__name__, tier, min_tier)
                    raise PermissionError(f"Requires tier {min_tier}, agent has tier {tier}")

    def setup_cross_module_auth(self):
        """Setup authentication for cross-module communication"""
        auth_config = {
            "core": {"level": "full", "method": "certificate"},
            "memory": {"level": "read_write", "method": "token"},
            "consciousness": {"level": "read", "method": "biometric"},
            "ethics": {"level": "audit", "method": "multi_factor"},
        }

        for module, config in auth_config.items():
            self.configure_auth(module, config)
            self.audit_logger.log_event("system", "auth_configured", {"module": module, "config": config})

    def configure_auth(self, module: str, config: dict[str, str]):
        """Configure authentication for a specific module"""
        # Store auth configuration (in production, this would be more sophisticated)
        if not hasattr(self, "auth_configs"):
            self.auth_configs = {}

        self.auth_configs[module] = config

        # Log configuration
        self.audit_logger.log_event(
            "system",
            "auth_configured",
            {
                "module": module,
                "level": config.get("level"),
                "method": config.get("method"),
            },
        )


# Global connector instance
_identity_connector = IdentityConnector()


def get_identity_connector() -> IdentityConnector:
    """Get the global identity connector."""
    return _identity_connector


# 🔁 Cross-layer: Identity system integration

# Register with hub
hub = get_integration_hub()
hub.register_component("identity_connector", _identity_connector)