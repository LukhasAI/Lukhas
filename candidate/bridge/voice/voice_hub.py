#!/usr/bin/env python3

"""
██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

Voice Hub - Central coordination for voice subsystem
====================================================

Advanced voice synthesis, recognition, and emotional modulation hub
orchestrating the symphony of human-AI communication through adaptive
speech interfaces and cognitive voice processing architectures.

Agent 10 Advanced Systems Implementation
"""

import asyncio
from typing import Any, Optional

# Import high-priority voice components
from .context_aware_voice_modular import ContextAwareVoiceSystem
from .recognition import VoiceRecognition


class VoiceHub:
    """Central hub for voice system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.initialized = False

        # Initialize high-priority components
        self._initialize_core_services()

    def _initialize_core_services(self) -> None:
        """Initialize core voice services"""
        try:
            # Context-aware voice modulation (priority 1)
            self.context_voice = ContextAwareVoiceSystem()
            self.register_service("context_aware", self.context_voice)

            # Voice recognition engine (priority 2)
            self.recognition_engine = VoiceRecognition()
            self.register_service("recognition", self.recognition_engine)

            # Additional voice components can be registered here
            logger.info("voice_core_services_initialized")

        except Exception as e:
            logger.error("voice_service_initialization_failed", error=str(e))

    def register_service(self, name: str, service: Any) -> None:
        """Register a voice service"""
        self.services[name] = service
        logger.debug("voice_service_registered", service=name)

    async def initialize(self) -> None:
        """Initialize voice hub"""
        if self.initialized:
            return

        try:
            # Initialize voice services
            self.initialized = True
            logger.info("voice_hub_initialized")

        except Exception as e:
            logger.warning("voice_hub_initialization_failed", error=str(e))

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered voice service"""
        return self.services.get(name)

    def list_services(self) -> list[str]:
        """List all registered voice services"""
        return list(self.services.keys())

    async def process_voice_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """Process voice request through registered services"""
        try:
            results = {}

            # Use context-aware voice system
            if "context_aware" in self.services:
                context_service = self.services["context_aware"]
                if hasattr(context_service, "process_input"):
                    results["context"] = await context_service.process_input(
                        request_data.get("text", ""),
                        request_data.get("context", {}),
                    )

            # Use recognition service if audio data provided
            if "recognition" in self.services and "audio" in request_data:
                recognition_service = self.services["recognition"]
                if hasattr(recognition_service, "transcribe"):
                    results["recognition"] = await recognition_service.transcribe(
                        request_data["audio"]
                    )

            results["timestamp"] = asyncio.get_event_loop().time()
            return results

        except Exception as e:
            logger.error("voice_processing_failed", error=str(e))
            return {"error": str(e)}

    async def shutdown(self) -> None:
        """Gracefully shutdown voice services"""
        shutdown_tasks = []

        for service in self.services.values():
            if hasattr(service, "shutdown"):
                shutdown_tasks.append(service.shutdown())

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        logger.info("voice_hub_shutdown_complete")


# Singleton pattern for voice hub
_voice_hub_instance: Optional[VoiceHub] = None


def get_voice_hub() -> VoiceHub:
    """Get the global voice hub instance"""
    global _voice_hub_instance
    if _voice_hub_instance is None:
        _voice_hub_instance = VoiceHub()
    return _voice_hub_instance


# Export the hub for easy access
__all__ = ["VoiceHub", "get_voice_hub"]
__all__ = ["VoiceHub", "get_voice_hub"]
